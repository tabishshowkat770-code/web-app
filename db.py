import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = "ecommerce.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            type TEXT NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(client_id) REFERENCES clients(id)
        )
        """
    )
    conn.commit()
    conn.close()


def add_client(name: str, email: Optional[str] = None, phone: Optional[str] = None) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (name, email, phone, created_at) VALUES (?,?,?,?)",
                (name, email or "", phone or "", datetime.utcnow().isoformat()))
    client_id = cur.lastrowid
    conn.commit()
    conn.close()
    return client_id


def get_clients() -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, phone, created_at FROM clients ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["id", "name", "email", "phone", "created_at"], r)) for r in rows]


def add_transaction(client_id: int, amount: float, type: str = "sale", note: Optional[str] = None) -> int:
    assert type in ("sale", "payment"), "type must be 'sale' or 'payment'"
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (client_id, amount, type, note, created_at) VALUES (?,?,?,?,?)",
        (client_id, amount, type, note or "", datetime.utcnow().isoformat()),
    )
    tid = cur.lastrowid
    conn.commit()
    conn.close()
    return tid


def get_transactions(client_id: Optional[int] = None):
    conn = get_conn()
    cur = conn.cursor()
    if client_id:
        cur.execute("SELECT id, client_id, amount, type, note, created_at FROM transactions WHERE client_id = ? ORDER BY created_at DESC", (client_id,))
    else:
        cur.execute("SELECT id, client_id, amount, type, note, created_at FROM transactions ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(zip(["id", "client_id", "amount", "type", "note", "created_at"], r)) for r in rows]


def get_summary(client_id: Optional[int] = None) -> Dict[str, float]:
    conn = get_conn()
    cur = conn.cursor()
    if client_id:
        cur.execute("SELECT COALESCE(SUM(CASE WHEN type='sale' THEN amount END),0), COALESCE(SUM(CASE WHEN type='payment' THEN amount END),0) FROM transactions WHERE client_id = ?", (client_id,))
    else:
        cur.execute("SELECT COALESCE(SUM(CASE WHEN type='sale' THEN amount END),0), COALESCE(SUM(CASE WHEN type='payment' THEN amount END),0) FROM transactions")
    sale_sum, payment_sum = cur.fetchone()
    conn.close()
    return {
        "total_taken": float(sale_sum or 0.0),
        "total_received": float(payment_sum or 0.0),
        "receivable": float((sale_sum or 0.0) - (payment_sum or 0.0)),
    }
