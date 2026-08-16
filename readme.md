# Task CRUD API (SQLite Persistence Engine)

A RESTful CRUD API built with Python and FastAPI for managing tasks. Built for Week 3 of the FlyRank AI Fluency backend track to demonstrate migrating from an in-memory storage array to an embedded SQLite database (`tasks.db`) while keeping external API endpoints completely unchanged.

---

## How to Run Locally

### Prerequisites

* Python 3.10+
* `pip` package manager

### 1. Install Dependencies

```bash
pip install fastapi uvicorn pydantic
```

### 2. Start the Server

```bash
python -m uvicorn main:app --reload
```

* **Base Service URL:** `http://127.0.0.1:8000`
* **Interactive Documentation (Swagger UI):** `http://127.0.0.1:8000/docs`

---

## API Endpoints Matrix

| Method | Endpoint      | Description                                              | Expected Request Body                | Success Status   | Error Status                       |
| ------ | ------------- | -------------------------------------------------------- | ------------------------------------ | ---------------- | ---------------------------------- |
| GET    | `/`           | API Metadata & Storage Engine Info                       | None                                 | `200 OK`         | -                                  |
| GET    | `/health`     | Server Pulse & Database Connection Check                 | None                                 | `200 OK`         | -                                  |
| GET    | `/stats`      | Task Statistics via SQL `COUNT()`                        | None                                 | `200 OK`         | -                                  |
| GET    | `/tasks`      | List Tasks (Supports `done` & `search` query parameters) | None                                 | `200 OK`         | -                                  |
| GET    | `/tasks/{id}` | Fetch Single Task Record by ID                           | None                                 | `200 OK`         | `404 Not Found`                    |
| POST   | `/tasks`      | Create Task Record (SQL `INSERT`)                        | `{"title": "Buy groceries"}`         | `201 Created`    | `400 Bad Request`                  |
| PUT    | `/tasks/{id}` | Update Task Record (SQL `UPDATE`)                        | `{"title": "Updated", "done": true}` | `200 OK`         | `400 Bad Request`, `404 Not Found` |
| DELETE | `/tasks/{id}` | Delete Task Record (SQL `DELETE`)                        | None                                 | `204 No Content` | `404 Not Found`                    |

---

## SQLite Database Engine Integration

### Storage Architecture

* **Database Engine:** Embedded SQLite3
* **Database File:** `tasks.db` (automatically generated on application startup)
* **Table Schema Definition:**

```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT 0
);
```

### Key Architectural Rationale

SQLite is a serverless, zero-configuration relational database engine that stores all data directly in a single disk file (`tasks.db`). By integrating Python's native `sqlite3` module, application state now persists across process terminations and server restarts without altering the consumer-facing REST contract.

### Direct SQL Exploration (Stage 4 Analysis)

Verified via DB Browser for SQLite:

* **Fetch All Records:** `SELECT * FROM tasks;`
* **Filter Completed Tasks:** `SELECT * FROM tasks WHERE done = 1;`
* **Aggregate Task Count:** `SELECT COUNT(*) FROM tasks;`
* **Bulk Complete All:** `UPDATE tasks SET done = 1;`
* **Delete Completed:** `DELETE FROM tasks WHERE done = 1;`

---

## Terminal Verification (`curl -i`)

A task was created successfully using `curl`:

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Persistent DB Task"}'
```

Expected response:

```text
HTTP/1.1 201 Created
date: Sun, 16 Aug 2026 19:30:00 GMT
server: uvicorn
content-type: application/json
```

```json
{
  "id": 1,
  "title": "Persistent DB Task",
  "done": false
}
```
