"""As federações como o jogador vê: a federação, a proposta, a prévia e as opções de parceiro."""

from datetime import date, timedelta
from decimal import Decimal

from backend.core.dto.government import (
    FederationDTO,
    FederationOptionDTO,
    FederationPreviewDTO,
    FederationProposalDTO,
    FederationRejectionDTO,
)
from backend.core.enum import FederationStatus
from backend.features.government import federations, house
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import Party


def _seats(book: GovernmentBook, today: date) -> dict[int, int]:
    """As cadeiras de cada partido na Câmara de hoje."""
    return {
        b.party_id: b.seats
        for b in book.state.house_on(today).blocs
        if b.party_id is not None
    }


def federation_dto(
    book: GovernmentBook, federation: federations.Federation, today: date
) -> FederationDTO:
    leader = book.state.parties[federation.candidate_party_id]
    seats = _seats(book, today)
    return FederationDTO(
        id=federation.id,
        name=federation.name,
        parties=list(federation.parties),
        candidate_party_id=leader.id,
        candidate=book.candidate_name(leader, federation.candidate_id),
        election_year=book.cycle(federation.cycle).first_round.year,
        formed_on=federation.formed_on,
        in_force_from=federation.in_force_from,
        ends_on=federation.ends_on,
        orienting_party_id=federations.orientation_party(federation.parties, seats),
    )


def standing_federations(book: GovernmentBook, today: date) -> list[FederationDTO]:
    """As federações de pé: em vigor ou agendadas para a posse."""
    return [
        federation_dto(book, f, today)
        for f in sorted(book.state.federations.values(), key=lambda f: f.id)
        if f.status is FederationStatus.ACTIVE and f.ends_on >= today
    ]


def congress_federations(book: GovernmentBook, today: date) -> list[FederationDTO]:
    """As federações cuja lista vale no Congresso de hoje."""
    return [
        federation_dto(book, f, today)
        for f in sorted(book.state.congress_federations(today), key=lambda f: f.id)
    ]


def proposal_dto(
    book: GovernmentBook, proposal: federations.FederationProposal, today: date
) -> FederationProposalDTO:
    leader = book.state.parties[proposal.candidate_party_id]
    seats = _seats(book, today)
    return FederationProposalDTO(
        id=proposal.id,
        from_party_id=proposal.from_party_id,
        to_party_id=proposal.to_party_id,
        name=proposal.name,
        candidate_party_id=leader.id,
        candidate=book.candidate_name(leader, proposal.candidate_id),
        election_year=book.cycle(proposal.cycle).first_round.year,
        sent_on=proposal.sent_on,
        expires_on=proposal.expires_on,
        ends_on=book.cycle(proposal.cycle + 1).inauguration - timedelta(days=1),
        orienting_party_id=federations.orientation_party(
            (proposal.from_party_id, proposal.to_party_id), seats
        ),
    )


def options(
    book: GovernmentBook, mine: Party, today: date
) -> list[FederationOptionDTO]:
    """Cada outro partido, com o motivo de não poder se federar hoje e se sozinho ficaria abaixo da barreira."""
    shares = book.house_shares()
    return [
        FederationOptionDTO(
            party_id=other.id,
            blocked=book.federation_blocker(mine, other, today),
            below_barrier=shares.get(book.house_key(other), Decimal(0)) < house.BARRIER,
        )
        for other in sorted(book.state.parties.values(), key=lambda p: p.id)
        if other.id != mine.id
    ]


def preview_dto(
    book: GovernmentBook, preview: federations.Preview
) -> FederationPreviewDTO:
    return FederationPreviewDTO(
        election_year=book.cycle(preview.cycle).first_round.year,
        own_share=preview.own_share,
        partner_share=preview.partner_share,
        barrier=preview.barrier,
        orienting_party_id=preview.orienting_party_id,
        leaving_promises=preview.leaving_promises,
        own_budget=preview.own_budget,
        partner_budget=preview.partner_budget,
        in_force_from=preview.in_force_from,
        ends_on=preview.ends_on,
        answer_until=preview.answer_until,
        rejection=[
            FederationRejectionDTO(
                group=r.group, own=r.own, partner=r.partner, federated=r.federated
            )
            for r in preview.rejection
        ],
    )
