# 原创轮独立验收

日期：2026-09-22。状态：门禁已建立，等待原创模型/软件冻结版本。

产品需求门G1：**PASS**，锁定`d33b74dba94b57000d1fa4714b13c33308f868f4`。已直接审PRODUCT_DECISION、HACKATHON_PRD、USER_JOURNEY、SOFTWARE_ALIGNMENT、T16–18及演示脚本，98d2d1c至d33b74d增量仅软件对齐回执。默认今日卡→封存→恢复，首次/卡住才Agent；封存先保存用户原句和原卡，失败不阻止停止；独立DEMO TIME不污染真历史。替代方案与竞品机制事实/产品推断有区分，吸引力有具体使用结果，仍未用户实测。此门不代替O1–O4。

当前不沿用旧版NO-GO：旧版本是第三方玩具附件，新版本按自身原创机构与试打工艺验收。未打印是O4 NOT_TESTED，不是O1自动失败。具体要求见ORIGINAL_CRITERIA.md。

| 门 | 当前结论 | 待收证据 |
|---|---|---|
| O1 数字制造试打包 | 待审 | 三原创SHA、完整机械件/校准/BOM/装配/运动/切片 |
| O2 软件安装闭环 | 待审 | 源码SHA、签名APK哈希、构建及安装运行、全流程/截图/错误测试 |
| O3 实机数据闭环 | NOT_TESTED | 板卡、固件、真实数据口与事件证据 |
| O4 实打体验 | NOT_TESTED | 明日样件装配、手感与保持/接口测试 |

模型分支：codex/original-pin-fidget、codex/original-press-spin、codex/original-orbit-fidget。软件：codex/android-demo。测试：codex/original-independent-testing。验收：codex/original-acceptance。分支名是追踪入口，不是验收SHA。

## 问题与证据追踪

尚无冻结版本，不能预写通过结论。每个发现记录ID/owner/优先级/版本/观察/解除条件；新版必须直接复审，不自动继承旧附件的通过或失败。

### 软件早期草稿反例（无提交SHA，待修订版重新核验）

已直接读取软件worktree的MainActivity.java、UsbTransport.java、firmware/src/main.cpp及说明；发现已发送软件owner/测试/协调。以下是草稿观察，不套用后续提交。

| ID / 优先级 | owner | 观察与用户影响 | 解除条件 |
|---|---|---|---|
| S-A01 / P1 | 软件 | USB只有OUT发送，无IN读帧/关联ACK/权限回调；选择任意首个USB设备 | 匹配设备/接口、权限生命周期、异步收帧、关联ACK与超时重连；测试不能以send成功代替设备保存 |
| S-A02 / P1 | 软件 | seal写SEALED、恢复写ACTIVE后界面将其当USB状态；失败自动模拟提交 | 模式独立持久字段且常驻；失败保持待交付，显式选择模拟才可模拟；封存/恢复/重启截图检查 |
| S-A03 / P1 | 软件/PM | completed布尔只显示0/1，无完整日期/恢复卡/回顾；Sealed仍可完成 | 按独立PM旅程实现最小完整状态与历史，封存保护/次日/已完成不重复/杀进程恢复测试 |
| S-A04 / P1 | 固件 | substring解析可被任务正文误触发；无ID/周期/版本/幂等；未检查存储就ack；无实体键事件 | 严格JSON/长度边界、错误拒绝、唯一事件、成功落盘才ack、真实KEY明确动作；编译与协议反例测试，实板另记 |
| S-A05 / P1 | 软件/PM | 单条输入被泛化动作替换、≤3结果未校验、静默截断短文本、返回编辑丢草稿/停车项 | Agent职责与可修改建议成立，边界校验/短文本确认/原输入停车项持久化，返回不丢内容 |
| S-A06 / P1 | 软件/测试 | 仅规则与构建证据，尚无安装/运行截图；真实LLM路径待实现 | 按产品范围交付明确模式，APK实际安装运行全流程；无key测试规则可通过O2相应模式，LLM不得假称 |

来源核对：已访问[M5官方规格](https://docs.m5stack.com/en/core/StickS3)与[尺寸图](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1207/K150-sticks3.pdf)，确认K150整机名义尺寸；下载模式需侧Reset可操作。接口可达检查应覆盖烧录维护，不只USB开口。

软件版本复审：`f042ce8b13354101e0ba3493e08722626d09f562`只增加构建脚本及CycleState/AgentClient骨架，MainActivity未接入新类，UsbTransport/firmware仍是上述草稿实现。S-A01..06未关闭，O2 NO-GO（只有构建基线），O3 NOT_TESTED且实现缺项。此事实已报协调继续推进；新增类/签名不代替用户入口结果。

### 原创首轮制造复核（等待修复冻结）

已直接阅读针板81c0682、环轨0fdf1ef的生成代码、README、验证数据及装配图；独立测试报告两者各9件STL实际PrusaSlicer无支撑切片退出0且无空挤出层。此处是中间证据，尚不授予O1通过。

- 针板：10根重力复位滑针、3.2mm行程；翻转复位，不宣称弹簧点击。16个塑料实例、8颗螺钉，校准需验证滑动与翻转。O-PIN-01定位耳孔外缘仅0.25mm，测试已要求至少1.2mm。
- 环轨：5个功能塑料件、4颗螺钉；无球簧也能旋转，球簧定位是可选玩法。O-ORB-01顶框沉孔口与boss同半径导致薄缘，测试要求增厚。M3x30名义全螺母啮合但无余牙，必须明确公差/倒角后的实际啮合条件。校准0.20仅比较片，不能暗示主件支持超出0.35–0.60范围；实体按键映射应引用最终固件而非自行定义。
- 按压旋转：待最终SHA；主体打印方向及分体轴套正在修订。PETG弹性件的机械效果不能用通用PLA切片成功替代。

首打候选排序尚未冻结。评价依据为完整玩法、校准与装配负担、防脱和打印风险；不得把CAD效果图当作手感实证。

### 软件新工作树复核（未冻结，2026-09-22）

新的USB接收、权限回调和JSON解析已出现，但尚不能关闭原缺陷。已汇总给协调者，待最终提交逐项复审：

1. USB重连使用共享connection/reading，旧reader可能读取新连接；负返回循环无detach处理；应使用连接代次及读线程隔离。
2. MainActivity连接尝试后即发送offer，尚未验证hello协议身份；超长帧清空后继续解析尾段，应丢弃至换行，手机与固件都需一致处理。
3. 固件先改RAM再persist，失败后同command/revision或seq重试可能直接ACK persisted:true。必须仅对已提交状态返回成功，失败回滚或采用临时事务状态。
4. MainActivity尚未消费实体event/status；event_ack未关联周期、指令、版本及期望序号。读帧存在不等于双向闭环。
5. 独立测试指出aeb100c APK缺uses-sdk、target<4阻止现代Android安装；等待修复APK实际安装，签名检查不替代安装证据。

以上是动态工作树观察，不将后续已修代码误判为仍有问题。O2/O3需固定SHA和对应APK/固件证据后重新定级。

### 冻结软件0daf340复审与可执行反例

版本：`0daf340988157b66cca29403c9e7492975b4533f`。协调提供APK SHA256 `882D4C97DAD8BB4106C67EA87F61B601CCC1B642DE8CE3E74D59CF6E07B4809B`，此处尚未独立核验安装与该哈希对应关系。固件编译下载工具链中，不能写编译通过。

确认改进：Android读线程使用局部connection及generation；Android超长帧discard到换行；设备ACK关联周期/指令/revision；固件失败回滚业务字段；Manifest已有min26/target35。上述仅为源码改进，不代表整个缺陷关闭。

仍需修复的协议P1：

- 固件persist在active写成功前递增snapshotVersion，失败回滚业务却不回滚version；重试可覆盖原提交槽，破坏双槽恢复。需故障注入slot/crc/active各写点。
- hello未验证protocol/device_id，status不匹配就发offer；complete/seal也能绕过握手发队首。须session级身份闸门覆盖全部业务出口。
- 实体event仅seq/type即改当前卡；缺完整身份关联。固件不消费event_ack或重放离线事件，手机status忽略state/last_seq，断线事件无法补同步。
- 初次status不匹配→offer→ack后不排出outbox，待发事件停滞。
- 固件超长帧仍清空后接收尾段，与Android修复不一致。
- connect并发线程共用成员连接，排队decode与write不带generation；快速重连仍可产生跨session回调/写入。

独立可执行证据：`state-probe/run.ps1`从Git固定SHA提取未修改的真实CycleState，使用JDK21及模拟SharedPreferences内存/磁盘行为运行。`result-0daf340.txt`记录6项复现；这不是Android安装或硬件测试。

| 反例 | 分级与可达性 | 结果 |
|---|---|---|
| CS01 新周期残留note/recovery/seq/outbox | P2，内部API；当前UI无重建周期入口 | REPRODUCED |
| CS02 demo次日→确认恢复→首页切USB | P1，UI可达，演示日和状态转真实 | REPRODUCED |
| CS03 NEXT未确认仍可completePhone | P2，内部API；首页会路由新卡，不能声称普通完成按钮可达 | REPRODUCED |
| CS04 commit=false封存后仍称phone_saved | P1，保存失败却成功提示，进程重启丢note | REPRODUCED |
| CS05 无身份绑定的seq1 complete | P1，MainActivity事件入口只传seq/type | REPRODUCED |
| CS06 真实日期未驱动next/resume/review | P1，USB模式无次日按钮且无日期转换 | REPRODUCED |

最小可交付修复：模拟与真实存储隔离或显式结束模拟后创建新真实周期；持久化失败必须返回错误并禁止保存成功提示；设备事件完整绑定且支持离线重放；真实日期转换进入恢复/新动作/回顾。O2完整旅程仍NO-GO；安装测试可独立继续。O3保持NOT_TESTED且源码仍有阻断项。

### 6883063修复回归

固定版本`6883063c63b9bea1dc658d5e62fa5ec120ad3e24`，新增StateProbeV2，旧probe与结果保留。命令：`state-probe/run.ps1 -Revision 6883063c63b9bea1dc658d5e62fa5ec120ad3e24 -Probe StateProbeV2`。原CS01–06六项均NOT_REPRODUCED：旧字段清理、显式新真实周期、ACTIVE守卫、失败返回值、事件绑定及次日转换已有针对性修复。

新增CS04B/CS07仍REPRODUCED：commit=false时内存已SEALED/DONE，返回首页可显示未落盘状态；complete重试受DONE guard阻止，重启后完成事实丢失。stub并非把失败误当成功：[Android官方SharedPreferencesImpl](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/app/SharedPreferencesImpl.java)的commit先修改内存，再等待磁盘写入结果。领域状态必须区分已持久化快照与失败待保存内容。

协议源码改进确认：snapshotVersion只在active提交成功后推进，固件超长帧丢弃至换行，关联offer ACK后发送队首，Android读帧与写操作增加generation。未关闭：connect本身仍并发使用共享成员；固件hello仅setup发送，重连握手缺明确定义；实体pending仅单字符串，离线complete(seq1)再seal(seq2)覆盖前者，重连仅seq2而手机last0严格+1拒绝，需FIFO或明确阻止未确认时继续产生事件。

以上已发作者和协调；属于修复回归，不声称APK安装、固件编译、板卡通信通过。
