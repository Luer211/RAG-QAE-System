from __future__ import annotations
from app.core.context import RequestContext
from app.pipelines.evaluation.models import (
    EvaluationPipelineInput,
    EvaluationPipelineOutput,
    EvaluationState,
)
from app.steps.evaluation.create_metrics import CreateEvaluationMetricsStep
from app.steps.evaluation.create_run import CreateEvaluationRunStep
from app.steps.evaluation.finalize_run import FinalizeEvaluationRunStep
from app.steps.evaluation.judge_items import JudgeEvaluationItemsStep
from app.steps.evaluation.run_items import RunEvaluationItemsStep


class EvaluationPipeline:
    def __init__(
        self,
        create_run_step: CreateEvaluationRunStep,
        run_items_step: RunEvaluationItemsStep,
        judge_items_step: JudgeEvaluationItemsStep,
        finalize_run_step: FinalizeEvaluationRunStep,
        create_metrics_step: CreateEvaluationMetricsStep,
    ) -> None:
        self.create_run_step = create_run_step
        self.run_items_step = run_items_step
        self.judge_items_step = judge_items_step
        self.finalize_run_step = finalize_run_step
        self.create_metrics_step = create_metrics_step

    async def run(
        self,
        input_data: EvaluationPipelineInput,
        ctx: RequestContext,
    ) -> EvaluationPipelineOutput:
        state = EvaluationState(ctx=ctx, input=input_data)

        await self.create_run_step.run(state)
        await self.run_items_step.run(state)
        await self.judge_items_step.run(state)
        await self.finalize_run_step.run(state)
        await self.create_metrics_step.run(state)

        if state.output is None:
            raise RuntimeError("Evaluation pipeline completed without output")
        return state.output

