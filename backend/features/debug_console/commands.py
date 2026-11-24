"""Os comandos do console do modo debug. Cada um chama a ação da partida pelo mesmo caminho do jogo e devolve a mensagem que o console mostra."""

from decimal import Decimal

from backend.core.dto.user import UserDTO
from backend.core.exceptions.http_exceptions import UnprocessableEntityError
from backend.core.utils import format_money
from backend.features.debug_console.registry import (
    Argument,
    ArgumentKind,
    Command,
    ConsoleContext,
)
from backend.features.government import measures


def _help(context: ConsoleContext, name: str | None = None) -> str:
    if name is None:
        width = max(len(c.usage) for c in COMMANDS.values())
        return "\n".join(f"{c.usage.ljust(width)}  {c.help}" for c in COMMANDS.values())
    found = COMMANDS.get(name)
    if found is None:
        raise UnprocessableEntityError(
            f"Comando desconhecido: {name}. help lista os disponíveis."
        )
    lines = [f"{found.usage}  {found.help}"]
    lines += [f"  <{a.name}>  {a.help}" for a in found.arguments]
    return "\n".join(lines)


def _signed(value: Decimal) -> str:
    return ("+" if value > 0 else "") + format_money(value)


def _add_cash(context: ConsoleContext, player: UserDTO, amount: Decimal) -> str:
    cash = context.simulation.debug_add_cash(player, amount)
    return f"Caixa de {player.nickname}: {format_money(cash)} ({_signed(amount)})."


def _set_cash(context: ConsoleContext, player: UserDTO, amount: Decimal) -> str:
    difference = context.simulation.debug_set_cash(player, amount)
    return (
        f"Caixa de {player.nickname}: {format_money(amount)} "
        f"({_signed(difference)} no extrato)."
    )


def _give_stock(
    context: ConsoleContext, player: UserDTO, ticker: str, quantity: Decimal
) -> str:
    price = context.simulation.debug_give_stock(player, ticker, quantity)
    return (
        f"{quantity.normalize():f} de {ticker} na carteira de {player.nickname}, "
        f"ao custo de {format_money(price)} cada."
    )


def _give_title(
    context: ConsoleContext, player: UserDTO, code: str, value: Decimal
) -> str:
    asset = context.simulation.debug_give_title(player, code, value)
    return f"{format_money(value)} em {asset.name} na carteira de {player.nickname}."


def _give_event(context: ConsoleContext, player: UserDTO, key: str) -> str:
    amount = context.simulation.debug_give_event(player, key)
    return f"Imprevisto {key} aplicado a {player.nickname} ({format_money(amount)})."


def _give_presidency(context: ConsoleContext, player: UserDTO) -> str:
    context.simulation.debug_assume_presidency(player)
    return f"{player.nickname} assumiu a presidência até a próxima posse."


def _start_impeachment(context: ConsoleContext) -> str:
    context.simulation.debug_start_impeachment()
    return "Pedido de impeachment aberto: a casa vota no próximo dia de votação."


def _set_selic(context: ConsoleContext, rate: Decimal) -> str:
    context.simulation.debug_set_selic(rate)
    return (
        f"SELIC em {measures.percent(rate)} ao ano a partir de amanhã, "
        "até a próxima reunião do Copom."
    )


def _join_party(context: ConsoleContext, player: UserDTO, abbr: str) -> str:
    context.simulation.debug_join_party(player, abbr)
    return f"{player.nickname} filiado ao {abbr}, já valendo para a próxima eleição."


def _pass_exam(context: ConsoleContext, player: UserDTO) -> str:
    context.simulation.debug_pass_exam(player)
    return f"{player.nickname} passa no concurso: o resultado sai na data de sempre."


def _unban_fund(context: ConsoleContext, player: UserDTO) -> str:
    context.simulation.debug_unban_fund(player)
    return f"{player.nickname} já pode fundar uma gestora."


_PLAYER = Argument("jogador", ArgumentKind.PLAYER, "apelido do jogador na sala")

COMMANDS: dict[str, Command] = {
    c.name: c
    for c in (
        Command(
            "help",
            "lista os comandos, ou explica um",
            (
                Argument(
                    "comando",
                    ArgumentKind.COMMAND,
                    "o comando a explicar",
                    required=False,
                ),
            ),
            _help,
        ),
        Command(
            "add_cash",
            "soma ao caixa (negativo retira); o caixa não fica negativo",
            (_PLAYER, Argument("valor", ArgumentKind.MONEY, "em reais, com sinal")),
            _add_cash,
        ),
        Command(
            "set_cash",
            "leva o caixa ao valor, gravando a diferença como depósito ou saque",
            (_PLAYER, Argument("valor", ArgumentKind.MONEY, "o caixa final, em reais")),
            _set_cash,
        ),
        Command(
            "give_stock",
            "põe ativos na carteira ao preço do dia, sem debitar o caixa",
            (
                _PLAYER,
                Argument("ticker", ArgumentKind.TICKER, "o código do ativo"),
                Argument("quantidade", ArgumentKind.QUANTITY, "quantas unidades"),
            ),
            _give_stock,
        ),
        Command(
            "give_title",
            "aplica em um título de renda fixa em oferta, sem debitar o caixa",
            (
                _PLAYER,
                Argument("título", ArgumentKind.TITLE, "o código curto do título"),
                Argument("valor", ArgumentKind.MONEY, "o valor aplicado, em reais"),
            ),
            _give_title,
        ),
        Command(
            "give_event",
            "aplica um imprevisto como se tivesse sido sorteado; a demissão também corta o salário do mês seguinte",
            (_PLAYER, Argument("evento", ArgumentKind.EVENT, "a chave do imprevisto")),
            _give_event,
        ),
        Command(
            "give_presidency",
            "o jogador assume hoje pelo partido dele, até a próxima posse",
            (_PLAYER,),
            _give_presidency,
        ),
        Command(
            "start_impeachment",
            "abre o pedido de impeachment do presidente em exercício",
            (),
            _start_impeachment,
        ),
        Command(
            "set_selic",
            "decide a SELIC de amanhã até a próxima reunião (só com a SELIC do governo)",
            (
                Argument(
                    "taxa",
                    ArgumentKind.PERCENT,
                    "% ao ano, em passos de 0,25 (13,75)",
                ),
            ),
            _set_selic,
        ),
        Command(
            "join_party",
            "filia o jogador a um partido, já valendo para a próxima eleição",
            (_PLAYER, Argument("sigla", ArgumentKind.PARTY, "a sigla do partido")),
            _join_party,
        ),
        Command(
            "pass_exam",
            "garante a aprovação do Administrador inscrito no concurso",
            (_PLAYER,),
            _pass_exam,
        ),
        Command(
            "unban_fund",
            "encerra a quarentena de 6 meses para fundar gestora",
            (_PLAYER,),
            _unban_fund,
        ),
    )
}
