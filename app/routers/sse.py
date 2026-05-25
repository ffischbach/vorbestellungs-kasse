import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter()


class EventBroadcaster:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[dict[str, object]]] = set()

    async def subscribe(self) -> asyncio.Queue[dict[str, object]]:
        queue: asyncio.Queue[dict[str, object]] = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, object]]) -> None:
        self._subscribers.discard(queue)

    async def broadcast(self, event: dict[str, object]) -> None:
        for queue in list(self._subscribers):
            await queue.put(event)


broadcaster = EventBroadcaster()


async def _event_stream(
    queue: asyncio.Queue[dict[str, object]],
) -> AsyncGenerator[str, None]:
    try:
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
    except asyncio.CancelledError:
        pass


@router.get("/events")
async def sse_events() -> StreamingResponse:
    queue = await broadcaster.subscribe()

    async def stream() -> AsyncGenerator[str, None]:
        try:
            async for chunk in _event_stream(queue):
                yield chunk
        finally:
            broadcaster.unsubscribe(queue)

    return StreamingResponse(stream(), media_type="text/event-stream")
