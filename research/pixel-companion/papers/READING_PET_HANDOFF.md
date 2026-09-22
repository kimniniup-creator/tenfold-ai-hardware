# 阅读宠物第一版协调记录

2026-09-22，Kim 明确授权本研究任务协调既有美术、固件与烧录任务落地阅读第一版。本文为实施交接，不替代产品 owner 的正式 PRD。

## 已确定方向

- 135×240 竖屏宠物养成书签。形象沿用 Kim 对美术任务的最新要求：黑白塔奇克马；不恢复旧彩色小芽。
- 中间通用键用于自由按压、按摩式互动，立即本地响应；累计互动支持幼年到成长阶段。用户提出种菜等可能玩法，首版先完成宠物成长，不扩成完整农场。
- 标注首版仅会话打点：模式、序号、设备时间；没有纸书页码或电子书位置数据，不声称保存了页码。
- 模式为阅读、工作、运动、学习的上下文标签；阅读先跑通，其他标签不代表已实现专门功能。
- 文案简短自然，标记提示“记下这一处”；不每次点击弹文字，不将互动次数称为专注成绩、阅读页数或已完成任务。

## 实体约束与分工

- 官方 https://docs.m5stack.com/en/core/StickS3 的 PinMap 只有 KEY1/G11 与 KEY2/G12；另一实体键负责 reset/power/download，不映射业务。
- 两键降级：A 自由互动，B 松开时判定短按标记、长按切模式；长按不能先产生短按标记。
- 美术 owner：01a0c7df-f2a2-7ef3-aca8-dc4f8c8bb26b；独占已有美术 worktree。新文件 design/pixel-companion/portrait/、firmware/include/pet_portrait_assets.h。
- 资产拟接口：namespace pet_portrait；Stage{Young,Grown}；State{Idle,Press,Rebound,Happy,Rest,Mark}；32×32 单色、2 倍显示。最终以交付头文件为准。
- 固件和串口唯一 owner：01a0c5c6-3e14-7e80-b9c0-3e7159c57977；D:/tenfold-worktrees/pixel-firmware，codex/pixel-firmware。
- 软件 owner 报告旧 pixel-0.1 已在 COM10/303A:1001 运行，hello 为 240×135、board26，已有 8MB 备份及 digest 核验。此为旧版本证据，不能当本轮竖屏交付。
- 产品 owner：01a0c5b4-a19c-7810-8c6e-d8a87bb68f70，负责产品文档与最终整合；不重复派固件工程或开串口。

## 验收与研究边界

1. 新形象竖屏无裁切、文字可读，按下/松开可辨识。
2. 一次物理按下只计一次；持续长按不自动刷互动数。
3. 成长阈值明确为演示参数；批量持久化并验证重启恢复，不每次按键写闪存。
4. 短按标记一次，长按切模式一次，二者不重复触发；重启/电源键行为保持正常。
5. 断开 Agent 时本地互动仍可用；不以本地回退冒充 Agent 响应。
6. 烧录验证须区分写入成功、运行 hello、实际按键、屏幕视觉；没有后两项证据不能宣称全部通过。
7. 互动成长能否带来依恋、是否干扰阅读仍须实际用户测试。不能把连续点击、设备在线时长或宠物成长解释为专注改善。

协调状态：美术及固件已接受任务，等待新资产提交、集成与实板证据。本协调任务不接管串口。

## 后续协调证据

- 美术 bc1f45f 已交付：24 帧、两阶段、135×240 预览；协调任务独立运行 verify.py 通过并目视两阶段预览。已交固件接入。
- 软件报告启动误识别造成黑屏；独立热修复 1f6ac1047a3f860095063411081b596b220e4ffb 经真实 app 烧录与三次重启，均 board26/240×135/display_ready=true。新阅读稿必须带入修复。
- Kim 在美术任务进一步要求成年体差异、喂食/清理/进化、读完论文成长。bc1f45f 及 100 次互动成长仅临时链路原型，非最终美术/养成验收。新玩法仍由其对应任务完善，不能由点击次数推出阅读完成或合理舒压频次。
- 临时竖屏固件 0312a6beeb728803119b42bfdf9d77fd8c1de0bc 已仅 app 烧录。协调任务读取 reading-first-boot.ndjson，确认 build reading-0.2、135×240、board26、portrait-mono-24、state_selftest=true。此版本仍使用 bc1f45f 资产。
- 重启证据出现反例：随机启动 session 已变化，reading_session 却仍为 1；storage_ok=true 不能证明持久化。软件 owner 正修复，不能将首启动通过写成养成保存通过。
- 异步请 Kim 试实体按键与观察画面；reading-physical-1.ndjson 当前没有真实互动事件，按键和肉眼显示仍未验收。
- 诊断进一步证明：Preferences 写返回成功后立即读回 NOT_FOUND，存储 opened=true 但 boot_length=0；已加写后校验避免误报。软件保留原8MB及前后NVS备份，禁止无限重试写。
- 协调授权评估匹配bootloader精确区修复（前置：构建与分区参数核验、目标区备份/hash、回滚路径）。不得擦除NVS/整板或改分区。兼容性仅推断，是否修复须真实读回与重启证据。
- 修复实证：匹配当前Arduino构建的bootloader后立即读回340字节成功；协调任务独立读取reading-matched-boot2.ndjson，loaded=true、boot_session=1、current_session=2、readback_ok=true、135×240、board26。仅bootloader精确区及app写入，未擦NVS或改分区。软件报告f1a90cf资产已一并接入。
- 这证明非零会话存档跨重启恢复，不等于已验证真实点击/成长记录持久化；当前真人互动仍为0，后者须用户按键后再核。
- 最终软件交付：源代码 a04f3e5fab7df357e9fa5604a70b90d7688a2f73；文档 3421a98037f467ec799e074ef8f97e7b0538b5b5，codex/pixel-firmware 已远端核验。运行 app SHA A6A46C122711407B13DF93C7C6BCEC70D3E21278D0097FF014FBEF2E4A7931C6。
- 非零互动持久化通过：boot3 lifetime10，boot4 presses_total0/lifetime10、reading_session4、boot_session3、loaded340/readback真；reading-nonzero-restart.ndjson 和 reading-reopen-check.ndjson。无按键注入。COM10已释放、设备运行。
- 未验：B标记与长按切模式、A长按时序、真实掉电、100次成长目视、竖屏肉眼显示、Agent实按链路。一次25秒串口无回应在受控重启后恢复，根因未知，不标已修。用户实板反馈待返回。
- 已将综合SHA、边界与证据交产品owner，阅读临时首版已烧录；后续养成规则另行迭代。
