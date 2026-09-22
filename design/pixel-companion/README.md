# 像素陪伴资产 v1

## 文案接入状态（2026-09-22）

本轮固件与bridge已统一使用以下五句严格原文白名单：`我在。`、`我在，陪你待会儿。`、`嗯，接住了。`、`慢慢来就好。`、`安静待着，也很好。`。运行协议为 `action` + `text`，动作白名单为小写 `blink` / `happy` / `rest`；不使用phrase_id。权威实现是 `bridge/companion.py` 的 PHRASES/ACTIONS 和 `firmware/src/main.cpp` 的 validText/receive，修改时须双端保持一致。

本目录 `copy.json` 的八句及其policy只作为后续设计候选，未接入首版，不能作为当前运行协议或验收依据。产品已决定不为八句数量或ID重构已实测链路。`rest` 是角色动画；`quiet` 是用户通过B选择的偏好，两者独立。Agent可在非安静模式选择rest动画，但不能改变quiet。安静模式拒收Agent回复。

软件报告五句白名单已通过真实模型选句；美术任务只核对双端源码的一致性，未独立重做模型请求或实板验证。首版软件采用2倍64×64角色、中文两行及独立底部按键提示；本目录3倍英文屏幕图保留为美术布局示例，不代表最终固件截图。

原创杏色小团子：不对称双芽、阶梯轮廓、小短脚。32×32 像素，7 个可见颜色加透明；没有现成角色描摹、饥饿值、死亡或惩罚。Claude Fable 本机额度已耗尽，本版由当前 Codex 执行确定性离线绘制。

官方 [StickS3 规格](https://docs.m5stack.com/en/core/StickS3) 为 135×240；横屏布局为 240×135，实际板卡旋转由软件确认。预览是设计渲染，不是实板截图。

## 使用

`python design/pixel-companion/generate.py`（Python 3，Pillow 12.2；无需网络）生成所有 PNG、palette.json 和 `firmware/include/pet_assets.h`。修改生成脚本，不手改头文件。帧数据 10240 字节，调色板 16 字节；无堆分配。

```cpp
#include "pet_assets.h"
// display supports fillRect(x,y,w,h,color); caller owns background clearing.
template<class Display>
void drawPet(Display& display, pet_assets::State state, uint32_t elapsed) {
  const auto frame = pet_assets::frameIndex(state, elapsed);
  for (uint8_t y=0; y<32; ++y)
    for (uint8_t x=0; x<32; ++x) {
      const auto p = pet_assets::pixel(frame,x,y);
      if (p != pet_assets::kTransparent)
        display.fillRect(72+x*3,24+y*3,3,3,pet_assets::kPalette[p]);
    }
}
```

数组为逐行 uint8 索引；透明索引 0，RGB565 是逻辑颜色值，逐像素 fillRect 不需端序交换。像素坐标越界返回透明。建议软件使用局部 sprite 缓冲或按行合并绘制，避免反复全屏清空闪烁。头文件只在一个渲染编译单元包含，避免 static 数组跨单元重复。

| 状态 | 帧 | 时序与含义 |
|---|---|---|
| Idle | 0–1 | 700 ms/帧，轻微起伏 |
| Blink | 2–3 | 90 ms/帧；软件在180 ms后回idle |
| Press | 4–5 | 首90 ms闭眼压扁，其后睁眼；软件在松开后回弹/idle |
| Happy | 6–7 | 首180 ms轻跳，其后高位；建议360 ms后回idle |
| Rest | 8–9 | 1200 ms/帧，闭眼安静，无催促 |

frameIndex 不切换业务状态、不读时钟，elapsedMs 为进入该状态以来的毫秒。A反馈优先，B安静模式是软件持久状态，不能被Happy或Agent回复退出。静置时不连续播放Happy。Blink与Happy的退出由软件控制。

## 布局

屏幕左右边距12 px；顶部9–25 px为小标题/来源；宠物画布 x72 y24，3倍放大96×96；底部119 px为按键提示。真正着色的宠物不与顶部或底部文字相碰。若加入Agent短句，应另留一行并把宠物改为2倍64×64，禁止把长文压在宠物上。示例英文只用于可复现预览，正式文案/字体归软件。

`frames-preview.png` 为4倍帧集；`screen-preview.png` 为四个屏幕的2倍预览；`*-screen.png` 为精确240×135像素。全部最近邻放大，无抗锯齿。

## 验证边界

已离线生成并目视检查帧集与屏幕布局；头文件接口、索引范围和生成确定性由本目录验证脚本检查。尚未在实板查看色彩、旋转、响应延迟和刷屏效果；由软件独占COM9集成并验证，不在美术任务烧录。
