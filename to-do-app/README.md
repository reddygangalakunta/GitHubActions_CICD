# Taskflow — Flask Todo App

A beautiful, full-featured todo web app built with Flask.

## Features
- ✅ Add, complete, and delete tasks
- 🔴 Priority levels: Low, Medium, High
- 📅 Due dates with overdue detection
- 🏷️ Categories / tags
- 🔍 Filter by status or priority
- 📊 Sort by date, priority, or due date
- 💾 Persistent JSON storage

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open in browser
http://localhost:5000
```

## Project Structure
```
todo_app/
├── app.py              # Flask backend + REST API
├── requirements.txt
├── todos.json          # Auto-created on first use
└── templates/
    └── index.html      # Frontend UI
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/todos` | Fetch all todos |
| POST | `/api/todos` | Create a todo |
| PUT | `/api/todos/<id>` | Update a todo |
| DELETE | `/api/todos/<id>` | Delete a todo |
