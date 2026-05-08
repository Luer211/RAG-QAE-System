# 技术债与后续演进

## 1. 技术债处理原则

MVP 阶段优先保证架构边界和数据模型正确。性能、批处理、状态机、失败恢复等能力作为后续迭代项。

当前各阶段可以通过 ID 列表衔接，后续可以平滑演进为基于 `release_id + status + batch_size` 的分页处理模式。

## 2. 可以容忍的技术债

可以容忍的技术债是指实现方式暂时粗糙，但不会破坏系统边界和核心模型。

例如：

```text
1. 暂时不做 batch，我们就直接就是说，service 层for循环调用 pipeline，就是说，先一次一个文档这样子做，而不做 batch。
2. 暂时不做模块级状态
3. 暂时不做断点续跑
4. 暂时不做失败恢复
5. 暂时用 ID 列表在 pipeline 阶段之间传递数据
6. 暂时不引入 MinIO 保存原始文档
```

这些问题会影响系统性能、健壮性或大规模处理能力，但不会破坏系统整体设计。

## 3. 不能容忍的技术债

不能容忍的技术债是指会破坏系统边界、模型隔离或后续演进能力的问题。

例如：

```text
1. release 隔离不清晰
2. domain 和 dao 混写
3. router 中直接调用 pipeline、step 或 dao
4. HTTP 请求模型贯穿 service、pipeline、domain 全层
5. 不同知识库版本共用检索索引后再用 release_id 过滤
6. 数据表缺少必要主键、外键、唯一约束
```

MVP 阶段必须优先解决这些问题。

## 4. 入库链路遗留问题

### 4.1 大量文档不能一次性全部加载

当前设计中，文档入库请求直接传入文档列表。后续如果文档数量较多，或者单个文档特别大，会导致内存压力和处理不稳定。

后续建议引入对象存储，例如 MinIO：

```text
上传原始文档
  ↓
保存到 MinIO
  ↓
数据库只记录文件元信息和对象存储地址
  ↓
pipeline 按文档逐个读取和处理
```

### 4.2 ID 列表传递会导致频繁查库

后续如果 pipeline 的每一步只传递 ID 列表，那么每个步骤都需要根据 ID 重新查数据库。

建议后续在 service 层中抽象批处理和数据加载能力：

```text
service 负责 batch 和数据加载
  ↓
pipeline 只编排链路
  ↓
step 组装 domain input
  ↓
domain 只处理纯业务策略
```

### 4.3 极大数据量下不应长期传递 ID 列表

当数据量继续增大后，不应该在 pipeline state 中保存大量 ID 列表。更好的方式是：

```text
只传 release_id
  ↓
service 或 step 按状态分页查询 document / chunk
  ↓
按 batch 调用 domain
  ↓
处理完成后更新状态
```

后续可以演进为：

```text
release_id + status + batch_size
```

## 5. 数据表后续增强方向

1. MVP 阶段只保证核心字段存在。后续建议补充以下字段：
```text
1. started_at
2. finished_at
3. duration_ms
4. error_message
5. status
6. retry_count
7. trace_id
8. created_by
9. updated_at
```
这些字段可用于观测、排障、状态恢复和任务审计。

2. 有些数据表还可以增加约束，从数据表层面去避免产生不当的数据。
就比如说：我们应该约束 item 和 dataset 的一致性，保证说，不会出现：
- run_1 属于 dataset_A
- evaluation_item 属于 run_1
- 但 question_id 指向 dataset_B 的题目
这种情况。
尽管我们在业务流程上已经规避了这种情况，但是不能保证说，我们后续扩展会不会触发这种问题。

## 6. 索引后续优化方向

MVP 阶段不追求完整索引覆盖，只保留两类核心检索索引：

```text
1. chunks.search_vector 的 GIN 索引，用于全文检索
2. chunk_embeddings.vector 的 HNSW 索引，用于向量检索
```

由于 `documents`、`chunks` 和 `chunk_embeddings` 按 `release_id` 分区，上述索引都应理解为分区内索引，而不是全表共享索引。

其他 B-tree 查询索引后续根据真实查询模式和 `EXPLAIN ANALYZE` 结果补充。

## 7. 版本数据对比

我们目前只是对每一个版本的一次评测进行了数据聚合，但是还未对多个版本之间的比较实际实际业务。这个留待后续去设计。