# 像素陪伴独立测试报告

**HOST_PASS_SCOPED；实板仍NOT_TESTED。** 最终bridge源码9186fa23873d58b3a6bf2b5fe43002681d97f184，文件SHA256 a6d3cccf4b1e9aa9f50db3fb1b450de0c25dad369d3e978430576dcef76d9825。19项主机反例、2项真实回环HTTP读取、1项真实OS子进程截止均通过。固件从500d9bd独立快照编译通过，与9186fa2的firmware目录无差异。

## 实际执行与结果

| 范围 | 实际操作 | 结论/证据 |
|---|---|---|
| 3次阈值/60秒冷却 | 导入冻结bridge，测2/3次、59.999/60秒、重复/乱序/新会话 | PASS，bridge-9186fa2.json |
| 安静与旧epoch | 真Gate和主循环，注入quiet及晚到结果，确认不输出reply | PASS；不是物理B按键 |
| 握手容错 | 非整数/负值/空值epoch后再发合法rhythm | PASS；旧版TypeError已关闭 |
| 重连 | runpy真正脚本入口+fake serial第一次read抛OSError，观察再次open；额外实际main两次连接确认仅一次respond | PASS；不是实际USB拔插 |
| 受限输出 | 三种动作、五句原文、未知动作/短句/额外字段/长度/控制字符/诊断内容 | PASS |
| 无密钥及故障 | 无密钥不调用网络；超时/错误/畸形/超大响应回退local；合成合法JSON返回agent | PASS；合成agent标签不是在线模型实测 |
| HTTP正常完整响应 | 真HTTPServer、真实HTTPResponse与socket，Content-Length合法JSON | PASS 0.281s；B03关闭 |
| HTTP慢流 | 每0.5秒一字节持续发送 | PASS约8.203s回退；deadline-9186fa2.json |
| 总截止与清理 | 真respond父进程，子请求替换为真实阻塞30秒的Python子进程 | PASS 8.031s，kill+reap后local；child-deadline-9186fa2.json |
| 独立固件构建 | git archive 500d9bd到测试忽略目录后实际PlatformIO构建 | PASS exit0/120s，RAM22892/Flash717085；firmware-build-500d9bd.json |

HTTP探针只在urlopen边界将HTTPS地址替换成无代理本机HTTP，验证读取/EOF/socket截止，未验证TLS或真实服务。早期探针受Windows代理影响的SSL失败已排除；正式保留结果来自禁代理的本机连接。子进程测试替换的是子请求程序，不伪称DNS故障实测，但8秒父进程强制终止为实际OS行为。

## 已发现并关闭的问题

- B01，46543f9：hello epoch为字符串后合法rhythm导致TypeError退出；严格类型校验修复，最终反例通过。
- B02，46543f9：串口read异常直接退出；重连外循环复用Gate修复，最终真正入口和保留冷却反例通过。
- B03，0e64612/500d9bd：完整Content-Length读完后fp=None，再访问fp.raw导致合法回答回退local；9186fa2在EOF检查关闭后修复，真实HTTPResponse通过。

中间bridge-46543f9/0e64612/500d9bd JSON用于故障和阶段证据。最终回归脚本增加三项边界后共有19项，不将中间16项说成最终完整范围。

## 实板门与限制

COM9仅只读枚举为VID303A/PID832B候选，测试从未打开、从未烧录；端口软件独占，等待产品发租约。下载模式需现场操作由产品另行协调。

T01–T03真实按键去抖/长按不虚增/同时按键；T04真实按压节奏摘要；T06断线时动画/输入仍流畅；T08真实USB拔插；T09低电、断电/重启、偏好持久化；T10真实屏幕分辨率/像素布局/短句不裁切，均NOT_TESTED。代码检查和编译不能替代这些证据。无振动能力或舒压效果结论。

软件作者报告实际在线模型返回agent，证据入口其docs/pixel-companion/SOFTWARE.md；本独测未独立发起真实LLM调用，不提升为独测在线闭环PASS。端到端板上输入→bridge→像素回应仍待实板。

独立构建bin SHA与作者bin不同，因此不声称字节可复现；只锁定源代码、依赖构建成功和本机bin哈希。构建物和完整日志留忽略目录，不入Git，不烧录。无测试服务或子进程残留。

## 复跑

在测试Python运行bridge_probe.py、deadline_probe.py、child_deadline_probe.py，传入--source冻结的bridge/companion.py与--out结果JSON。脚本不访问真实COM，全部合成数据。真实设备门在租约和可观察输入具备后按TEST_PLAN.md继续。
