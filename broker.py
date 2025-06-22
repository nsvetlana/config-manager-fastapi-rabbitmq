import asyncio
import json
import aio_pika

# In-memory storage for tasks
tasks_db = {}

# URL to connect to RabbitMQ
import os
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq")


# Queue name for configuration tasks
QUEUE_NAME = "config_tasks"


async def publish_message(message: dict):
    """
    Publishes a message to the RabbitMQ queue.
    """
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    try:
        async with connection:
            channel = await connection.channel()
            # Declare the queue (durable – the queue is preserved when the server restarts)
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
    Consumes messages from the RabbitMQ queue and calls the callback with the message data.
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
