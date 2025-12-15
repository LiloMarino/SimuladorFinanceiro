from backend.core.dto.events.base_event import BaseEventDTO


class EventRepository:
    def insert_many(self, events: list[BaseEventDTO]):
        raise NotImplementedError
