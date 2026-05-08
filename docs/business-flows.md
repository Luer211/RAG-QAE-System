# 业务链路设计

## 1. 入库链路

### 1.1 总体流程

```text
IngestService
  ↓
IngestPipeline
  ↓
CleanDocumentsStep：清洗、入库
  ↓
ChunkDocumentsStep：切块、入库
  ↓
EmbedChunksStep：向量化、入库
  ↓
MarkReleaseReadyStep：将版本状态置为 ready
```

业务流程：

```text
新建知识库版本
  ↓
创建 documents / chunks / chunk_embeddings 对应 release_id 的分区
  ↓
创建分区内全文检索索引和向量索引（这里我们会在建立表时先做，pgsql会自动帮我们建立）
  ↓
上传一系列文档
  ↓
文档清洗、入库
  ↓
文档切块、入库
  ↓
切块向量化、入库
  ↓
知识库版本状态置为 ready
```

### 1.2 Pipeline Input

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

### 1.3 Pipeline Runtime

```json
{
  "documents_cleaned_ids": ["document.id"],
  "chunk_ids": ["chunk.id"],
  "chunk_embedding_ids": ["chunk_embedding.id"]
}
```

### 1.4 Pipeline Output

```json
{
  "release_status": "ready"
}
```

### 1.5 CleanDocumentsStep

输入：

```json
{
  "release_id": "str",
  "documents": [
    {
      "title": "str",
      "content_raw": "str"
    }
  ],
  "cleaner_config": {
    "strategy_key": "mock_clean"
  }
}
```

输出：

```json
{
  "documents_cleaned_ids": ["document.id"]
}
```

### 1.6 ChunkDocumentsStep

输入：

```json
{
  "release_id": "str",
  "documents_cleaned_ids": ["document.id"],
  "chunker_config": {
    "strategy_key": "mock_chunk"
  }
}
```

输出：

```json
{
  "chunk_ids": ["chunk.id"]
}
```

### 1.7 EmbedChunksStep

输入：

```json
{
  "release_id": "str",
  "chunk_ids": ["chunk.id"],
  "embedding_config": {
    "strategy_key": "mock_model"
  }
}
```

输出：

```json
{
  "chunk_embedding_ids": ["chunk_embedding.id"]
}
```

### 1.8 MarkReleaseReadyStep

输入：

```json
{
  "release_id": "str"
}
```

输出：

```json
{
  "release_status": "ready"
}
```

## 2. 检索生成链路

### 2.1 总体流程

```text
RetrievalService
  ↓
RetrievalPipeline
  ↓
CreateRetrievalLogStep：创建一次检索日志
  ↓
RewriteQueryStep：重写问题
  ↓
RetrieveChunksStep：检索 chunk
  ↓
RerankChunksStep：重排序、入库、选取 top-k
  ↓
GenerateAnswerStep：生成答案、入库引用
```

业务流程：

```text
输入问题
  ↓
问题重写
  ↓
检索
  ↓
重排序
  ↓
生成答案
  ↓
记录检索日志、候选项、最终引用
```

### 2.2 Pipeline Input

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

### 2.3 Pipeline Runtime

```json
{
  "retrieval_log_id": "str",
  "rewrite_query": "str",
  "retrieval_chunks": ["retrieval_item"],
  "rerank_chunks": ["rerank_item"],
  "selected_chunks": ["chunk"]
}
```

### 2.4 Pipeline Output

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

### 2.5 CreateRetrievalLogStep

输入：

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

输出：

```json
{
  "retrieval_log_id": "str"
}
```

### 2.6 RewriteQueryStep

输入：

```json
{
  "release_id": "str",
  "retrieval_log_id": "str",
  "query": "str",
  "rewrite_config": {
    "strategy_key": "mock_rewrite"
  }
}
```

输出：

```json
{
  "rewrite_query": "str"
}
```

### 2.7 RetrieveChunksStep

输入：

```json
{
  "release_id": "str",
  "retrieval_log_id": "str",
  "rewrite_query": "str",
  "retrieval_config": {
    "strategy_key": "mock_retrieval"
  }
}
```

输出：

```json
{
  "retrieval_chunks": ["retrieval_item"]
}
```

### 2.8 RerankChunksStep

输入：

```json
{
  "release_id": "str",
  "retrieval_log_id": "str",
  "rerank_config": {
    "strategy_key": "mock_rerank"
  },
  "retrieval_chunks": ["retrieval_item"]
}
```

输出：

```json
{
  "rerank_chunks": ["rerank_item"],
  "selected_chunks": ["chunk"]
}
```

### 2.9 GenerateAnswerStep

输入：

```json
{
  "release_id": "str",
  "retrieval_log_id": "str",
  "generation_config": {
    "strategy_key": "mock_gen"
  },
  "selected_chunks": ["chunk"]
}
```

输出：

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

## 3. 批量评测链路

### 3.1 总体流程

```text
EvaluationService
  ↓
EvaluationPipeline
  ↓
CreateEvaluationRunStep：创建评测运行记录
  ↓
RunEvaluationItemsStep：数据集批量跑检索生成链路
  ↓
JudgeEvaluationItemsStep：逐条评测
  ↓
FinalizeEvaluationRunStep：汇总并更新评测运行状态
  ↓
CreateEvaluationMetricsStep：创建评测聚合指标
```

业务流程：

```text
上传评测数据集
  ↓
选择知识库版本
  ↓
将问题依次输入检索生成链路得到答案
  ↓
保存 evaluation_items
  ↓
对问答对依次评测
  ↓
汇总 evaluation_metrics
```

### 3.2 Pipeline Input

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

### 3.3 Pipeline Runtime

```json
{
  "evaluation_run_id": "str"
}
```

### 3.4 Pipeline Output

```json
{
  "evaluation_run_id": "str"
}
```

### 3.5 CreateEvaluationRunStep

输入：

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

输出：

```json
{
  "evaluation_run_id": "str"
}
```

### 3.6 RunEvaluationItemsStep

复用检索生成链路，为数据集中的每一个问题生成答案，并写入 `evaluation_items`。

输入：

```json
{
  "release_id": "str",
  "dataset_id": "str",
  "evaluation_run_id": "str",
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

输出：

```json
{}
```

### 3.7 JudgeEvaluationItemsStep

根据 `evaluation_run_id` 获取一系列 `evaluation_items`，依次进行评测，并将结果写入 `judge_result`。

输入：

```json
{
  "release_id": "str",
  "dataset_id": "str",
  "evaluation_run_id": "str",
  "judge_config": {
    "strategy_key": "mock_judge"
  }
}
```

输出：

```json
{}
```

### 3.8 FinalizeEvaluationRunStep

根据 `evaluation_items` 数量和执行结果更新 `evaluation_runs` 中的统计字段。

输入：

```json
{
  "release_id": "str",
  "dataset_id": "str",
  "evaluation_run_id": "str"
}
```

输出：

```json
{}
```

### 3.9 CreateEvaluationMetricsStep

创建评测聚合指标快照。

输入：

```json
{
  "release_id": "str",
  "dataset_id": "str",
  "evaluation_run_id": "str"
}
```

输出：

```json
{}
```
