# cpe_locate_service.py
import re
import time
import logging
from fastapi import FastAPI, HTTPException, Path
from models import EquipmentConfigRequest, EquipmentConfigResponse

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cpe_locate_service")

app = FastAPI(title="cpe-locate-service")

# Регулярное выражение для проверки серийного номера устройства
DEVICE_ID_REGEX = re.compile(r"^[a-zA-Z0-9]{6,}$")

@app.post("/api/v1/equipment/cpe/{id}", response_model=EquipmentConfigResponse)
def configure_equipment(
        id: str = Path(...),
        payload: EquipmentConfigRequest | None = None,
):
    """
    Принимает запрос конфигурации для устройства.
    Если идентификатор не соответствует шаблону, выбрасывается исключение с кодом 404.
    Иначе производится имитация конфигурации с ожиданием.
    """
    logger.info(f"Service A: Получен запрос для {id} с данными: {payload}")

    # Если id не соответствует шаблону, выбрасываем исключение HTTP 404
    if not re.fullmatch(DEVICE_ID_REGEX, id):
        logger.error(f"Service A: Устройство {id} не найдено.")
        raise HTTPException(status_code=404, detail="The requested equipment is not found")

    try:
        time.sleep(60)
    except Exception as e:
        logger.exception("Service A: Ошибка при эмуляции работы")
        raise HTTPException(status_code=500, detail="Internal provisioning exception")

    logger.info(f"Service A: Конфигурация для {id} выполнена успешно.")
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
