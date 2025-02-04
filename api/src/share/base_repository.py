from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from uuid import UUID

T = TypeVar("T")  # Model type


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def get_by_id(self, db_session, id: UUID, user_id: UUID) -> Optional[T]:
        pass

    @abstractmethod
    def get_all(self, db_session, user_id: UUID) -> List[T]:
        pass

    @abstractmethod
    def create(self, db_session, obj: T) -> T:
        pass

    @abstractmethod
    def update(self, db_session, id: UUID, obj: T, user_id: UUID) -> T:
        pass

    @abstractmethod
    def delete(self, db_session, id: UUID, user_id: UUID) -> None:
        pass
