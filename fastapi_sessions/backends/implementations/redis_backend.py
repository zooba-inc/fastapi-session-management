from uuid import UUID, uuid4

from pydantic import BaseModel
from typing import List, Generic
from redis.client import Redis
import json

from fastapi_sessions.backends.session_backend import ( # noqa
    BackendError,
    SessionBackend,
    SessionModel,
)
from fastapi_sessions.frontends.session_frontend import ID # noqa


class InRedisBackend(Generic[ID, SessionModel], SessionBackend[ID, SessionModel]):
    """Stores session data in a dictionary."""

    def __init__(self, connect: Redis, cls: SessionModel) -> None:
        """
        Initialize a new in-redis database.
            Parameters:
                connect (Redis): open connection with redis
                cls (SessionModel): actual model for session data
        """
        self._connect = connect
        self._cls = cls

    async def create(self, session_id: ID, data: SessionModel):
        """Create a new session entry."""
        if self._connect.get(str(session_id)):
            raise BackendError("create can't overwrite an existing session")

        self._connect.set(str(session_id), data.json())

    async def read(self, session_id: ID):
        """Read an existing session data."""
        data = self._connect.get(str(session_id))
        if not data:
            return

        model = self._cls(**json.loads(data))
        return model

    async def update(self, session_id: ID, data: SessionModel) -> None:
        """Update an existing session."""
        if self._connect.get(str(session_id)):
            self._connect.set(str(session_id), data.json())
        else:
            raise BackendError("session does not exist, cannot update")

    async def delete(self, session_id: ID) -> None:
        """Delete"""
        self._connect.delete(str(session_id))
