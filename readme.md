# 🚀 Task CRUD API (FastAPI)

A lightweight RESTful CRUD API built with Python and FastAPI for managing to-do tasks. Built for Week 2 of the AI Fluency backend track to demonstrate HTTP request-response cycles, status codes, input validation, and automated OpenAPI documentation.

---

## 🛠️ How to Run Locally

### Prerequisites
* Python 3.10+
* `pip` package manager

### 1. Install Dependencies
```bash
pip install fastapi uvicorn pydantic
2. Start the ServerBashpython -m uvicorn main:app --reload
Base URL: http://127.0.0.1:8000Interactive Swagger UI: http://127.0.0.1:8000/docs📋 API Endpoints MatrixMethodEndpointDescriptionExpected BodySuccess StatusError StatusGET/API Metadata & RoutesNone200 OK-GET/healthServer Health StatusNone200 OK-GET/statsTask Counts (Total/Done/Open)None200 OK-GET/tasksList Tasks (Optional done/search)None200 OK-GET/tasks/{id}Get Single Task by IDNone200 OK404 Not FoundPOST/tasksCreate New Task{"title": "Buy milk"}201 Created400 Bad RequestPUT/tasks/{id}Update Task{"title": "New", "done": true}200 OK400 Bad Request, 404 Not FoundDELETE/tasks/{id}Delete TaskNone204 No Content404 Not FoundPOST/resetReset DB to 3 initial seed itemsNone200 OK-🧪 Terminal Verification (curl -i)Bash$ curl -i -X POST [http://127.0.0.1:8000/tasks](http://127.0.0.1:8000/tasks) \
  -H "Content-Type: application/json" \
  -d '{"title":"Complete Week 2 Assignment"}'

HTTP/1.1 201 Created
date: Sun, 16 Aug 2026 17:00:00 GMT
server: uvicorn
content-type: application/json

{"id":4,"title":"Complete Week 2 Assignment","done":false}
🔬 In-Memory Mortality ExperimentObservation: When new tasks are created and the Uvicorn server is restarted (Ctrl+C followed by python -m uvicorn main:app --reload), all newly created tasks disappear, resetting back to the initial 3 seed tasks.Why it happens: The application stores state in a volatile Python list (tasks_db) in RAM. When the process terminates, all temporary memory is wiped. This demonstrates why real-world systems require persistent storage engines like SQL or NoSQL databases.🤖 Stage 7 — AI Rematch ("AI vs Me")Full Prompt Used"Write a single-file Python REST API using FastAPI that manages an in-memory task to-do list. Implement GET /, GET /health, GET /tasks, GET /tasks/{id} (404 if missing), POST /tasks (generates next ID, validates non-empty title returning 400 Bad Request, sets default done=False), PUT /tasks/{id} (updates title/done, returns 400 or 404), and DELETE /tasks/{id} (returns 204 No Content). Ensure Swagger UI is available at /docs."Code Comparison & FindingsWhat the AI Did Better:Used Pydantic's Field(min_length=1) schema annotations for clean declarative validation directly in the request model.What the AI Got Wrong / Ignored:Whitespace Bypass: The AI accepted empty whitespace strings ("   ") as valid titles. Manual string stripping (payload.title.strip()) was required to prevent blank task creation.HTTP 204 Protocol Violation: On DELETE /tasks/{id}, the AI returned {"message": "Task deleted"} alongside status code 204. Standard HTTP protocol forbids returning a JSON body with a 204 No Content status.What Prompting Missed:The prompt did not specify ID generation rules. The AI used len(tasks_db) + 1, which creates duplicate IDs if an earlier task is deleted. I updated my prompt logic to specify max(existing_ids) + 1.