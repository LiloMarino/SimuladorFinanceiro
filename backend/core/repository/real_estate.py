from datetime import date
from decimal import Decimal

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.real_estate import PropertyDraft, PropertyDTO
from backend.core.enum import PropertyStatus
from backend.core.models.models import RealEstateProperties


class RealEstateRepository:
    @transactional
    def of_simulation(
        self, session: Session, simulation_id: int
    ) -> dict[int, list[PropertyDTO]]:
        """Os imóveis de cada jogador da partida, na ordem em que entraram."""
        rows = session.scalars(
            select(RealEstateProperties)
            .where(RealEstateProperties.simulation_id == simulation_id)
            .order_by(RealEstateProperties.id)
        )
        properties: dict[int, list[PropertyDTO]] = {}
        for row in rows:
            properties.setdefault(row.user_id, []).append(
                PropertyDTO.model_validate(row)
            )
        return properties

    @transactional
    def insert(
        self,
        session: Session,
        simulation_id: int,
        user_id: int,
        drafts: list[PropertyDraft],
    ) -> list[PropertyDTO]:
        """Grava os imóveis novos do jogador, todos alugados no contrato que o rascunho traz."""
        rows = [
            RealEstateProperties(
                simulation_id=simulation_id,
                user_id=user_id,
                size=draft.size.value,
                name=draft.name,
                base_price=draft.base_price,
                offer_month=draft.offer_month,
                contract_rent=draft.contract_rent,
                contract_start=draft.contract_start,
                status=PropertyStatus.RENTED.value,
            )
            for draft in drafts
        ]
        session.add_all(rows)
        session.flush()
        return [PropertyDTO.model_validate(row) for row in rows]

    @transactional
    def rent(
        self,
        session: Session,
        property_id: int,
        contract_rent: Decimal,
        contract_start: date,
    ) -> None:
        """O imóvel vago volta ao aluguel num contrato novo."""
        session.execute(
            update(RealEstateProperties)
            .where(RealEstateProperties.id == property_id)
            .values(
                status=PropertyStatus.RENTED.value,
                contract_rent=contract_rent,
                contract_start=contract_start,
                vacant_since=None,
            )
        )

    @transactional
    def vacate(self, session: Session, property_id: int, day: date) -> None:
        """O imóvel alugado fica vago desde `day`."""
        session.execute(
            update(RealEstateProperties)
            .where(RealEstateProperties.id == property_id)
            .values(status=PropertyStatus.VACANT.value, vacant_since=day)
        )

    @transactional
    def put_on_sale(self, session: Session, property_id: int, due: date) -> None:
        """O imóvel entra em venda, que conclui em `due`."""
        session.execute(
            update(RealEstateProperties)
            .where(RealEstateProperties.id == property_id)
            .values(status=PropertyStatus.SELLING.value, sale_due=due)
        )

    @transactional
    def remove(self, session: Session, property_ids: list[int]) -> None:
        """Tira os imóveis vendidos da carteira."""
        session.execute(
            delete(RealEstateProperties).where(
                RealEstateProperties.id.in_(property_ids)
            )
        )

    @transactional
    def clear(self, session: Session, simulation_id: int, user_id: int) -> None:
        """Esvazia a carteira de imóveis do jogador: a troca de profissão vende tudo."""
        session.execute(
            delete(RealEstateProperties).where(
                RealEstateProperties.simulation_id == simulation_id,
                RealEstateProperties.user_id == user_id,
            )
        )
