# Tenfold 十日环｜工作记录

## 2026-09-22 方向更新：注意力与专注

用户经原协调任务明确将产品与汇报核心转向注意力/专注，候选标题为 Attention Is All You Need；Agent机制尚未确定。既有像素陪伴是已实现技术原型，不再作为新核心价值的定案。保留按键、屏幕、节奏摘要、USB桥接与硬件验证作为可复用基础；具体功能在机制提案评审后更新，不自行增加专注分数、情绪推断或未经验证的效果宣称。

机制汇报由任务01a0c82e-9815-7e91-aa07-386a37d8d611负责，其owner汇总后向产品交换接口；部门内例行进展仅写WORKLOG/HANDOFF，子任务只向直接owner报告交付、真实阻塞、接口需求或范围/结论变更。


## 2026-09-22｜像素陪伴整合验证

- 独立美术、固件、USB桥接及验收记录已集成；PRD限定五句已审文案与动作，按压不解释为情绪诊断。
- 整合工作树 PlatformIO 完整编译成功：RAM 22892 bytes，Flash 717085 bytes；固件 SHA256 0544E8E88BEBDB44DA2C39AD8D507F25DF6B1D3A4C00FB04A8F870EB4B276DEB（构建路径不同可使二进制hash不同）。
- 原创10帧确定性、调色板、屏幕尺寸校验通过；桥接6项测试通过，含真实Content-Length EOF与8秒网络停顿子进程终止。独立最终复测另见testing/acceptance记录。
- 实板仍未写入：USB已枚举，但ROM握手超时；已向Kim请求保持USB连接并按官方步骤进入下载模式。等待动作后软件唯一串口owner继续完整备份、烧录、物理按键与屏幕验收。Lucas CLI本机不可用，正常动作请求已发出。
- 不把编译/真实合成摘要模型请求冒充板端到端成功。

## 2026-09-22｜M5像素陪伴重新开工

- Kim授权PRD、固件、必要软件、美术与实板全套开发；取消本轮外壳。PRD为docs/hackathon/product/PIXEL_COMPANION_PRD.md。
- 产品任务接协调，旧总控退出写入。背景整合worktree D:/tenfold-worktrees/pixel-integration，分支codex/pixel-companion。
- 软件复用01a0c5c6-3e14-7e80-b9c0-3e7159c57977；测试复用01a0c5b4-aff1-7102-85c2-bb1a66b8368f；验收复用01a0c5b4-bd94-7110-94a8-5b2c9e190508；新美术01a0c7df-f2a2-7ef3-aca8-dc4f8c8bb26b。
- COM9发现USB VID303A:832B候选，唯一串口/烧录租约给软件。备份原flash再更新，不无故全擦。实板型号、烧录和物理按键证据待软件回传。
- 美术32x32索引帧及RGB565调色板，横屏240x135；实际屏幕再核。Agent桥接先USB，密钥仅主机环境配置；无网设备独立可玩。
## 2026-09-22｜阅读版聚焦收尾

- 保存失败锁止期间的屏幕提示改为“保存失败，请重启”，不暗示再次标记能解锁。
- 阅读竖屏尚无Agent显示/入口，rhythm只保留遥测，candidate恒false且不arm请求；不冒充Agent已经上屏。文案独立任务继续。
- 新增无candidate门控回归：0/3/10/10000次均不触发模型；7项bridge测试通过。仅app更新，已验证匹配bootloader不再写入。
- eaef7c0编译后仅app写入并hash校验；新app81182568…E5ED5F，715248bytes。实板session5/135x240/board26启动已保留lifetime25、mark1；本轮真实6次按键rhythm candidate=false，随后连续互动到48，不再重启干扰用户。日志.delivery/reading-telemetry-only.ndjson。关开串口一次5秒无回包，间歇通信仍未定位。

## 2026-09-22｜阅读保存反例与匹配启动链修复

- 首版发现会话重启仍1；新增storage_query揭示putBytes返回成功但立即读回NOT_FOUND，非schema长度错误。已加入逐次读回比对、失败锁止，禁止无限重写故障NVS。
- 原UIFlow启动程序IDF5.4.2-dirty搭配当前Arduino2/IDF4应用；精确备份启动区并核对分区边界后，仅改匹配bootloader和app，不发NVS擦除、不改分区。匹配后读回340字节，三次启动session1→2→3成功。底层兼容失效机理尚未证明。
- 当前app SHA A6A46C122711407B13DF93C7C6BCEC70D3E21278D0097FF014FBEF2E4A7931C6；f1a90cf资产原样集成。6项bridge测试、24帧资产校验和编译通过。
- 原始闪存/NVS/串口证据仅保留忽略目录.delivery。细节与恢复哈希见docs/pixel-companion/READING.md；真人按键、屏幕和实体断电不能用编译或session保存替代。
- 第三次启动现场收到10次设备互动（未注入），尚待现场动作关联及重启非零计数验证。Agent文案按Kim要求拆为独立用户任务，禁止该任务占COM10或烧板。
- 后续受控重启已验证session4、presses_total0、lifetime10，340字节loaded/readback均真；再次打开串口同样读回，非零设备输入计数保存PASS。期间一次约25秒只读请求无回应，重启恢复，原因仍未知；B标记/长按模式/实体掉电/屏幕目视/Agent实按端到端未验。

## 2026-09-22｜竖屏阅读原型与黑屏热修

- 现场pixel0.1黑屏读取到board155/0x0；独立pixel-display-fix分支1f6ac10已修复板型缓存并仅app烧录，3次受控重启board26/240x135/display_ready=true，仍区分目视确认。
- 阅读版正在接新24帧黑白资产（6aad542），A真实互动、B短标记/长模式、批量NVS；100次成长仅demo，不扩喂食/清理/论文完成。
- readingSelfTest为状态机测试，真实按键和屏幕须另验。详细接口docs/pixel-companion/READING.md。

## 2026-09-22｜像素陪伴新方向

- 15:32 用户经产品任务回复“亮了，推进”后重新检查：COM9仍303A:832B，Windows USB Composite/Ports均OK；default与no_reset握手仍Write timeout，没有chip回应，未备份也未写flash。已停止无效重试，产品统一确认是否绿灯闪烁，保持实板未验边界。

- 独立 codex/pixel-firmware 分支；保留旧 android-demo 未提交多承诺稿，不覆盖旧发布。
- 接入原创5状态10帧、本机A互动/B安静、USB节奏摘要与严格短句Agent桥接。
- 编译通过；主机独测0e64612 16/16通过，验收8项通过；随后加强全链路网络8秒子进程截止，待复测。
- DeepSeek真实合成摘要请求通过source=agent，非实板输入；密钥仅环境变量。
- COM9握手两种重置均超时，未改写flash。等产品协调手动下载模式，随后备份再烧录。
- 详细协议与边界见 docs/pixel-companion/SOFTWARE.md。
- 19824c6 新增5项真实函数测试全部通过，真实本地TLS卡住反例8.048秒完成fallback；真实provider脱敏证据见docs/pixel-companion/provider-evidence.json。固件SHA256 DCB0DCE7BF0C0AE5B41C88EE8947DF067F3AC27D63E4B5F5E614A075D2CDA079。

## 2026-09-22｜原创整机与 APK 夜间交付

- 用户明确替换此前“原玩具适配附件”范围：从零原创三版机械 EDC，M5StickS3 为首个板型，明天试打；不再等待原玩具尺寸。
- 用户再次强调：产品经理先研究真实用户场景和硬件价值，再与软件任务对齐，不采用协调者未经论证的通用任务流水线。
- 三个建模任务分别推进原创针阵/触觉滑块、按压旋转、捕获环轨；独立测试与验收任务同步更新门禁。
- 新可见软件任务 `01a0c5c6-3e14-7e80-b9c0-3e7159c57977` 负责 APK、任务 Agent、硬件通信与完整 UI，独占后台 worktree。
- 当前来源：官方 M5StickS3 结构文件已由环轨作者读取并共享。数字检查与实打印结论分开；尚无用户打印机型号，先按明确通用参数做切片筛查。
- 协调者负责最终集成、打包、远端恢复证据和通过已确认 offerlai 身份发送最终 APK。
- 产品已与软件直接对齐“今天到这里，明天接得上”，补齐官方竞品及 GitHub 方案取舍；产品审查覆盖真实 APK 截图，旧版视觉尚不放行。
- 原创首轮共 40 种 STL 已由独立任务实际切片（针阵9、环轨9、旋压22）；定位耳/沉头薄缘修订须按新 SHA 复测，不能沿用首轮通过结论。
- Android 模拟器从官方镜像建立，已实际安装启动候选 APK 并测试持久恢复；签名更换、恢复动作丢失、系统栏重叠等发现已派修。
- 验收任务以真实 CycleState 配合存储故障 stub 复现并驱动修复，最新一轮八个状态反例关闭；固件跨卡 FIFO 与时钟握手、最终视觉/升级测试仍在收口。

## 2026-08-03｜GitHub 首次归档

### 结果

- Kim 确认十日机械盘外形方向。
- 整理正式 PRD、工业设计规范和跨硬件 / 固件 / App / AI 实现方案。
- 收录已验收的外观渲染、交互 HTML 和 2026-07-22 市场研究底稿。

### 证据

- `docs/PRD.md`
- `docs/INDUSTRIAL_DESIGN.md`
- `docs/IMPLEMENTATION.md`
- `design/Tenfold十日机械盘-v2.png`
- `prototype/Tenfold十日环-v2.html`

### 卡点

- 渲染不是 CAD；十珠锁定 / 复位、公差、天线、电池和认证仍需工程验证。
- BOM 为工程估算，不是供应商报价。

### 下一动作

- 制作 P0 十珠机械样机和 46 / 48 mm 握持模型，再决定 EVT 结构。

## 2026-09-22｜Android USB P0

### 结果

- 新增可安装 Android P0：离线收敛、用户确认、状态持久化、完成/封存/恢复和清楚的模拟设备标记。
- 新增 M5StickS3 PlatformIO 固件源和 UTF-8 换行 JSON USB 协议。

### 边界

- Android 端实现 USB Host bulk 端点发现、系统权限申请和传输；当前没有接入板卡，因此不得称设备 ACK 或实机闭环已验证。
- 早期候选仅有离线规则；后续真实 Agent 接口已实现，云端请求仍未使用实际凭证验证。

## 2026-09-22｜原创整机与 Android 最终收口

- 三版原创整机已集成：针板 e76eb52、环轨 7a370bc、旋压 5ef4013。环轨光滑版为唯一首打推荐；针板完整重力玩法备选，旋压完整模式依赖 PETG，侧键原位访问有限。
- 针板三块排版板及环轨九件已由独立测试实际切片。旋压最终变件与混合紧固正在独立复核，实物打印未进行。
- Android a5b99b0 已集成；候选 APK SHA-256 为 34BB815E483BBA25D60DEEF145F5050B8219F912558EDF4898E1158F8FA7513D。15项状态/ACK/归档反例已由独立验收关闭，最终模拟器 T19 与产品视觉复验进行中。
- 可选 HTTPS Agent 已实现；未使用真实云凭证调用。Android USB 与 M5 固件待真实板/手机联调，固件真实编译仍在推进。
- 稳定开发签名保存在主仓和软件工作树各自的忽略目录 .signing，未进入 Git。最终交付仅打包经过哈希冻结的 APK，不以重新构建的不同哈希替代验收包。
- 新增 docs/hackathon/DELIVERY.md 与 scripts/package_delivery.py；待最终验收结果集成后生成三款 ZIP、APK 和 SHA256SUMS，再上传 GitHub Release 并经 offerlai 发送给 Kim。

### 最终审图发现的 R17 补漏

- 三款打印包和 34BB APK 已进入 GitHub 草稿，服务端四附件 SHA 与本地一致，尚未发布或发送。
- 总控发现：已确认但未完成/未封存的 ACTIVE 卡跨日未写本日快照；当前设备事件只改 phase，没有更新每日事实。34BB 已封存路径通过不能覆盖此缺口。
- 已要求软件最小修复，并由独立验收新增跨日/真实事件状态反例、测试任务增量跑新 APK。保留原 T19 证据，最终包必须更换精确哈希后再发布。非阻断图例文案不重开设计。

### 2026-09-22 收口证据

- Android 冻结候选源码 `6e2bf0e`，APK SHA-256 `B9604D2572CAD083F2A72D1D95628985EFBDB565E93FA4B9A3BBFB19C76259A8`，稳定签名证书 SHA-256 `EB55B62C374F6A58766625F52B83BA34B17E8A6B8C0D2CB95257781884CB153A`。
- 独立状态反例探针共 22 项全部关闭；模拟器覆盖安装、冷启动、十日回顾和恢复路径由独立测试任务复核。
- 固件以 PlatformIO Espressif32 6.12.0、M5Unified 0.2.22、M5GFX 0.2.29、ArduinoJson 7.4.3 编译并链接成功：RAM 22,684 B（6.9%），Flash 716,517 B（21.4%）。
- PlatformIO 无设备上传 dry run 给出精确烧录偏移：bootloader `0x0000`、partitions `0x8000`、boot_app0 `0xe000`、app `0x10000`。
- R05 增量把完成事实按日独立持久化，同日 revision、封存和重启均不能再次完成；跨日才重新允许。板端 P0 明确限定单周期，不自动接受新 cycle，以免静默丢弃离线事件。
- 最终固件发布包 `firmware/release/tenfold-firmware-p0-final.zip` SHA-256 为 `629A330BA42C19D713EAB3F454DF322A5099144627589B28FF294F12D2F9187A`；二进制按发布资产处理，不纳入 Git，包内附精确版本清单与实际许可证原文。
- 真实 M5StickS3、Android OTG 和云 LLM 未测试，保持明确 `NOT_TESTED`，不可由编译/模拟证据替代。

### 最终验收与交付

- 独测最终 c6f044b、产品最终 a8cd787、验收最终 f78d5da 已合并。三款 O1 数字制造 PASS；APK B960 的 O2 本地模拟运行 PASS_SCOPED；O3 实板与 O4 实打仍 NOT_TESTED。
- 固件 0e7b044 修正按日完成事实保护，698e344 补齐真实依赖许可文本；最终固件 ZIP 629A330B…D2F9187A，app 二进制 FB0EB0D7…236EC09 不变。
- 最终五项附件通过 scripts/package_delivery.py 从固定 Git 版本和精确哈希生成，公开校验清单保存在 docs/hackathon/release-manifest.json。
- 2026-09-22 06:19，GitHub `v0.1.0-hackathon` 已发布为预发布版本，五项附件服务端 SHA 与本地完全一致；重新下载公开 APK 后哈希仍为 B960。
- APK、首打 Orbit ZIP 和完整交付说明均已通过 offerlai 实际发送给 Kim，三条消息回读确认附件名称、正文与 bot 身份。私人会话信息只保留本地，不进入公开仓库。
- 全部已授权数字产物交付完成。实物打印、真实手机/M5联调及云 LLM 请求仍须现场验证，未以任何方式标为通过。

## 2026-09-22｜注意力候选整合

已整合汇报部门6a8efdf，产品评审推荐先评估中断恢复书签，但尚未获机制选择，不新增工程派单。PRD区分已验证技术基础与未实现语义卡链路；实板仍待下载模式排障。支线暂存和下一步缩小后置，硬件/Agent分别对照，禁止旧像素回应改名冒充新机制。

## 阅读第一版范围交接

已读取用户在研究任务最新原始指令，建立READING_PET_PRD，更新README/RULES和旧PRD优先级。01a0c813直接协调工程/美术；本任务仅文档/整合，不占串口、不重复派单。第三键不可直接当通用键，成长非专注指标，标记不伪造页码。

## 后续养成选择更新

据当前协调owner转达的最新用户选择，PRD已撤销无条件无死亡并记录死亡重开、性格、照料/成年和论文完成成长；保持待实施/阈值未定，100点击只作demo。当前竖屏临时烧录由原owner继续，未重复派单。

## reading-0.2整合审查

已按提交顺序合入软件3421a98及美术f1a90cf等价资产，无重复整体覆盖。产品亲读reading-nonzero-restart/reopen本地日志：session4/lifetime10/本次0、340bytes/readback true；portrait资源24帧确定性校验通过。保留物理B/长按/断电/目视未测与25秒串口静默未解。发现保存故障文案及不可见自动Agent请求问题，已交当前协调owner处理。

## reading-0.2收尾增量整合

已合eaef7c0/04e0fb1等价增量，亲读reading-telemetry-only：新启动5保留lifetime25、marks1、当前press0，随后实际计数增加。整合7项bridge测试PASS，PlatformIO编译PASS RAM23276/Flash714889，自动candidate关闭；保存提示准确指向重启。串口再次打开偶发无回应仍未解决，已由当前协调owner续派唯一软件owner诊断，产品不抢串口。
