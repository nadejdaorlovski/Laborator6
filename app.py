import os
import time
import mysql.connector
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "Myapp_base")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rootpass")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

def get_connection(retries=20, delay=3):
    for _ in range(retries):
        try:
            return mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT
            )
        except Exception:
            time.sleep(delay)
    raise Exception("Nu s-a putut realiza conexiunea la MySQL.")

def init_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            content VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    init_table()

    if request.method == "POST":
        msg = request.form.get("message", "").strip()
        if msg:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO messages (content) VALUES (%s)", (msg,))
            conn.commit()
            cur.close()
            conn.close()
        return redirect("/")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content, created_at FROM messages ORDER BY id DESC")
    messages = cur.fetchall()
    cur.close()
    conn.close()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ro">
    <head>
        <meta charset="UTF-8">
        <title>Laborator 6</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 40px auto; }
            input { padding: 8px; width: 70%; }
            button { padding: 8px 12px; }
            .msg { background:#f3f3f3; margin:10px 0; padding:10px; border-radius:8px; }
        </style>
    </head>
    <body>
        <h1>Aplicație Flask + MySQL</h1>
        <form method="post">
            <input type="text" name="message" placeholder="Scrie un mesaj..." required>
            <button type="submit">Adaugă</button>
        </form>

        <h2>Mesaje</h2>
        {% for m in messages %}
            <div class="msg">
                <b>#{{ m[0] }}</b> - {{ m[1] }}<br>
                <small>{{ m[2] }}</small>
            </div>
        {% else %}
            <p>Nu există mesaje.</p>
        {% endfor %}
    </body>
    </html>
    """, messages=messages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)