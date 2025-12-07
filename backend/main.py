from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

todos = []  # temporary database
class TodoItem(BaseModel):
    title: str

@app.get("/")
def read_root():
    return {"status": "backend running OK"}

@app.get("/todos")
def get_todos():
    return {"todos": todos}
@app.post("/todos")
def create_todo(item: TodoItem):
    todos.append(item.title)
    return {"message": "todo added", "todos": todos}
@app.delete("/todos/{index}")
def delete_todo(index: int):
    if index < 0 or index >= len(todos):
        return {"error": "index out of range"}

    deleted_item = todos.pop(index)
    return {"message": "todo deleted", "deleted": deleted_item, "todos": todos}
@app.put("/todos/{index}")
def update_todo(index: int, item: TodoItem):
    if index < 0 or index >= len(todos):
        return {"error": "index out of range"}

    todos[index] = item.title
    return {"message": "todo updated", "todos": todos}