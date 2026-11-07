"""
Os lugares do mapa: os 27 estados e as 5 regiões, e a mistura de grupos de eleitores de
cada um. O estado é a base; a região é a soma dos estados dela pesada pelo eleitorado.
Tudo aqui é função pura sobre tabelas fixas.
"""

from decimal import ROUND_HALF_UP, Decimal

from backend.core.enum import BrazilState, Region, VoterGroup
from backend.features.government import voters

S = BrazilState
G = VoterGroup

Place = BrazilState | Region

ZERO = Decimal(0)
ONE = Decimal(1)

# Amostra de uma pesquisa nacional: cada lugar fica com a fatia dele dela
POLL_SAMPLE = 4800
# 98 ÷ √n é a margem de erro, em pontos, com 95% de confiança
MARGIN_NUMERATOR = Decimal(98)
MIN_MARGIN = 3
MAX_MARGIN = 12

# Reescalas do ajuste proporcional até a tabela parar de mudar
RAKE_TOLERANCE = Decimal("1e-18")
RAKE_MAX_ROUNDS = 500

REGION_OF: dict[BrazilState, Region] = {
    **dict.fromkeys((S.AC, S.AP, S.AM, S.PA, S.RO, S.RR, S.TO), Region.NORTH),
    **dict.fromkeys(
        (S.AL, S.BA, S.CE, S.MA, S.PB, S.PE, S.PI, S.RN, S.SE), Region.NORTHEAST
    ),
    **dict.fromkeys((S.DF, S.GO, S.MT, S.MS), Region.MIDWEST),
    **dict.fromkeys((S.ES, S.MG, S.RJ, S.SP), Region.SOUTHEAST),
    **dict.fromkeys((S.PR, S.RS, S.SC), Region.SOUTH),
}

NAMES: dict[Place, str] = {
    S.AC: "Acre",
    S.AL: "Alagoas",
    S.AP: "Amapá",
    S.AM: "Amazonas",
    S.BA: "Bahia",
    S.CE: "Ceará",
    S.DF: "Distrito Federal",
    S.ES: "Espírito Santo",
    S.GO: "Goiás",
    S.MA: "Maranhão",
    S.MT: "Mato Grosso",
    S.MS: "Mato Grosso do Sul",
    S.MG: "Minas Gerais",
    S.PA: "Pará",
    S.PB: "Paraíba",
    S.PR: "Paraná",
    S.PE: "Pernambuco",
    S.PI: "Piauí",
    S.RJ: "Rio de Janeiro",
    S.RN: "Rio Grande do Norte",
    S.RS: "Rio Grande do Sul",
    S.RO: "Rondônia",
    S.RR: "Roraima",
    S.SC: "Santa Catarina",
    S.SP: "São Paulo",
    S.SE: "Sergipe",
    S.TO: "Tocantins",
    Region.NORTH: "Norte",
    Region.NORTHEAST: "Nordeste",
    Region.MIDWEST: "Centro-Oeste",
    Region.SOUTHEAST: "Sudeste",
    Region.SOUTH: "Sul",
}

# Eleitores aptos por UF em 2022 (TSE, pela tabela 2.7.1.2 do Anuário Estatístico do Brasil 2023 do IBGE).
# Não inclui o eleitorado no exterior, que o mapa não tem.
ELECTORATE: dict[BrazilState, int] = {
    S.AC: 588433,
    S.AL: 2325656,
    S.AP: 550687,
    S.AM: 2647748,
    S.BA: 11291528,
    S.CE: 6820673,
    S.DF: 2203045,
    S.ES: 2921506,
    S.GO: 4870354,
    S.MA: 5042999,
    S.MT: 2469414,
    S.MS: 1996510,
    S.MG: 16290870,
    S.PA: 6082312,
    S.PB: 3091684,
    S.PR: 8475632,
    S.PE: 7018098,
    S.PI: 2573810,
    S.RJ: 12827296,
    S.RN: 2554727,
    S.RS: 8593469,
    S.RO: 1230987,
    S.RR: 366240,
    S.SC: 5489658,
    S.SP: 34667793,
    S.SE: 1671801,
    S.TO: 1094003,
}

# Os números brutos de cada fonte, por estado. As colunas têm unidades diferentes: o ajuste
# proporcional preserva só as razões entre estados e entre grupos, então a unidade não importa.
#   WELFARE: famílias no Bolsa Família, abril de 2026 (MDS, Informe do Bolsa Família nº 115).
#   RETIREES: benefícios emitidos do RGPS, agosto de 2026 (Boletim Estatístico da Previdência Social, tabela 19).
#   FORMAL_WORKERS: empregados do setor privado com carteira, em mil pessoas, 2º trimestre de 2026
#     (PNAD Contínua, tabela 4097 do SIDRA).
#   PUBLIC_SERVANTS: empregados do setor público, militares incluídos, em mil pessoas, mesma tabela.
#   ENTREPRENEURS: empregadores mais conta própria, em mil pessoas, mesma tabela.
#   INVESTORS: investidores pessoa física em renda variável, dezembro de 2025 (B3).
RAW_COUNTS: dict[BrazilState, dict[VoterGroup, int]] = {
    S.AC: {
        G.WELFARE: 123705,
        G.RETIREES: 82759,
        G.FORMAL_WORKERS: 87,
        G.PUBLIC_SERVANTS: 85,
        G.ENTREPRENEURS: 71,
        G.INVESTORS: 9302,
    },
    S.AL: {
        G.WELFARE: 505485,
        G.RETIREES: 499782,
        G.FORMAL_WORKERS: 353,
        G.PUBLIC_SERVANTS: 248,
        G.ENTREPRENEURS: 339,
        G.INVESTORS: 38073,
    },
    S.AP: {
        G.WELFARE: 111551,
        G.RETIREES: 49269,
        G.FORMAL_WORKERS: 83,
        G.PUBLIC_SERVANTS: 90,
        G.ENTREPRENEURS: 115,
        G.INVESTORS: 9037,
    },
    S.AM: {
        G.WELFARE: 598564,
        G.RETIREES: 314680,
        G.FORMAL_WORKERS: 461,
        G.PUBLIC_SERVANTS: 327,
        G.ENTREPRENEURS: 609,
        G.INVESTORS: 51202,
    },
    S.BA: {
        G.WELFARE: 2360335,
        G.RETIREES: 2480906,
        G.FORMAL_WORKERS: 1824,
        G.PUBLIC_SERVANTS: 943,
        G.ENTREPRENEURS: 2102,
        G.INVESTORS: 205215,
    },
    S.CE: {
        G.WELFARE: 1353648,
        G.RETIREES: 1481810,
        G.FORMAL_WORKERS: 1068,
        G.PUBLIC_SERVANTS: 578,
        G.ENTREPRENEURS: 1082,
        G.INVESTORS: 134751,
    },
    S.DF: {
        G.WELFARE: 152175,
        G.RETIREES: 426517,
        G.FORMAL_WORKERS: 581,
        G.PUBLIC_SERVANTS: 338,
        G.ENTREPRENEURS: 356,
        G.INVESTORS: 148005,
    },
    S.ES: {
        G.WELFARE: 281263,
        G.RETIREES: 709411,
        G.FORMAL_WORKERS: 750,
        G.PUBLIC_SERVANTS: 255,
        G.ENTREPRENEURS: 602,
        G.INVESTORS: 114355,
    },
    S.GO: {
        G.WELFARE: 436104,
        G.RETIREES: 845835,
        G.FORMAL_WORKERS: 1489,
        G.PUBLIC_SERVANTS: 441,
        G.ENTREPRENEURS: 1074,
        G.INVESTORS: 151071,
    },
    S.MA: {
        G.WELFARE: 1154413,
        G.RETIREES: 1141608,
        G.FORMAL_WORKERS: 538,
        G.PUBLIC_SERVANTS: 513,
        G.ENTREPRENEURS: 992,
        G.INVESTORS: 60598,
    },
    S.MT: {
        G.WELFARE: 215219,
        G.RETIREES: 479518,
        G.FORMAL_WORKERS: 884,
        G.PUBLIC_SERVANTS: 251,
        G.ENTREPRENEURS: 557,
        G.INVESTORS: 73348,
    },
    S.MS: {
        G.WELFARE: 179180,
        G.RETIREES: 409204,
        G.FORMAL_WORKERS: 594,
        G.PUBLIC_SERVANTS: 233,
        G.ENTREPRENEURS: 387,
        G.INVESTORS: 60515,
    },
    S.MG: {
        G.WELFARE: 1444001,
        G.RETIREES: 4192059,
        G.FORMAL_WORKERS: 4171,
        G.PUBLIC_SERVANTS: 1349,
        G.ENTREPRENEURS: 3275,
        G.INVESTORS: 553764,
    },
    S.PA: {
        G.WELFARE: 1264145,
        G.RETIREES: 878854,
        G.FORMAL_WORKERS: 884,
        G.PUBLIC_SERVANTS: 588,
        G.ENTREPRENEURS: 1292,
        G.INVESTORS: 90134,
    },
    S.PB: {
        G.WELFARE: 626233,
        G.RETIREES: 722248,
        G.FORMAL_WORKERS: 491,
        G.PUBLIC_SERVANTS: 307,
        G.ENTREPRENEURS: 473,
        G.INVESTORS: 56688,
    },
    S.PR: {
        G.WELFARE: 555106,
        G.RETIREES: 2231193,
        G.FORMAL_WORKERS: 2803,
        G.PUBLIC_SERVANTS: 654,
        G.ENTREPRENEURS: 1813,
        G.INVESTORS: 348530,
    },
    S.PE: {
        G.WELFARE: 1488030,
        G.RETIREES: 1395154,
        G.FORMAL_WORKERS: 1142,
        G.PUBLIC_SERVANTS: 559,
        G.ENTREPRENEURS: 1059,
        G.INVESTORS: 143433,
    },
    S.PI: {
        G.WELFARE: 547537,
        G.RETIREES: 687556,
        G.FORMAL_WORKERS: 293,
        G.PUBLIC_SERVANTS: 273,
        G.ENTREPRENEURS: 413,
        G.INVESTORS: 34514,
    },
    S.RJ: {
        G.WELFARE: 1401468,
        G.RETIREES: 2852571,
        G.FORMAL_WORKERS: 3164,
        G.PUBLIC_SERVANTS: 1109,
        G.ENTREPRENEURS: 2591,
        G.INVESTORS: 549603,
    },
    S.RN: {
        G.WELFARE: 465782,
        G.RETIREES: 568823,
        G.FORMAL_WORKERS: 435,
        G.PUBLIC_SERVANTS: 251,
        G.ENTREPRENEURS: 402,
        G.INVESTORS: 54736,
    },
    S.RS: {
        G.WELFARE: 523628,
        G.RETIREES: 2799416,
        G.FORMAL_WORKERS: 2595,
        G.PUBLIC_SERVANTS: 661,
        G.ENTREPRENEURS: 1655,
        G.INVESTORS: 298471,
    },
    S.RO: {
        G.WELFARE: 126634,
        G.RETIREES: 258937,
        G.FORMAL_WORKERS: 261,
        G.PUBLIC_SERVANTS: 143,
        G.ENTREPRENEURS: 236,
        G.INVESTORS: 32699,
    },
    S.RR: {
        G.WELFARE: 75267,
        G.RETIREES: 41059,
        G.FORMAL_WORKERS: 76,
        G.PUBLIC_SERVANTS: 79,
        G.ENTREPRENEURS: 78,
        G.INVESTORS: 9086,
    },
    S.SC: {
        G.WELFARE: 207112,
        G.RETIREES: 1755527,
        G.FORMAL_WORKERS: 2239,
        G.PUBLIC_SERVANTS: 454,
        G.ENTREPRENEURS: 1331,
        G.INVESTORS: 262966,
    },
    S.SP: {
        G.WELFARE: 2226419,
        G.RETIREES: 8156373,
        G.FORMAL_WORKERS: 11650,
        G.PUBLIC_SERVANTS: 1943,
        G.ENTREPRENEURS: 7041,
        G.INVESTORS: 1919926,
    },
    S.SE: {
        G.WELFARE: 360270,
        G.RETIREES: 364322,
        G.FORMAL_WORKERS: 283,
        G.PUBLIC_SERVANTS: 157,
        G.ENTREPRENEURS: 276,
        G.INVESTORS: 33444,
    },
    S.TO: {
        G.WELFARE: 142895,
        G.RETIREES: 218154,
        G.FORMAL_WORKERS: 219,
        G.PUBLIC_SERVANTS: 188,
        G.ENTREPRENEURS: 180,
        G.INVESTORS: 21661,
    },
}


def code(place: Place) -> str:
    return place.value


def states_of(region: Region) -> list[BrazilState]:
    return [s for s in BrazilState if REGION_OF[s] is region]


TOTAL_ELECTORATE = sum(ELECTORATE.values())

# Os estados do maior para o menor eleitorado: a ordem do Tab e da tabela do mapa
TAB_ORDER: list[BrazilState] = sorted(
    BrazilState, key=lambda s: (-ELECTORATE[s], s.value)
)


def electorate(place: Place) -> int:
    if isinstance(place, Region):
        return sum(ELECTORATE[s] for s in states_of(place))
    return ELECTORATE[place]


def share(place: Place) -> Decimal:
    """A fatia do lugar no eleitorado do país, de 0 a 1."""
    return Decimal(electorate(place)) / Decimal(TOTAL_ELECTORATE)


def rake(
    counts: dict[BrazilState, dict[VoterGroup, Decimal]],
    rows: dict[BrazilState, Decimal],
    columns: dict[VoterGroup, Decimal],
) -> dict[BrazilState, dict[VoterGroup, Decimal]]:
    """
    Ajuste proporcional iterativo: parte dos números brutos de cada fonte e reescala as
    linhas (cada estado soma a fatia dele) e as colunas (cada grupo soma o peso dele no
    país), uma depois da outra, até a tabela parar de mudar. Mantém o formato dos dados e
    fecha exatamente as duas somas.
    """
    table = {s: dict(row) for s, row in counts.items()}
    for _ in range(RAKE_MAX_ROUNDS):
        for s, row in table.items():
            factor = rows[s] / sum(row.values(), ZERO)
            table[s] = {g: v * factor for g, v in row.items()}
        change = ZERO
        for g, wanted in columns.items():
            factor = wanted / sum((row[g] for row in table.values()), ZERO)
            for row in table.values():
                scaled = row[g] * factor
                change = max(change, abs(scaled - row[g]))
                row[g] = scaled
        if change < RAKE_TOLERANCE:
            break
    # A última reescala é a das colunas; as linhas voltam a somar a fatia do estado
    for s, row in table.items():
        factor = rows[s] / sum(row.values(), ZERO)
        table[s] = {g: v * factor for g, v in row.items()}
    return table


def _mixtures() -> dict[BrazilState, dict[VoterGroup, Decimal]]:
    shares = {s: share(s) for s in BrazilState}
    table = rake(
        {s: {g: Decimal(v) for g, v in row.items()} for s, row in RAW_COUNTS.items()},
        shares,
        voters.WEIGHTS,
    )
    return {s: {g: v / shares[s] for g, v in row.items()} for s, row in table.items()}


# Em cada estado, a fatia de cada grupo no eleitorado dele (soma 1)
MIXTURES: dict[BrazilState, dict[VoterGroup, Decimal]] = _mixtures()


def region_mixture(region: Region) -> dict[VoterGroup, Decimal]:
    """A média das misturas dos estados da região, pesada pelo eleitorado."""
    total = Decimal(electorate(region))
    return {
        g: sum((MIXTURES[s][g] * ELECTORATE[s] for s in states_of(region)), ZERO)
        / total
        for g in VoterGroup
    }


def mixture(place: Place) -> dict[VoterGroup, Decimal]:
    return region_mixture(place) if isinstance(place, Region) else MIXTURES[place]


def margin(place: Place) -> int:
    """A margem da pesquisa no lugar, em pontos: 98 ÷ √n arredondada, entre ±3 e ±12."""
    sample = Decimal(POLL_SAMPLE) * share(place)
    raw = (MARGIN_NUMERATOR / sample.sqrt()).quantize(ONE, ROUND_HALF_UP)
    return int(max(Decimal(MIN_MARGIN), min(Decimal(MAX_MARGIN), raw)))


def all_places() -> list[Place]:
    """Os 27 estados do maior para o menor eleitorado e depois as 5 regiões."""
    return [*TAB_ORDER, *Region]
