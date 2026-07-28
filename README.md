\# Task API



A simple CRUD API for managing a to-do list, built with FastAPI. Tasks are stored in memory (no database) — data resets when the server restarts.



\## Run it



```bash

python -m venv venv

venv\\Scripts\\activate        # Windows

pip install fastapi uvicorn

uvicorn main:app --reload --port 8000

```



Server runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.



\## Endpoints



| Method | Path        | Description         |

|--------|-------------|----------------------|

| GET    | /           | API info             |

| GET    | /health     | Health check         |

| GET    | /tasks      | List all tasks       |

| GET    | /tasks/{id} | Get a single task    |

| POST   | /tasks      | Create a new task    |

| PUT    | /tasks/{id} | Update a task        |

| DELETE | /tasks/{id} | Delete a task        |



\## Example request



```

$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\\"title\\":\\"Buy milk\\"}"



HTTP/1.1 201 Created

content-type: application/json



{"id":4,"title":"Buy milk","done":false}

```



\## Swagger UI



!\[Swagger UI](swagger-screenshot.png)







\## Notes



Data is stored in memory only — restarting the server resets tasks back to the 3 seeded examples. This is intentional; persistence is next week's topic.

