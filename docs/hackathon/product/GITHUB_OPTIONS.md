# GitHub可行方案与本轮取舍

核查日期2026-09-22。只查维护者主仓库、许可证和官方示例，并只读当前软件；不是已完成各库集成或实机测试。目标是复用可靠基础，避免为了框架扩大今晚范围。

| 主仓库/许可 | 能复用什么 | 本轮选择与边界 |
|---|---|---|
| [mik3y/usb-serial-for-android](https://github.com/mik3y/usb-serial-for-android)，[MIT](https://github.com/mik3y/usb-serial-for-android/blob/master/LICENSE.txt) | Android USB Host串口驱动、CDC/ACM识别、串口参数、异步收发；仓库usbSerialExamples给权限与连接起点 | 推荐为串口成熟替代/代码核对来源。当前项目已有手写CDC且直接SDK打包，今晚不无条件换构建路线；若真板枚举/初始化失败优先考虑此库。库不替代业务ACK/幂等/持久化，也不证明M5已经连通 |
| [m5stack/M5Unified](https://github.com/m5stack/M5Unified)，[MIT](https://github.com/m5stack/M5Unified/blob/master/LICENSE) | 官方列出StickS3支持，提供显示/按钮/声音接口；[Button示例](https://github.com/m5stack/M5Unified/blob/master/examples/Basic/Button/Button.ino)展示更新循环和按下/释放/长按等事件 | 当前固件已声明依赖；用库读取真实按键并驱动屏/声，业务双阶段确认仍自己实现。示例是多机型，不照搬不存在的键，更不能由IMU推断原创机械旋转 |
| [bblanchon/ArduinoJson](https://github.com/bblanchon/ArduinoJson)，[MIT](https://github.com/bblanchon/ArduinoJson/blob/7.x/LICENSE.txt) | [JsonParserExample](https://github.com/bblanchon/ArduinoJson/blob/7.x/examples/JsonParserExample/JsonParserExample.ino)演示反序列化、错误检查和取值 | 当前platformio.ini实际声明`^7.3.1`、固件include已存在，应继续使用而不是字符串截取。解析成功后仍须字段/长度/版本/type校验；JSON库不提供协议正确性 |
| [openai/openai-agents-python](https://github.com/openai/openai-agents-python)，[MIT](https://github.com/openai/openai-agents-python/blob/main/LICENSE) | Agent运行、工具、交接、人类确认、会话和追踪；README要求Python运行环境 | 暂不引入。该SDK本身不强制云部署，但当前原生Java APK若使用它需额外Python进程/服务或运行环境；本轮没有多Agent工具执行需求，不值得增加部署与故障点。后续多工具长流程才重新评估 |

## 今晚建议的软件组合

Android本地状态和明确确认 → 单次HTTPS请求获得结构化候选 → 本地校验/用户确认 → USB传输 → M5Unified按钮/屏/声 + ArduinoJson解析 + 本地存储。Agent负责缩小动作和恢复线索，业务状态不交给模型决定。直接API不是一个额外开源库，也不应伪称成熟Agent框架已接入；目前AgentClient使用Java HttpURLConnection，真实提供商适配、鉴权和输出格式需用实际请求验证。

手机自填API端点/凭据只作为个人Demo配置，不把服务方共享密钥写入APK；面向多人发行时再评估后端代理。此次不新增后台。请求超时、认证失败、非JSON或字段不足都保留原卡与原句；成功输出也不能自动激活。

## 当前仓库事实与收口

只读软件worktree时见M5Unified依赖指向GitHub未锁commit，ArduinoJson使用范围版本；最终构建应记录实际解析的依赖版本/commit并保留依赖许可。MIT允许复用，分发相应代码需保留版权与许可文本；不因“开源”而省略许可证。

`docs/android-demo.md`仍称ArduinoJson未包含、解析器是固定消息，与当前include/依赖矛盾；该缺陷已直接通知软件负责人，要求最终更新依赖、协议字段、LLM/规则模式、构建安装与实机未测边界。产品不改软件文件。

选择标准是是否减少本轮真实故障：M5官方库和严格JSON解析已在路线内；USB成熟库是有来源的可用替代；多Agent框架暂不采用。所有“能用”的判断均不替代APK安装、真实模型调用和M5端到端测试。
