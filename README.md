
# Distributed Configuration System

This project implements a distributed configuration system that consists of several components:

- **Service A (cpe_locate_service):**  
  A synchronous HTTPS service that provides an endpoint for device configuration. It simulates a long-running 
  configuration process by pausing (60 seconds delay) before responding with success or an error message.

- **Service B (config_status_service):**  
  An asynchronous HTTPS service for managing configuration tasks. It provides a POST endpoint to create a configuration 
  task and a GET endpoint to check the status of a task. The service stores task data in an in‑memory datastore and 
  publishes tasks to a RabbitMQ queue.

- **Worker (task_messenger):**  
  A background worker that consumes messages from RabbitMQ, calls Service A to actually perform the configuration, and 
 then updates the task status accordingly.

- **Broker (broker.py):**  
  Contains functions for publishing and consuming messages via RabbitMQ (using [aio-pika](https://aio-pika.readthedocs.io)) 
  as well as managing the in‑memory storage for tasks (`tasks_db`).

All HTTP services support HTTPS using self‑signed certificates (`cert.pem` and `key.pem`). The provided mock 
certificates are for local development and testing only—they are not suitable for production use!

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed.
- (Optional) Python 3.12 if you wish to run components locally.
- (Optional) OpenSSL if you need to generate your own self‑signed certificates.

---

## Automatic Certificate Generation via Docker Compose

Instead of manually generating self‑signed certificates and placing them in the project root, this project leverages 
an automated process using Docker Compose. The openssl service defined in compose.yaml is based on Alpine Linux and 
performs the following actions during startup:

Certificate Check: The service checks if a certificate file (cert.pem) exists in the mounted ./private volume.

Automatic Generation: If the certificate is missing, the service installs OpenSSL inside the container and runs a command 
to generate a new self‑signed certificate and key using a 4096‑bit RSA key. The generated certificate is valid for 365 days 
and is assigned the subject /CN=localhost.

Graceful Exit: If the certificate already exists, the service simply logs that no generation is needed and exits successfully.
---
This automated process ensures that your HTTPS services (cpe_locate_service and config_status_service) always have access 
to the required certificates without manual intervention.

## Building the Docker Image

A Dockerfile is provided that uses a pre‑configured Python image (with `uv` pre‑installed) and installs the project alongside 
the certificate files. To build the Docker image, run the following command from the project root:

```bash
docker build -t config-manager-fastapi-rabbitmq .
```

---

## Running the Project with Docker Compose

A `compose.yaml` file is included to orchestrate all components of the project. This file sets up the following services:

- **RabbitMQ:** Uses the official image with management UI on ports 5672 (AMQP) and 15672 (UI).
- **Service A (cpe_locate_service):** Runs on HTTPS port 8080.
- **Service B (config_status_service):** Runs on HTTPS port 8081 and provides endpoints to create configuration tasks 
  and to check task status.
- **Worker (task_messenger):** A background process that consumes RabbitMQ messages and invokes Service A.

To start all services, run:

```bash
docker-compose up --build
```

After startup, you can access the endpoints:

- **Service A:** `https://<host>:8080/api/v1/equipment/cpe/{id}`
- **Service B (Create configuration task):** `https://<host>:8081/api/v1/equipment/cpe/{id}`
- **Service B (Check task status):** `https://<host>:8081/api/v1/equipment/cpe/{id}/task/{task}`

> **Note:** Replace `<host>` with `localhost` or your machine’s IP address if accessing externally.

---

## Running Tests

Unit tests are provided for all major components (Service A, Service B, Task Messenger, and Broker). To run the tests:

1. Ensure you have Python 3.12 and the required dependencies installed (e.g., `pytest`, `pytest-asyncio`).
2. From the project root, run:

```bash
pytest
```

This command will execute all tests located in the `tests/` directory.

---

## Additional Notes

- **HTTPS for Production:** Replace self‑signed certificates with ones issued by a trusted Certificate Authority (such 
  as via Let's Encrypt) or use a reverse proxy (like Nginx) for TLS termination when deploying in production.
- **Persistent Storage:** The project uses in‑memory storage (i.e., `tasks_db`). For production scenarios, consider 
  integrating persistent storage (e.g., a database or Redis).
- **Modularity and Scaling:** Each service runs in its own Docker container. You can scale or update individual 
  components as needed.

---

## Contact

For issues or feature requests, please open an issue in the repository.

Enjoy working with the project and happy coding!

---

This file provides a detailed, step‑by‑step guide to building, running, and testing the project using Docker and Docker 
Compose, along with instructions for generating self‑signed certificates.