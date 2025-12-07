from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2

app = FastAPI()

# --- تنظیمات دیتابیس RDS ---
DB_HOST = "aws-todo-db.cluster-czk8m48e4mry.eu-north-1.rds.amazonaws.com"      
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "yV9_X1JQPX.a9kJYP-B>?Jyn2AKd"  
DB_PORT = 5432


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
    )


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()


# وقتی برنامه بالا می‌آد، اگر جدول نبود، ساخته می‌شود
init_db()


class TodoItem(BaseModel):
    title: str
    description: str | None = None


@app.get("/")
def read_root():
    return {"status": "backend running OK"}


@app.get("/todos")
def get_todos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description FROM todos ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    todos = [
        {"id": r[0], "title": r[1], "description": r[2]}
        for r in rows
    ]
    return {"todos": todos}


@app.post("/todos")
def create_todo(item: TodoItem):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO todos (title, description) VALUES (%s, %s) RETURNING id;",
        (item.title, item.description),
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "todo added", "id": new_id}


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM todos WHERE id = %s;", (todo_id,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {"message": "todo deleted"}


@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, item: TodoItem):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE todos SET title = %s, description = %s WHERE id = %s;",
        (item.title, item.description, todo_id),
    )
    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    if updated == 0:
        raise HTTPException(status_code=404, detail="Todo not found")

    return {"message": "todo updated"}