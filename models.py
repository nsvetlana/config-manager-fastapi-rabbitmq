from pydantic import BaseModel
from typing import Dict, List, Union, Optional

# Запрос для вызова конфигурации (одинаков для обоих сервисов)
class EquipmentConfigRequest(BaseModel):
    timeoutInSeconds: int
    parameters: Dict[str, Union[str, int, List[int]]]

# Ответ сервиса A (stub)
class EquipmentConfigResponse(BaseModel):
    code: int
    message: str

# Ответ при создании задачи (сервис B)
class TaskCreationResponse(BaseModel):
    code: int
    taskId: str

# Ответ для проверки состояния задачи (сервис B)
class TaskStatusResponse(BaseModel):
    code: int
    message: str
