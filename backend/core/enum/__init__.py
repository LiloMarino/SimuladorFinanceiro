from enum import Enum


class FixedIncomeType(Enum):
    CDB = "CDB"
    LCI = "LCI"
    LCA = "LCA"
    TESOURO_DIRETO = "Tesouro Direto"

    @property
    def db_value(self) -> str:
        return {
            FixedIncomeType.CDB: "CDB",
            FixedIncomeType.LCI: "LCI",
            FixedIncomeType.LCA: "LCA",
            FixedIncomeType.TESOURO_DIRETO: "TESOURO_DIRETO",
        }[self]

    @classmethod
    def from_db(cls, value: str) -> "FixedIncomeType":
        mapping = {
            "CDB": cls.CDB,
            "LCI": cls.LCI,
            "LCA": cls.LCA,
            "TESOURO_DIRETO": cls.TESOURO_DIRETO,
        }
        return mapping[value]


class RateIndexType(Enum):
    CDI = "CDI"
    IPCA = "IPCA"
    SELIC = "SELIC"
    PREFIXADO = "Prefixado"

    @property
    def db_value(self) -> str:
        return {
            RateIndexType.CDI: "CDI",
            RateIndexType.IPCA: "IPCA",
            RateIndexType.SELIC: "SELIC",
            RateIndexType.PREFIXADO: "PREFIXADO",
        }[self]

    @classmethod
    def from_db(cls, value: str) -> "RateIndexType":
        mapping = {
            "CDI": cls.CDI,
            "IPCA": cls.IPCA,
            "SELIC": cls.SELIC,
            "PREFIXADO": cls.PREFIXADO,
        }
        return mapping[value]


class CashflowEventType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    DIVIDEND = "DIVIDEND"


class EquityEventType(Enum):
    BUY = "BUY"
    SELL = "SELL"


class FixedIncomeEventType(Enum):
    BUY = "BUY"
    REDEEM = "REDEEM"
