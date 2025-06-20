import re
import time
import logging
from fastapi import FastAPI, HTTPException, Path
from models import EquipmentConfigRequest, EquipmentConfigResponse

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cpe_locate_service")

app = FastAPI(title="cpe-locate-service")

# Regular expression to validate the device serial number
DEVICE_ID_REGEX = re.compile(r"^[a-zA-Z0-9]{6,}$")

@app.post("/api/v1/equipment/cpe/{id}", response_model=EquipmentConfigResponse)
def configure_equipment(
        id: str = Path(...),
        payload: EquipmentConfigRequest | None = None,
):
    """
    Receives a configuration request for a device.
    If the identifier does not match the pattern, a 404 exception is raised.
    Otherwise, it simulates configuration with a delay.
    """
    logger.info(f"Service A: Received request for {id} with data: {payload}")

    # If the id does not match the pattern, raise an HTTP 404 exception
    if not re.fullmatch(DEVICE_ID_REGEX, id):
        logger.error(f"Service A: Device {id} not found.")
        raise HTTPException(status_code=404, detail="The requested equipment is not found")

    try:
        time.sleep(60)
    except Exception as e:
        logger.exception("Service A: Error during simulation")
        raise HTTPException(status_code=500, detail="Internal provisioning exception")

    logger.info(f"Service A: Configuration for {id} completed successfully.")
    return EquipmentConfigResponse(code=200, message="success")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem",
    )
