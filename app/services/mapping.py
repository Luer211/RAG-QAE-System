from __future__ import annotations
from app.pipelines.common import PipelineStrategyConfig
from app.services.dto.common import StrategyConfigDTO


def to_pipeline_config(config: StrategyConfigDTO) -> PipelineStrategyConfig:
    return PipelineStrategyConfig(strategy_key=config.strategy_key, params=config.params)

