# 需求—证据矩阵

版本基线均见REVIEW完整SHA，不适用于后续未审版本。

| 需求 | 当前证据 | 判定/缺口 | owner |
|---|---|---|---|
| V1/V2/V4 硬件价值与替代 | 三README交互映射；PM交流提出对照 | 论证待审；用户价值NOT_TESTED | PM |
| V3 机械把玩 | 三README描述原机构与保留方式 | 机构描述可接受；装配后体验BLOCKED；球倒置FAIL | 模型owner/测试 |
| S1 输入AI确认 | 旧PRD 1/3/1上限与Schema | 新黑客松实现契约待审；运行NOT_TESTED | PM/软件owner待协调指定 |
| S2/S4 ACK/持久/恢复 | 旧IMPLEMENTATION seq幂等建议 | 非M5已实现证据；新协议待审 | PM/固件owner待指定 |
| S3/M1 实体输出 | 三README均承认无固件、机械不检测 | 边界表述PASS；运行NOT_TESTED | PM/固件/测试 |
| M2 附件网格 | 三作者JSON正体积/闭合/零相交 | 作者自测局部接受，独立复现待收 | 测试 |
| M2 真实适配 | 三README原尺寸/接口未知 | G3 BLOCKED；球保持限制明确 | 对应模型owner |
| D1 完整演示 | 无端到端记录 | G4 NOT_TESTED/NO-GO | PM/实现/测试 |
| 证据真实性 | 文件主动标注假设、无实物、许可边界 | 当前所读文字边界PASS；不等于独立法律审核 | 各owner |

待实测记录禁止填假人数/成功率。填入数据需同时记录原始观察与不支持价值的负例。

产品最终候选：e948b2c5edc28ca34301903b3066f07119a379ee。

| 需求 | 指定版本直接证据 | 独立结论 |
|---|---|---|
| V1/V2/V4 | HACKATHON_PRD产品判断、五组试验、48次分母、停止标准 | G1论证与实验可执行PASS；用户价值NOT_TESTED |
| S1 | R01–R04，旅程Draft/Proposed/Confirmed，T01–04 | 入口/数据/确认/兜底明确，文档PASS；运行NOT_TESTED |
| S2/S4 | query、周期锚点、状态菜单、time_untrusted、Done次日待新动作，T03/10/11 | P-01..04修复PASS；实现/掉电/同步NOT_TESTED |
| S3/M1 | R06/07/09，音码与静音，USB路线与P0 BOM | 能力与输出责任边界PASS；实机可用性NOT_TESTED |
| D1 | DEMO_AND_QA时间表与真假标签、T14 | 脚本可执行性PASS；90秒节奏/实机闭环NOT_TESTED |

模型最终证据提交：ad0c363bdaeb95702185c0f9bc3ce14204ad161e。

| 需求/模型SHA | 证据文件（testing目录） | 最终结论 |
|---|---|---|
| M2/471703 58072e0dbfa61e7f32510851f2d33c43b6c4b284 | pin-retest.json、REPORT修复节 | 默认T8/LAND6指定M3几何PASS；全参数/M2.5/源接口不扩展 |
| M2/2710405 2aaf60b72875c992623210256f05deeea44ea261 | press-retest.json、press-check-summary.json | 指定五金/顺序下几何PASS；静止原底座BLOCKED |
| M2/2673323 8ba49f0d8c56d5c531611860dcf0996722f94a82 | ball-retest.json、ball-range-retest.json、ball_fastener_probe.json | 指定3参数点/工具五金几何PASS；任意翻转保持FAIL |
| V3/M1/三修复SHA | REPORT分项总表与修复节 | 真人握持、实际屏键USB、材料/打印NOT_TESTED或BLOCKED；无升级整机 |
| 证据版本隔离 | probes.py/probes.json、reproduce.py | 跨SHA覆盖已修，基线反例与修复分开PASS |

最终产品68dbb10bd414d80be85657f497de9e390434d8c3已做增量复审：三模型事实与上述测试证据一致，状态/交互/价值协议未变，G1 PASS适用于该SHA。其相对e948b2c的变化不产生软件运行通过证据。
