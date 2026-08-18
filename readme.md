# Task CRUD API (PostgreSQL + Docker Compose)

A RESTful CRUD API built with FastAPI and containerized with Docker & PostgreSQL. Built for Week 3 Assignment 3 of the FlyRank AI Fluency backend track to demonstrate storage swapping (**In-Memory → SQLite → PostgreSQL in Docker**) while keeping HTTP routes strictly unchanged.

---

## How to Launch the Full Stack

### Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### 1. Environment Setup

Copy `.env.example` to create your local `.env` file:

```bash
cp .env.example .env
```

### 2. Run Single Command Stack Launch

```bash
docker compose up --build
```

* **Base Service URL:** `http://localhost:8000`
* **Interactive Swagger Documentation:** `http://localhost:8000/docs`

---

## Architectural Integrity

As per assignment constraints, **routes and service handlers in `main.py` remained 100% unchanged**.

Only the repository persistence layer (`database.py`) was modified to execute parameterized SQL against a containerized PostgreSQL instance.

---

## Proof of Data Persistence Across Container Restarts

### 1. Insert Record via `curl`

```bash
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Docker Volume Persistence Test"}'
```

**Response ID:** `4`

---

### 2. Destroy Containers

```bash
docker compose down
```

---

### 3. Re-launch Containers

```bash
docker compose up -d
```

---

### 4. Verify Data Retrieval Post-Restart

```bash
curl -i http://localhost:8000/tasks/4
```

**Outcome:** Returns task `4` with status `200 OK`. Data persisted safely inside the named Docker volume `postgres_data`.
