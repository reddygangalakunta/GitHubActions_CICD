import pytest
import json
import os
import tempfile
from app import app, DATA_FILE


@pytest.fixture
def client(tmp_path):
    """Create a test client with a temporary data file."""
    test_data_file = str(tmp_path / "test_todos.json")
    app.config["TESTING"] = True

    import app as app_module
    original = app_module.DATA_FILE
    app_module.DATA_FILE = test_data_file

    with app.test_client() as client:
        yield client

    app_module.DATA_FILE = original


# ── Helpers ───────────────────────────────────────────────────────────────────

def add_todo(client, title="Test Task", priority="medium", category="Work", due_date=""):
    return client.post("/api/todos", json={
        "title": title,
        "priority": priority,
        "category": category,
        "due_date": due_date,
    })


# ── Index route ───────────────────────────────────────────────────────────────

class TestIndex:
    def test_homepage_returns_200(self, client):
        res = client.get("/")
        assert res.status_code == 200

    def test_homepage_contains_taskflow(self, client):
        res = client.get("/")
        assert b"Taskflow" in res.data


# ── GET /api/todos ─────────────────────────────────────────────────────────────

class TestGetTodos:
    def test_empty_list_on_start(self, client):
        res = client.get("/api/todos")
        assert res.status_code == 200
        assert res.get_json() == []

    def test_returns_added_todo(self, client):
        add_todo(client, "Buy groceries")
        res = client.get("/api/todos")
        data = res.get_json()
        assert len(data) == 1
        assert data[0]["title"] == "Buy groceries"

    def test_returns_multiple_todos(self, client):
        add_todo(client, "Task A")
        add_todo(client, "Task B")
        res = client.get("/api/todos")
        assert len(res.get_json()) == 2


# ── POST /api/todos ────────────────────────────────────────────────────────────

class TestAddTodo:
    def test_add_valid_todo(self, client):
        res = add_todo(client, "Finish report")
        assert res.status_code == 201
        data = res.get_json()
        assert data["title"] == "Finish report"

    def test_add_todo_defaults(self, client):
        res = add_todo(client)
        data = res.get_json()
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data

    def test_add_todo_with_priority(self, client):
        res = add_todo(client, priority="high")
        assert res.get_json()["priority"] == "high"

    def test_add_todo_with_due_date(self, client):
        res = add_todo(client, due_date="2025-12-31")
        assert res.get_json()["due_date"] == "2025-12-31"

    def test_add_todo_with_category(self, client):
        res = add_todo(client, category="Personal")
        assert res.get_json()["category"] == "Personal"

    def test_empty_title_returns_400(self, client):
        res = client.post("/api/todos", json={"title": ""})
        assert res.status_code == 400
        assert "error" in res.get_json()

    def test_missing_title_returns_400(self, client):
        res = client.post("/api/todos", json={"priority": "low"})
        assert res.status_code == 400

    def test_whitespace_only_title_returns_400(self, client):
        res = client.post("/api/todos", json={"title": "   "})
        assert res.status_code == 400

    def test_todo_id_is_unique(self, client):
        r1 = add_todo(client, "Task 1").get_json()
        r2 = add_todo(client, "Task 2").get_json()
        assert r1["id"] != r2["id"]


# ── PUT /api/todos/<id> ────────────────────────────────────────────────────────

class TestUpdateTodo:
    def test_mark_todo_completed(self, client):
        todo_id = add_todo(client).get_json()["id"]
        res = client.put(f"/api/todos/{todo_id}", json={"completed": True})
        assert res.status_code == 200
        assert res.get_json()["completed"] is True

    def test_update_title(self, client):
        todo_id = add_todo(client, "Old title").get_json()["id"]
        res = client.put(f"/api/todos/{todo_id}", json={"title": "New title"})
        assert res.get_json()["title"] == "New title"

    def test_update_priority(self, client):
        todo_id = add_todo(client, priority="low").get_json()["id"]
        res = client.put(f"/api/todos/{todo_id}", json={"priority": "high"})
        assert res.get_json()["priority"] == "high"

    def test_update_nonexistent_todo_returns_404(self, client):
        res = client.put("/api/todos/999999", json={"completed": True})
        assert res.status_code == 404

    def test_id_cannot_be_overwritten(self, client):
        original_id = add_todo(client).get_json()["id"]
        client.put(f"/api/todos/{original_id}", json={"id": 99999})
        todos = client.get("/api/todos").get_json()
        assert todos[0]["id"] == original_id


# ── DELETE /api/todos/<id> ─────────────────────────────────────────────────────

class TestDeleteTodo:
    def test_delete_existing_todo(self, client):
        todo_id = add_todo(client).get_json()["id"]
        res = client.delete(f"/api/todos/{todo_id}")
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_deleted_todo_not_in_list(self, client):
        todo_id = add_todo(client).get_json()["id"]
        client.delete(f"/api/todos/{todo_id}")
        todos = client.get("/api/todos").get_json()
        assert all(t["id"] != todo_id for t in todos)

    def test_delete_nonexistent_todo_still_succeeds(self, client):
        res = client.delete("/api/todos/999999")
        assert res.status_code == 200

    def test_delete_one_preserves_others(self, client):
        id1 = add_todo(client, "Keep me").get_json()["id"]
        id2 = add_todo(client, "Delete me").get_json()["id"]
        client.delete(f"/api/todos/{id2}")
        todos = client.get("/api/todos").get_json()
        assert len(todos) == 1
        assert todos[0]["id"] == id1


# ── Persistence ────────────────────────────────────────────────────────────────

class TestPersistence:
    def test_todos_saved_to_file(self, client, tmp_path):
        import app as app_module
        add_todo(client, "Persistent task")
        assert os.path.exists(app_module.DATA_FILE)
        with open(app_module.DATA_FILE) as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["title"] == "Persistent task"
