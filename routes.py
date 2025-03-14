from flask import Blueprint, render_template, session, request, jsonify, send_from_directory
import time
import random
import string
import psycopg2
import os

# Blueprint yaratish
routes = Blueprint("routes", __name__)

# Bazaga ulanish funksiyasi
def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL") + "?sslmode=require")

# Foydalanuvchi nomini yaratish
def generate_random_name():
    return "User-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Sessiyadan foydalanuvchi ID olish yoki yaratish
def get_user_id():
    if "user_id" not in session:
        session["user_id"] = generate_random_name()
    return session["user_id"]

# Foydalanuvchini olish yoki yaratish
def get_or_create_user():
    user_id = get_user_id()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance, farming, farming_start FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()

            if not user:
                cur.execute(
                    "INSERT INTO users (user_id, balance, farming, farming_start) VALUES (%s, %s, %s, %s)",
                    (user_id, 0, False, None),
                )
                conn.commit()
                return 0, False, None

            return user

@routes.route("/")
def home():
    """Asosiy sahifa"""
    session.permanent = True
    session.modified = True

    balance, farming, farming_start = get_or_create_user()
    current_time = int(time.time())

    # Vaqtni hisoblash
    remaining_time = max(0, 3600 - (current_time - farming_start)) if farming and farming_start else 0

    return render_template(
        "home.html",
        username=get_user_id(),
        balance=balance,
        farming=farming,
        remaining_time=remaining_time,
    )

@routes.route("/claim", methods=["POST"])
def claim():
    """1000 QODEX olish"""
    user_id = get_user_id()
    current_time = int(time.time())

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance, farming, farming_start FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()

            if not user:
                return jsonify({"success": False, "message": "Foydalanuvchi topilmadi!"})

            balance, farming, farming_start = user

            # Agar farming hali davom etayotgan bo'lsa, kutish kerak
            if farming and farming_start:
                remaining_time = max(3600 - (current_time - farming_start), 0)
                if remaining_time > 0:
                    return jsonify({
                        "success": False,
                        "message": f"Qayta bosish uchun {remaining_time // 60}:{remaining_time % 60:02d} kuting!",
                        "remaining_time": remaining_time,
                    })

            # Yangi balansni hisoblash va bazaga yozish
            new_balance = balance + 1000
            farming_start = current_time  # Yangi bosish vaqtini saqlaymiz
            cur.execute(
                "UPDATE users SET balance = %s, farming = TRUE, farming_start = %s WHERE user_id = %s",
                (new_balance, farming_start, user_id),
            )
            conn.commit()

    return jsonify({
        "success": True,
        "message": "1000 QODEX qo'shildi!",
        "balance": new_balance,
        "remaining_time": 3600,  # Sekund sifatida qaytariladi
    })

@routes.route("/get_timer", methods=["GET"])
def get_timer():
    """Real vaqt rejimida taymerni olish"""
    user_id = get_user_id()
    current_time = int(time.time())

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT farming, farming_start FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()

            if not user:
                return jsonify({"remaining_time": 0})

            farming, farming_start = user
            remaining_time = max(0, 3600 - (current_time - farming_start)) if farming and farming_start else 0

    return jsonify({"remaining_time": remaining_time})

@routes.route("/wallet", methods=["GET", "POST"])
def wallet():
    """Hamyon ma'lumotlari"""
    user_id = get_user_id()

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

@routes.route("/admin")
def admin():
    """Admin sahifasi"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, balance, wallet_address FROM users")
            users = cur.fetchall()

    return render_template("admin.html", users=users)

@routes.route("/earn")
def earn():
    """Earn sahifasi"""
    user_id = get_user_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
            balance = cur.fetchone()[0] if cur.rowcount > 0 else 0

    bot_username = "@QODEX_COINBot"
    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    return render_template("earn.html", username=user_id, balance=balance, referral_link=referral_link)

@routes.route("/watch-ad", methods=["POST"])
def watch_ad():
    """Reklama ko‘rib QODEX olish"""
    user_id = get_user_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET balance = balance + 1000 WHERE user_id = %s RETURNING balance", (user_id,))
            new_balance = cur.fetchone()[0]
            conn.commit()

    return jsonify({"success": True, "message": "1000 QODEX qo'shildi!", "balance": new_balance})

@routes.route("/leaderboard")
def leaderboard():
    """Eng ko‘p QODEX ishlaganlar"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
            top_users = cur.fetchall()

    return render_template(
        "leaderboard.html",
        top_users=[{"username": u[0], "balance": u[1]} for u in top_users],
    )

@routes.route("/reset", methods=["POST"])
def reset():
    """Foydalanuvchi balansini nollash"""
    user_id = get_user_id()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET balance = 0, farming = FALSE, farming_start = NULL, wallet_address = NULL WHERE user_id = %s RETURNING balance",
                (user_id,),
            )
            new_balance = cur.fetchone()[0]
            conn.commit()

    return jsonify({"success": True, "message": "Balansingiz nollandi!", "balance": new_balance})

@routes.route("/static/<path:filename>")
def serve_static(filename):
    """Statik fayllarni serverdan yuborish"""
    return send_from_directory("static", filename)