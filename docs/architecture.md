# 系统架构设计

## 1. 总体分层

系统采用六层架构：

```text
router → service → pipeline → steps → domain → dao
```

每一层只负责自己的事情，避免业务边界混乱。

## 2. Router 层

Router 层只做协议适配，不理解业务流程。

它负责：

```text
HTTP Request / FastAPI / CLI / MQ
        ↓
ServiceInput
        ↓
调用 service
        ↓
ServiceOutput
        ↓
HTTP Response
```

Router 层不应该出现：

```python
pipeline.run(...)
clean_step.run(...)
dao.insert(...)
```

Router 层应该像这样：

```python
@router.post("/ingest")
async def ingest(req: IngestRequest):
    service_input = IngestServiceInput.from_request(req)
    result = await ingest_service.ingest(service_input)
    return IngestResponse.from_service_output(result)
```

这样以后从 FastAPI 切换到 gRPC、CLI 或 MQ 时，不会影响内部业务实现。

## 3. Service 层

Service 层负责业务用例。它代表一个对外业务动作，但不负责具体算法，也不负责单个步骤细节。

以入库链路为例，`IngestService` 可以负责：

```text
1. 校验 release 是否存在
2. 分批（实际上是for循环）调用 pipeline
3. 处理事务、状态流转
4. 汇总 pipeline 结果
5. 更新 release 状态
6. 返回 service output
```

示例：

```python
class IngestService:
    async def ingest(self, input: IngestServiceInput) -> IngestServiceOutput:
        # 1. 校验 release
        # 2. for 传 documents
        # 3. 多次调用 pipeline
        # 4. 更新 release 状态
        # 5. 返回结果
        pass
```

Service 层为 Pipeline 层挡住业务用例层面的复杂度，让 Pipeline 专注于链路编排。

## 4. Pipeline 层

Pipeline 层负责链路编排。

它不处理业务细节，也不直接处理数据库逻辑，只决定步骤顺序：

```text
先做 A
再做 B
再做 C
最后做 D
```

入库链路示例：

```text
clean_documents_step
  ↓
chunk_documents_step
  ↓
embed_chunks_step
  ↓
mark_release_ready_step
```

示例：

```python
class IngestPipeline:
    async def run(self, input: IngestPipelineInput, ctx: RequestContext) -> IngestPipelineOutput:
        state = IngestState(ctx=ctx, input=input)

        await self.clean_step.run(state)
        await self.chunk_step.run(state)
        await self.embed_step.run(state)
        await self.mark_ready_step.run(state)

        return state.output
```

## 5. Steps 层

Steps 层负责连接 pipeline、domain 和 dao。

一个 step 通常负责：

```text
1. 从 state 中取数据
2. 组装 domain input
3. 调用 domain strategy
4. 调用 dao 入库或查询
5. 将结果写回 state
```

示例：

```python
class CleanDocumentsStep:
    async def run(self, state: IngestState) -> None:
        domain_input = CleanDocumentsInput(
            documents=state.input.documents,
            config=state.input.cleaner_config,
        )

        domain_output = await self.clean_domain.clean(domain_input)

        document_ids = await self.document_dao.batch_insert_cleaned_documents(
            release_id=state.input.release_id,
            documents=domain_output.documents,
        )

        state.runtime.documents_cleaned_ids = document_ids
```

边界关系：

```text
pipeline：决定要不要执行 clean step
step：决定 clean step 里面如何串联 domain 和 dao
domain：决定具体怎么 clean
dao：决定怎么落库
```

## 6. Domain 层

Domain 层只做核心策略，不关心数据库。

Domain 内部可以使用策略工厂，例如清洗策略、切块策略、向量模型策略、重排策略、生成策略、评测策略。

示例：

```python
class CleanDomain:
    def __init__(self, strategy_factory: CleanerStrategyFactory):
        self.strategy_factory = strategy_factory

    async def clean(self, input: CleanDocumentsInput) -> CleanDocumentsOutput:
        strategy = self.strategy_factory.get(input.config.strategy_key)
        return await strategy.clean(input)
```

## 7. Dao 层

Dao 层只处理数据访问。

包括：

```text
1. insert
2. update
3. select
4. delete
5. vector search
6. full-text search / BM25 search
```

Dao 不应该知道业务流程，也不应该决定 pipeline 如何编排。

## 8. 数据结构命名规范

建议为每一层设计独立的输入输出结构体，避免请求模型贯穿全层。

```text
router 层：
- XxxRequest
- XxxResponse

service 层：
- XxxServiceInput
- XxxServiceOutput

pipeline 层：
- XxxPipelineInput
- XxxPipelineOutput
- XxxState
- XxxRuntime

steps 层：
- XxxStep
- XxxStepInput   # 可选
- XxxStepOutput  # 可选

domain 层：
- XxxDomainInput
- XxxDomainOutput
- XxxStrategy
- XxxStrategyConfig

dao 层：
- XxxDao
- XxxRecord
- XxxEntity
```

Router 层通常使用 Pydantic；内部业务数据流转建议使用 dataclass。

## 9. Pipeline State 模板

```python
from dataclasses import dataclass, field

@dataclass
class IngestState:
    ctx: RequestContext
    input: IngestPipelineInput
    runtime: IngestRuntime = field(default_factory=IngestRuntime)
    output: IngestPipelineOutput | None = None
```

数据流转方式：

```text
Pipeline 持有 State
    ↓
Pipeline 调用 Step
    ↓
Step 从 State 取数据
    ↓
Step 组装 DomainInput
    ↓
Step 调用 Domain
    ↓
Domain 返回 DomainOutput
    ↓
Step 视情况调用 Dao 入库 / 查询
    ↓
Step 把 StepOutput 写回 State
    ↓
Pipeline 继续调下一个 Step
```
