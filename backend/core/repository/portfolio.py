class PortfolioRepository:
    def get_portfolio(client_id: str) -> PortfolioDTO:
        pass

    def get_equity_positions(client_id: str) -> list[PositionDTO]:
        pass

    def get_fixed_income_positions(client_id: str) -> list[PositionDTO]:
        pass
