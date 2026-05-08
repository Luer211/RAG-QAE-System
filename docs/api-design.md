# 接口设计

## 1. 通用说明

接口按照三条业务链路划分：

```text
1. 入库链路
2. 检索生成链路
3. 批量评测链路
```

接口层只负责协议适配，请求结构体不要直接传入 service、pipeline、domain 全层。Router 应将 Request 转换为 ServiceInput，再调用 Service。

## 2. 入库链路接口

### 2.1 创建 release

```text
POST /api/v1/releases
```

请求结构体：`CreateReleaseRequest`

```json
{
  "name": "str",
  "description": "str, default=''",
  "config_snapshot": {}
}
```

响应结构体：`ReleaseResponse`

```json
{
  "id": "str",
  "name": "str",
  "description": "str",
  "status": "ReleaseStatus",
  "config_snapshot": {},
  "created_at": "datetime"
}
```

### 2.2 文档入库

```text
POST /api/v1/ingestion
```

请求结构体：`IngestJobRequest`

```json
{
  "release_id": "str",
  "documents": [
    {
      "title": "str",
      "content_raw": "str"
    },
    {
      "title": "str",
      "content_raw": "str"
    }
  ],
  "cleaner_config": {
    "strategy_key": "mock_clean"
  },
  "chunker_config": {
    "strategy_key": "mock_chunk"
  },
  "embedding_config": {
    "strategy_key": "mock_model"
  }
}
```

响应结构体：`SuccessResponse`

```json
{
  "message": "success"
}
```

### 2.3 查询 release 列表

```text
GET /api/v1/releases
```

请求结构体：无

响应结构体：`ReleaseListResponse`

```json
{
  "items": ["ReleaseResponse"],
  "total": "int"
}
```

### 2.4 查询某 release 下的文档列表

```text
GET /api/v1/releases/{release_id}/documents
```

请求结构体：

```json
{
  "Path": {
    "release_id": "str"
  }
}
```

响应结构体：`DocumentListResponse`

```json
{
  "items": ["DocumentResponse"],
  "total": "int"
}
```

### 2.5 查询文档详情

```text
GET /api/v1/releases/{release_id}/documents/{document_id}
```

请求结构体：

```json
{
  "Path": {
    "release_id": "str",
    "document_id": "str"
  }
}
```

响应结构体：`DocumentResponse`

```json
{
  "id": "str",
  "release_id": "str",
  "title": "str",
  "content_raw": "str",
  "content_cleaned": "str | null",
  "created_at": "datetime"
}
```

### 2.6 查询某文档下的 chunk 列表

```text
GET /api/v1/releases/{release_id}/documents/{document_id}/chunks
```

请求结构体：

```json
{
  "Path": {
    "release_id": "str",
    "document_id": "str"
  }
}
```

响应结构体：`ChunkListResponse`

```json
{
  "items": ["ChunkResponse"],
  "total": "int"
}
```

## 3. 检索生成链路接口

### 3.1 单次检索

接收用户问题，基于指定 release 执行改写、召回、重排和生成，返回答案与引用。

```text
POST /api/v1/retrieval/query
```

请求结构体：`RetrievalRequest`

```json
{
  "release_id": "str",
  "query": "str",
  "rewrite_config": {
    "strategy_key": "mock_rewrite"
  },
  "retrieval_config": {
    "strategy_key": "mock_retrieval"
  },
  "rerank_config": {
    "strategy_key": "mock_rerank"
  },
  "generation_config": {
    "strategy_key": "mock_gen"
  }
}
```

响应结构体：`RetrievalResult`

```json
{
  "answer": "str",
  "citations": [
    {
      "release_id": "str",
      "chunk_id": "str",
      "citation_order": "int",
      "content": "str"
    }
  ],
  "release_id": "str",
  "retrieval_log_id": "str"
}
```

说明：

```text
RetrievalResult.release_id 表示本次查询实际使用的知识库版本。
citations[].release_id 表示该引用片段所属的知识库版本。
单版本检索模式下，二者应保持一致。
```

### 3.2 查询检索日志详情

查询一次检索问答的完整日志摘要，包括原始 query、改写 query、答案和配置快照。

```text
GET /api/v1/retrieval/logs/{retrieval_log_id}
```

请求结构体：

```json
{
  "Path": {
    "retrieval_log_id": "str"
  }
}
```

响应结构体：`RetrievalLogResponse`

```json
{
  "id": "str",
  "release_id": "str",
  "query_raw": "str",
  "query_rewritten": "str | null",
  "rewrite_used": "str | null",
  "answer_text": "str | null",
  "config_snapshot": {},
  "created_at": "datetime"
}
```

### 3.3 查询检索明细项

查询一次检索日志下的候选 chunk 明细，用于分析召回和重排效果。

```text
GET /api/v1/retrieval/logs/{retrieval_log_id}/items
```

请求结构体：

```json
{
  "Path": {
    "retrieval_log_id": "str"
  }
}
```

响应结构体：`list[RetrievalItemResponse]`

```json
[
  {
    "id": "str",
    "chunk_id": "str",
    "source_type": "str",
    "raw_score": "float",
    "rerank_score": "float | null",
    "rank_before_rerank": "int | null",
    "rank_after_rerank": "int | null",
    "selected_for_context": "bool"
  }
]
```

### 3.4 查询检索引用

查询一次检索问答最终引用的 chunk 内容，便于展示答案依据。

```text
GET /api/v1/retrieval/logs/{retrieval_log_id}/citations
```

请求结构体：

```json
{
  "Path": {
    "retrieval_log_id": "str"
  }
}
```

响应结构体：`list[AnswerCitationResponse]`

```json
[
  {
    "release_id": "str",
    "chunk_id": "str",
    "citation_order": "int",
    "content": "str | null"
  }
]
```

## 4. 评测链路接口

### 4.1 创建评测数据集

```text
POST /api/v1/evaluation/datasets
```

请求结构体：`CreateDatasetRequest`

```json
{
  "name": "str",
  "description": "str, default=''"
}
```

响应结构体：`DatasetResponse`

```json
{
  "id": "str",
  "name": "str",
  "description": "str",
  "created_at": "datetime"
}
```

### 4.2 查询评测数据集列表

```text
GET /api/v1/evaluation/datasets
```

请求结构体：无

响应结构体：`list[DatasetResponse]`

```json
[
  {
    "id": "str",
    "name": "str",
    "description": "str",
    "created_at": "datetime"
  }
]
```

### 4.3 批量导入评测数据

```text
POST /api/v1/evaluation/datasets/{dataset_id}/questions
```

请求结构体：`AddQuestionsRequest`

```json
{
  "Path": {
    "dataset_id": "str"
  },
  "Body": {
    "questions": [
      {
        "question_text": "str",
        "reference_answer": "str | null"
      },
      {
        "question_text": "str",
        "reference_answer": "str | null"
      }
    ]
  }
}
```

响应结构体：`AddSuccessResponse`

```json
{
  "dataset_id": "str",
  "added_count": "int"
}
```

### 4.4 查询某个数据集下的评测问题

```text
GET /api/v1/evaluation/datasets/{dataset_id}/questions
```

请求结构体：

```json
{
  "Path": {
    "dataset_id": "str"
  }
}
```

响应结构体：`list[QuestionResponse]`

```json
[
  {
    "id": "str",
    "dataset_id": "str",
    "question_text": "str",
    "reference_answer": "str | null",
    "created_at": "datetime"
  }
]
```

### 4.5 发起批量评测

```text
POST /api/v1/evaluation/runs
```

请求结构体：`EvaluationRunRequest`

```json
{
  "release_id": "str",
  "dataset_id": "str",
  "rewrite_config": {
    "strategy_key": "mock_rewrite"
  },
  "retrieval_config": {
    "strategy_key": "mock_retrieval"
  },
  "rerank_config": {
    "strategy_key": "mock_rerank"
  },
  "generation_config": {
    "strategy_key": "mock_gen"
  },
  "judge_config": {
    "strategy_key": "mock_judge"
  }
}
```

响应结构体：`EvaluationRunSubmitResponse`

```json
{
  "evaluation_run_id": "str",
  "run_status": "EvaluationRunStatus"
}
```

### 4.6 查询一次评测运行详情

查看某次评测运行的运行状态。

```text
GET /api/v1/evaluation/runs/{evaluation_run_id}
```

请求结构体：

```json
{
  "Path": {
    "evaluation_run_id": "str"
  }
}
```

响应结构体：`EvaluationRunResponse`

```json
{
  "id": "str",
  "release_id": "str",
  "dataset_id": "str",
  "run_status": "EvaluationRunStatus",
  "total_count": "int",
  "success_count": "int",
  "failed_count": "int",
  "created_at": "datetime"
}
```

### 4.7 查询一次评测的明细

查看某次评测下每道题的答案、引用快照、指标、裁判结果。

```text
GET /api/v1/evaluation/runs/{evaluation_run_id}/items
```

请求结构体：

```json
{
  "Path": {
    "evaluation_run_id": "str"
  }
}
```

响应结构体：`list[EvaluationItemResponse]`

```json
[
  {
    "id": "str",
    "evaluation_run_id": "str",
    "question_id": "str",
    "retrieval_log_id": "str | null",
    "answer_text": "str | null",
    "citations_snapshot": [{}],
    "judge_result": {},
    "created_at": "datetime"
  }
]
```

### 4.8 查询评测聚合指标

查询某次评测运行的聚合指标快照。

```text
GET /api/v1/evaluation/runs/{evaluation_run_id}/metrics
```

请求结构体：

```json
{
  "Path": {
    "evaluation_run_id": "str"
  }
}
```

响应结构体：`EvaluationMetricResponse`

```json
{
  "evaluation_run_id": "str",
  "metric_snapshot": {}
}
```
