# 自检与问题记录（Self-Check & Issue Log）

> v7.0 自我优化循环的问题存档。每次生成后由 Agent 写入，联网研究后回填知识库。

## 2026-07-31 — 第二周工作周报.pptx

| 严重度 | 类型 | 页码 | 描述 | 根因 | 状态 |
|--------|------|------|------|------|------|
| FATAL | overflow | 3 | 内容堆到 Y=9.29"，画布仅 7.50" | 7条要点+验证挤一页，无强制分页闸 | ✅ v7.0 加溢出闸+自动分页 |
| WARN | empty | 1 | 封面内容从 Y=2.55" 起，上半页全空 | 标题未居中/无锚点填充 | ✅ v7.0 焦点留白+装饰线 |
| WARN | empty | 11/12/13 | 表格/结论仅几行，下方大片空白 | 低密度内容页无增强策略 | ✅ v7.0 状态卡+内容扩展 |

## 修复方案（已回填知识库）
- 溢出：渲染每页后 `check_overflow`，超界即分页（5.2/5.3）
- 空页：区分健康留白 vs 病态空，用 6.2 方案 B/C/D 增强
- 页码豁免：页脚区(7.30"–7.50")元素不计入溢出

## 待复核
- 是否需要"过渡页/章节页"专用模板（v6.1 未覆盖）
- 中文行高估算在不同字体下的误差（微软雅黑 vs 思源黑体）

## 2026-07-31（续）— v7.0 已落地到真实文件

将 v7.0 全流程应用于真实周报 `第二周工作周报.pptx` → 输出 `第二周工作周报_v7.pptx`（13 页）。

| 项 | 原文件 | v7.0 输出 | 结果 |
|----|--------|-----------|------|
| 第3页最大底边 | 9.29"（溢出 1.79"） | 6.78" | ✅ 溢出清零 |
| 全页溢出门禁 | — | 13/13 OK（底≤7.30"） | ✅ 全部通过 |
| 空页 1/11/12 | 内容稀疏 | 状态卡+装饰线+内容扩展 | ✅ 已增强 |
| 空页 5/7 | **仅标题，正文缺失**（v6.x 生成 bug） | 从文档自身上下文重建（ML每日详情 / 蒸馏升级要点） | ✅ 已重建 |
| 页 6/9 | 内容悬空中段 | 双列映射 / 发现+改进卡 | ✅ 已锚定 |

**重建说明（透明标注）**：原文件第 5、7 页为纯标题、无正文，属历史生成缺陷。其重建内容全部源自本文档既有上下文（P4/P10 的 ML 排期、P8/P9 的蒸馏结果），未引入外部虚构数据。

**交付物**：
- `D:\Desktop\大模型\第二周工作周报_v7.pptx`（最终成果）
- `D:\Desktop\大模型\第二周工作周报_v7_preview.html`（可视化预览）
- `D:\Desktop\大模型\regen_weekly_v7.py`（v7.0 实战生成器，含 check_overflow 硬闸）

**自我优化循环验证**：本次真实问题（溢出+空页）→ 触发 v7.0 知识（唯一硬约束+空页增强）→ 联网研究结论已在 research_log 沉淀 → 生成并自动门禁校验 → 全部通过。循环闭环有效。

---

## 2026-07-31（再续）— v7.1：强化自检 + 宋体 + 真实度量 + 底部平衡

将用户反馈的"其他可优化项"落地为 v7.1，并**用新自检反向抓出 v7.0 漏检的真实缺陷**（证明自检强化有效）。

| 严重度 | 类型 | 页码 | 描述 | 状态 |
|--------|------|------|------|------|
| WARN | card_overflow | 10 | 5 张日期卡高 0.75"，但"ML 学习启动 + 框架规划"折 2 行撑爆卡片（门禁过了、卡片内仍溢出） | ✅ 卡高 0.75→1.05"，详情框下移 |
| WARN | bottom_deadzone | 1(封面误报) | 封面内容底 5.15" < 6.0" 被误报 | ✅ 封面排除该检测（焦点留白合法） |
| — | font | 全部 | 用户指定"宋体或楷书" | ✅ 全文字体改宋体（`FONT_BODY/TITLE` 常量，可一键切楷体） |
| — | metric | 全部 | 近似字宽(0.55系数)存"门禁过、PPT仍微溢出"残差 | ✅ 改用 PIL 加载 simsun.ttc 真实度量 |
| — | balance | 2/4/9/10/12 | 内容止于 ~5.7"，下方 1.4" 空白→上重下轻 | ✅ 加页脚信息带(细线+章节标签)+小结下移至 6.15" |

**关键证据（自检闭环有效）**：v7.1 新自检 `detect_text_overflow_in_card` 直接抓出第 10 页卡片内文字溢出——这是 v7.0 只检形状边界时**根本发现不了**的盲区。修复后重跑，四类检测（空体页/卡片溢出/底部死区/同质化）全绿。

**交付物**：`D:\Desktop\大模型\第二周工作周报_v7.1.pptx` + `第二周工作周报_v7.1_preview.html` + 升级版 `regen_weekly_v7.py`（含 PIL 度量 + 四类自检）。

**知识库回填**：2.4 字体、5.4 真实度量、6.4 底部死区平衡、8 字体规范、11.1 四类检测器、3.4 闭环示例、research_log 新增两主题。

## 自优化诊断 2026-07-31 09:59
- 文件：D:/Desktop/大模型/第二周工作周报.pptx
- 问题统计：{'font_mismatch': 79, 'bottom_deadzone': 9, 'empty_body': 2, 'text_overflow': 2, 'overflow': 1}
  - [WARN] font_mismatch p1: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p1: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p1: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p1: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p1: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] bottom_deadzone p2: 内容最大底边 3.70” < 6.0”，上重下轻
  - [WARN] font_mismatch p2: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p2: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p2: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p2: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p3: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p3: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p3: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p3: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p3: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p3: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p3: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p3: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p3: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
  - [WARN] font_mismatch p3: run 字体 latin=Microsoft YaHei ea=None 非('宋体', '楷体')
- 闭环动作：按 SEARCH_MAP 联网研究 → 回填知识库 → 修订生成器/重跑

## v7.2 修复（2026-07-31，自查发现真问题）
- **中文 ea 字体漏设（最严重）**：v7.1 成品 203 个 run 全部 `latin=宋体` 但 `ea=None` → 中文实际走系统默认东亚字体，跨机渲染漂移。根因：`run.font.name` 只写 `a:latin`，不写中文 `a:ea`。已用 `set_run_font()` 双写 latin/ea/cs，v7.2 验证 203/203 均 `ea=宋体`。
- **普通文本框溢出盲区**：v7.1 仅检卡片内溢出；新增 `detect_text_overflow_general` 覆盖所有文本框。首跑即抓出第4页说明文字（框高 0.55" 实际 0.67"）并修复（框高→0.78"）。
- **字体声明自检**：新增 `detect_font`，任意 run 的 latin/ea 非宋体/楷体即 WARN，使循环能自证字体声明。
- **可执行闭环**：新增 `assets/optimize_loop.py`，复用检测器输出结构化报告 + 定向搜索映射(SEARCH_MAP) + 自动修复剧本(AUTO_FIX) + 写 issue_log；对原始问题文件跑一遍可抓出 overflow/字体/空体/底部死区，证明闭环有效（回归测试）。
- 验证：`第二周工作周报_v7.2.pptx` 13 页 → 溢出门禁 13/13 通过 + 六类自检全绿；`optimize_loop.py` 诊断 0 问题。
