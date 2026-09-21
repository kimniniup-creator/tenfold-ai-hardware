# HANDOFF — 471703 针板式 EDC 侧舱

## 当前交付边界
独立侧舱和夹具CAD；原针板未取得，因此针板接口与运动干涉未验证。不得把默认8 mm厚/6 mm夹持宽写成原模型尺寸。主协调任务：01a0c3c3-e4c7-7b71-be7e-110ef965a333。

## 恢复路径
Worktree: D:\tenfold-worktrees\471703
Branch: codex/471703-m5-adapter
Formal directory: design/hackathon/471703-pin-array-sidecar/
No main merge authorized. Third-party references and venv are in ignored .local/, not committed.

## 原文件获取
https://makerworld.com.cn/models/471703
绿色按钮右侧下拉 → 下载STL/CAD文件 → Pin art board medium.stl（52 MB）→ 下载。
2026-09-22实际点击要求登录。需要Kim正常登录或提供已合法下载的本地STL；不需要绕过登录，不读取cookie。只作本地测量，不上传原文件或衍生针阵。

## 源模型补测清单
- STL真实单位、总尺寸、静态框厚度；不按封面推算。
- 外框可夹持宽度/圆角、相距22 mm的两个10 mm夹持位是否可用。
- 滑销两端行程与限位外扩，及倾斜/翻转极限时的空间。
- 把手/接缝/薄壁是否影响夹持；无静态可夹边框则重做接口。
- 用真实源STL在本地做全行程相交检查；只提交检查数值与原创接口，不提交源网格。

## M5补测清单
- 核对官方STL分离件与整机姿态，不能把138.529 mm整体排布跨度当整机长度。
- 现用48×24×15标称包络，侧面开放但接口绝对坐标未测；实际USB插头、Reset、KEY1/2、Hat2/Grove逐项操作。
- 四角盖唇与屏幕有效区、按钮不得重叠；背面软垫/天线/磁吸结构需实机核对。
- 螺钉导孔、PETG翘曲、夹爪预紧、翻转与滑销自由运动；未做实物打印。

## 验收后
总控统一验收/cherry-pick本分支，保留后台worktree直至整合和源文件补测完成。不要清理其他任务目录。

已执行验证：四件STL闭合且各一连通体，21组装配相交体积为0，夹爪11步闭合检查通过，STEP回读有效。默认独立配件整体包络约82×40×23.6 mm（不含原针板、螺钉突出与电缆）；此尺寸不是整机最终外形。实际装配/爆炸图已查看。待总控验收及原文件补测，不能合并后把其状态改成“已完成针板适配”。
