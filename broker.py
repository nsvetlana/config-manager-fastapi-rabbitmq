
import asyncio
import json
import aio_pika

# In-memory хранилище для задач
tasks_db = {}

# URL для подключения к RabbitMQ
RABBITMQ_URL = "amqp://guest:guest@localhost/"

# Имя очереди для задач конфигурации
QUEUE_NAME = "config_tasks"


async def publish_message(message: dict):
    """
    Публикует сообщение в очередь RabbitMQ.
    """
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    try:
        async with connection:
            channel = await connection.channel()
            # Объявляем очередь (durable – очередь сохраняется при рестарте сервера)
            queue = await channel.declare_queue(QUEUE_NAME, durable=True)
            body = json.dumps(message).encode()
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=queue.name,
            )
    except Exception as e:
        print(f"Error publishing message to RabbitMQ: {e}")
        raise


async def consume_messages(callback):
    """
    Потребляет сообщения из очереди RabbitMQ и вызывает callback с данными сообщения.
    """
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    data = json.loads(message.body.decode())
                    await callback(data)
                except Exception as e:
                    print(f"Error processing message: {e}")
