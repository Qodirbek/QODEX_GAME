from flask import Blueprint, render_template, session, request, jsonify, redirect, url_for, send_from_directory
import time
import random
import string
import psycopg2
import os

# Blueprint yaratish
routes = Blueprint("routes", __name__)

# .env fayldan bazaga ulanish
DATABASE_URL = os.getenv("DATABASE_URL") + "?sslmode=require"
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Foydalanuvchilar jadvalini yaratish
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        balance INT DEFAULT 0,
        farming BOOLEAN DEFAULT FALSE,
        farming_start BIGINT DEFAULT NULL,
        wallet_address TEXT DEFAULT NULL
    )
""")
conn.commit()

# Random foydalanuvchi nomi yaratish funksiyasi
def generate_random_name():
    return "User-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

@routes.route("/")
def home():
    """Asosiy sahifa (QODEX tanga ishlash)"""
    session.permanent = True
    session.modified = True

    if "user_id" not in session:
        session["user_id"] = generate_random_name()

    user_id = session["user_id"]

    # Foydalanuvchini tekshirish yoki yaratish
    cur.execute("SELECT balance, farming, farming_start FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()

    if not user:
        cur.execute("INSERT INTO users (user_id) VALUES (%s)", (user_id,))
        conn.commit()
        balance, farming, farming_start = 0, False, None
    else:
        balance, farming, farming_start = user

    # Taymer to‘g‘ri ishlashi uchun tekshirish
    if farming and farming_start:
        elapsed_time = int(time.time()) - farming_start
        remaining_time = max(3600 - elapsed_time, 0)
    else:
        remaining_time = 0

    return render_template("home.html", username=user_id, balance=balance, farming=farming, remaining_time=remaining_time)

@routes.route("/claim", methods=["POST"])
def claim():
    """1000 QODEX olish"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Foydalanuvchi aniqlanmadi!"})

    user_id = session["user_id"]

    cur.execute("SELECT balance, farming, farming_start FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()

    if not user:
        return jsonify({"success": False, "message": "Foydalanuvchi topilmadi!"})

    balance, farming, farming_start = user

    # 1 soat oldin bosgan bo‘lsa, yana bosishga ruxsat bermaydi
    if farming and farming_start:
        elapsed_time = int(time.time()) - farming_start
        if elapsed_time < 3600:
            remaining_time = 3600 - elapsed_time
            return jsonify({"success": False, "message": f"Qayta bosish uchun {remaining_time} sekund kuting!"})

    new_balance = balance + 1000
    cur.execute("UPDATE users SET balance = %s, farming = TRUE, farming_start = %s WHERE user_id = %s",
                (new_balance, int(time.time()), user_id))
    conn.commit()

    return jsonify({"success": True, "message": "1000 QODEX qo'shildi!", "balance": new_balance})

@routes.route("/wallet", methods=["GET", "POST"])
def wallet():
    """Foydalanuvchi hamyoni"""
    if "user_id" not in session:
        return redirect(url_for("routes.home"))

    user_id = session["user_id"]

    if request.method == "POST":
        wallet_address = request.form.get("wallet_address")
        if wallet_address:
            cur.execute("UPDATE users SET wallet_address = %s WHERE user_id = %s", (wallet_address, user_id))
            conn.commit()

    cur.execute("SELECT balance, wallet_address FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    balance, wallet_address = user if user else (0, None)

    return render_template("wallet.html", username=user_id, balance=balance, wallet_address=wallet_address)

@routes.route("/admin")
def admin():
    """Admin sahifasi - barcha foydalanuvchilarni ko‘rish"""
    cur.execute("SELECT user_id, balance, wallet_address FROM users")
    users = cur.fetchall()
    return render_template("admin.html", users=users)

@routes.route("/earn")
def earn():
    """Earn sahifasi"""
    if "user_id" not in session:
        return redirect(url_for("routes.home"))

    user_id = session["user_id"]

    cur.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
    balance = cur.fetchone()[0] if cur.rowcount > 0 else 0

    bot_username = "@QODEX_COINBot"
    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    return render_template("earn.html", username=user_id, balance=balance, referral_link=referral_link)

@routes.route("/watch-ad", methods=["POST"])
def watch_ad():
    """Reklama ko‘rish orqali 1000 QODEX olish"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "User not found!"})

    user_id = session["user_id"]

    cur.execute("UPDATE users SET balance = balance + 1000 WHERE user_id = %s RETURNING balance", (user_id,))
    new_balance = cur.fetchone()[0]
    conn.commit()

    return jsonify({"success": True, "message": "1000 QODEX qo'shildi!", "balance": new_balance})

@routes.route("/leaderboard")
def leaderboard():
    """Eng ko‘p QODEX ishlagan foydalanuvchilar ro‘yxati"""
    cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
    top_users = cur.fetchall()

    return render_template("leaderboard.html", top_users=[{"username": u[0], "balance": u[1]} for u in top_users])

@routes.route("/reset", methods=["POST"])
def reset():
    """Foydalanuvchi balansini noldan boshlash"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "User not found!"})

    user_id = session["user_id"]

    cur.execute("UPDATE users SET balance = 0, farming = FALSE, farming_start = NULL, wallet_address = NULL WHERE user_id = %s RETURNING balance",
                (user_id,))
    new_balance = cur.fetchone()[0]
    conn.commit()

    return jsonify({"success": True, "message": "Balansingiz nollandi!", "balance": new_balance})

@routes.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)