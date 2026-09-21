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
