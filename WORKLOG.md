# Tenfold 十日环｜工作记录

## 2026-08-03｜GitHub 首次归档

### 结果

- Kim 确认十日机械盘外形方向。
- 整理正式 PRD、工业设计规范和跨硬件 / 固件 / App / AI 实现方案。
- 收录已验收的外观渲染、交互 HTML 和 2026-07-22 市场研究底稿。

### 证据

- `docs/PRD.md`
- `docs/INDUSTRIAL_DESIGN.md`
- `docs/IMPLEMENTATION.md`
- `design/Tenfold十日机械盘-v2.png`
- `prototype/Tenfold十日环-v2.html`

### 卡点

- 渲染不是 CAD；十珠锁定 / 复位、公差、天线、电池和认证仍需工程验证。
- BOM 为工程估算，不是供应商报价。

### 下一动作

- 制作 P0 十珠机械样机和 46 / 48 mm 握持模型，再决定 EVT 结构。

## 2026-09-22｜Android USB P0

### 结果

- 新增可安装 Android P0：离线收敛、用户确认、状态持久化、完成/封存/恢复和清楚的模拟设备标记。
- 新增 M5StickS3 PlatformIO 固件源和 UTF-8 换行 JSON USB 协议。

### 边界

- Android 端实现 USB Host bulk 端点发现、系统权限申请和传输；当前没有接入板卡，因此不得称设备 ACK 或实机闭环已验证。
- 离线规则与云 LLM 明确区分；真实 Agent 能力已接入但没有可用凭证，因此云端请求仍为未验证项。

### 2026-09-22 收口证据

- Android 冻结候选源码 `6e2bf0e`，APK SHA-256 `B9604D2572CAD083F2A72D1D95628985EFBDB565E93FA4B9A3BBFB19C76259A8`，稳定签名证书 SHA-256 `EB55B62C374F6A58766625F52B83BA34B17E8A6B8C0D2CB95257781884CB153A`。
- 独立状态反例探针共 22 项全部关闭；模拟器覆盖安装、冷启动、十日回顾和恢复路径由独立测试任务复核。
- 固件以 PlatformIO Espressif32 6.12.0、M5Unified 0.2.22、M5GFX 0.2.29、ArduinoJson 7.4.3 编译并链接成功：RAM 22,676 B（6.9%），Flash 715,645 B（21.4%）。
- PlatformIO 无设备上传 dry run 给出精确烧录偏移：bootloader `0x0000`、partitions `0x8000`、boot_app0 `0xe000`、app `0x10000`。
- 本地固件发布包 `firmware/release/tenfold-firmware-p0.zip` SHA-256 为 `B94F3C282D7B28B3E1650514505714A106FAE1E0C7D7D9BB32AA32C6F4E195C3`；二进制按发布资产处理，不纳入 Git。
- 真实 M5StickS3、Android OTG 和云 LLM 未测试，保持明确 `NOT_TESTED`，不可由编译/模拟证据替代。
