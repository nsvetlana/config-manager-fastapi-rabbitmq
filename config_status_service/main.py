import uuid
import re
from fastapi import FastAPI, HTTPException, Path
from models import EquipmentConfigRequest, TaskCreationResponse, TaskStatusResponse
from broker import publish_message, tasks_db  # Import the publish function and in-memory storage

app = FastAPI(title="config_status_service")

DEVICE_ID_REGEX = re.compile(r"^[a-zA-Z0-9]{6,}$")

@app.post("/api/v1/equipment/cpe/{id}", response_model=TaskCreationResponse)
async def create_config_task(
        id: str = Path(...),
        req: EquipmentConfigRequest = ...,
):
    if not DEVICE_ID_REGEX.match(id):
        raise HTTPException(status_code=404, detail="The requested equipment is not found")

    # Generate a unique task identifier
    task_id = str(uuid.uuid4())
    # Save the task in in-memory storage
    tasks_db[task_id] = {
        "equipment_id": id,
        "parameters": req.dict(),
        "status": "running",  # Initial status – running
    }
    # Publishing a message to a RabbitMQ queue
    await publish_message({
        "task_id": task_id,
        "equipment_id": id,
        "task_payload": req.dict()
    })

    return TaskCreationResponse(code=200, taskId=task_id)

@app.get("/api/v1/equipment/cpe/{id}/task/{task}", response_model=TaskStatusResponse)
async def get_task_status(
        id: str = Path(...),
        task: str = ...,
):
    if not DEVICE_ID_REGEX.match(id):
        raise HTTPException(status_code=404, detail="The requested equipment is not found")

    if task not in tasks_db:
        raise HTTPException(status_code=404, detail="The requested task is not found")

    task_info = tasks_db[task]
    if task_info["status"] == "running":
        return TaskStatusResponse(code=204, message="Task is still running")
    elif task_info["status"] == "completed":
        return TaskStatusResponse(code=200, message="Completed")
    else:
        return TaskStatusResponse(code=500, message="Internal provisioning exception")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="localhost",
        port=8081,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem",
    )


# Launch via uvicorn::
# uvicorn config_status_service:app --host 0.0.0.0 --port 8081 --ssl-keyfile=... --ssl-certfile=...
