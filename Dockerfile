# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set the working directory in the container
WORKDIR /app

# Enable bytecode compilation and set uv's copy mode
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install project dependencies (dependencies are listed in pyproject.toml and uv.lock)
# Run uv sync with mounting support for faster caching
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy the remaining project sources into the container
ADD . /app

# Install the project (the fourth layer creates the final virtual environment)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Add the path to installed packages (executables will be available in PATH)
ENV PATH="/app/.venv/bin:$PATH"

# Expose ports: 8080 for service A (cpe_locate_service) and 8081 for service B (config_status_service)
EXPOSE 8080 8081

# Reset the ENTRYPOINT to prevent uv from running by default
ENTRYPOINT []
