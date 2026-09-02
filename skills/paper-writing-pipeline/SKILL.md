---
name: paper-writing-pipeline
description: |
  论文写作流水线式多智能体协作系统，包含五个专业角色：大纲设计、任务分发、内容生成、质量检测、整合校验。
  采用流水线顺序传递通信架构，支持智能体五向任意前置智能体发起重做请求，各智能体间维护共享上下文确保风格统一与内容连贯。
  支持文献预处理、图表/公式占位、领域适配、修订模式、用户确认点、上下文压缩、进度通知等增强功能。
  触发：用户以"论文流水线""论文多智能体""五角色论文"开头，或要求使用流水线式论文写作系统，或工作目录中有 paper-pipeline.md 文件。
agent_created: true
---

# 论文写作流水线多智能体协作系统

## 一、系统概览

### 1.1 架构总览

采用**流水线顺序传递 + 回路重做**的通信架构，五个智能体按序协作完成论文写作。在关键节点设置用户确认点，支持修订模式与进度通知：

```
用户 → [文献预处理(可选)] → 智能体一(大纲设计) → ⏸用户确认 → 智能体二(任务分发)
    → 智能体三(内容生成) → 智能体四(质量检测) → 智能体五(整合校验+摘要生成) → 用户
                                    ↑                      ↑                      ↑                ↑
                                    └──────────────────────┴──────────────────────┴────────────────┘
                                          重做请求回路（智能体四/五→任意前置智能体）
```

### 1.2 角色速览

| 角色 | 智能体 | 职责 | 输入 | 输出 |
|------|--------|------|------|------|
| 智能体一 | 大纲设计 | 理解主题需求，需求完整性检查，生成完整论文大纲 | 用户需求 | 论文大纲（JSON） |
| 智能体二 | 任务分发+写作策略 | 拆解大纲为写作任务，为每章制定写作策略，分发章节 | 论文大纲 | 任务清单+写作策略（JSON） |
| 智能体三 | 内容生成 | 逐章撰写正文，确保学术规范，使用引用池引用 | 分发任务 | 章节初稿（Markdown文件） |
| 智能体四 | 质量检测 | 查重、逻辑检查、语言润色、原创性评估 | 章节初稿 | 质检报告 + 修订稿 |
| 智能体五 | 整合校验+摘要 | 合并全章，检测衔接，生成摘要/关键词，发起重做 | 修订稿 | 完整论文（Markdown） |

### 1.3 核心规则

- **流水线顺序**：智能体一→二→三→四→五，严格按序传递
- **用户确认点**：智能体一产出大纲后暂停流水线，向用户展示大纲并请求确认（可通过 `REQUIRE_OUTLINE_APPROVAL` 参数关闭）
- **回路重做**：智能体四可向智能体三退回，智能体五可向任意前置智能体（一~四）发起重做
- **重做冲突裁决**：多个重做请求冲突时，按优先级 critical > major > minor 排序，同级按章节顺序处理，由智能体五裁决
- **共享上下文**：全流程维护统一的 `SharedContext`，确保风格、术语、引用一致；正文内容以文件形式存储，上下文中仅保留摘要（防膨胀）
- **引用真实性**：所有引用必须来自用户提供的文献池或真实检索结果，**严禁虚构参考文献**
- **摘要延迟生成**：摘要/关键词不进入正常章节流，由智能体五在全文整合后单独生成
- **重做上限**：单环节最多重做 MAX_RETRY 轮（默认 3 轮）
- **进度通知**：每个智能体完成后向用户输出简短进度状态
- **修订模式**：支持用户指定章节进行修订，跳过大纲和任务分发阶段

---

## 二、角色定义

### 智能体一：大纲设计

#### 职责
理解论文主题与用户需求，进行需求完整性检查，生成结构完整、逻辑严密的论文大纲。

#### 输入
- 用户提供的论文主题、类型（综述/研究/学位论文）、学科领域、字数要求、特殊需求
- 用户提供的参考文献列表（如有，支持 BibTeX/RIS/纯文本格式）
- 领域配置（详见 `references/domain_profiles.md`）

#### 执行步骤
1. **需求完整性检查**（P2-9 模糊输入处理）：
   - 检查以下必要信息是否齐全：论文主题、论文类型、学科领域、字数要求、引用格式
   - 缺失关键信息时**暂停并向用户追问**，而非猜测
   - 追问格式：`[需求确认] 缺少以下信息，请补充：1. 论文类型（研究/综述/学位/课程）2. 字数要求 3. 学科领域 ...`
2. **文献预处理**（P1-5 文献检索步骤）：
   - 若用户提供了参考文献列表，解析并录入 `reference_pool`
   - 若用户未提供，使用 WebSearch 检索相关文献（可选，默认关闭，通过 `AUTO_LITERATURE_SEARCH` 参数控制）
   - 若未提供且未检索，在大纲中对应位置标注 `[REF_NEEDED]`
3. 分析论文主题，确定核心研究问题和论文类型
4. 根据论文类型套用对应的章节框架（详见 `references/paper_structures.md`）
5. 根据学科领域加载领域配置（详见 `references/domain_profiles.md`）
6. 为每个章节/小节撰写主题描述、逻辑关联和预期字数
7. **摘要标注为延迟生成**（P0-2 摘要时序倒置）：摘要章节标记 `deferred: true`，不进入正常章节流
8. 标注关键引用位置和所需文献方向，引用来源标注为 `ref_pool` 或 `[REF_NEEDED]`
9. 输出结构化大纲 JSON
10. **暂停流水线，向用户展示大纲并请求确认**（P0-3 用户确认点）

#### 输出格式
```yaml
type: outline
content:
  paper_title: ""
  paper_type: "research | review | thesis | dissertation | course"
  discipline: ""
  domain_profile: ""          # 学科领域配置标识
  total_word_count: N
  citation_style: "GB/T 7714"

  # 文献池状态
  reference_pool_status:
    provided_by_user: true | false
    auto_searched: true | false
    count: N
    needs_user_verification: true | false  # 若无文献池则标注

  # 风格基线（全流程参照）
  style_baseline:
    tone: "学术正式"
    voice: "第三人称"
    sentence_length: "中等"
    paragraph_structure: "主题句-论据-小结"

  chapters:
    - chapter_id: "CH00"
      title: "摘要"
      level: 1
      deferred: true            # P0-2: 标记为延迟生成，不进入正常章节流
      theme: "概括全文研究背景、方法、结果与结论"
      word_count: 250
      subsections: []
      logical_link: "全文总览，由智能体五在全文完成后生成"
      dependencies: ["ALL"]      # 依赖所有章节完成
      key_points:
        - "研究背景与目的"
        - "研究方法"
        - "主要发现"
        - "结论"
      citation_hints: []

    - chapter_id: "CH01"
      title: ""
      level: 1
      deferred: false            # 正常章节
      theme: ""
      word_count: N
      subsections:
        - chapter_id: "CH01.1"
          title: ""
          level: 2
          theme: ""
          word_count: N
          key_points: []
          citation_hints:
            - ref_source: "ref_pool"  # ref_pool | REF_NEEDED
              hint: ""                 # 引用方向提示
      logical_link: ""
      dependencies: []
```

#### 质量要求
- 大纲覆盖论文类型的标准章节结构
- 各章节间逻辑递进清晰，无断裂
- 每个章节有明确的主题和预期字数
- 关键引用位置已标注，来源已区分 ref_pool / REF_NEEDED
- 摘要章节已标记 `deferred: true`
- 需求完整性检查通过（或已向用户追问并获得补充）

#### 用户确认机制（P0-3）
- 智能体一产出大纲后，**暂停流水线**
- 向用户展示大纲概要（标题、章节结构、字数分配、引用格式）
- 用户可调整：章节结构增删、字数重新分配、引用格式变更、主题方向修正
- 用户确认后，将确认后的大纲传递给智能体二
- 若 `REQUIRE_OUTLINE_APPROVAL=false`，跳过此步骤

---

### 智能体二：任务分发 + 写作策略（P2-12 增强）

#### 职责
将大纲分解为具体写作任务，按章节分发，明确每项任务的内容要求与字数约束。**同时为每个章节制定写作策略**，包括论证结构、论据类型、文献使用方案。

#### 输入
- 智能体一输出的论文大纲（经用户确认）
- 共享上下文（风格基线、文献池）

#### 执行步骤
1. 遍历大纲，将每个叶子节点（最末级章节，排除 `deferred=true` 的章节）转化为一个写作任务
2. 为每个任务指定：内容要求、字数约束、写作风格指引、引用规范
3. **制定写作策略**（P2-12 增强）：
   - **论证结构**：演绎式/归纳式/对比式/问题驱动式
   - **论据类型**：数据论证/文献论证/案例论证/理论推演
   - **文献使用方案**：引用哪些文献池中的文献、引用密度建议
   - **图表建议**：是否需要图表/公式，建议类型
4. 标注任务间的依赖关系（如引言需在结论前完成）
5. 生成任务执行顺序（优先处理无依赖的章节，可并行处理的部分标注）
6. 从共享上下文中提取风格基线和文献池，随任务下发

#### 输出格式
```yaml
type: task_distribution
content:
  tasks:
    - task_id: "TASK-001"
      chapter_id: "CH01"
      title: ""
      objective: ""
      content_requirements:
        - ""
      word_limit:
        min: N
        max: N
      style_guide:
        tone: ""
        perspective: ""
        terminology: ""
      citation_style: "APA | MLA | GB/T 7714 | Chicago | IEEE"
      depends_on: []
      priority: "high | medium | low"

      # P2-12: 写作策略（新增）
      writing_strategy:
        argument_structure: "deductive | inductive | comparative | problem_driven"
        evidence_type: "data | literature | case | theoretical"
        citation_plan:
          suggested_refs: []     # 建议使用的文献池中的文献 ID
          citation_density: "high | medium | low"
        figure_suggestions:       # 图表建议
          - type: "table | chart | diagram | formula"
            description: ""
            placement: "after_section X"
        key_arguments: []         # 核心论点列表

      shared_context_snapshot: {}
```

#### 质量要求
- 每个任务有明确的字数上下限
- 任务粒度合理（单任务 500-3000 字为宜）
- 依赖关系标注准确，无循环依赖
- 风格指引完整，可直接指导写作
- 写作策略明确，论证结构和论据类型清晰
- 文献使用方案可操作（引用哪些文献、引用密度）

---

### 智能体三：内容生成

#### 职责
接收分发任务，完成各章节的正文写作，确保学术语言规范、引用格式正确。**引用只能从文献池中选取，严禁虚构文献。**

#### 输入
- 智能体二分发的写作任务（含写作策略）
- 共享上下文（风格基线、已有章节摘要、术语表、文献池）

#### 执行步骤
1. 解析任务要求和写作策略，确认字数、风格、引用格式、论证结构
2. 参考共享上下文中的术语表、风格基线和已有章节摘要
3. 撰写正文，确保：
   - 学术语言规范，避免口语化
   - 论点有据，按写作策略的论证结构组织
   - 引用格式正确（详见 `references/citation_formats.md`）
   - 段落间逻辑衔接自然
   - 字数在约束范围内
4. **引用处理**（P0-1 引用真实性）：
   - 从 `reference_pool` 中选取文献，使用 `[CITE:ref_id]` 标记
   - 若文献池中无合适文献，使用 `[REF_NEEDED:描述]` 标记，**不得虚构文献**
   - 同一文献多次引用使用相同 ref_id
5. **图表/公式占位**（P1-6 图表公式管线）：
   - 图表占位：`[FIG:type|description]`，如 `[FIG:table|三种方法性能对比]`
   - 公式占位：`[EQ:latex_code]`，如 `[EQ:E=mc^2]`
6. 将正文写入文件（`chapters/CH01.md`），在共享上下文中仅记录摘要和文件路径（P0-4 上下文压缩）
7. 生成内容元数据：实际字数、引用列表、写作说明

#### 输出格式
```yaml
type: content_draft
content:
  task_id: "TASK-001"
  chapter_id: "CH01"
  file_path: "chapters/CH01.md"    # P0-4: 正文存储为文件
  summary: ""                       # 一句话摘要（存入上下文）
  metadata:
    actual_word_count: N
    citations:
      - marker: "[CITE:ref_001]"
        ref_pool_id: "ref_001"      # 引用池中的文献 ID
        location: "paragraph N"
      - marker: "[REF_NEEDED:关于XX的实证研究]"
        ref_pool_id: null           # 文献池中无匹配
        location: "paragraph N"
    figures:                        # P1-6: 图表占位
      - marker: "[FIG:table|三种方法性能对比]"
        type: "table"
        description: ""
        placement: "paragraph N"
    equations:                      # P1-6: 公式占位
      - marker: "[EQ:E=mc^2]"
        latex: ""
        placement: "paragraph N"
    writing_notes:
      assumptions: []
      limitations: []
      pending_issues: []
```

#### 质量要求
- 正文字数在任务约束范围内（±10% 容差）
- 学术语言规范，无口语化表达
- 引用标记格式正确，来源可追溯（ref_pool 或 REF_NEEDED）
- 段落逻辑连贯，过渡自然
- 术语使用与共享上下文一致
- **无虚构文献**（所有引用均有来源或标注 REF_NEEDED）

---

### 智能体四：质量检测

#### 职责
对生成内容进行查重检测、逻辑一致性检查、语言润色优化与原创性评估，标记需修改的部分。

#### 输入
- 智能体三输出的章节初稿（文件路径 + 摘要）
- 共享上下文

#### 执行步骤
1. **查重检测**：检测内容是否存在重复、抄袭嫌疑（内部查重：检测与共享上下文中已有章节摘要的重复度）
2. **逻辑一致性检查**：
   - 论点与大纲主题是否一致
   - 章节内逻辑是否自洽
   - 数据/结论是否矛盾
3. **语言润色**：
   - 修正语法错误、标点问题
   - 优化学术表达（被动语态、专业术语）
   - 统一引用格式
4. **引用真实性校验**（P0-1）：
   - 检查所有 `[CITE:ref_id]` 是否在文献池中存在
   - 检查 `[REF_NEEDED]` 标记是否合理
   - **若发现虚构文献（引用池中不存在但未标注 REF_NEEDED），直接 reject**
5. **原创性评估**（P2-11）：
   - 评估是否有明确的创新点声明
   - 评估研究贡献的阐述是否充分
6. **评分**：按五维度评分（完整性/正确性/学术规范性/语言质量/原创性，详见 `references/quality_criteria.md`）
7. 输出质检报告和修订稿

#### 输出格式
```yaml
type: quality_report
content:
  task_id: "TASK-001"
  chapter_id: "CH01"
  file_path: "chapters/CH01_revised.md"  # 修订稿文件路径
  scores:
    completeness: N          # 完整性 1-5
    correctness: N           # 正确性 1-5
    academic_norm: N         # 学术规范性 1-5
    language_quality: N      # 语言质量 1-5
    originality: N           # P2-11: 原创性 1-5（研究论文/学位论文必评，综述/课程论文可选）
  citation_verification:     # P0-1: 引用真实性校验
    total_citations: N
    verified: N              # 在文献池中验证通过的
    ref_needed: N           # 标注为 REF_NEEDED 的
    fabricated: N           # 虚构文献数量（必须为 0，否则 reject）
  issues:
    - issue_id: "ISS-001"
      type: "plagiarism | logic | language | format | citation | originality"
      severity: "critical | major | minor"
      location: "paragraph N, sentence M"
      description: ""
      suggestion: ""
      resolved: true | false
  overall_verdict: "pass | revise | reject"
```

#### 质量要求
- 五维度评分全部 >= 3 分方可通过（原创性维度仅研究论文/学位论文必评）
- critical 级别问题必须修复或在报告中明确标记
- 润色后的文本不得改变原意
- 引用格式统一为目标格式
- **fabricated 必须为 0，否则直接 reject**

#### 退回规则
- `overall_verdict: reject` → 退回智能体三重写（附退回原因）
- `overall_verdict: revise` → 附修改建议退回智能体三修订
- `overall_verdict: pass` → 传递给智能体五

---

### 智能体五：整合校验 + 摘要生成

#### 职责
合并所有章节，检测上下文衔接与内容合理性。**在全文整合后单独生成摘要和关键词**（P0-2 摘要时序倒置）。若发现不合理部分，将问题回传对应智能体重做。最终整合为完整论文并输出。

#### 输入
- 智能体四通过的所有章节修订稿（文件路径列表）
- 共享上下文
- 智能体一的大纲（用于对照检查完整性）

#### 执行步骤
1. **章节合并**：按大纲顺序读取并合并所有章节文件
2. **衔接检测**：
   - 章节间过渡是否自然
   - 术语是否前后一致
   - 引用编号是否连续
   - 交叉引用是否正确
3. **全局一致性检查**：
   - 全文逻辑主线是否贯穿
   - 结论是否回应引言提出的问题
4. **图表/公式处理**（P1-6）：
   - 将 `[FIG:type|description]` 替换为图表描述（文字描述 + 建议制图方案）
   - 将 `[EQ:latex]` 替换为公式编号
   - 生成图表/公式索引
5. **引用整合**（P0-1）：
   - 将 `[CITE:ref_id]` 替换为正式引用编号 `[1]`、`[2]`...
   - 从文献池生成参考文献列表
   - `[REF_NEEDED]` 标记保留并在文末汇总为"需人工核实的引用清单"
6. **摘要生成**（P0-2 摘要时序倒置）：
   - 基于全文内容生成摘要（涵盖研究背景、方法、结果、结论）
   - 提取关键词（3-6 个）
   - 确保摘要准确概括全文，与正文呼应
7. **完整性校验**：对照大纲检查是否所有章节均已完成
8. **格式统一**：统一全文格式（标题层级、图表编号、参考文献格式）
9. **决策**：
   - 全部通过 → 输出完整论文
   - 发现问题 → 向对应智能体发起重做请求（按 P2-10 优先级规则处理冲突）

#### 输出格式（最终论文）
```yaml
type: final_paper
content:
  title: ""
  authors: []
  abstract: ""                  # P0-2: 由智能体五生成
  keywords: []                  # P0-2: 由智能体五生成
  body_file: "论文_标题.md"     # 完整论文文件路径
  references:
    - id: 1
      entry: ""
      ref_pool_id: "ref_001"    # 对应文献池中的 ID
  ref_needed_list:              # P0-1: 需人工核实的引用
    - marker: "[REF_NEEDED:描述]"
      location: "chapter X, paragraph Y"
      description: ""
  figure_index:                 # P1-6: 图表索引
    - id: "图 1-1"
      title: ""
      type: "table | chart | diagram"
      source: "auto_generated | user_provided"
  equation_index:               # P1-6: 公式索引
    - id: "(2-1)"
      latex: ""
      description: ""
  metadata:
    total_word_count: N
    chapter_count: N
    reference_count: N
    ref_needed_count: N         # 需人工核实的引用数量
    quality_scores:
      completeness: N
      correctness: N
      academic_norm: N
      language_quality: N
      originality: N            # P2-11
      coherence: N
      consistency: N
      responsiveness: N
      overall: N
```

#### 重做请求格式
```yaml
type: redo_request
content:
  target_agent: "1 | 2 | 3 | 4"
  trigger_task_id: "TASK-001"
  issue:
    type: "coherence | gap | conflict | format | citation | originality"
    severity: "critical | major | minor"   # P2-10: 优先级标记
    description: ""
    location: "chapter X, section Y"
    suggested_fix: ""
  shared_context_update: {}
```

#### 重做冲突裁决规则（P2-10）
当智能体五需要同时向多个智能体发起重做请求时：
1. **按优先级排序**：critical > major > minor
2. **同级按章节顺序**：CH01 优先于 CH02，以此类推
3. **冲突裁决**：若两个请求针对同一章节但方向矛盾（如"加长引言"vs"缩短引言"），由智能体五根据全局质量裁决，取其一执行
4. **批量处理**：同优先级、同章节的多个问题合并为一个重做请求
5. **串行执行**：高优先级重做完成后，重新评估低优先级重做是否仍需执行

#### 质量要求
- 全文章节完整，无遗漏
- 章节衔接自然，无断裂感
- 术语全文一致
- 引用编号连续无缺
- 摘要准确概括全文，与正文呼应（P0-2）
- 无虚构文献（P0-1）
- 图表/公式占位已全部替换（P1-6）

---

## 三、共享上下文管理

### 3.1 SharedContext 结构

全流程维护一个共享上下文对象。**正文内容以文件形式存储，上下文中仅保留摘要和文件路径**（P0-4 上下文压缩），防止上下文膨胀：

```yaml
shared_context:
  # 论文元信息（智能体一初始化，全流程只读）
  paper_meta:
    title: ""
    type: ""
    discipline: ""
    domain_profile: ""            # P1-7: 学科领域配置标识
    target_word_count: N
    citation_style: ""
    language: "zh-CN"

  # 风格基线（智能体一初始化，智能体三参照）
  style_baseline:
    tone: ""
    voice: ""
    sentence_length: ""
    paragraph_structure: ""
    example_paragraph: ""

  # 文献池（P0-1/P1-5: 智能体一初始化，全流程只读）
  reference_pool:
    provided_by_user: true | false
    auto_searched: true | false
    references:
      - ref_id: "ref_001"
        entry: ""                 # 完整引用条目
        type: "journal | book | conference | thesis | online"
        verified: true            # 是否已验证真实性
    unverified_count: N           # 需人工核实的数量

  # 术语表（各智能体追加）
  glossary:
    - term: ""
      definition: ""
      first_used_in: "CH01"
      english_equiv: ""
      variations: []

  # 已完成章节索引（P0-4: 仅保留摘要+文件路径，不存正文全文）
  completed_chapters:
    - chapter_id: "CH01"
      task_id: "TASK-001"
      file_path: "chapters/CH01.md"    # 正文文件路径
      word_count: N
      status: "drafted | reviewed | integrated"
      summary: ""                       # 一句话摘要（≤100字）
      key_terms: []                     # 本章引入的关键术语

  # 引用登记（智能体三追加，智能体四校验，智能体五整合）
  citation_registry:
    - marker: "[CITE:ref_001]"
      chapter_id: "CH01"
      ref_pool_id: "ref_001"
      status: "pending | resolved | ref_needed"  # P0-1: 增加 ref_needed 状态

  # 图表/公式登记（P1-6: 智能体三追加，智能体五整合）
  figure_registry:
    - marker: "[FIG:table|描述]"
      chapter_id: "CH01"
      type: "table | chart | diagram"
      description: ""
      resolved: false
  equation_registry:
    - marker: "[EQ:latex]"
      chapter_id: "CH02"
      latex: ""
      resolved: false

  # 全局问题追踪（智能体四/五追加）
  issue_log:
    - issue_id: ""
      raised_by: "agent4 | agent5"
      status: "open | resolved | deferred"
      description: ""

  # 重做请求队列（P2-10: 智能体五维护，按优先级排序）
  redo_queue:
    - request_id: "REDO-001"
      target_agent: 3
      task_id: "TASK-001"
      severity: "critical | major | minor"
      status: "pending | executing | completed | cancelled"
      description: ""

  # 流程状态
  pipeline_state:
    current_agent: 1
    current_task: null
    mode: "full | revision"          # P1-8: 运行模式
    revision_targets: []             # P1-8: 修订模式下的目标章节
    retry_counts: {}
    total_chapters: 0
    completed_count: 0
    progress_log: []                  # P2-13: 进度日志
```

### 3.2 上下文压缩策略（P0-4）

当 SharedContext 体积增长时，采取以下压缩策略：

| 策略 | 触发条件 | 操作 |
|------|---------|------|
| 文件外置 | 所有章节 | 正文写入 `chapters/` 目录文件，上下文仅存路径+摘要 |
| 摘要压缩 | 单个 chapter summary > 100 字 | 截断为 100 字以内的核心摘要 |
| 术语表瘦身 | glossary 条目 > 50 | 仅保留当前章节及前一章引入的术语 |
| 引用登记归档 | citation_registry > 100 条 | 已 resolved 的引用归档为摘要统计 |
| 历史问题清理 | issue_log > 30 条 | 已 resolved 的问题移至归档文件 |

### 3.3 上下文更新规则

| 时机 | 更新者 | 更新内容 |
|------|--------|---------|
| 大纲完成后 | 智能体一 | paper_meta, style_baseline, reference_pool, glossary(初始), pipeline_state |
| 用户确认后 | 系统 | pipeline_state.current_agent=2 |
| 任务分发后 | 智能体二 | pipeline_state.current_agent=3 |
| 章节初稿后 | 智能体三 | completed_chapters(追加摘要+路径), citation_registry, figure_registry, equation_registry, glossary(追加) |
| 质检完成后 | 智能体四 | issue_log, citation_registry(status更新), completed_chapters(status→reviewed) |
| 整合校验后 | 智能体五 | completed_chapters(status→integrated), issue_log, pipeline_state |

### 3.4 上下文传递方式

采用**快照传递**：每个智能体产出时附带 `shared_context_snapshot`，下游智能体基于快照工作。重做时传递最新快照 + 变更说明。

---

## 四、协作流程

### 4.1 主流程（流水线）

```
[用户输入]
    │
    ▼
[需求完整性检查] ──缺失──→ [向用户追问] ──补充──→ [重新检查]
    │ (齐全)
    ▼
[文献预处理(可选)] ──解析文献列表/检索──→ [建立 reference_pool]
    │
    ▼
[智能体一] 理解需求 → 生成大纲 → 更新共享上下文
    │
    ▼
⏸ [用户确认大纲] ──调整──→ [智能体一修订大纲] ──再确认
    │ (确认)
    ▼
[智能体二] 拆解任务 + 制定写作策略 → 生成任务清单
    │
    ▼ (逐任务)
[智能体三] 撰写正文 → 标注引用(仅限文献池) → 标注图表/公式占位 → 写入文件
    │
    ▼
[智能体四] 查重 → 逻辑检查 → 润色 → 引用真实性校验 → 原创性评估 → 评分
    │
    ├── verdict=reject/revise ──退回──→ [智能体三] (≤MAX_RETRY轮)
    │
    └── verdict=pass
            │
            ▼
[智能体五] 合并 → 衔接检测 → 全局一致性 → 图表/公式替换 → 引用整合
    │
    ├── 摘要/关键词生成(基于全文) ──→ 填入论文
    │
    ├── 发现问题 ──重做请求(按优先级排序)──→ [智能体一/二/三/四] (≤MAX_RETRY轮)
    │
    └── 全部通过
            │
            ▼
[输出完整论文] → [生成需人工核实引用清单] → [用户]
```

### 4.2 进度通知机制（P2-13）

每个智能体完成当前阶段后，向用户输出简短进度状态：

```
[1/5] 大纲设计完成 — 共 N 章, M 个写作任务, 文献池 K 篇 → 等待用户确认大纲
[2/5] 任务分发完成 — 共 M 个任务, 开始逐章撰写...
[3/5] 内容生成中 — 已完成 X/M 章 (当前: CH03 方法)
[4/5] 质量检测中 — 已检测 X/M 章 (当前: CH03, 评分: 完整性4 正确性4...)
[5/5] 整合校验完成 — 全文 N 字, K 篇引用, L 个图表, J 个需人工核实引用 → 输出论文
```

- 退回重做时通知：`[重做] CH03 质检未通过(正确性2分), 退回智能体三修订 (第2/3轮)`
- 重做请求时通知：`[全局重做] 智能体五发现 CH02-CH03 衔接断裂, 请求智能体三重写 CH03 (第1/3轮)`

### 4.3 修订模式（P1-8）

用户可指定修订已有论文的特定章节，跳过大纲和任务分发阶段：

```
用户：修订论文，修改第三章方法部分，增加消融实验
    │
    ▼
[修订模式启动]
    ├── 读取已有论文 + 共享上下文
    ├── 定位修订目标：CH03
    ├── 从智能体三开始：重写 CH03
    ├── 智能体四质检
    └── 智能体五重新整合全文
```

修订模式规则：
- `pipeline_state.mode = "revision"`
- `pipeline_state.revision_targets = ["CH03"]`
- 跳过智能体一和智能体二（除非大纲需要调整）
- 智能体三仅处理 revision_targets 中的章节
- 智能体五重新整合全文（检查修订章节与未修订章节的衔接）

### 4.4 重做回路

#### 智能体四 → 智能体三（章节级重做）
- 触发条件：质检不通过（任一维度 < 3 分，或 fabricated > 0）
- 重做范围：单个章节
- 上限：MAX_RETRY 轮
- 传递内容：质检报告 + 退回意见 + 共享上下文快照

#### 智能体五 → 智能体一（大纲级重做）
- 触发条件：全局逻辑断裂、章节缺失、主题偏离
- 重做范围：大纲调整
- 上限：MAX_RETRY 轮
- 传递内容：重做请求 + 问题描述 + 全局上下文

#### 智能体五 → 智能体二（任务级重做）
- 触发条件：任务分配不合理、字数约束偏差大、依赖关系错误
- 重做范围：任务重新分发
- 上限：MAX_RETRY 轮

#### 智能体五 → 智能体三（内容级重做）
- 触发条件：章节衔接断裂、术语不一致、引用缺失
- 重做范围：指定章节重写
- 上限：MAX_RETRY 轮

#### 智能体五 → 智能体四（质检遗漏）
- 触发条件：整合后发现质检未覆盖的问题
- 重做范围：补充质检
- 上限：MAX_RETRY 轮

### 4.5 超限降级

当某环节重做超过 MAX_RETRY 轮仍未通过：
1. 智能体五向用户报告问题
2. 提供选项：
   - **降标使用**：接受当前版本，标注已知问题
   - **补充信息重试**：用户提供额外指引后重试
   - **人工接管**：用户自行修改标注部分

---

## 五、质量评审标准

### 5.1 评审维度

#### 核心维度（智能体四必评）

| 维度 | 说明 | 5分 | 3分 | 1分 |
|------|------|-----|-----|-----|
| **完整性** | 任务要求覆盖度 | 超出要求，主动补充关联内容 | 核心要求全覆盖，边缘项略有遗漏 | 遗漏 >50% 核心要求 |
| **正确性** | 学术事实与逻辑 | 数据可溯源，逻辑无懈可击 | 核心逻辑正确，有次要瑕疵 | 核心论点错误或事实矛盾 |
| **学术规范性** | 格式、引用、术语 | 完全符合学术规范，可投稿标准 | 主体合规，个别格式瑕疵 | 格式混乱，引用缺失 |
| **语言质量** | 学术表达水平 | 学术语言精准，行文流畅 | 语言通顺，个别口语化 | 语言混乱，无法阅读 |
| **原创性** (P2-11) | 创新点与贡献 | 有明确创新点声明，贡献阐述充分 | 有一定创新性，但阐述不够突出 | 无创新点，纯堆砌已有工作 |

> **原创性维度**：研究论文和学位论文必评，综述论文和课程论文可选（通过 `EVALUATE_ORIGINALITY` 参数控制）

#### 全局维度（智能体五必评）

| 维度 | 说明 | 5分 | 3分 | 1分 |
|------|------|-----|-----|-----|
| **连贯性** | 章节衔接与逻辑主线 | 全文一气呵成，过渡自然 | 主体连贯，个别章节衔接生硬 | 章节割裂，逻辑断裂 |
| **一致性** | 术语、风格、引用统一 | 全文完全统一 | 主体一致，个别术语不一致 | 多处不一致 |
| **呼应性** | 摘要-正文-结论呼应 | 完美呼应，无偏差 | 基本呼应，细节略有出入 | 结论与引言脱节 |

#### 领域特有维度（P1-7）

根据学科领域，加载额外的评审维度（详见 `references/domain_profiles.md`）：
- CS/工程：可复现性、代码可用性
- 医学：伦理声明、临床试验注册
- 社科：数据来源说明、研究伦理
- 人文：文本细读深度、引文准确性

### 5.2 通过条件

- 智能体四：核心维度全 >= 3 分 且 fabricated=0 → 通过
- 智能体五：全局维度全 >= 3 分 且 无 critical 级问题 → 通过
- 任一维度 < 3 分 → 退回重做

### 5.3 退回反馈规范

退回意见必须包含三要素，禁止模糊反馈：

```
[维度] 得分X — 具体问题描述（位置+现象） → 建议：可操作的修改方案
```

**禁止**："不够好""再改改""太单薄""优化一下""感觉不对"等模糊表述

---

## 六、消息格式总览

### 智能体间通信统一信封

所有智能体间消息使用统一信封格式：

```yaml
message:
  msg_id: "MSG-{uuid}"
  msg_type: "outline | task_distribution | content_draft | quality_report | final_paper | redo_request | progress | approval_request"
  from_agent: "1 | 2 | 3 | 4 | 5"
  to_agent: "1 | 2 | 3 | 4 | 5 | user"
  timestamp: "ISO 8601"
  attempt: N                    # 第几轮（重做计数）
  shared_context_snapshot: {}
  payload: {}
```

### 消息流转规则

| 消息类型 | 发送方 → 接收方 | 说明 |
|---------|----------------|------|
| outline | 智能体一 → 用户 | 大纲产出，请求确认 |
| approval | 用户 → 系统 | 用户确认/调整大纲 |
| task_distribution | 智能体二 → 智能体三 | 任务分发 |
| content_draft | 智能体三 → 智能体四 | 章节初稿 |
| quality_report | 智能体四 → 智能体三 | 质检退回（revise/reject） |
| quality_report | 智能体四 → 智能体五 | 质检通过（pass） |
| redo_request | 智能体五 → 智能体一/二/三/四 | 整合阶段重做请求 |
| progress | 智能体N → 用户 | 进度通知 |
| final_paper | 智能体五 → 用户 | 最终论文输出 |

---

## 七、参数配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| MAX_RETRY | 3 | 单环节最大重做次数 |
| PASS_THRESHOLD | 3 | 单维度最低通过分 |
| WORD_TOLERANCE | 10% | 字数容差百分比 |
| PARALLEL_CHAPTERS | false | 是否允许并行章节写作 |
| CITATION_STYLE | GB/T 7714 | 默认引用格式 |
| CHECK_PLAGIARISM | true | 是否启用查重检测 |
| STRICT_MODE | true | 严格模式：任一不达标即退回 |
| DEFAULT_PAPER_TYPE | research | 默认论文类型 |
| LANGUAGE | zh-CN | 默认写作语言 |
| REQUIRE_OUTLINE_APPROVAL | true | P0-3: 大纲产出后是否暂停等待用户确认 |
| AUTO_LITERATURE_SEARCH | false | P1-5: 是否自动检索文献（需用户未提供文献时） |
| EVALUATE_ORIGINALITY | true | P2-11: 是否评估原创性（研究/学位论文建议 true） |
| ENABLE_FIGURE_PIPELINE | true | P1-6: 是否启用图表/公式占位管线 |
| CONTEXT_COMPRESSION | true | P0-4: 是否启用上下文压缩（正文文件外置） |
| MAX_CONTEXT_SIZE | 50000 | P0-4: SharedContext 最大字符数，超过触发强制压缩 |
| ENABLE_PROGRESS_NOTIFICATION | true | P2-13: 是否启用进度通知 |
| ENABLE_REVISION_MODE | true | P1-8: 是否启用修订模式 |
| REVISION_SKIP_AGENTS | [1, 2] | P1-8: 修订模式跳过的智能体 |

---

## 八、执行指南

### 8.1 触发条件

以下任一条件触发本系统：
- 用户以"论文流水线""论文多智能体""五角色论文"开头
- 用户要求使用流水线式论文写作系统
- 工作目录中存在 `paper-pipeline.md` 文件
- 用户明确要求使用本 Skill 的五角色协作架构

### 8.2 执行步骤（完整模式）

1. **初始化**：创建共享上下文，读取用户需求
2. **需求完整性检查**（P2-9）：检查必要信息是否齐全，缺失则追问
3. **文献预处理**（P1-5）：解析用户提供的文献列表或自动检索
4. **智能体一启动**：生成大纲，更新共享上下文
5. **⏸ 用户确认**（P0-3）：展示大纲，等待用户确认/调整
6. **智能体二启动**：拆解任务 + 制定写作策略
7. **逐章节循环**：
   - 智能体三撰写（写入文件） → 智能体四质检
   - 不通过则退回（≤MAX_RETRY 轮）
   - 通过则继续下一章节
   - 每章完成后输出进度通知（P2-13）
8. **智能体五启动**：合并所有章节，全局校验
9. **摘要生成**（P0-2）：基于全文生成摘要和关键词
10. **图表/公式替换**（P1-6）：替换占位标记
11. **引用整合**（P0-1）：替换引用编号，生成参考文献列表
12. **重做回路**：如需重做，按优先级排序后向对应智能体发起请求（≤MAX_RETRY 轮）
13. **输出**：生成完整论文 + 需人工核实引用清单，呈现给用户

### 8.3 执行步骤（修订模式 P1-8）

1. 读取已有论文和共享上下文
2. 确定修订目标和范围
3. 跳过智能体一、二，直接从智能体三开始
4. 智能体三重写指定章节
5. 智能体四质检
6. 智能体五重新整合全文（检查修订章节与未修订章节的衔接）
7. 输出修订后的完整论文

### 8.4 论文类型适配

不同论文类型的章节结构不同，智能体一根据论文类型选择对应框架：
- 详见 `references/paper_structures.md`
- 研究论文：引言 → 相关工作 → 方法 → 实验 → 讨论 → 结论
- 综述论文：引言 → 分类框架 → 分主题综述 → 对比分析 → 趋势展望 → 结论
- 学位论文：绪论 → 文献综述 → 研究方法 → 研究内容(多章) → 总结
- 课程论文：引言 → 正文(分析/论证) → 结论
- **所有类型**：摘要/关键词均由智能体五在全文完成后生成（P0-2）

### 8.5 领域适配（P1-7）

根据学科领域加载领域配置（详见 `references/domain_profiles.md`）：
- 加载特有章节（如医学的伦理审查、CS 的代码仓库链接）
- 加载特有评审维度（如 CS 的可复现性）
- 加载引用格式偏好

### 8.6 引用格式支持

系统支持以下引用格式，由智能体二根据需求指定：
- 详见 `references/citation_formats.md`
- GB/T 7714（中国国家标准，默认）
- APA（美国心理学会）
- MLA（现代语言协会）
- Chicago（芝加哥格式）
- IEEE（电气电子工程师学会）

### 8.7 引用真实性声明（P0-1）

**本系统严禁虚构参考文献。** 所有引用必须满足以下条件之一：
1. 来自用户提供的文献池（`reference_pool`）
2. 来自自动检索的真实文献（`AUTO_LITERATURE_SEARCH=true` 时）
3. 标注为 `[REF_NEEDED:描述]`，由用户后续人工核实

最终输出的论文中，所有 `[REF_NEEDED]` 标记将汇总为"需人工核实的引用清单"，附在论文末尾。

### 8.8 输出文件

最终论文以 Markdown 格式输出到工作目录：
- 论文文件：`论文_论文标题.md`
- 质检报告：`质检报告_论文标题.md`
- 修改日志（如有重做）：`修改日志_论文标题.md`
- 需人工核实引用清单（如有）：`需核实引用_论文标题.md`
- 章节文件（中间产物）：`chapters/CHXX.md`

---

## 九、参考资源索引

| 资源 | 路径 | 用途 |
|------|------|------|
| 论文结构框架 | `references/paper_structures.md` | 智能体一选择章节框架 |
| 引用格式指南 | `references/citation_formats.md` | 智能体三/四/五统一引用格式 |
| 质量评审标准 | `references/quality_criteria.md` | 智能体四/五评分参照 |
| 领域适配配置 | `references/domain_profiles.md` | P1-7: 学科领域特有配置 |
| 论文大纲模板 | `assets/outline_template.md` | 智能体一大纲输出模板 |
| 共享上下文模板 | `assets/shared_context_template.md` | 全流程上下文初始化模板 |
| 论文输出模板 | `assets/paper_template.md` | 智能体五最终输出模板 |
