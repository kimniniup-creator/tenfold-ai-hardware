# Attention pitch 交接

status: 文稿与产品机制完成，待owner产品取舍；不是新机制实现完成。

- **结论**：推荐先验证“中断恢复书签”：主动留上下文→Agent候选→用户确认保存→EDC主动取回→回原任务。暂存支线、缩小卡点是另外两种机制，均已比较，非P0必需。
- **影响**：不是旧像素宠物改名。需要新增语义输入、版本化任务卡、持久化/ACK和取回协议，取消按压阈值触发专注建议。EDC与Agent都不是先验必要，必须分别与软件/表单比较。现有主机测试不能替代该闭环的实机证据。
- **证据位置**：本目录README为入口；ONE_PAGE、MECHANISMS、EVIDENCE、PITCH、DEMO_QA、VALIDATION、SCOPE完整覆盖交付。原始研究边界与访问限制逐项标注。无用户效果数据。
- **下一owner/动作**：唯一直属创建任务 `01a0c3c3-e4c7-7b71-be7e-110ef965a333` 汇总后与产品协调对齐是否采用B及最小实现时间；不让工程把提案当已授权规格。正式演示前根据固定版本验收证据更新SCOPE与PITCH第5页，未过门使用概念演示。
- **交付/整合**：仓库 `https://github.com/kimniniup-creator/tenfold-ai-hardware`，分支 `codex/attention-pitch`；后台worktree `D:/tenfold-attention-pitch`，独占写入仅 `docs/hackathon/attention-pitch/`。owner可选择cherry-pick文档提交，确认远端整合后再安排worktree清理；本任务不修改主仓、不删除其他工作树。
- **尚未发生**：任务卡代码、实机烧录、实际屏幕与按键验收、参与者研究、真人路演计时、成品幻灯制作。它们不是本轮Markdown材料缺失，不能据文稿声称已经完成。
