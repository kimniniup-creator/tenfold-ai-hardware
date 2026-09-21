package io.tenfold.app;
import android.app.*;import android.content.*;import android.hardware.usb.*;import java.nio.charset.StandardCharsets;
/** CDC-style bulk endpoints; M5 firmware owns validation and sends ACK only after persistence. */
final class UsbTransport {
 private final Activity activity; private final UsbManager manager; private UsbDeviceConnection conn; private UsbEndpoint out;
 UsbTransport(Activity a){activity=a;manager=(UsbManager)a.getSystemService(Context.USB_SERVICE);}
 UsbDevice findDevice(){for(UsbDevice d:manager.getDeviceList().values()) return d;return null;}
 void requestOrConnect(){UsbDevice d=findDevice();if(d==null)return;if(!manager.hasPermission(d)){PendingIntent p=PendingIntent.getBroadcast(activity,0,new Intent("io.tenfold.USB_PERMISSION"),PendingIntent.FLAG_IMMUTABLE);manager.requestPermission(d,p);return;}connect(d);}
 private void connect(UsbDevice d){conn=manager.openDevice(d);if(conn==null)return;for(int i=0;i<d.getInterfaceCount();i++){UsbInterface f=d.getInterface(i);for(int j=0;j<f.getEndpointCount();j++){UsbEndpoint p=f.getEndpoint(j);if(p.getDirection()==UsbConstants.USB_DIR_OUT&&p.getType()==UsbConstants.USB_ENDPOINT_XFER_BULK){conn.claimInterface(f,true);out=p;return;}}}}
 boolean send(String json){if(out==null)requestOrConnect();if(out==null||conn==null)return false;byte[] b=(json+"\n").getBytes(StandardCharsets.UTF_8);return conn.bulkTransfer(out,b,b.length,1500)==b.length;}
}
