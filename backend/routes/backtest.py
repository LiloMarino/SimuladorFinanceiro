from typing import Annotated

from fastapi import APIRouter, Query, status

from backend.core.dependencies import HostVerified
from backend.core.dto.backtest import (
    BacktestConfigDTO,
    BacktestResultDTO,
    BacktestSetupDTO,
    BacktestStatusDTO,
    BacktestStoppedDTO,
)
from backend.features.backtest import config as backtest_config
from backend.features.backtest import service

backtest_router = APIRouter(prefix="/api/backtest", tags=["Backtest"])


@backtest_router.get(
    "/setup",
    response_model=BacktestSetupDTO,
    summary="Preparar a tela de novo backtest",
    description="Até onde há mercado (primeiro dado, fim do real e fim do gerado) e a configuração inicial: a do backtest mais recente ou, com `from`, a de um backtest salvo (rodar de novo). O nome vem livre. Apenas o host pode executar.",
)
def get_setup(
    _: HostVerified, from_id: Annotated[int | None, Query(alias="from")] = None
):
    return backtest_config.setup(from_id)


@backtest_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=BacktestStatusDTO,
    summary="Iniciar um backtest",
    description="Roda as estratégias escolhidas sobre o mesmo mercado, sem esperar entre os pregões. Recusa com 409 se já há partida ou backtest, e com 422 se o período, as vagas ou os parâmetros não valem. Apenas o host pode executar.",
)
def start_backtest(payload: BacktestConfigDTO, _: HostVerified):
    return service.start(payload)


@backtest_router.post(
    "/stop",
    response_model=BacktestStoppedDTO,
    summary="Parar o backtest e salvar",
    description="Para o backtest em andamento e o deixa salvo até onde chegou. Apenas o host pode executar.",
)
def stop_backtest(_: HostVerified):
    return BacktestStoppedDTO(simulation_id=service.stop())


@backtest_router.post(
    "/discard",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Descartar o backtest",
    description="Para o backtest em andamento e apaga o que ele gravou. Apenas o host pode executar.",
)
def discard_backtest(_: HostVerified):
    service.discard()


@backtest_router.get(
    "/status",
    response_model=BacktestStatusDTO,
    summary="Andamento do backtest",
    description="O andamento do backtest que roda, com os pontos do gráfico e as falhas; vazio quando não há. Qualquer jogador pode consultar.",
)
def get_status():
    return service.status()


@backtest_router.get(
    "/{simulation_id}",
    response_model=BacktestResultDTO,
    summary="Backtest salvo",
    description="A configuração do backtest salvo, onde parou e a série de referência (aportado, CDI e Ibovespa) para o relatório.",
)
def get_backtest(simulation_id: int):
    return service.result(simulation_id)
