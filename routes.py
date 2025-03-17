from datetime import datetime
from flask import request, render_template, session, jsonify, Blueprint
from flask import send_from_directory
import time
import random
import string
import psycopg2
import os

# Blueprint yaratish
routes = Blueprint("routes", __name__)

# **Bazaga ulanish funksiyasi**
def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL") + "?sslmode=require")

# **Foydalanuvchini aniqlash**
def get_user_identifier():
    telegram_user_id, _, _ = get_telegram_data()
    user_id = get_user_id()
    return telegram_user_id or user_id

# **Foydalanuvchi nomini yaratish**
def generate_random_name():
    return "User-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

# **Sessiyadan foydalanuvchi ID olish yoki yaratish**
def get_user_id():
    if "user_id" not in session:
        session["user_id"] = generate_random_name()
    return session["user_id"]

# **Telegram ma'lumotlarini olish**
def get_telegram_data():
    return session.get("telegram_user_id"), session.get("telegram_username"), session.get("telegram_first_name")

# **Foydalanuvchini olish yoki yaratish**
def get_or_create_user():
    user_id = get_user_identifier()
    telegram_user_id, telegram_username, telegram_first_name = get_telegram_data()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance, farming, farming_start FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()

            if not user:
                cur.execute(
                    "INSERT INTO users (user_id, balance, farming, farming_start, username, first_name) VALUES (%s, %s, %s, %s, %s, %s)",
                    (user_id, 0, False, None, telegram_username, telegram_first_name)
                )
                conn.commit()
                return 0, False, None, telegram_username, telegram_first_name

            return user[0], user[1], user[2], telegram_username, telegram_first_name

# **Asosiy sahifa**
@routes.route("/")
def home():
    session.permanent = True
    session.modified = True

    telegram_id = request.args.get("telegram_id")
    telegram_username = request.args.get("username")

    if telegram_id:
        session["telegram_user_id"] = telegram_id
    if telegram_username:
        session["telegram_username"] = telegram_username

    balance, farming, farming_start, username, first_name = get_or_create_user()
    current_time = int(time.time())

    remaining_time = max(0, 3600 - (current_time - farming_start.timestamp())) if farming and farming_start else 0

    return render_template("home.html", username=username or get_user_id(), balance=balance, farming=farming, remaining_time=remaining_time, telegram_first_name=first_name)

# **1000 QODEX olish**
@routes.route("/claim", methods=["POST"])
def claim():
    user_id = get_user_identifier()
    current_time = int(time.time())

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance, farming, farming_start FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()

            if not user:
                return jsonify({"success": False, "message": "Foydalanuvchi topilmadi!"})

            balance, farming, farming_start = user
            farming_start_timestamp = int(farming_start.timestamp()) if farming_start else 0
            remaining_time = max(0, 3600 - (current_time - farming_start_timestamp))

            if remaining_time > 0:
                return jsonify({"success": False, "message": f"Qayta bosish uchun {remaining_time // 60}:{remaining_time % 60:02d} kuting!", "remaining_time": remaining_time})

            new_balance = balance + 1000
            cur.execute("UPDATE users SET balance = %s, farming = TRUE, farming_start = %s WHERE user_id = %s",
                        (new_balance, datetime.now(), user_id))
            conn.commit()

    return jsonify({"success": True, "message": "1000 QODEX qo'shildi!", "balance": new_balance, "remaining_time": 3600})

# **Taymerni olish**
@routes.route("/get_timer", methods=["GET"])
def get_timer():
    user_id = get_user_identifier()
    current_time = int(time.time())

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT farming, farming_start FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()
            remaining_time = max(0, 3600 - (current_time - user[1].timestamp())) if user and user[0] and user[1] else 0

    return jsonify({"remaining_time": remaining_time})

# **Hamyon sahifasi**
@routes.route("/wallet", methods=["GET", "POST"])
def wallet():
    user_id = get_user_identifier()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if request.method == "POST":
                wallet_address = request.form.get("wallet_address")
                if wallet_address:
                    cur.execute("UPDATE users SET wallet_address = %s WHERE user_id = %s", (wallet_address, user_id))
                    conn.commit()

            cur.execute("SELECT balance, wallet_address FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()
            balance, wallet_address = user if user else (0, None)

    return render_template("wallet.html", username=user_id, balance=balance, wallet_address=wallet_address)

# **Admin sahifasi**
@routes.route("/admin")
def admin():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, user_id, username, first_name, balance, wallet_address FROM users")
            users = [{"id": u[0], "user_id": u[1], "username": u[2], "first_name": u[3], "balance": u[4], "wallet_address": u[5]} for u in cur.fetchall()]

    return render_template("admin.html", users=users)

# **Referal tizimi (Earn sahifasi)**
@routes.route("/earn")
def earn():
    user_id = get_user_identifier()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
            balance = cur.fetchone()[0] if cur.rowcount > 0 else 0

    bot_username = "QODEX_COINBot"
    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    return render_template("earn.html", username=user_id, balance=balance, referral_link=referral_link)

# **Reklama ko‘rib QODEX olish**
@routes.route("/watch-ad", methods=["POST"])
def watch_ad():
    user_id = get_user_identifier()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET balance = balance + 1000 WHERE user_id = %s RETURNING balance", (user_id,))
            new_balance = cur.fetchone()[0]
            conn.commit()

    return jsonify({"success": True, "message": "1000 QODEX qo'shildi!", "balance": new_balance})

@routes.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)