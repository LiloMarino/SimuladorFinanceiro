"""
As regras do Administrador: o fator da experiência por setor, o calendário da troca de
setor, os editais do concurso para Servidor e o sorteio da aprovação, em Decimal e sem
estado.
"""

import calendar
import random
from datetime import date
from decimal import Decimal

from backend.core.dates import add_months
from backend.core.enum import Profession

# Os setores onde o Administrador trabalha
SECTORS = (
    Profession.CLT,
    Profession.ENTREPRENEUR,
    Profession.EXPORTER,
    Profession.BANKER,
    Profession.FREELANCER,
    Profession.BROKER,
)

# A renda leva o fator da experiência no setor: de 0,85 no primeiro mês a 1 com 12 meses
JUNIOR_FACTOR = Decimal("0.85")
SENIOR_MONTHS = 12

# A troca de setor leva este tanto de meses e, enquanto dura, a renda vale esta fração
SWITCH_MONTHS = 1
SWITCH_INCOME_FACTOR = Decimal("0.5")

# O estudo do concurso dura tantos meses e, enquanto dura, a renda vale esta fração
STUDY_MONTHS = 6
STUDY_INCOME_FACTOR = Decimal("0.8")
# A chance de passar em uma inscrição
PASS_CHANCE = Decimal("0.18")

# Os editais saem em abril e outubro; com o gasto do governo acima do normal, também em julho
EXAM_MONTHS = (4, 10)
EXTRA_EXAM_MONTH = 7

# Política dos bots: trocam de setor quando o melhor rende mais que o atual por este ganho
BOT_SWITCH_GAIN = Decimal("0.2")


def experience_factor(months: int) -> Decimal:
    """O quanto da renda do setor o Administrador leva com `months` meses nele: sobe em linha reta de 0,85 a 1 em 12 meses."""
    done = Decimal(min(max(months, 0), SENIOR_MONTHS)) / SENIOR_MONTHS
    return JUNIOR_FACTOR + (1 - JUNIOR_FACTOR) * done


def is_senior(months: int) -> bool:
    return months >= SENIOR_MONTHS


def months_between(start: date, day: date) -> int:
    """Quantas viradas de mês do calendário passaram de `start` até `day`."""
    return (day.year - start.year) * 12 + day.month - start.month


def switch_entry_on(started_on: date) -> date:
    """O dia em que o setor novo entra: a mesma data do mês seguinte à troca."""
    return add_months(started_on, SWITCH_MONTHS)


def switch_concluded(started_on: date, day: date) -> bool:
    """A troca conclui na primeira virada depois da entrada: a virada do meio paga a metade."""
    return months_between(started_on, day) > SWITCH_MONTHS


def exam_result_due(enrolled_on: date, day: date) -> bool:
    """O resultado sai na primeira virada depois dos meses de estudo, que pagam a renda reduzida."""
    return months_between(enrolled_on, day) > STUDY_MONTHS


def exam_result_month(enrolled_on: date) -> date:
    """O primeiro dia do mês em que o resultado sai."""
    return add_months(enrolled_on.replace(day=1), STUDY_MONTHS + 1)


def exam_open(day: date, extra_notice: bool) -> bool:
    """Se há edital aberto no mês de `day`: abril e outubro sempre, julho só com o edital extra."""
    return day.month in EXAM_MONTHS or (day.month == EXTRA_EXAM_MONTH and extra_notice)


def exam_deadline(day: date) -> date:
    """O último dia de inscrição do edital do mês de `day`."""
    return day.replace(day=calendar.monthrange(day.year, day.month)[1])


def next_exam_month(day: date) -> date:
    """O primeiro dia do próximo mês de edital fixo depois do mês de `day`; o edital extra de julho só se conhece quando julho chega."""
    month = day.replace(day=1)
    while True:
        month = add_months(month, 1)
        if month.month in EXAM_MONTHS:
            return month


def exam_passed(seed: int, user_id: int, enrolled_on: date) -> bool:
    """O sorteio da aprovação da inscrição: a semente é da sala, do jogador e do dia da inscrição, e o mesmo resultado sai em toda leitura."""
    key = f"{seed}:{user_id}:{enrolled_on.isoformat()}:exam"
    return random.Random(key).random() < float(PASS_CHANCE)
