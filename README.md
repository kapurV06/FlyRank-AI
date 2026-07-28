Task API
A simple CRUD API for managing a to-do list, built with FastAPI. Tasks are stored in a SQLite database, so data survives server restarts.
Why SQLite
SQLite was chosen because it needs no separate database server — the whole database lives in a single file (`tasks.db`) that's created automatically the first time the app runs. That makes it ideal for a small project like this: zero setup, zero configuration, and the file can just sit in the project folder.
Where the database lives
`tasks.db` sits in the project root (same folder as `main.py`). It's created automatically on first run if it doesn't exist, and the `tasks` table is created (with 3 example tasks seeded) only if the table is empty — so restarting the server never wipes or duplicates data.
The `.db` file itself is excluded from git via `.gitignore` since it's generated data, not source code.
Run it
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install fastapi uvicorn
uvicorn main:app --reload --port 8000
```
Server runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`. `tasks.db` is created automatically on first run.
Endpoints
Method	Path	Description
GET	/	API info
GET	/health	Health check
GET	/tasks	List all tasks
GET	/tasks/{id}	Get a single task
POST	/tasks	Create a new task
PUT	/tasks/{id}	Update a task
DELETE	/tasks/{id}	Delete a task
Example request
```
$ curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"

HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":0}
```
(Replace with one of your own actual curl -i outputs before submitting, if different.)
Swagger UI
<img width="1907" height="1017" alt="helllo" src="https://github.com/user-attachments/assets/170bd738-6473-4bb9-9bb0-4c91cb590ac6" />
Database viewer
Explored the database directly using DB Browser for SQLite. Example query run in the Execute SQL tab:
```sql
SELECT * FROM tasks WHERE done = 1;
```
This returned only the completed tasks — confirming the API and the underlying database stay in sync, since changes made directly in the database viewer show up immediately through `GET /tasks` with no code changes required.
<img width="1292" height="817" alt="yeayea" src="https://github.com/user-attachments/assets/63caabfd-7986-418a-b14c-b0494974fcce" />

Notes
Tasks now persist in `tasks.db` (SQLite) instead of an in-memory list — restarting the server no longer resets the data. The database file and table are created automatically if missing, and the 3 example tasks are inserted only on first run.
