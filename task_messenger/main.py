
import asyncio
import httpx
from broker import consume_messages, tasks_db

async def process_task(task_data):
    task_id = task_data["task_id"]
    equipment_id = task_data["equipment_id"]
    task_payload = task_data["task_payload"]

    try:
        # Предполагается, что сервис A доступен по HTTPS на 8080
        async with httpx.AsyncClient(verify="cert.pem") as client:
            response = await client.post(
                f"https://localhost:8080/api/v1/equipment/cpe/{equipment_id}",
                json=task_payload,
            )
            response_json = response.json()
    except Exception as e:
        tasks_db[task_id]["status"] = "failed"
        print(f"Task {task_id} failed: {e}")
        return

    tasks_db[task_id]["status"] = "completed"
    print(f"Task {task_id} completed with response: {response_json}")

async def on_message(data):
    # Запускаем обработку задачи в отдельной корутине для параллельной обработки
    asyncio.create_task(process_task(data))

async def main():
    await consume_messages(on_message)

if __name__ == "__main__":
    asyncio.run(main())
