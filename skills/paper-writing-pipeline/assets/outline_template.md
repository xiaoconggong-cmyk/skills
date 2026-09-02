# 论文大纲输出模板

> 本模板供智能体一（大纲设计）使用，按以下 YAML 格式输出论文大纲。
>
> **P0-1 引用真实性**：citation_hints 必须标注来源（ref_pool / REF_NEEDED）
> **P0-2 摘要延迟**：摘要章节标记 `deferred: true`，不进入正常章节流
> **P2-9 模糊输入处理**：智能体一在生成大纲前必须进行需求完整性检查

## 前置：需求完整性检查（P2-9）

在生成大纲前，智能体一必须检查以下必要信息：

| 必要信息 | 是否必须 | 缺失时处理 |
|---------|---------|-----------|
| 论文主题 | ✅ 必须 | 向用户追问 |
| 论文类型 | ✅ 必须 | 向用户追问（研究/综述/学位/课程） |
| 学科领域 | ✅ 必须 | 向用户追问 |
| 字数要求 | ✅ 必须 | 向用户追问 |
| 引用格式 | ⬜ 可选 | 按决策树自动选择 |
| 参考文献列表 | ⬜ 可选 | 标注 REF_NEEDED 或自动检索 |

> 缺失必须信息时，暂停大纲生成，向用户发送：
> `[需求确认] 缺少以下信息，请补充：1. 论文类型 2. 字数要求 ...`

## 大纲模板

```yaml
type: outline
content:
  paper_title: ""           # 论文标题
  paper_type: "research"    # research | review | thesis | dissertation | course
  discipline: ""            # 学科领域
  domain_profile: ""        # P1-7: 学科领域配置标识（cs_ai | medical | humanities | social_science | engineering | general）
  total_word_count: 8000    # 总字数
  citation_style: "GB/T 7714"  # 引用格式

  # P0-1/P1-5: 文献池状态
  reference_pool_status:
    provided_by_user: false  # 用户是否提供了参考文献列表
    auto_searched: false     # 是否自动检索了文献
    count: 0                 # 文献池中的文献数量
    needs_user_verification: true  # 是否需要用户核实引用

  # 风格基线（全流程参照）
  style_baseline:
    tone: "学术正式"          # 学术正式 | 通俗科普 | 半正式
    voice: "第三人称"         # 第一人称 | 第三人称 | 被动语态为主
    sentence_length: "中等"  # 短句为主 | 中等 | 长句为主
    paragraph_structure: "主题句-论据-小结"  # 段落组织模式

  chapters:
    # === 摘要（P0-2: 延迟生成，不进入正常章节流）===
    - chapter_id: "CH00"
      title: "摘要"
      level: 1
      deferred: true             # P0-2: 标记为延迟生成
      theme: "概括全文研究背景、方法、结果与结论"
      word_count: 250
      subsections: []
      logical_link: "全文总览，由智能体五在全文完成后生成"
      dependencies: ["ALL"]      # 依赖所有正文章节完成
      key_points:
        - "研究背景与目的"
        - "研究方法"
        - "主要发现"
        - "结论"
      citation_hints: []

    # === 引言 ===
    - chapter_id: "CH01"
      title: "引言"
      level: 1
      deferred: false             # 正常章节
      theme: "阐述研究背景、问题陈述、研究意义与论文结构"
      word_count: 1200
      subsections:
        - chapter_id: "CH01.1"
          title: "研究背景"
          level: 2
          theme: "介绍领域现状与研究动机"
          word_count: 400
          key_points:
            - "领域发展现状"
            - "现有研究的不足"
          citation_hints:
            - ref_source: "ref_pool"   # P0-1: 来源标注
              hint: "引用领域综述文献"
            - ref_source: "REF_NEEDED"  # P0-1: 文献池中无匹配
              hint: "需要引用最新的领域发展数据"
        - chapter_id: "CH01.2"
          title: "问题陈述"
          level: 2
          theme: "明确本文要解决的核心问题"
          word_count: 300
          key_points:
            - "研究问题的精确定义"
            - "问题的学术/实际意义"
          citation_hints: []
        - chapter_id: "CH01.3"
          title: "论文结构"
          level: 2
          theme: "概述后续各章内容安排"
          word_count: 200
          key_points:
            - "各章节内容概述"
          citation_hints: []
      logical_link: "引言是全文开篇，为后续章节设定背景和方向"
      dependencies: []
      key_points: []
      citation_hints: []

    # === 方法（按需添加更多章节）===
    - chapter_id: "CH02"
      title: "方法"
      level: 1
      deferred: false
      theme: "详细描述研究方法与技术路线"
      word_count: 2000
      subsections:
        - chapter_id: "CH02.1"
          title: "总体框架"
          level: 2
          theme: "方法整体架构概述"
          word_count: 400
          key_points:
            - "方法整体设计思路"
            - "各模块功能划分"
          citation_hints: []
        - chapter_id: "CH02.2"
          title: "核心方法"
          level: 2
          theme: "核心技术/算法详细描述"
          word_count: 1000
          key_points:
            - "方法原理"
            - "技术细节"
            - "创新点"
          citation_hints:
            - ref_source: "ref_pool"
              hint: "引用方法相关的理论基础文献"
      logical_link: "承接引言中的问题陈述，提出解决方法"
      dependencies: ["CH01"]
      key_points: []
      citation_hints: []

    # === 更多章节按此模式添加 ===

    # === 结论 ===
    - chapter_id: "CH99"
      title: "结论"
      level: 1
      deferred: false
      theme: "总结全文贡献，指出未来方向"
      word_count: 500
      subsections: []
      logical_link: "回应引言中提出的问题，总结全文"
      dependencies: ["CH01", "CH02"]
      key_points:
        - "主要贡献总结"
        - "未来工作方向"
      citation_hints: []
```

## 使用说明

1. 先进行**需求完整性检查**（P2-9），缺失必要信息时向用户追问
2. 根据 `references/paper_structures.md` 选择论文类型的章节框架
3. 根据 `references/domain_profiles.md` 加载学科领域配置（P1-7）
4. 按上述模板填充每个章节的信息
5. `chapter_id` 按层级编码：`CH01`（一级）、`CH01.1`（二级）、`CH01.1.1`（三级）
6. `logical_link` 描述本章节与前后章节的逻辑关系
7. `dependencies` 标注依赖的前序章节 ID
8. `citation_hints` 标注该章节需要的引用方向，`ref_source` 必须标注为 `ref_pool` 或 `REF_NEEDED`（P0-1）
9. `word_count` 为预期字数，各章节字数之和应约等于 `total_word_count`
10. **摘要章节必须标记 `deferred: true`**，不生成写作任务（P0-2）
11. 大纲产出后暂停，等待用户确认（P0-3，`REQUIRE_OUTLINE_APPROVAL=true` 时）
