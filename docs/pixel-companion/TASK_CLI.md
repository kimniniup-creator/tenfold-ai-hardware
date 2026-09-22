# 任务节点 CLI

`bridge/task_cli.py` 是首版本地入口：创建任务节点、展示文本、由本人明确确认，再在需要时手动同步到设备。它没有后台进程、定时发送或 `--yes` 自动确认选项。

账本默认保存在被 Git 忽略的 `.delivery/task_cli.sqlite3`。其中保留任务标题、节点文本、确认时间和同步状态；USB 只接收协议要求的安全 `task_id`、`node_id`，不接收正文。

```powershell
# 创建：会生成安全的 task-/node- UUID 标识，但不代表完成
python bridge/task_cli.py create --title "阅读论文" --node "读完这一节并写一句理解"

# 阅读本地文本；确认会展示任务和节点，只有输入“完成”才写入本地账本
python bridge/task_cli.py show node-REPLACE_WITH_GENERATED_ID
python bridge/task_cli.py confirm node-REPLACE_WITH_GENERATED_ID

# 只读查看本地记录
python bridge/task_cli.py list
python bridge/task_cli.py status

# 只有这一条命令才会打开指定串口；没有匹配 ACK 的记录保持“待同步”
python bridge/task_cli.py sync --port COM10
```

同步发送的唯一完成帧是：

```json
{"type":"node_complete","protocol":2,"version":1,"task_id":"task-…","node_id":"node-…","confirmed":true}
```

设备回复同一 `node_id` 且状态为 `applied` 或 `duplicate` 时，账本才标记“已同步”。`conflict`、`reject`、`storage_error`、`capacity_full` 与丢失/错误 ID 的 ACK 都不会标记已同步，保留原 ID 供稍后幂等重试。每次 `sync` 会持有本地独占锁，避免两个 CLI 进程同时打开串口。
