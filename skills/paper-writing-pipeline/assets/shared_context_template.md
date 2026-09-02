# 共享上下文模板

> 本模板定义全流程共享上下文的初始结构，由智能体一初始化，各智能体按规则更新。
>
> **P0-4 上下文压缩**：正文内容以文件形式存储（`chapters/` 目录），上下文中仅保留摘要和文件路径，防止上下文膨胀。
> **P0-1 引用真实性**：新增 `reference_pool` 模块，所有引用必须来自文献池或标注 REF_NEEDED。
> **P1-6 图表/公式管线**：新增 `figure_registry` 和 `equation_registry`。
> **P2-10 重做冲突处理**：新增 `redo_queue` 模块，按优先级排序。

```yaml
shared_context:
  # ===== 论文元信息（智能体一初始化，全流程只读）=====
  paper_meta:
    title: ""
    type: ""                    # research | review | thesis | dissertation | course
    discipline: ""
    domain_profile: ""          # P1-7: 学科领域配置标识
    target_word_count: 8000
    citation_style: "GB/T 7714"
    language: "zh-CN"

  # ===== 风格基线（智能体一初始化，智能体三参照）=====
  style_baseline:
    tone: "学术正式"
    voice: "第三人称"
    sentence_length: "中等"
    paragraph_structure: "主题句-论据-小结"
    example_paragraph: ""       # 智能体一提供的风格样例段落

  # ===== 文献池（P0-1/P1-5: 智能体一初始化，全流程只读）=====
  reference_pool:
    provided_by_user: false      # 用户是否提供了参考文献列表
    auto_searched: false         # 是否自动检索了文献
    references:
      # 格式：
      # - ref_id: "ref_001"
      #   entry: "张三, 李四. 深度学习在NLP中的应用[J]. 计算机学报, 2023, 46(3): 512-528."
      #   type: "journal"        # journal | book | conference | thesis | online
      #   verified: true          # 是否已验证真实性
      []
    unverified_count: 0          # 需人工核实的数量

  # ===== 术语表（各智能体追加）=====
  glossary:
    # 格式：
    # - term: "深度学习"
    #   definition: "基于多层神经网络的机器学习方法"
    #   first_used_in: "CH01"
    #   english_equiv: "Deep Learning"
    #   variations: ["深层学习"]  # 其他可能写法，需统一
    []

  # ===== 已完成章节索引（P0-4: 仅保留摘要+文件路径，不存正文全文）=====
  completed_chapters:
    # 格式：
    # - chapter_id: "CH01"
    #   task_id: "TASK-001"
    #   file_path: "chapters/CH01.md"     # 正文文件路径
    #   word_count: 1180
    #   status: "drafted"                   # drafted | reviewed | integrated
    #   summary: "一句话摘要（≤100字），供后续章节参照"
    #   key_terms: ["术语1", "术语2"]      # 本章引入的关键术语
    []
    # P0-4 注意：不要在此处存储正文全文！正文写入 chapters/ 目录文件。

  # ===== 引用登记（P0-1: 智能体三追加，智能体四校验，智能体五整合）=====
  citation_registry:
    # 格式：
    # - marker: "[CITE:ref_001]"
    #   chapter_id: "CH01"
    #   ref_pool_id: "ref_001"              # 文献池中的 ID（若为 REF_NEEDED 则为 null）
    #   status: "pending"                   # pending | resolved | ref_needed
    #   resolved_ref_id: null               # 智能体五分配的正式编号
    []

  # ===== 图表登记（P1-6: 智能体三追加，智能体五整合）=====
  figure_registry:
    # 格式：
    # - marker: "[FIG:table|三种方法性能对比]"
    #   chapter_id: "CH01"
    #   type: "table"                       # table | chart | diagram
    #   description: ""
    #   resolved: false                     # 智能体五是否已替换为正式编号
    #   assigned_id: null                   # 智能体五分配的编号（如 "表 1-1"）
    []

  # ===== 公式登记（P1-6: 智能体三追加，智能体五整合）=====
  equation_registry:
    # 格式：
    # - marker: "[EQ:\mathcal{L}=-\sum y_i \log(\hat{y}_i)]"
    #   chapter_id: "CH02"
    #   latex: ""
    #   resolved: false
    #   assigned_id: null                   # 如 "(2-1)"
    []

  # ===== 全局问题追踪（智能体四/五追加）=====
  issue_log:
    # 格式：
    # - issue_id: "ISS-001"
    #   raised_by: "agent4"                 # agent4 | agent5
    #   chapter_id: "CH01"
    #   type: "plagiarism | logic | language | format | citation | coherence | consistency | originality"
    #   severity: "critical | major | minor"
    #   status: "open"                      # open | resolved | deferred
    #   description: ""
    #   resolution: ""
    []

  # ===== 重做请求队列（P2-10: 智能体五维护，按优先级排序）=====
  redo_queue:
    # 格式：
    # - request_id: "REDO-001"
    #   target_agent: 3                     # 目标智能体编号
    #   task_id: "TASK-001"
    #   severity: "critical"                # critical > major > minor
    #   status: "pending"                   # pending | executing | completed | cancelled
    #   description: ""
    #   conflict_with: []                   # 与哪些其他 redo 请求冲突（如有）
    #   conflict_resolution: ""             # 冲突裁决结果
    []

  # ===== 流程状态（系统维护）=====
  pipeline_state:
    current_agent: 1            # 当前正在执行的智能体编号
    current_task: null          # 当前正在处理的 task_id
    mode: "full"                # P1-8: full | revision
    revision_targets: []        # P1-8: 修订模式下的目标章节 ID 列表
    retry_counts:               # 各任务的重试次数
      # TASK-001: 0
    total_chapters: 0           # 总章节数（不含 deferred 的摘要）
    completed_count: 0          # 已完成章节数
    redo_requests: []           # 重做请求历史
    progress_log: []             # P2-13: 进度日志
    # 格式：
    # - timestamp: "2024-01-01T12:00:00Z"
    #   agent: 1
    #   message: "大纲设计完成，共 6 章"
    #   level: "info | warning | error"
```

## P0-4 上下文压缩策略

当 SharedContext 体积增长时，采取以下压缩策略：

| 策略 | 触发条件 | 操作 |
|------|---------|------|
| 文件外置 | 所有章节 | 正文写入 `chapters/` 目录文件，上下文仅存路径+摘要 |
| 摘要压缩 | 单个 chapter summary > 100 字 | 截断为 100 字以内的核心摘要 |
| 术语表瘦身 | glossary 条目 > 50 | 仅保留当前章节及前一章引入的术语 |
| 引用登记归档 | citation_registry > 100 条 | 已 resolved 的引用归档为摘要统计 |
| 历史问题清理 | issue_log > 30 条 | 已 resolved 的问题移至归档文件 |
| 强制压缩 | SharedContext > MAX_CONTEXT_SIZE | 触发全量压缩，保留最近 3 章的完整上下文 |

## 更新时机与规则

| 时机 | 更新者 | 更新字段 |
|------|--------|---------|
| 大纲完成后 | 智能体一 | paper_meta, style_baseline, reference_pool, glossary(初始), pipeline_state |
| 用户确认后 | 系统 | pipeline_state.current_agent=2 |
| 任务分发后 | 智能体二 | pipeline_state.current_agent=3 |
| 章节初稿后 | 智能体三 | completed_chapters(追加摘要+路径), citation_registry, figure_registry, equation_registry, glossary(追加), pipeline_state |
| 质检完成后 | 智能体四 | issue_log, citation_registry(status更新), completed_chapters(status→reviewed) |
| 整合校验后 | 智能体五 | completed_chapters(status→integrated), issue_log, pipeline_state |

## 快照传递

每个智能体产出时附带 `shared_context_snapshot` 字段，包含当前共享上下文的完整快照。
下游智能体基于快照工作，重做时传递最新快照 + 变更说明。
