from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.preparation import PartyIdentityDTO
from backend.core.dto.strategy import StrategyParamValue
from backend.core.enum import PreparationKind, Profession
from backend.core.exceptions.http_exceptions import NotFoundError
from backend.core.models.models import Users

MY_PARTY_KEY = "my_party"
PARTY_CONTRIBUTION_KEY = "party_contribution"
STRATEGY_PARAMS_KEY = "strategy_params"
PREPARATION_CHOICE_KEY = "preparation_choice"
COVER_WITH_TREASURY_KEY = "cover_with_treasury"
PROFESSION_KEY = "profession"
# As chaves que o jogador grava pelas rotas próprias do perfil, e que as preferências atravessam
PROFILE_KEYS = frozenset(
    {
        MY_PARTY_KEY,
        PARTY_CONTRIBUTION_KEY,
        STRATEGY_PARAMS_KEY,
        PREPARATION_CHOICE_KEY,
        COVER_WITH_TREASURY_KEY,
        PROFESSION_KEY,
    }
)


class SettingsRepository:
    @transactional
    def get_by_user_id(self, session: Session, user_id: int) -> dict[str, Any]:
        settings = session.query(Users.settings).filter(Users.id == user_id).scalar()
        if settings is None:
            raise NotFoundError("Usuário não encontrado.")
        return settings

    @transactional
    def update_by_user_id(
        self, session: Session, user_id: int, settings: dict[str, Any]
    ) -> None:
        (
            session.query(Users)
            .filter(Users.id == user_id)
            .update(
                {"settings": settings},
                synchronize_session=False,
            )
        )

    def get_my_party(self, user_id: int) -> PartyIdentityDTO | None:
        """O Meu partido salvo no perfil; nulo enquanto o jogador não salvou um."""
        raw = self.get_by_user_id(user_id).get(MY_PARTY_KEY)
        return None if raw is None else PartyIdentityDTO.model_validate(raw)

    def set_my_party(self, user_id: int, party: PartyIdentityDTO) -> None:
        self._set_key(user_id, MY_PARTY_KEY, party.model_dump(mode="json"))

    def get_party_contribution(self, user_id: int) -> Decimal:
        """A contribuição mensal que o jogador leva a cada partido; zero enquanto não salvou uma."""
        return Decimal(
            str(self.get_by_user_id(user_id).get(PARTY_CONTRIBUTION_KEY, "0"))
        )

    def set_party_contribution(self, user_id: int, amount: Decimal) -> None:
        self._set_key(user_id, PARTY_CONTRIBUTION_KEY, str(amount))

    def get_cover_with_treasury(self, user_id: int) -> bool:
        """Se o resgate automático também vende Prefixado e IPCA+ (a mercado) para cobrir despesas; desligado até o jogador ligar."""
        return bool(self.get_by_user_id(user_id).get(COVER_WITH_TREASURY_KEY, False))

    def set_cover_with_treasury(self, user_id: int, enabled: bool) -> None:
        self._set_key(user_id, COVER_WITH_TREASURY_KEY, enabled)

    def get_profession(self, user_id: int) -> Profession | None:
        """A profissão que o jogador levou da última sala; nula enquanto ele não escolheu uma."""
        raw = self.get_by_user_id(user_id).get(PROFESSION_KEY)
        return None if raw is None else Profession(raw)

    def set_profession(self, user_id: int, profession: Profession) -> None:
        self._set_key(user_id, PROFESSION_KEY, profession.value)

    def get_strategy_params(
        self, user_id: int
    ) -> dict[str, dict[str, StrategyParamValue]]:
        """Os últimos parâmetros de cada estratégia, pela chave dela; só as que o jogador já ajustou."""
        return self.get_by_user_id(user_id).get(STRATEGY_PARAMS_KEY, {})

    def set_strategy_params(
        self, user_id: int, key: str, params: dict[str, StrategyParamValue]
    ) -> None:
        saved = self.get_strategy_params(user_id)
        self._set_key(user_id, STRATEGY_PARAMS_KEY, {**saved, key: params})

    def get_preparation_choice(self, user_id: int) -> PreparationKind:
        """A última escolha da preparação; quem entrou no partido de outro volta sem partido."""
        raw = self.get_by_user_id(user_id).get(PREPARATION_CHOICE_KEY)
        return (
            PreparationKind.FOUND
            if raw == PreparationKind.FOUND.value
            else PreparationKind.NONE
        )

    def set_preparation_choice(self, user_id: int, kind: PreparationKind) -> None:
        self._set_key(user_id, PREPARATION_CHOICE_KEY, kind.value)

    def _set_key(self, user_id: int, key: str, value: object) -> None:
        settings = self.get_by_user_id(user_id)
        self.update_by_user_id(user_id, {**settings, key: value})
