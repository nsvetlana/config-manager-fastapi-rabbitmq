import pytest
import asyncio
import json
from broker import publish_message, consume_messages
import aio_pika


# Fake implementation of message exchange
class FakeExchange:
    async def publish(self, message, routing_key):
        self.last_message = message
        self.last_routing_key = routing_key


# Fake channel: declare_queue returns a FakeQueue with the given name.
class FakeChannel:
    async def declare_queue(self, queue_name, durable):
        return FakeQueue(queue_name, [FakeMessage(json.dumps({"fake": "data"}).encode())])

    @property
    def default_exchange(self):
        return FakeExchange()


# Fake connection, returning a FakeChannel.
class FakeConnection:
    async def channel(self):
        return FakeChannel()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, tb):
        pass


async def fake_connect_robust(url):
    return FakeConnection()


# Fake message class.
class FakeMessage:
    def __init__(self, body):
        self.body = body

    # The process method is now synchronous and returns a context manager.
    def process(self):
        return FakeMessageContext(self)


# Fake context manager for processing a message.
class FakeMessageContext:
    def __init__(self, message):
        self.message = message

    async def __aenter__(self):
        return self.message

    async def __aexit__(self, exc_type, exc, tb):
        pass


# Updated FakeQueueIterator supporting an asynchronous context manager.
class FakeQueueIterator:
    def __init__(self, messages):
        self._messages = messages.copy()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._messages:
            return self._messages.pop(0)
        raise StopAsyncIteration


# Updated FakeQueue that returns a FakeQueueIterator.
class FakeQueue:
    def __init__(self, name, messages):
        self.name = name
        self._messages = messages

    def iterator(self):
        return FakeQueueIterator(self._messages)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, tb):
        pass


@pytest.mark.asyncio
async def test_publish_message(monkeypatch):
    monkeypatch.setattr(aio_pika, "connect_robust", fake_connect_robust)
    message = {"task_id": "test", "equipment_id": "ABC123", "task_payload": {}}
    # If the function completes without errors, the test is considered successful.
    await publish_message(message)


@pytest.mark.asyncio
async def test_consume_messages(monkeypatch):
    monkeypatch.setattr(aio_pika, "connect_robust", fake_connect_robust)
    collected = []

    async def test_callback(data):
        collected.append(data)

    await consume_messages(test_callback)
    # Expect that the fake message will contain data {"fake": "data"}
    assert collected == [{"fake": "data"}]
