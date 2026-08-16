# Task CRUD API (FastAPI)

A lightweight RESTful CRUD API built with Python and FastAPI for managing to-do tasks.

Built for **Week 2 of the AI Fluency backend track** to demonstrate:

* HTTP request-response cycles
* HTTP status codes
* Input validation
* RESTful CRUD operations
* Automated OpenAPI documentation with Swagger UI

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

**Base URL:** `http://127.0.0.1:8000`

**Interactive Swagger UI:**
http://127.0.0.1:8000/docs

---

## API Endpoints

| Method | Endpoint      | Description                           | Expected Body                    | Success Status   | Error Status                       |
| ------ | ------------- | ------------------------------------- | -------------------------------- | ---------------- | ---------------------------------- |
| GET    | `/`           | API Metadata & Routes                 | None                             | `200 OK`         | -                                  |
| GET    | `/health`     | Server Health Status                  | None                             | `200 OK`         | -                                  |
| GET    | `/stats`      | Task Counts (Total/Done/Open)         | None                             | `200 OK`         | -                                  |
| GET    | `/tasks`      | List Tasks (Optional `done`/`search`) | None                             | `200 OK`         | -                                  |
| GET    | `/tasks/{id}` | Get Single Task by ID                 | None                             | `200 OK`         | `404 Not Found`                    |
| POST   | `/tasks`      | Create New Task                       | `{"title": "Buy milk"}`          | `201 Created`    | `400 Bad Request`                  |
| PUT    | `/tasks/{id}` | Update Task                           | `{"title": "New", "done": true}` | `200 OK`         | `400 Bad Request`, `404 Not Found` |
| DELETE | `/tasks/{id}` | Delete Task                           | None                             | `204 No Content` | `404 Not Found`                    |
| POST   | `/reset`      | Reset DB to 3 initial seed items      | None                             | `200 OK`         | -                                  |

---

## Terminal Verification

The API can be tested from the terminal using `curl`.

### Create a Task

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Complete Week 2 Assignment"}'
```

Expected response:

```text
HTTP/1.1 201 Created
date: Sun, 16 Aug 2026 17:00:00 GMT
server: uvicorn
content-type: application/json
```

```json
{
  "id": 4,
  "title": "Complete Week 2 Assignment",
  "done": false
}
```

---

## In-Memory Persistence Experiment

### Observation

When new tasks are created and the Uvicorn server is restarted using:

```text
Ctrl+C
```

followed by:

```bash
python -m uvicorn main:app --reload
```

all newly created tasks disappear, and the application returns to the initial **3 seed tasks**.

### Why Does This Happen?

The application stores its data in a volatile Python list called:

```python
tasks_db
```

This list exists only in the computer's **RAM (memory)** while the Python process is running.

When the server process stops:

1. The Python process terminates.
2. The `tasks_db` list is destroyed.
3. All newly created tasks are lost.
4. When the server starts again, the original seed data is created.

This demonstrates why real-world applications require **persistent storage** such as:

* SQL databases
* NoSQL databases
* Other persistent storage engines

---

# Stage 7 — AI Rematch ("AI vs Me")

## Full Prompt Used

```text
Write a single-file Python REST API using FastAPI that manages an in-memory task to-do list. Implement GET /, GET /health, GET /tasks, GET /tasks/{id} (404 if missing), POST /tasks (generates next ID, validates non-empty title returning 400 Bad Request, sets default done=False), PUT /tasks/{id} (updates title/done, returns 400 or 404), and DELETE /tasks/{id} (returns 204 No Content). Ensure Swagger UI is available at /docs.
```

---

## Code Comparison & Findings

### What the AI Did Better

The AI used Pydantic's:

```python
Field(min_length=1)
```

for declarative validation directly inside the request model.

This provides a clean way to prevent completely empty strings from being submitted.

---

### What the AI Got Wrong / Ignored

#### 1. Whitespace Bypass

The AI accepted whitespace-only strings such as:

```text
"   "
```

as valid task titles.

Although `min_length=1` rejects an actually empty string, whitespace characters still count toward the length.

### Fix

Manual string stripping was required:

```python
payload.title.strip()
```

This ensures that a title containing only whitespace is rejected.

---

#### 2. HTTP 204 Protocol Violation

The AI returned:

```json
{
  "message": "Task deleted"
}
```

alongside:

```text
204 No Content
```

This is incorrect.

A `204 No Content` response must not contain a response body.

### Correct Behavior

The DELETE endpoint should return only:

```text
204 No Content
```

with no JSON response body.

---

## What the Prompt Was Missing

The original prompt did not explicitly specify how new task IDs should be generated.

The AI used:

```python
len(tasks_db) + 1
```

This can create duplicate IDs.

### Example

Suppose the database contains:

```text
1
2
3
```

If task `3` is deleted, the database now contains:

```text
1
2
```

Using:

```python
len(tasks_db) + 1
```

would generate:

```text
3
```

which happens to work in this case.

But if an earlier ID is deleted:

```text
1
3
4
```

then:

```python
len(tasks_db) + 1
```

would produce:

```text
4
```

which is already being used.

### Fix

The ID-generation logic was updated to:

```python
max(existing_ids) + 1
```

This generates the next ID based on the highest existing ID rather than the number of tasks currently stored.

---

## Key Learning Outcomes

This project demonstrates practical backend concepts including:

* REST API architecture
* FastAPI routing
* HTTP methods
* HTTP status codes
* CRUD operations
* Pydantic validation
* Swagger / OpenAPI documentation
* In-memory data storage
* API testing with `curl`
* Server lifecycle and data persistence
* AI-generated code evaluation
* Identifying and fixing AI coding mistakes

---

## Project Status

**Week 2 — AI Fluency Backend Track**

**Technology:** Python + FastAPI + Pydantic + Uvicorn

**Storage:** In-memory Python list

**Documentation:** OpenAPI / Swagger UI
