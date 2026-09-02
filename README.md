# AI 技能合集

本仓库收录若干可直接安装的 AI 技能（Skills），每个子目录 `skills/<name>/` 对应一个独立技能，核心定义见各目录下的 `SKILL.md`。

## 技能清单

| 技能 | 目录 | 简介 | 触发方式 |
|------|------|------|----------|
| 多智能体协作系统 | `skills/multi-agent-system` | 三角色（管家-工作者-监督）协作，监督按「跨领域通用四核心 + 四扩展维度」严格评审 | 用户以"管家模式"/"多智能体"/"三角色"开头，或工作目录含 `agents.md` |
| 论文写作流水线 | `skills/paper-writing-pipeline` | 五角色流水线式论文写作（大纲/分发/生成/质检/整合），支持文献预处理、图表公式占位、领域适配、修订模式 | 用户以"论文流水线"/"五角色论文"开头，或含 `paper-pipeline.md` |
| PPT 多智能体生成 | `skills/ppt-multiagent` | 知识驱动 + 联网研究 + 自我优化 的 PPT 自动生成（v7.2），唯一硬约束：内容不得溢出画布 | 见 `SKILL.md` |
| 简历制作与优化 | `skills/resume-builder` | 对话式简历顾问，结合最新简历方法论与模拟面试发现薄弱环节同步优化 | 制作简历/优化简历/简历润色/模拟面试/求职准备 |

## 目录结构

```
skills/
├── multi-agent-system/
│   └── SKILL.md
├── paper-writing-pipeline/
│   ├── SKILL.md
│   ├── assets/        # 模板文件
│   └── references/    # 引用格式、领域画像、结构、质量准则
├── ppt-multiagent/
│   ├── SKILL.md
│   ├── assets/        # SVG 架构图、演示 pptx/html、生成脚本
│   └── scripts/       # ppt_pipeline.py
└── resume-builder/
    ├── SKILL.md
    └── references/    # 面试模拟、简历方法论
```

## 安装方法

将所需技能目录复制到技能目录下：

- **用户级**（所有项目可用）：`~/.workbuddy/skills/<name>/`
- **项目级**（仅当前项目）：`<项目根>/.workbuddy/skills/<name>/`

示例（PowerShell / Git Bash）：

```bash
cp -r skills/ppt-multiagent ~/.workbuddy/skills/
```

## 使用方法

1. 按上方「安装方法」把技能目录复制到对应技能目录。
2. 重启运行环境，使技能生效（新复制的技能会被自动加载）。
3. 在对话中按各技能的触发方式调用，例如：
   - 输入"管家模式，帮我……"→ 触发多智能体协作系统；
   - 输入"论文流水线"→ 触发论文写作流水线；
   - 输入"制作简历 / 模拟面试"→ 触发简历制作与优化；
   - PPT 多智能体生成按 `skills/ppt-multiagent/SKILL.md` 中的说明调用。
4. 每个技能的能力、参数与执行流程，以该目录下的 `SKILL.md` 为准。

## 说明

- 本仓库已通过 `.gitignore` 排除 `.workbuddy` 项目本地数据（含个人记忆与凭证），不会上传。
- 各技能为可复用的工作流定义，需配合对应运行环境使用。
- `node_modules/`、`*.bak`、`*.tmp` 等依赖与临时文件已排除。
