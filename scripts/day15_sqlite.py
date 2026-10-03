from pathlib import Path
import sqlite3

DB_PATH = Path("data/day15_raw_demo.db")

def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    DB_PATH.parent.mkdir(exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def create_table(connection: sqlite3.Connection) -> None:
    """创建 tasks 表"""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed int NOT NULL DEFAULT 0,
            priority INTEGER NOT NULL DEFAULT 3
                CHECK(priority BETWEEN 1 AND 5)
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_tasks_priority
        ON tasks(completed, priority)
        """
    )
    connection.commit()

def create_task(
        connection: sqlite3.Connection,
        title: str,
        priority: int = 3,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO tasks (title, priority)
        VALUES (?, ?)
        """,
        (title, priority),
    )
    connection.commit()
    return int(cursor.lastrowid)

def list_tasks(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    cursor = connection.execute(
        """
        SELECT id, title, completed, priority
        FROM tasks
        ORDER BY id
        """
    )
    return cursor.fetchall()

def mark_task_completed(connection: sqlite3.Connection, task_id: int) -> None:
    connection.execute(
        """
        UPDATE tasks
        SET completed = 1
        WHERE id = ?
        """,
        (task_id,),
    )
    connection.commit()

def delete_task(
    connection: sqlite3.Connection, 
    task_id: int
) -> None:
    connection.execute(
        """
        DELETE FROM tasks
        WHERE id = ?
        """,
        (task_id,),
    )
    connection.commit()

def main() -> None:
    with get_connection() as connection:
        create_table(connection)

        task_id = create_task(
            connection, 
            "理解 SQLite CRUD", 
            priority=1
        )
        print(f"创建任务，ID: {task_id}")

        mark_task_completed(connection, task_id)

        print("当前任务:")
        for task in list_tasks(connection):
            print(dict(task))

        delete_task(connection, 2)
        print(f"已删除任务：id={task_id}")

if __name__ == "__main__":
    main()