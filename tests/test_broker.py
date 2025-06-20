import pytest
import asyncio
import json
from broker import publish_message, consume_messages
import aio_pika


# Фейковая реализация обмена сообщений
class FakeExchange:
    async def publish(self, message, routing_key):
        self.last_message = message
        self.last_routing_key = routing_key


# Фейковый канал: declare_queue возвращает FakeQueue с заданным именем.
class FakeChannel:
    async def declare_queue(self, queue_name, durable):
        return FakeQueue(queue_name, [FakeMessage(json.dumps({"fake": "data"}).encode())])

    @property
    def default_exchange(self):
        return FakeExchange()


# Фейковое подключение, возвращающее FakeChannel.
class FakeConnection:
    async def channel(self):
        return FakeChannel()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, tb):
        pass


async def fake_connect_robust(url):
    return FakeConnection()


# Фейковый класс сообщения.
class FakeMessage:
    def __init__(self, body):
        self.body = body

    # Метод process теперь является синхронным и возвращает контекстный менеджер.
    def process(self):
        return FakeMessageContext(self)


# Фейковый контекст для обработки сообщения.
class FakeMessageContext:
    def __init__(self, message):
        self.message = message

    async def __aenter__(self):
        return self.message

    async def __aexit__(self, exc_type, exc, tb):
        pass


# Обновлённый FakeQueueIterator, поддерживающий асинхронный контекстный менеджер.
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


# Обновлённый FakeQueue, который возвращает FakeQueueIterator.
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
    # Если функция завершится без ошибок, тест считается успешным.
    await publish_message(message)


@pytest.mark.asyncio
async def test_consume_messages(monkeypatch):
    monkeypatch.setattr(aio_pika, "connect_robust", fake_connect_robust)
    collected = []

    async def test_callback(data):
        collected.append(data)

    await consume_messages(test_callback)
    # Ожидаем, что фейковое сообщение будет содержать данные {"fake": "data"}
    assert collected == [{"fake": "data"}]
