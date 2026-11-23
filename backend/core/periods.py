"""
As medidas de tempo do simulador.

Dia útil é sessão da B3: 252 por ano, a base das taxas dos indexadores e do
retorno anualizado. Dia corrido é dia de calendário: 365,25 por ano, a base do
prazo dos títulos e da idade das medidas.
"""

from datetime import date
from decimal import Decimal

BUSINESS_DAYS_PER_YEAR = 252
CALENDAR_DAYS_PER_YEAR = Decimal("365.25")
MONTHS_PER_YEAR = 12
DAYS_PER_MONTH = CALENDAR_DAYS_PER_YEAR / MONTHS_PER_YEAR

# O IVG-R (preço dos imóveis) começa em março de 2001, o primeiro mês da série: antes
# disso o imóvel não tem preço e o Locador não existe
IVG_R_START = date(2001, 3, 1)
