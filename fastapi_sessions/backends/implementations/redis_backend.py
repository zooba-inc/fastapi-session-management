from typing import Generic, cast
from redis.client import Redis

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
        if await self._connect.get(str(session_id)):
            raise BackendError("create can't overwrite an existing session")

        await self._connect.set(str(session_id), data.model_dump_json())

    async def read(self, session_id: ID):
        """Read an existing session data."""
        data = await self._connect.get(str(session_id))
        if not data:
            return
        data = cast(bytes, data)
        model = self._cls.model_validate_json(data)
        return model

    async def update(self, session_id: ID, data: SessionModel) -> None:
        """Update an existing session."""
        if await self._connect.get(str(session_id)):
            await self._connect.set(str(session_id), data.model_dump_json())
        else:
            raise BackendError("session does not exist, cannot update")

    async def delete(self, session_id: ID) -> None:
        """Delete"""
        await self._connect.delete(str(session_id))
