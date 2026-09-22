# 像素伙伴独立验收

当前状态：已审PRD 7a1eff5与软件500d9bd5e0263fcbc4bd14079a2400a469ebca1a，主机9项回归通过；整体验收仍待实机。范围为M5Stick原生按键互动、节奏摘要给Agent、本机原创像素宠物；不新增外壳，不占串口或烧录。下方历次问题表保留发现时状态，最新结论以末尾回归为准。

| 门 | 当前结论 | 所需证据 |
|---|---|---|
| P1 产品与解释边界 | 源码/主机通过 | 固定动作与文案白名单；无情绪诊断与惩罚 |
| P2 本地按键与动画 | 源码已修，实机待测 | PC01/02/03/06需实际时序与屏幕证据 |
| P3 Agent约束与异常回退 | 主机9项通过，板上链路待测 | PC04/05/07关闭；固定候选与测试范围见末尾 |
| P4 发布与可见结果 | 未通过 | 构建与作者真实Agent调用记录已有；烧录、实际显示与按钮闭环未验证 |

## 固定反例清单（按PRD补充精确值）

1. 同样按压节奏只能形成统计或中性互动描述，不能输出情绪诊断；Agent文本也不能绕过此边界显示。
2. 一次按下跨多个主循环只记一次；抖动、长按释放、双键同时按按照定义处理，不把动画结束当输入。
3. 连续按键时动画持续推进；Agent请求阻塞/失联时本地计数和反馈保持工作。需要实际时序或等价运行证据，不以代码中无delay作为唯一证明。
4. 输出未知动作、超长字符串、缺字段、负值/极值、非JSON、重复或旧请求ID时不越过本地动作约束；明确超时后迟到回复是否丢弃。
5. 断网、未配凭证、超时与恢复联网都不丢当前互动、不积压无限请求；本地回退与真实Agent结果区分。
6. 长时间不互动、关机重启、跨日不导致死亡/饥饿惩罚、负面羞辱或催促。保存策略不让每次点击同步写盘阻塞输入。
7. 只允许声明已验证的交付层：编译不等于按键/显示/Agent端到端通过；不得为展示擅自占用串口或烧录。

## 分工与版本

验收唯一写入目录：docs/pixel-companion/acceptance；独立分支codex/pixel-companion-acceptance。软件与素材仅只读审查，反例直接发作者并抄协调。旧十日环验收结论不自动继承至本产品。

## PRD对齐

已直接读取产品提交7a1eff5的docs/hackathon/product/PIXEL_COMPANION_PRD.md，P01–P10范围接受。P06自动提示至少60秒冷却；B短按安静状态拥有本地优先级，过期回复不得覆盖；P03 session/window序号去重；P07至少idle/blink/press/happy/rest。窗口/阈值待软件协议定值，不自创产品参数。P09不逐次写闪存，升级与旧固件备份由唯一软件owner执行。COM9租约归软件，本验收不连接。

旧android工作树仍有multi-commitment在途文件，不能当pixel候选审；已向软件请求实际pixel工作树/文件入口。下一步以冻结SHA审代码与可复现反例，不等待美术完成才启动源码审查。

## 首候选46543f9预审

固定bridge源码46543f964e72a62909b01ef3427f576852c39892，真实函数只读导入，8项测试见bridge-46543f9.json；未连接串口或网络。60秒冷却、重复窗口、quiet旧epoch、无key本地与模拟Timeout回退5项通过。

| ID | 层/状态 | 反例与最小修正 |
|---|---|---|
| PC01 | 固件源码/P1待修 | render先quiet再A，安静下A始终Rest；本地按压反馈应优先于quiet空闲态 |
| PC02 | 固件源码/P1待修 | 9s按下11s松：10s窗口press1/held0，20s窗口press0/held2000；跨窗按住需切段累计，长按计数仍一次 |
| PC03 | 固件源码/P1待修 | pending非空时send静默return，summarize仍清计数/置waiting/消耗冷却；需成功入队后推进或明确有界drop/合并，不能无限队列 |
| PC04 | bridge实跑/P1待修 | hello epoch={}后rhythm抛TypeError，main未捕获；hello严格类型范围 |
| PC05 | bridge实跑/P1待修 | validate_reply接受责备“你太懒了，快来陪我。”及情绪推断“你现在很难过。”；用受控文案或短句ID，不以关键词过滤证明无推断 |
| PC06 | 固件源码/P2待修 | 合法72字节中文可超224px，被fit静默截断；按实际字体宽度限制或明确换行 |
| PC07 | bridge源码/P1待核 | urlopen8秒I/O超时不等于总时限，future无独立截止，慢速流可长期占唯一worker；需有界总截止/过期回退，不增加无限线程 |

固件草稿反例已发软件和PM，PM接受PC01–03并强调有界策略。bridge结果已直接发双方；当前没有整体验收通过结论。软件真实路径D:/tenfold-worktrees/pixel-firmware，替代此前等待路径的记录。

## 0e64612修订回归

冻结0e6461230ee3506069fa256c19ab3ec8ea215641，bridge文件sha256 45cefb8521e54fc17e482b2674a9bbe18b6a23f1be85a0cacb572e086a769fa2。原8项真实函数反例全通过，bridge-0e64612.json；PC04畸形hello与PC05责备/情绪短句关闭。产品接受模型选择已审短句，实际文案由双端5句精确白名单约束；不得描述为任意文案生成。

源码层PC01按压优先于quiet、PC02逐loop累计held、PC03仅send成功消费候选/冷却、PC06两行加固定短句均已修订。仍待真实时序/显示证据；摘要采用有界丢弃、不重播，不能声称完整离线历史。

PC07仍未关闭：read1+剩余socket timeout限制响应体读取，但urlopen返回前的DNS/响应头阶段没有独立总截止；future未完成时无外层截止，ThreadPool退出等待可阻塞重连。已要求有界可终止请求或准确限制，不宣称严格8秒全请求上限。作者报告DeepSeek真实调用成功，待脱敏证据，不索取密钥、不代替板上链路。

## 500d9bd硬超时回归

2026-09-22，固定500d9bd5e0263fcbc4bd14079a2400a469ebca1a；bridge SHA256 b16ea1807ae60b2d6e5aa0daa205969a14a335e7dd25b8041ceca9b9df838588。bridge-500d9bd.json记录9/9通过。

PC07关闭（主机层）：respond把整个_request放进单个OS子进程，subprocess.run(timeout=8)在超时后终止并回收；唯一executor worker不创建无限请求。独立探针在subprocess边界替换为真实sleep(30)子进程，保留生产调用参数与超时处理，8.027秒返回source=local。另以mock urlopen验证_request异常回退。没有访问网络、串口，也没有把该试验描述为真实DNS或慢HTTP服务测试；它证明外层进程截止独立于内部卡住的阶段。进程创建与调度有开销，不承诺严格8.000秒。

作者SOFTWARE.md记录DeepSeek合成摘要调用产生白名单action/text，属于作者提供的真实提供商证据，并非本验收亲自调用或真实按键链路。PC01/02/03/06源码修订保持待实机验证；COM9仍归软件owner，烧录和屏幕证据NOT_TESTED，不重复请求用户进入下载模式。

## 最终主机复验 aae670e（B03）

固定软件aae670e1ff77b008c179d8c9b24a25117b5be778（修复9186fa2），bridge SHA256 a6d3cccf4b1e9aa9f50db3fb1b450de0c25dad369d3e978430576dcef76d9825。B03为正常Content-Length耗尽后HTTPResponse关闭fp，下一循环访问fp.raw导致合法Agent响应误回退。修复在访问socket前检测isclosed并结束读取。

独立验收从Git提取冻结源码与test_companion.py到本工作树忽略runtime目录运行：python -m unittest discover -s docs/pixel-companion/acceptance/runtime -v，6/6通过，耗时8.602秒。test_real_http_content_length_eof使用真实本地HTTPServer/HTTPResponse和Content-Length，合法JSON返回source=agent；test_real_stalled_tls_process_deadline使用真实本地TCP连接停顿TLS，生产respond返回local且7–10秒断言通过。仅回环网络、合成凭证，无外部提供商或串口。

原有独立9项回归亦9/9通过，bridge-aae670e.json，停顿进程8.027秒回退。B03关闭。结论仅主机层通过；实板仍未烧录验证，PC01/02/03/06真实按键、显示、USB闭环仍NOT_TESTED。全量编译及美术verify由PM报告通过，不能替代实机验收。
