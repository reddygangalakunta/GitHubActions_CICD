from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = os.environ.get("DATA_FILE", "todos.json")

# Ensure data directory exists (important when running in Docker with a volume)
_data_dir = os.path.dirname(DATA_FILE)
if _data_dir:
    os.makedirs(_data_dir, exist_ok=True)

def load_todos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_todos(todos):
    with open(DATA_FILE, "w") as f:
        json.dump(todos, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/todos", methods=["GET"])
def get_todos():
    return jsonify(load_todos())

@app.route("/api/todos", methods=["POST"])
def add_todo():
    data = request.json
    todos = load_todos()
    todo = {
        "id": int(datetime.now().timestamp() * 1000),
        "title": data.get("title", "").strip(),
        "priority": data.get("priority", "medium"),
        "due_date": data.get("due_date", ""),
        "category": data.get("category", "General"),
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    if not todo["title"]:
        return jsonify({"error": "Title is required"}), 400
    todos.append(todo)
    save_todos(todos)
    return jsonify(todo), 201

@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    data = request.json
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo.update({k: v for k, v in data.items() if k != "id"})
            save_todos(todos)
            return jsonify(todo)
    return jsonify({"error": "Not found"}), 404

@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todos = load_todos()
    todos = [t for t in todos if t["id"] != todo_id]
    save_todos(todos)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)
