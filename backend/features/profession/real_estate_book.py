from datetime import date
from decimal import Decimal

from backend.core import repository
from backend.core.dto.real_estate import PropertyDraft, PropertyDTO
from backend.core.enum import PropertyStatus


class PropertyBook:
    """
    Os imóveis dos Locadores de uma partida. Lê o banco inteiro na primeira consulta e
    grava cada mudança no mesmo instante, para que o que a memória diz seja o que o
    banco guarda; quem entra na partida pede `forget`.
    """

    def __init__(self, simulation_id: int):
        self._simulation_id = simulation_id
        self._items: dict[int, list[PropertyDTO]] | None = None

    def forget(self) -> None:
        """Descarta o que a memória guarda: a próxima consulta lê o banco de novo."""
        self._items = None

    def _loaded(self) -> dict[int, list[PropertyDTO]]:
        if self._items is None:
            self._items = repository.real_estate.of_simulation(self._simulation_id)
        return self._items

    def of(self, user_id: int) -> list[PropertyDTO]:
        """Os imóveis do jogador, na ordem em que entraram; vazio sem nenhum."""
        return self._loaded().get(user_id, [])

    def add(self, user_id: int, drafts: list[PropertyDraft]) -> None:
        """Grava imóveis novos, todos alugados no contrato do rascunho."""
        items = self._loaded()
        created = repository.real_estate.insert(self._simulation_id, user_id, drafts)
        items[user_id] = [*items.get(user_id, []), *created]

    def _replace(self, user_id: int, property_id: int, **changes: object) -> None:
        self._loaded()[user_id] = [
            item.model_copy(update=changes) if item.id == property_id else item
            for item in self.of(user_id)
        ]

    def vacate(self, user_id: int, property_id: int, day: date) -> None:
        """O imóvel alugado fica vago desde `day`."""
        repository.real_estate.vacate(property_id, day)
        self._replace(
            user_id,
            property_id,
            status=PropertyStatus.VACANT,
            vacant_since=day,
        )

    def rent(
        self,
        user_id: int,
        property_id: int,
        contract_rent: Decimal,
        contract_start: date,
    ) -> None:
        """O imóvel vago volta ao aluguel num contrato novo."""
        repository.real_estate.rent(property_id, contract_rent, contract_start)
        self._replace(
            user_id,
            property_id,
            status=PropertyStatus.RENTED,
            contract_rent=contract_rent,
            contract_start=contract_start,
            vacant_since=None,
        )

    def put_on_sale(self, user_id: int, property_id: int, due: date) -> None:
        """O imóvel entra em venda, que conclui em `due`."""
        repository.real_estate.put_on_sale(property_id, due)
        self._replace(user_id, property_id, status=PropertyStatus.SELLING, sale_due=due)

    def remove(self, user_id: int, property_ids: list[int]) -> None:
        """Tira os imóveis vendidos da carteira."""
        repository.real_estate.remove(property_ids)
        self._loaded()[user_id] = [
            item for item in self.of(user_id) if item.id not in property_ids
        ]

    def clear(self, user_id: int) -> None:
        """Esvazia a carteira do jogador: a troca de profissão vende tudo."""
        repository.real_estate.clear(self._simulation_id, user_id)
        self._loaded()[user_id] = []
