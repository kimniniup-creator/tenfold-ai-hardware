# 黑白塔奇克马 · 竖屏阅读书签资产

这是《攻壳机动队》塔奇克马的同人像素改绘，不是原创角色。按Kim最新选择取消旧彩色小芽。修订版幼体为小圆舱、单眼、两只短轮足；成年才展开完整多足底盘、后舱和天线，避免只改细节。幼体是养成同人衍生形态，不是动画官方设定。最新需求为读完论文推动成长、点击负责照料，详见CARE_RESEARCH.md；此前累计点击成长仅是旧版原型参数。死亡重开或休眠机制待Kim回复，资产不含生存逻辑。

## 交付与接口

- `firmware/include/pet_portrait_assets.h`：新独立接口，不覆盖旧 `pet_assets.h`。`namespace pet_portrait`；`Stage {Young,Grown}`；`State {Idle,Press,Rebound,Happy,Rest,Mark}`。
- `frameIndex(Stage, State, uint32_t elapsedMs)` 返回0–23；非法枚举回第0帧。`pixel(frame,x,y)` 返回0黑/1白，越界返回0。无透明，背景黑色。
- `kFrames[24][128]` 是逐行1bit位图，每行4字节，每字节最高位在左。共3072字节；`kPalette[2]` 是逻辑RGB565黑/白。不要当作1024字节索引帧或直接RGB565数组。
- 32×32源帧，屏幕135×240，2倍绘制64×64，左上角(35,74)。每次重绘完整黑白64×64区域，防止动作残影。建议缓冲后推屏。
- `manifest.json` 包含阶段、状态、位置、文案和资产顺序。PNG均为1bit；两个 `*-portrait-preview.png` 为2倍整屏预览，不是实板截图。

```cpp
#include "pet_portrait_assets.h"
template<class Display>
void drawPortraitPet(Display& display, pet_portrait::Stage stage,
                     pet_portrait::State state, uint32_t elapsedMs) {
  const auto f=pet_portrait::frameIndex(stage,state,elapsedMs);
  for(uint8_t y=0;y<32;++y)
    for(uint8_t x=0;x<32;++x)
      display.fillRect(35+x*2,74+y*2,2,2,
        pet_portrait::kPalette[pet_portrait::pixel(f,x,y)]);
}
```

## 状态与按钮

| 状态 | 两帧间隔/建议时长 | 反馈 |
|---|---|---|
| Idle | 850ms循环 | 机身轻移、镜头巡视 |
| Press | 80ms后第二帧 | 支脚压低；新有效按下可立即重置 |
| Rebound | 100ms后第二帧，建议200ms退出 | 松开抬起 |
| Happy | 160ms循环，建议480ms退出 | 举机械臂；偶尔触发，避免每下弹文案 |
| Rest | 1400ms循环 | 收脚、镜头横线；与用户quiet偏好分开 |
| Mark | 160ms后第二帧，建议650ms退出 | 小书签与确认点；仅保存成功后显示 |

frameIndex只选帧，不累计互动、不决定成长门槛、不管理按键/持久化/quiet。软件负责状态退出和优先级：有效轻按即刻压扁，松开回弹；按住不能重复计数。长按换模式与短按业务需互斥，不在未达阈值前执行标记。具体哪个业务键承担长按由硬件实现确认；reset/power/download不作第三业务键。

底部两行：`轻按互动`、`侧键标记` / `长按换模式`。顶栏为阅读与本地/Agent来源。首版只跑阅读；工作/健身/学习是模式候选，不在预览冒充已实现入口。

默认与连续点击保持一句“陪你读会儿”，只动角色。安静显示“安静陪着你”；会话打点成功可短暂显示“记下这一处”。这些是本地UI文案，不修改旧版Agent五句白名单或协议。当前只做会话打点，没有纸书页码或电子书位置，不能提示已保存书本位置或下次从这里继续。

## 再生成与验收

Python 3 + Pillow：`python design/pixel-companion/portrait/generate.py`；`python design/pixel-companion/portrait/verify.py`。Windows默认读取宋体；其他系统用 `PET_PREVIEW_FONT` 指向支持中文的字体。字体只用于预览，未随仓库分发；实机字体由固件选择。

脚本验证1bit帧、24帧区别、头文件位图与PNG逐像素一致、135×240整屏尺寸、文字不越界、输出可重复。ESP32S3编译器检查头文件C++11语法。美术已目视检查两阶段预览；实际板卡方向、按键映射、字形与刷新延迟待固件任务验证，本任务不占串口、不烧录。
