# 项目总体说明

## 1. 项目目标

本项目是一个面向 AI 知识库业务的 MVP 系统，核心目标是围绕知识库版本完成入库、检索生成、批量评测和不同版本效果比较。

MVP 阶段明确去除异步模块，同步执行后返回最终状态。不优先处理复杂任务调度、批处理状态机、失败恢复等工程能力，而是先保证架构边界、数据模型和核心业务链路正确。



## 2. 核心业务范围

项目当前只关注三条核心链路：

1. **入库链路**：创建知识库版本，上传文档，清洗，切块，向量化，按版本隔离索引，最终将知识库版本置为 ready。
2. **检索生成链路**：输入问题，执行问题改写、检索、重排序、答案生成，并记录引用和检索日志。
3. **批量评测链路**：上传评测数据集，选择知识库版本，批量执行检索生成，并对问答结果进行评测。



## 3. 当前骨架运行方式

当前代码骨架先使用内存 DAO 和 mock domain strategy 跑通三条链路，真实 PostgreSQL、向量检索和模型调用后续可以从 `dao/` 与 `infra/` 层替换。

项目已切换为 uv 管理 Python 环境和依赖，依赖以 `pyproject.toml` / `uv.lock` 为准。

首次准备环境：

```powershell
uv sync
```

启动开发服务：

```powershell
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

启动后入口为：

```text
GET  /health
POST /api/v1/releases
POST /api/v1/ingestion
POST /api/v1/retrieval/query
POST /api/v1/evaluation/runs
```

轻量验证：

```powershell
uv run python -m compileall app tests
uv run python -c "import runpy; ns = runpy.run_path('tests/test_smoke.py'); ns['test_smoke_ingest_retrieve_evaluate'](); print('smoke ok')"
```



## 4. 项目目录骨架

RAG-QAE-System/
├── README.md                    # 项目入口说明：目标、启动方式、核心链路
├── docs/                        # 项目设计文档
│   ├── README.md                # 文档总览
│   ├── architecture.md          # 六层架构说明
│   ├── business-flows.md        # 入库、检索、评测三条链路
│   ├── database-schema.md       # 数据库表、索引、约束、分区设计
│   ├── api-design.md            # HTTP API 设计
│   ├── pt_using_demo.md         # PostgreSQL 分区表示例
│   └── roadmap-and-tech-debt.md # MVP 边界与后续技术债
│
├── app/                         # 后端主应用代码
│   ├── main.py                  # FastAPI 应用入口
│   ├── dependencies.py          # 依赖注入入口
│   │
│   ├── core/                    # 通用基础能力
│   │   ├── config.py            # 配置读取
│   │   ├── context.py           # RequestContext 等上下文对象
│   │   ├── enums.py             # ReleaseStatus、EvaluationRunStatus 等枚举
│   │   ├── errors.py            # 业务异常定义
│   │   └── ids.py               # ID 生成工具
│   │
│   ├── api/v1/                  # Router 层，只做协议适配
│   │   ├── router.py            # v1 路由聚合
│   │   ├── releases.py          # release 相关接口
│   │   ├── ingestion.py         # 文档入库接口
│   │   ├── retrieval.py         # 检索问答接口
│   │   └── evaluation.py        # 批量评测接口
│   │
│   ├── schemas/                 # HTTP 请求/响应模型，通常用 Pydantic
│   │   ├── release.py
│   │   ├── ingestion.py
│   │   ├── retrieval.py
│   │   └── evaluation.py
│   │
│   ├── services/                # Service 层，负责业务用例
│   │   ├── dto/                 # ServiceInput / ServiceOutput
│   │   ├── release_service.py
│   │   ├── ingest_service.py
│   │   ├── retrieval_service.py
│   │   └── evaluation_service.py
│   │
│   ├── pipelines/               # Pipeline 层，只负责编排步骤顺序
│   │   ├── ingestion/           # 入库链路 Pipeline
│   │   ├── retrieval/           # 检索生成链路 Pipeline
│   │   └── evaluation/          # 批量评测链路 Pipeline
│   │
│   ├── steps/                   # Step 层，连接 pipeline、domain、dao
│   │   ├── ingestion/           # 清洗、切块、向量化、标记 ready
│   │   ├── retrieval/           # 建日志、改写、检索、重排、生成
│   │   └── evaluation/          # 建运行、跑题目、裁判、汇总指标
│   │
│   ├── domain/                  # Domain 层，只放核心策略，不访问数据库
│   │   ├── cleaning/            # 文档清洗策略
│   │   ├── chunking/            # 文档切块策略
│   │   ├── embedding/           # 向量化策略
│   │   ├── query_rewrite/       # 问题改写策略
│   │   ├── retrieval/           # 检索策略
│   │   ├── reranking/           # 重排序策略
│   │   ├── generation/          # 答案生成策略
│   │   └── judging/             # 评测裁判策略
│   │
│   ├── dao/                     # Dao 层，只处理数据库访问
│   │   ├── db.py                # pgsql数据库连接
│   │   ├── session.py           # 会话管理
│   │   ├── release_dao.py       # knowledge_releases 表访问
│   │   ├── document_dao.py      # documents 分区表访问
│   │   ├── chunk_dao.py         # chunks 分区表访问
│   │   ├── embedding_dao.py     # chunk_embeddings 分区表访问
│   │   ├── retrieval_log_dao.py # retrieval_logs/items/citations 访问
│   │   ├── evaluation_dao.py    # evaluation 相关表访问
│   │   └── partition_dao.py     # 按 release_id 创建分区
│   │
│   └── infra/                   # 外部基础设施适配
│       ├── llm/                 # 大模型调用封装
│       ├── embedding/           # embedding 模型调用封装
│       └── vector_search/       # pgvector / BM25 等检索适配
│
├── .env                         # 放真实 API key 且不上传
├── .env.example                 # 写 API key 占位示例
├── migrations/                  # 数据库表创建脚本
├── scripts/                     # 建分区、导入测试数据、启动fastapi服务等脚本
└── tests/                       # 单元测试和集成测试