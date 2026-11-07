"""
As medidas de tempo do simulador.

Dia útil é sessão da B3: 252 por ano, a base das taxas dos indexadores e do
retorno anualizado. Dia corrido é dia de calendário: 365,25 por ano, a base do
prazo dos títulos e da idade das medidas.
"""

from decimal import Decimal

BUSINESS_DAYS_PER_YEAR = 252
CALENDAR_DAYS_PER_YEAR = Decimal("365.25")
MONTHS_PER_YEAR = 12
DAYS_PER_MONTH = CALENDAR_DAYS_PER_YEAR / MONTHS_PER_YEAR
