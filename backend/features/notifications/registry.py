"""
O registro único dos tipos de notificação da partida: cada tipo de manchete do jornal e
cada aviso do jogador, com a seção, o texto da configuração e o padrão. A configuração de
cada jogador, o histórico do jornal e a escolha da manchete numa rajada leem daqui.
"""

from dataclasses import dataclass
from uuid import UUID

from backend.core.dto.pending import PendingDTO
from backend.core.enum import (
    NewsLevel,
    NewsPosition,
    NewsSection,
    NewsType,
    PendingSeverity,
    PendingType,
    ToastType,
)


@dataclass(frozen=True)
class SectionSpec:
    section: NewsSection
    label: str
    # Quando a seção existe na partida; nulo quando existe sempre
    note: str | None


@dataclass(frozen=True)
class NewsSpec:
    type: NewsType
    section: NewsSection
    label: str
    description: str
    default_level: NewsLevel
    # Fixo: o tipo abre a janela com pausa para a sala inteira e não se configura
    fixed: bool = False


@dataclass(frozen=True)
class ToastSpec:
    type: ToastType
    label: str
    description: str
    default_on: bool = True


@dataclass(frozen=True)
class PendingSpec:
    type: PendingType
    severity: PendingSeverity
    label: str
    # Quando ela some; pendência não se desliga, só acaba com a condição
    resolves: str


DEFAULT_POSITION = NewsPosition.BOTTOM_LEFT

# A ordem das seções é a da importância: numa rajada sobe a manchete da primeira seção
SECTIONS: tuple[SectionSpec, ...] = (
    SectionSpec(NewsSection.ECONOMY, "Economia", None),
    SectionSpec(NewsSection.COMPANIES, "Empresas", None),
    SectionSpec(NewsSection.POLITICS, "Política", "só com Governo & Política ligado"),
    SectionSpec(NewsSection.HISTORY, "História", "só em período real"),
)

# A ordem é a da importância numa rajada: as seções na ordem de SECTIONS e, dentro delas, o mais grave antes
NEWS: tuple[NewsSpec, ...] = (
    NewsSpec(
        NewsType.ELECTION_RESULT,
        NewsSection.POLITICS,
        "Resultado do turno e impeachment",
        "A sala inteira pausa e a janela abre no centro",
        NewsLevel.WINDOW,
        fixed=True,
    ),
    NewsSpec(
        NewsType.TERM_STARTED,
        NewsSection.POLITICS,
        "Posse",
        "“Bia toma posse; o mandato vai até 2019”",
        NewsLevel.JOURNAL,
    ),
    NewsSpec(
        NewsType.MEASURE_VOTED,
        NewsSection.POLITICS,
        "Medida votada e em vigor",
        "Aprovada, rejeitada e quando passa a valer",
        NewsLevel.JOURNAL,
    ),
    NewsSpec(
        NewsType.ELECTION_CALENDAR,
        NewsSection.POLITICS,
        "Calendário da eleição",
        "Campanha abre, chapas fecham, véspera do turno",
        NewsLevel.JOURNAL,
    ),
    NewsSpec(
        NewsType.MEASURE_PROPOSED,
        NewsSection.POLITICS,
        "Medida proposta ou retirada",
        "“Bia propõe: Ações: IR das vendas com lucro em 10%”",
        NewsLevel.JOURNAL,
    ),
    NewsSpec(
        NewsType.CAMPAIGN,
        NewsSection.POLITICS,
        "Campanha",
        "Ação que viraliza ou dá errado, ataque, promessas e apoio no 2º turno",
        NewsLevel.JOURNAL,
    ),
    NewsSpec(
        NewsType.PARTY_LIFE,
        NewsSection.POLITICS,
        "Vida dos partidos",
        "Partido fundado, doação, expulsão",
        NewsLevel.JOURNAL,
    ),
)

TOASTS: tuple[ToastSpec, ...] = (
    ToastSpec(
        ToastType.ORDER_EXECUTED,
        "Ordem executada",
        "Compra ou venda concluída, inclusive a limite",
    ),
    ToastSpec(
        ToastType.ORDER_PARTIAL,
        "Ordem executada em parte",
        "Faltou contraparte no book",
    ),
    ToastSpec(
        ToastType.STRATEGY_ORDERS,
        "Ordens do modo automático",
        "O que a estratégia mandou no pregão",
    ),
    ToastSpec(
        ToastType.PLAYER_PRESENCE, "Jogador entrou ou saiu", "Na sala e no lobby"
    ),
    ToastSpec(
        ToastType.CREDIT_PAYMENTS,
        "Parcelas pagas e empréstimo quitado",
        "Débito automático do crédito",
    ),
    ToastSpec(ToastType.CREDIT_RATING, "Nota de risco mudou", "“Nota de risco: B → C”"),
    ToastSpec(
        ToastType.LIFE_EVENT, "Imprevisto", "Conta inesperada da vida financeira"
    ),
    ToastSpec(
        ToastType.MONTH_SUMMARY,
        "Resumo do mês e retrospectiva",
        "Na virada do mês, com o atalho para abrir",
    ),
    ToastSpec(
        ToastType.VICE_ANSWER, "Resposta do vice", "Aceitou ou recusou o seu convite"
    ),
)

# A ordem é a da gravidade: as graves primeiro e, dentro de cada gravidade, a que custa mais antes
PENDING: tuple[PendingSpec, ...] = (
    PendingSpec(
        PendingType.OVERDUE_INSTALLMENT,
        PendingSeverity.SEVERE,
        "Parcela em atraso",
        "Some quando a parcela é paga",
    ),
    PendingSpec(
        PendingType.NEGATIVE_CASH,
        PendingSeverity.SEVERE,
        "Caixa negativo",
        "Some quando o caixa volta a zero",
    ),
    PendingSpec(
        PendingType.IMPEACHMENT_RISK,
        PendingSeverity.SEVERE,
        "Risco de impeachment",
        "Só para o presidente; some quando a aprovação sai da faixa de risco",
    ),
    PendingSpec(
        PendingType.CASH_SHORT,
        PendingSeverity.WARNING,
        "Caixa não cobre a próxima parcela",
        "Some quando o caixa cobre; no vencimento, vira atraso",
    ),
    PendingSpec(
        PendingType.STRATEGY_ERROR,
        PendingSeverity.WARNING,
        "Estratégia desligada por erro",
        "Some quando a estratégia volta a rodar",
    ),
    PendingSpec(
        PendingType.VICE_INVITE,
        PendingSeverity.WARNING,
        "Convite para vice",
        "Some ao responder ou quando as chapas fecham",
    ),
    PendingSpec(
        PendingType.CAMPAIGN_OPEN,
        PendingSeverity.WARNING,
        "Campanha aberta sem filiação",
        "Some ao se filiar ou quando as chapas fecham",
    ),
)

NEWS_BY_TYPE: dict[NewsType, NewsSpec] = {spec.type: spec for spec in NEWS}
TOASTS_BY_TYPE: dict[ToastType, ToastSpec] = {spec.type: spec for spec in TOASTS}
PENDING_BY_TYPE: dict[PendingType, PendingSpec] = {spec.type: spec for spec in PENDING}


def pending(
    pending_type: PendingType,
    detail: str,
    ref: str = "",
    loan_id: UUID | None = None,
) -> PendingDTO:
    """A pendência do tipo com título e gravidade do registro; `ref` distingue duas do mesmo tipo."""
    spec = PENDING_BY_TYPE[pending_type]
    return PendingDTO(
        key=f"{pending_type.value}:{ref}" if ref else pending_type.value,
        type=pending_type,
        severity=spec.severity,
        title=spec.label,
        detail=detail,
        loan_id=loan_id,
    )


def sort_pending(items: list[PendingDTO]) -> list[PendingDTO]:
    """As graves primeiro, na ordem do registro; as do mesmo tipo pela chave."""
    order = {spec.type: index for index, spec in enumerate(PENDING)}
    return sorted(items, key=lambda item: (order[item.type], item.key))


def news_levels(chosen: dict[NewsType, NewsLevel]) -> dict[NewsType, NewsLevel]:
    """O nível de cada tipo de manchete: o escolhido pelo jogador, senão o padrão; o fixo não muda."""
    return {
        spec.type: spec.default_level
        if spec.fixed
        else chosen.get(spec.type, spec.default_level)
        for spec in NEWS
    }


def toasts_on(chosen: dict[ToastType, bool]) -> dict[ToastType, bool]:
    """Se cada aviso aparece: o escolhido pelo jogador, senão o padrão."""
    return {spec.type: chosen.get(spec.type, spec.default_on) for spec in TOASTS}
