# 数据库设计

## 1. 设计说明

MVP 阶段数据库设计优先保证：

```text
1. 表结构清晰
2. 主键、外键、唯一约束正确
3. release 隔离关系正确
4. 建立分区表隔离
4. 核心检索索引可表达
5. 后续可以平滑演进到批处理状态机
```

MVP 阶段不追求完整索引覆盖、完整状态流转机制，也不强制记录所有耗时、错误消息和模块级状态。

## 2. PostgreSQL 扩展与枚举

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

```sql
CREATE TYPE release_status AS ENUM (
    'draft',
    'testing',
    'ready',
    'published',
    'archived'
);
```

```sql
CREATE TYPE evaluation_run_status AS ENUM (
    'pending',
    'running',
    'partial_success',
    'success',
    'failed'
);
```

## 3. knowledge_releases

知识版本主表，表示一次可测试、可发布、可归档的知识快照。

```sql
CREATE TABLE knowledge_releases (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status release_status NOT NULL DEFAULT 'draft',
    config_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_knowledge_releases_name UNIQUE (name)
);
```

## 4. documents

文档表，记录某个知识版本下的原始文档和处理状态。

```sql
CREATE TABLE documents (
    id UUID NOT NULL,
    release_id VARCHAR(64) NOT NULL,
    title VARCHAR(512) NOT NULL,
    content_raw TEXT NOT NULL,
    content_cleaned TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_documents PRIMARY KEY (release_id, id),
    CONSTRAINT fk_documents_release
        FOREIGN KEY (release_id)
        REFERENCES knowledge_releases(id)
        ON DELETE CASCADE
) PARTITION BY LIST (release_id);
```

> 注意：`documents` 按 `release_id` 分区。

## 5. chunks

文档切块表，是检索、引用、评测的核心知识单元。

```sql
CREATE TABLE chunks (
    id UUID NOT NULL,
    release_id VARCHAR(64) NOT NULL,
    document_id UUID NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    search_vector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('simple', content)
    ) STORED,
    char_count INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_chunks PRIMARY KEY (release_id, id),
    CONSTRAINT fk_chunks_release
        FOREIGN KEY (release_id)
        REFERENCES knowledge_releases(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_chunks_document
        FOREIGN KEY (release_id, document_id)
        REFERENCES documents(release_id, id)
        ON DELETE CASCADE,
    CONSTRAINT uq_chunks_release_document_chunk_index
        UNIQUE (release_id, document_id, chunk_index)
) PARTITION BY LIST (release_id);
```

全文检索索引：

```sql
CREATE INDEX idx_chunks_search_vector
ON chunks
USING GIN (search_vector);
```

> 注意：`chunks` 按 `release_id` 分区，上述 GIN 索引应理解为创建在每个 release 分区上的分区内索引。

## 6. chunk_embeddings

切块向量表，记录 chunk 的 embedding 结果。

```sql
CREATE TABLE chunk_embeddings (
    id UUID NOT NULL,
    release_id VARCHAR(64) NOT NULL,
    chunk_id UUID NOT NULL,
    embedding_model VARCHAR(255) NOT NULL,
    embedding_dim INTEGER NOT NULL,
    vector VECTOR(1536) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_chunk_embeddings PRIMARY KEY (release_id, id),
    CONSTRAINT fk_chunk_embeddings_release
        FOREIGN KEY (release_id)
        REFERENCES knowledge_releases(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_chunk_embeddings_chunk
        FOREIGN KEY (release_id, chunk_id)
        REFERENCES chunks(release_id, id)
        ON DELETE CASCADE,
    CONSTRAINT uq_chunk_embeddings_release_chunk_model
        UNIQUE (release_id, chunk_id, embedding_model)
) PARTITION BY LIST (release_id);
```

向量索引：

```sql
CREATE INDEX idx_chunk_embeddings_vector_hnsw_cosine
ON chunk_embeddings
USING hnsw (vector vector_cosine_ops);
```

> 注意：`chunk_embeddings` 按 `release_id` 分区，上述 HNSW 索引应理解为创建在每个 release 分区上的分区内索引。

## 7. retrieval_logs

检索日志主表，记录一次完整问答链路。

```sql
CREATE TABLE retrieval_logs (
    id VARCHAR(64) PRIMARY KEY,
    release_id VARCHAR(64) NOT NULL,
    query_raw TEXT NOT NULL,
    query_rewritten TEXT NULL,
    rewrite_used VARCHAR(255) NULL,
    answer_text TEXT NULL,
    config_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_retrieval_logs_release
        FOREIGN KEY (release_id)
        REFERENCES knowledge_releases(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_retrieval_logs_id_release
        UNIQUE (id, release_id)
);
```

`uq_retrieval_logs_id_release` 用于让 `retrieval_items` 和 `answer_citations` 建立复合外键，保证日志、引用、候选 chunk 都属于同一个 release。

## 8. retrieval_items

检索结果项表，记录一次检索中召回或重排出现的 chunk。

```sql
CREATE TABLE retrieval_items (
    id VARCHAR(64) PRIMARY KEY,
    retrieval_log_id VARCHAR(64) NOT NULL,
    release_id VARCHAR(64) NOT NULL,
    chunk_id UUID NOT NULL,
    source_type VARCHAR(64) NOT NULL,
    raw_score DOUBLE PRECISION NOT NULL,
    rerank_score DOUBLE PRECISION NULL,
    rank_before_rerank INTEGER NULL,
    rank_after_rerank INTEGER NULL,
    selected_for_context BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_retrieval_items_log
        FOREIGN KEY (retrieval_log_id, release_id)
        REFERENCES retrieval_logs(id, release_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_retrieval_items_chunk
        FOREIGN KEY (release_id, chunk_id)
        REFERENCES chunks(release_id, id)
        ON DELETE CASCADE
);
```

## 9. answer_citations

回答引用表，记录最终答案引用了哪些 chunk。

```sql
CREATE TABLE answer_citations (
    id VARCHAR(64) PRIMARY KEY,
    retrieval_log_id VARCHAR(64) NOT NULL,
    release_id VARCHAR(64) NOT NULL,
    chunk_id UUID NOT NULL,
    citation_order INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_answer_citations_log
        FOREIGN KEY (retrieval_log_id, release_id)
        REFERENCES retrieval_logs(id, release_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_answer_citations_chunk
        FOREIGN KEY (release_id, chunk_id)
        REFERENCES chunks(release_id, id)
        ON DELETE CASCADE,
    CONSTRAINT uq_answer_citations_log_order
        UNIQUE (retrieval_log_id, citation_order),
    CONSTRAINT uq_answer_citations_log_chunk
        UNIQUE (retrieval_log_id, chunk_id)
);
```

## 10. evaluation_datasets

评测数据集表。

```sql
CREATE TABLE evaluation_datasets (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_evaluation_datasets_name UNIQUE (name)
);
```

## 11. evaluation_questions

评测问题表，记录数据集中的单题。

```sql
CREATE TABLE evaluation_questions (
    id VARCHAR(64) PRIMARY KEY,
    dataset_id VARCHAR(64) NOT NULL,
    question_text TEXT NOT NULL,
    reference_answer TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_evaluation_questions_dataset
        FOREIGN KEY (dataset_id)
        REFERENCES evaluation_datasets(id)
        ON DELETE CASCADE
);
```

## 12. evaluation_runs

评测运行表，记录一次针对某 release 和 dataset 的批量评测。

```sql
CREATE TABLE evaluation_runs (
    id VARCHAR(64) PRIMARY KEY,
    release_id VARCHAR(64) NOT NULL,
    dataset_id VARCHAR(64) NOT NULL,
    config_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    run_status evaluation_run_status NOT NULL DEFAULT 'pending',
    total_count INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    failed_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_evaluation_runs_release
        FOREIGN KEY (release_id)
        REFERENCES knowledge_releases(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_evaluation_runs_dataset
        FOREIGN KEY (dataset_id)
        REFERENCES evaluation_datasets(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_evaluation_runs_id_release
        UNIQUE (id, release_id)
);
```

## 13. evaluation_items

评测明细表，记录一次评测运行中每道题的执行结果。

```sql
CREATE TABLE evaluation_items (
    id VARCHAR(64) PRIMARY KEY,
    evaluation_run_id VARCHAR(64) NOT NULL,
    question_id VARCHAR(64) NOT NULL,
    release_id VARCHAR(64) NOT NULL,
    retrieval_log_id VARCHAR(64) NULL,
    answer_text TEXT NULL,
    citations_snapshot JSONB NOT NULL DEFAULT '[]'::jsonb,
    judge_result JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_evaluation_items_run
        FOREIGN KEY (evaluation_run_id, release_id)
        REFERENCES evaluation_runs(id, release_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_evaluation_items_question
        FOREIGN KEY (question_id)
        REFERENCES evaluation_questions(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_evaluation_items_retrieval_log
        FOREIGN KEY (retrieval_log_id, release_id)
        REFERENCES retrieval_logs(id, release_id)
        ON DELETE CASCADE
);
```

> 注意：`retrieval_log_id` 可为空。PostgreSQL 在复合外键中，只要任意一个外键字段为 NULL，就不会触发外键校验。因此这里允许评测题目执行失败时不产生检索日志。

## 14. evaluation_metrics

评测聚合指标表，记录一次评测运行的整体指标。

```sql
CREATE TABLE evaluation_metrics (
    id VARCHAR(64) PRIMARY KEY,
    evaluation_run_id VARCHAR(64) NOT NULL,
    metric_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_evaluation_metrics_run
        FOREIGN KEY (evaluation_run_id)
        REFERENCES evaluation_runs(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_evaluation_metrics_run_id
        UNIQUE (evaluation_run_id)
);
```

## 15. 状态枚举说明

### 15.1 ReleaseStatus

```text
draft      草稿态，刚创建
testing    测试中，可用于检索 / 评测验证
ready      已就绪，可以发布
published  已发布，正式生效
archived   已归档
```

### 15.2 EvaluationRunStatus

```text
pending          待执行
running          执行中
partial_success  部分成功
success          全部成功
failed           运行失败
```
