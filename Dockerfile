# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Включаем компиляцию байткода и задаём режим копирования для uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Устанавливаем зависимости проекта (зависимости прописаны в pyproject.toml и uv.lock)
# Выполняем uv sync с поддержкой монтирований для более быстрого кэширования
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Копируем оставшиеся исходники проекта в контейнер
ADD . /app

# Устанавливаем проект (четвертый слой создаёт окончательный виртуальный env)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Добавляем путь к установленным пакетам (исполняемые файлы будут доступны в PATH)
ENV PATH="/app/.venv/bin:$PATH"

# Открываем порты: 8080 для сервиса A (cpe_locate_service) и 8081 для сервиса B (config_status_service)
EXPOSE 8080 8081

# Копируем сертификаты в контейнер (ключ и сертификат должны находиться рядом с Dockerfile)
COPY cert.pem key.pem ./

# Сбрасываем ENTRYPOINT, чтобы не вызывать uv по умолчанию
ENTRYPOINT []

# По умолчанию запускаем сервис B (config_status_service) с поддержкой HTTPS
CMD ["uvicorn", "config_status_service:app", "--host", "0.0.0.0", "--port", "8081", "--ssl-keyfile", "key.pem", "--ssl-certfile", "cert.pem", "--reload"]
