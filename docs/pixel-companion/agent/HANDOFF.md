# Agent 架构交接

2026-09-22：Kim 要求回到 Agent 制作流程，先完成架构，不能把制作等同于扩充语料。

权威草案：../AGENT_ARCHITECTURE.md。当前任务分支 codex/companion-agent-architecture；只新增文档。

已确认：保留现有美术；好奇爱玩、跟用户同一节奏；“你累啦，我正好也想休息”代表期望语感，不代表允许根据按键推断疲倦。此前语料表未定稿。

只读参考 pixel-firmware 的 c96363a：candidate=false，portrait 未显示 message，也未映射 replyState。仅改 companion.py 无法完成 Agent 可见体验；双端白名单和纯动作协议同样需要集成。

下一步：依据架构完成无串口离线 reducer/policy/corpus 回放；先让 Kim 审连续情境，再由固件 owner 接协议和渲染。当前没有改 COM10、烧录、持久化或美术。未执行设备验证，不得报告 Agent 已生效。
