# 原创轮独立测试工作记录

2026-09-22：新要求为从零原创完整机械EDC，基于origin/main建立codex/original-independent-testing，继续独占D:/tenfold-worktrees/testing。上一轮源玩具缺失不再作为本轮阻塞。三作者和APK任务已收到交付接口/测试要求。

本机常用安装路径/卸载注册表未找到Bambu/Orca/Prusa；从prusa3d官方GitHub release取得PrusaSlicer2.9.6 zip放忽略目录，准备真实CLI切片。打印机未知，按总控指令通用0.4喷嘴/0.2层高PLA筛查，G-code只作本地证据，绝不作为匹配机器的打印文件交付。

ADB存在于D:/手机电脑连接桥/tools/scrcpy-win64-v4.0/adb.exe，devices列表为空；未发现模拟器，已通知软件任务。未占用真机。M5统一官方结构证据由orbit任务提供，等待其本地路径与姿态说明。

2026-09-22 独立重建针板81c0682和环轨0fdf1ef均退出0，verify_exports.py确认提交STL与重建体积/包围盒一致及全部STEP可回读。9+9种STL实际无支撑切片均成功；制造薄区O-PIN-01/O-ORB-01已交作者修订。针板官方M5三壳组件与32装配实体相交为0。APK包装发现S-A05根DEX与S-A06缺uses-sdk，软件作者修订中。
模拟器由测试任务独占接管：下载官方Emulator37.1.11并核对SHA1，WHPX加速可用；API35 AOSP镜像正在下载。无物理手机或板端测试。
