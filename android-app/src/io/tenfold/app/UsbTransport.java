package io.tenfold.app;

import android.app.Activity;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.hardware.usb.UsbConstants;
import android.hardware.usb.UsbDevice;
import android.hardware.usb.UsbDeviceConnection;
import android.hardware.usb.UsbEndpoint;
import android.hardware.usb.UsbInterface;
import android.hardware.usb.UsbManager;
import android.os.Handler;
import android.os.Looper;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.json.JSONObject;

/** Android USB Host CDC-ACM transport with permission callback, framing and bidirectional bulk I/O. */
final class UsbTransport {
  interface Listener { void onUsbState(String state); void onFrame(JSONObject frame); void onUsbError(String code); }
  private static final String ACTION_PERMISSION="io.tenfold.app.USB_PERMISSION";
  private final Activity activity; private final UsbManager manager; private final Listener listener;
  private final Handler main=new Handler(Looper.getMainLooper()); private final ExecutorService writes=Executors.newSingleThreadExecutor();
  private UsbDeviceConnection connection; private UsbEndpoint input; private UsbEndpoint output; private volatile boolean reading; private volatile int generation; private volatile boolean connecting;
  UsbTransport(Activity activity,Listener listener){
    this.activity=activity;this.listener=listener;manager=(UsbManager)activity.getSystemService(Context.USB_SERVICE);
    IntentFilter filter=new IntentFilter(ACTION_PERMISSION);filter.addAction(UsbManager.ACTION_USB_DEVICE_DETACHED);
    if(android.os.Build.VERSION.SDK_INT>=33)activity.registerReceiver(permissionReceiver,filter,Context.RECEIVER_NOT_EXPORTED);else activity.registerReceiver(permissionReceiver,filter);
  }
  UsbDevice findDevice(){for(UsbDevice device:manager.getDeviceList().values())if(hasCdcInterface(device))return device;return null;}
  void requestOrConnect(){
    if(connection!=null){postState("USB_CONNECTED_WAITING_HELLO");return;}
    UsbDevice device=findDevice();if(device==null){postState("NO_SUPPORTED_USB_DEVICE");return;}
    if(!manager.hasPermission(device)){PendingIntent p=PendingIntent.getBroadcast(activity,0,new Intent(ACTION_PERMISSION).setPackage(activity.getPackageName()),PendingIntent.FLAG_IMMUTABLE|PendingIntent.FLAG_UPDATE_CURRENT);manager.requestPermission(device,p);postState("USB_PERMISSION_REQUIRED");return;}
    startConnect(device);
  }
  private boolean hasCdcInterface(UsbDevice device){for(int i=0;i<device.getInterfaceCount();i++){int cls=device.getInterface(i).getInterfaceClass();if(cls==UsbConstants.USB_CLASS_COMM||cls==UsbConstants.USB_CLASS_CDC_DATA)return true;}return false;}
  private synchronized void startConnect(UsbDevice device){if(connecting)return;connecting=true;new Thread(()->{try{connect(device);}finally{connecting=false;}},"tenfold-usb-connect").start();}
  private void connect(UsbDevice device){
    closeConnection();connection=manager.openDevice(device);if(connection==null){postError("OPEN_FAILED");return;}
    int controlIndex=-1;UsbInterface controlFace=null,dataFace=null;UsbEndpoint selectedIn=null,selectedOut=null;
    for(int i=0;i<device.getInterfaceCount();i++){UsbInterface face=device.getInterface(i);if(face.getInterfaceClass()==UsbConstants.USB_CLASS_COMM&&controlFace==null){controlFace=face;controlIndex=face.getId();}if(face.getInterfaceClass()==UsbConstants.USB_CLASS_CDC_DATA){UsbEndpoint candidateIn=null,candidateOut=null;for(int j=0;j<face.getEndpointCount();j++){UsbEndpoint endpoint=face.getEndpoint(j);if(endpoint.getType()!=UsbConstants.USB_ENDPOINT_XFER_BULK)continue;if(endpoint.getDirection()==UsbConstants.USB_DIR_IN)candidateIn=endpoint;else candidateOut=endpoint;}if(candidateIn!=null&&candidateOut!=null){dataFace=face;selectedIn=candidateIn;selectedOut=candidateOut;break;}}}
    if(dataFace==null||!connection.claimInterface(dataFace,true)||(controlFace!=null&&!connection.claimInterface(controlFace,true))){postError("CLAIM_FAILED");closeConnection();return;}
    input=selectedIn;output=selectedOut;
    if(input==null||output==null){postError("CDC_BULK_ENDPOINTS_MISSING");closeConnection();return;}
    if(controlIndex>=0){byte[] lineCoding=new byte[]{0x00,(byte)0xC2,0x01,0x00,0x00,0x00,0x08};int wrote=connection.controlTransfer(0x21,0x20,0,controlIndex,lineCoding,lineCoding.length,1000);int dtr=connection.controlTransfer(0x21,0x22,3,controlIndex,null,0,1000);if(wrote<0||dtr<0){postError("CDC_INIT_FAILED");closeConnection();return;}}
    reading=true;int session=++generation;UsbDeviceConnection localConnection=connection;UsbEndpoint localInput=input;
    new Thread(()->readLoop(session,localConnection,localInput),"tenfold-usb-reader").start();postState("USB_CONNECTED_WAITING_HELLO");
  }
  void send(JSONObject frame){
    final String wire=frame.toString()+"\n";final int session=generation;final UsbDeviceConnection c=connection;final UsbEndpoint ep=output;
    writes.execute(()->{if(session!=generation||c==null||ep==null){postError("USB_NOT_CONNECTED");return;}byte[] bytes=wire.getBytes(StandardCharsets.UTF_8);if(bytes.length>4096){postError("OUTBOUND_FRAME_TOO_LARGE");return;}int count=c.bulkTransfer(ep,bytes,bytes.length,2000);if(session!=generation)return;if(count!=bytes.length)postError("USB_WRITE_FAILED");else postState("USB_SENT_WAITING_ACK");});
  }
  private void readLoop(int session,UsbDeviceConnection localConnection,UsbEndpoint localInput){ByteArrayOutputStream line=new ByteArrayOutputStream();byte[] buffer=new byte[512];boolean discarding=false;while(reading&&session==generation){int count=localConnection.bulkTransfer(localInput,buffer,buffer.length,500);if(count<0)continue;if(session!=generation)break;for(int i=0;i<count;i++){int value=buffer[i]&0xFF;if(value=='\n'){if(!discarding&&line.size()>0)decode(line.toByteArray(),session);line.reset();discarding=false;}else if(value!='\r'&&!discarding){if(line.size()>=4096){line.reset();discarding=true;postError("FRAME_TOO_LARGE");}else line.write(value);}}}if(session==generation)postState("USB_DISCONNECTED");}
  private void decode(byte[] bytes,int session){try{JSONObject frame=new JSONObject(new String(bytes,StandardCharsets.UTF_8));main.post(()->{if(session==generation)listener.onFrame(frame);});}catch(Exception error){postError("INVALID_JSON_FRAME");}}
  private final BroadcastReceiver permissionReceiver=new BroadcastReceiver(){@Override public void onReceive(Context context,Intent intent){if(UsbManager.ACTION_USB_DEVICE_DETACHED.equals(intent.getAction())){closeConnection();postState("USB_DETACHED");return;}if(!ACTION_PERMISSION.equals(intent.getAction()))return;UsbDevice device=intent.getParcelableExtra(UsbManager.EXTRA_DEVICE);boolean granted=intent.getBooleanExtra(UsbManager.EXTRA_PERMISSION_GRANTED,false);if(granted&&device!=null)startConnect(device);else postError("USB_PERMISSION_DENIED");}};
  private void postState(String state){main.post(()->listener.onUsbState(state));} private void postError(String code){main.post(()->listener.onUsbError(code));}
  void close(){try{activity.unregisterReceiver(permissionReceiver);}catch(Exception ignored){}writes.shutdownNow();closeConnection();}
  private synchronized void closeConnection(){reading=false;generation++;if(connection!=null)connection.close();connection=null;input=null;output=null;}
}
