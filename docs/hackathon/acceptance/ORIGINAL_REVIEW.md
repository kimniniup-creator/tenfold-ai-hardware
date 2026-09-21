# 原创轮独立验收

日期：2026-09-22。状态：门禁已建立，等待原创模型/软件冻结版本。

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
