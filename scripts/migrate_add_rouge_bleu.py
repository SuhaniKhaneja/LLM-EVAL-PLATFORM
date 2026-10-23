
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = Path("eval.db")

if not DB_PATH.exists():
    raise FileNotFoundError(
        f"Database not found: {DB_PATH.resolve()}"
    )

# Preserve the database before making any schema changes.
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup_path = DB_PATH.with_name(f"eval.pre-migration.{timestamp}.db")
shutil.copy2(DB_PATH, backup_path)
print(f"Backup created: {backup_path}")

connection = sqlite3.connect(DB_PATH)

try:
    columns = {
        row[1]
        for row in connection.execute(
            "PRAGMA table_info(eval_results)"
        ).fetchall()
    }

    additions = {
        "rouge_l_score": "FLOAT",
        "bleu_score": "FLOAT",
    }

    for column_name, column_type in additions.items():
        if column_name not in columns:
            connection.execute(
                f"ALTER TABLE eval_results "
                f"ADD COLUMN {column_name} {column_type}"
            )
            print(f"Added column: {column_name}")
        else:
            print(f"Column already exists: {column_name}")

    connection.commit()

    count = connection.execute(
        "SELECT COUNT(*) FROM eval_results"
    ).fetchone()[0]
    print(f"Existing evaluation records preserved: {count}")

    final_columns = connection.execute(
        "PRAGMA table_info(eval_results)"
    ).fetchall()
    print("Current eval_results columns:")
    for column in final_columns:
        print(f"  {column[1]}: {column[2]}")

except Exception:
    connection.rollback()
    raise
finally:
    connection.close()
