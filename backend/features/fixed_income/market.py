import logging
from collections.abc import Callable
from datetime import date
from decimal import Decimal
from uuid import UUID

from backend.core import repository
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.features.fixed_income import house_cdb, treasury
from backend.features.fixed_income.factory import FixedIncomeFactory
from backend.features.realtime import notify
from backend.features.realtime.schemas import FixedAssetsUpdateEventDTO

logger = logging.getLogger(__name__)


class FixedIncomeMarket:
    """
    Gerenciador de hall de ativos de renda fixa disponíveis.

    Responsável por:
    - Gerar novos ativos mensalmente usando FixedIncomeFactory, com o CDB de liquidez
      diária e a conta em dólar fixos e, de vez em quando, a oferta rara
    - Emitir todo mês os seis títulos do catálogo do Tesouro, com a taxa travada do mês
    - Emitir todo mês os três CDBs da casa de cada Bancário, que só o dono vê e compra
    - Manter catálogo de ativos disponíveis por UUID
    - Notificar players sobre atualizações do hall via realtime
    - Fornecer consultas de ativos disponíveis e busca por UUID
    """

    def __init__(
        self,
        simulation_id: int,
        end_date: date,
        risk_premium_on: Callable[[date], Decimal] = lambda _day: Decimal(0),
        start_date: date | None = None,
    ):
        """
        `risk_premium_on` dá o prêmio de risco do país que o Tesouro soma às taxas do mês.
        `start_date` é a largada da partida, de onde o catálogo do Tesouro é recalculado;
        sem ela vale o mês da primeira emissão.
        """
        self._simulation_id = simulation_id
        self._end_date = end_date
        self._risk_premium_on = risk_premium_on
        self._start_date = start_date
        self._current_month: tuple[int, int] | None = None
        self._assets: dict[str, FixedIncomeAssetDTO] = {}
        self._issued_assets: dict[str, FixedIncomeAssetDTO] = {}
        # Os CDBs da casa do mês, por dono e prazo em anos; fora do catálogo público
        self._house: dict[UUID, dict[int, FixedIncomeAssetDTO]] = {}
        # O dono de cada CDB da casa emitido enquanto o título não vence
        self._house_owners: dict[str, UUID] = {}
        self._house_caps_on: Callable[[date], dict[UUID, Decimal]] = lambda _day: {}

    def use_house_cdb(self, caps_on: Callable[[date], dict[UUID, Decimal]]) -> None:
        """`caps_on` devolve, para o dia 1º do mês, o teto de cada Bancário da partida; quem não está nele não recebe o CDB."""
        self._house_caps_on = caps_on

    def refresh_assets(self, current_date: date):
        self._issued_assets = {
            uuid: asset
            for uuid, asset in self._issued_assets.items()
            if asset.maturity_date > current_date
        }
        self._house_owners = {
            uuid: owner
            for uuid, owner in self._house_owners.items()
            if uuid in self._issued_assets
        }
        current_month = (current_date.year, current_date.month)
        if self._current_month == current_month:
            return

        self._current_month = current_month
        self._generate_assets()

    def get_available_assets(self) -> list[FixedIncomeAssetDTO]:
        """O catálogo público, igual para todos; o CDB da casa não entra."""
        return list(self._assets.values())

    def get_house_assets(self, client_id: UUID) -> list[FixedIncomeAssetDTO]:
        """Os CDBs da casa do mês que `client_id` recebeu, do prazo mais curto ao mais longo."""
        return list(self._house.get(client_id, {}).values())

    def get_house_asset(
        self, client_id: UUID, years: int
    ) -> FixedIncomeAssetDTO | None:
        return self._house.get(client_id, {}).get(years)

    def house_catalog(self) -> list[tuple[UUID, FixedIncomeAssetDTO]]:
        """Cada CDB da casa do mês com o dono dele."""
        return [
            (owner, asset)
            for owner, assets in self._house.items()
            for asset in assets.values()
        ]

    def is_house_asset(self, uuid: str) -> bool:
        return uuid in self._house_owners

    def get_asset(self, client_id: UUID, uuid: str) -> FixedIncomeAssetDTO | None:
        """O ativo de `uuid` como `client_id` o enxerga: o CDB da casa de outro jogador não existe para ele."""
        owner = self._house_owners.get(uuid)
        if owner is not None and owner != client_id:
            return None

        asset = self._issued_assets.get(uuid)
        if asset:
            return asset

        asset = repository.fixed_income.get_asset_by_uuid(self._simulation_id, uuid)
        return asset

    def _generate_assets(self):
        if self._current_month is None:
            return

        year, month = self._current_month
        current_date = date(year, month, 1)

        # O CDB de 100% do CDI abre a vitrine; a oferta rara aparece em parte dos meses
        fixed = FixedIncomeFactory.daily_liquidity_cdb(
            self._simulation_id, self._end_date
        )
        dollar = FixedIncomeFactory.dollar_account(self._simulation_id, self._end_date)
        rare = FixedIncomeFactory.rare_daily_liquidity_offer(current_date)
        self._assets = {
            str(asset.asset_uuid): asset
            for asset in (fixed, dollar, rare)
            if asset is not None
        }
        self._assets.update(FixedIncomeFactory.generate_assets(current_date, n=10))
        self._start_date = self._start_date or current_date
        self._assets.update(
            treasury.issue(
                self._simulation_id,
                self._start_date,
                current_date,
                self._risk_premium_on(current_date),
            )
        )
        self._house = {
            owner: house_cdb.issue(self._simulation_id, owner, current_date, cap)
            for owner, cap in self._house_caps_on(current_date).items()
        }
        # A renovação da vitrine não invalida uma oferta ainda aberta no navegador.
        self._issued_assets.update(self._assets)
        for owner, assets in self._house.items():
            for asset in assets.values():
                self._issued_assets[str(asset.asset_uuid)] = asset
                self._house_owners[str(asset.asset_uuid)] = owner
        notify(
            "fixed_assets_update",
            FixedAssetsUpdateEventDTO(assets=self.get_available_assets()).to_json(),
        )
        logger.info(f"Gerados {len(self._assets)} ativos de renda fixa")
