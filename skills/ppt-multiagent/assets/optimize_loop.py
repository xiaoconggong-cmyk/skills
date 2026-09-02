# -*- coding: utf-8 -*-
"""
自我优化驱动（v7.2 新增）：把 SKILL.md 第十一章的"自我优化循环"变成可执行脚本。

流程：输入 PPTX → 跑全部检测器（溢出/空体/卡片溢出/文本框溢出/底部死区/字体/同质化）
      → 输出结构化诊断报告 → 按失败模式映射"定向联网搜索 query" → 写 issue_log。

设计哲学：
- 不是一堆禁止规则，而是"生成 → 自检 → 查问题 → 搜方案 → 回填知识库 → 再生成"的闭环。
- 每种失败模式都对应一个针对性的联网搜索（SEARCH_MAP），而不是泛泛搜一次。
- 检测器复用 regen_weekly_v7.py，保证诊断与生成使用同一套度量与阈值。

用法：
    python optimize_loop.py [pptx路径]
不传路径则默认诊断 v7.2 成品。
"""
import sys
import os
import datetime

# 复用生成器的检测器与常量
sys.path.insert(0, r"D:\Desktop\大模型")
import regen_weekly_v7 as G

# 失败模式 → 定向联网搜索 query（闭环核心：每种新失败都针对性去搜）
SEARCH_MAP = {
    "overflow":        "PPT 内容过多 分页 自动布局 防止文字溢出画布",
    "empty_body":      "PPT 空白页面 内容少 怎么填充 设计技巧 线框 引用数据",
    "card_overflow":   "PPT 卡片 文字溢出 自适应高度 排版 圆角矩形",
    "text_overflow":   "PPT 文本框 文字溢出 自动换行 行高 真实字体度量",
    "bottom_deadzone": "PPT 页面 上重下轻 底部留白 页脚信息带 视觉平衡",
    "font_mismatch":   "python-pptx 中文 字体 ea typeface 设置 宋体 楷体",
    "homogenization":  "PPT 标题 对齐 变化 视觉节奏 避免千篇一律",
}

# 失败模式 → 自动修复剧本（供生成器/下一轮修订参考）
AUTO_FIX = {
    "overflow":        "对超长要点启用自动分页，或收紧 estimate_text_height 系数",
    "empty_body":      "依据文档自身上下文重建内容，或用 status_card/引用数据/线框造层次填充",
    "card_overflow":   "增大卡片高(>1.0\")或缩减正文至 1 行，用真实度量复核",
    "text_overflow":   "放大文本框高，或减字号/缩字数，用 PIL 真实度量",
    "bottom_deadzone": "内容下移 + 加页脚信息带(细线+章节标签)",
    "font_mismatch":   "统一用 set_run_font 双写 latin/ea/cs=宋体(或楷体)",
    "homogenization":  "标题 X 从 TITLE_X_POOL 轮换，奇偶页切换 accent 色",
}


def optimize(pptx_path, log_path=None):
    prs = G.Presentation(pptx_path)
    issues = []
    title_x = []
    for i, slide in enumerate(prs.slides, 1):
        for sh in slide.shapes:
            if sh.has_text_frame and sh.top / 914400.0 < 0.75 and sh.height / 914400.0 < 0.5:
                title_x.append(sh.left / 914400.0)
        dz = None if i == 1 else G.detect_bottom_deadzone(slide, i)
        for det in (G.detect_empty_body(slide, i), dz):
            if det:
                issues.append(det)
        issues += G.detect_text_overflow_in_card(slide, i)
        issues += G.detect_text_overflow_general(slide, i)
        issues += G.detect_font(slide, i)
    # 唯一硬约束：溢出门禁
    for i, slide in enumerate(prs.slides, 1):
        if G.check_overflow(slide):
            issues.append(("FATAL", "overflow", i, "内容超出画布 SAFE_BOTTOM"))
    h = G.detect_homogenization(title_x)
    if h:
        issues.append(h)

    print(f"\n===== 自我优化诊断报告：{os.path.basename(pptx_path)} =====")
    print(f"总页数：{len(prs.slides._sldIdLst)}  问题数：{len(issues)}")
    kinds = {}
    for sev, kind, pg, msg in issues:
        kinds[kind] = kinds.get(kind, 0) + 1
        mark = "❌" if sev == "FATAL" else "⚠️"
        print(f"  {mark} [{sev}] {kind} 第{pg}页: {msg}")
    print("\n--- 触发联网研究（每种失败模式对应一个定向 query）---")
    for k in kinds:
        print(f"  {k}: {SEARCH_MAP.get(k, '（无映射，需补充）')}")
    print("\n--- 自动修复剧本 ---")
    for k in kinds:
        if k in AUTO_FIX:
            print(f"  {k}: {AUTO_FIX[k]}")

    if log_path and issues:
        _append_log(log_path, pptx_path, issues, kinds)
    return issues


def _append_log(log_path, pptx_path, issues, kinds):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n## 自优化诊断 {now}\n")
        f.write(f"- 文件：{pptx_path}\n")
        f.write(f"- 问题统计：{dict(kinds)}\n")
        for sev, kind, pg, msg in issues[:20]:
            f.write(f"  - [{sev}] {kind} p{pg}: {msg}\n")
        f.write("- 闭环动作：按 SEARCH_MAP 联网研究 → 回填知识库 → 修订生成器/重跑\n")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else r"D:\Desktop\大模型\第二周工作周报_v7.2.pptx"
    log = r"C:\Users\25124\.workbuddy\skills\ppt-multiagent\assets\issue_log.md"
    optimize(path, log_path=log)
