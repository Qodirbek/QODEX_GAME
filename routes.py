from datetime import datetime
from flask import request, render_template, session, jsonify, Blueprint, send_from_directory
import time
import psycopg2
import os

routes = Blueprint("routes", __name__)

# Ma'lumotlar bazasi ulanishi
def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL") + "?sslmode=require")

# Telegram ma'lumotlarini olish
def get_telegram_data():
    return (
        session.get("telegram_id"),
        session.get("telegram_username"),
        session.get("telegram_first_name"),
    )

# Foydalanuvchini olish yoki yaratish
def get_or_create_user():
    telegram_id, telegram_username, telegram_first_name = get_telegram_data()

    if not telegram_id:
        return None

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance, farming, farming_start FROM users WHERE telegram_id = %s", (telegram_id,))
            user = cur.fetchone()

            if not user:
                cur.execute(
                    "INSERT INTO users (telegram_id, balance, farming, farming_start, username, first_name) "
                    "VALUES (%s, %s, %s, %s, %s, %s) RETURNING balance, farming, farming_start",
                    (telegram_id, 0, False, None, telegram_username, telegram_first_name),
                )
                conn.commit()
                user = cur.fetchone()
            return user[0], user[1], user[2], telegram_username, telegram_first_name

# Bosh sahifa
@routes.route("/")
def home():
    session.permanent = True
    session.modified = True

    if request.args.get("telegram_id"):
        session["telegram_id"] = request.args["telegram_id"]
    if request.args.get("username"):
        session["telegram_username"] = request.args["username"]
    if request.args.get("first_name"):
        session["telegram_first_name"] = request.args["first_name"]

    user_data = get_or_create_user()
    if not user_data:
        return "❌ Faqat Telegram orqali kirish mumkin!", 403

    balance, farming, farming_start, username, first_name = user_data
    current_time = int(time.time())
    remaining_time = max(0, 3600 - (current_time - farming_start.timestamp())) if farming and farming_start else 0

    return render_template(
        "home.html",
        username=username,
        balance=balance,
        farming=farming,
        remaining_time=remaining_time,
        telegram_first_name=first_name,
    )

# Tasks sahifasi
@routes.route("/tasks")
def tasks():
    telegram_id, _, _ = get_telegram_data()
    if not telegram_id:
        return "❌ Faqat Telegram orqali kirish mumkin!", 403

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance FROM users WHERE telegram_id = %s", (telegram_id,))
            user = cur.fetchone()
            balance = user[0] if user else 0

            # Dinamik vazifalar (masalan, tasks jadvalidan)
            cur.execute("SELECT id, name, link FROM tasks")
            tasks = [{"id": row[0], "name": row[1], "link": row[2]} for row in cur.fetchall()]

    return render_template("tasks.html", username=telegram_id, balance=balance, tasks=tasks)

# Leaderboard sahifasi
@routes.route("/leaderboard")
def leaderboard():
    telegram_id, telegram_username, _ = get_telegram_data()
    if not telegram_id:
        return "❌ Faqat Telegram orqali kirish mumkin!", 403

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Barcha foydalanuvchilarni balans bo‘yicha saralash
                cur.execute(
                    "SELECT telegram_id, username, balance FROM users ORDER BY balance DESC"
                )
                all_users = [
                    {
                        "id": row[0],
                        "username": row[1] or f"User_{row[0]}",  # Agar username bo‘lmasa, telegram_id ishlatiladi
                        "balance": row[2] or 0,
                    }
                    for row in cur.fetchall()
                ]

                # Top-100 foydalanuvchilarni olish
                top_100 = all_users[:100]

                # Joriy foydalanuvchining reytingini aniqlash
                user_rank = next(
                    (i + 1 for i, user in enumerate(all_users) if user["id"] == telegram_id),
                    None
                )

                # Joriy foydalanuvchining balansini olish
                cur.execute(
                    "SELECT balance FROM users WHERE telegram_id = %s",
                    (telegram_id,)
                )
                user_balance = cur.fetchone()[0] if cur.rowcount > 0 else 0

        return render_template(
            "leaderboard.html",
            leaderboard=enumerate(top_100, 1),  # 1-dan boshlab raqamlash
            user_rank=user_rank,
            user_balance=user_balance,
            current_user_id=telegram_id,
        )

    except Exception as e:
        return f"❌ Xatolik: {str(e)}", 500

@routes.route("/daily-bonus-data", methods=["GET"])
def daily_bonus_data():
    telegram_id = session.get("telegram_id")
    if not telegram_id:
        return jsonify({"success": False, "message": "Telegram ID not found"}), 400

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT current_day, claimed_today FROM daily_bonus WHERE telegram_id = %s", (telegram_id,))
        result = cur.fetchone()
        if not result:
            cur.execute(
                "INSERT INTO daily_bonus (telegram_id, current_day, claimed_today) VALUES (%s, 1, false) RETURNING current_day, claimed_today",
                (telegram_id,)
            )
            result = cur.fetchone()
        conn.commit()

    return jsonify({"current_day": result[0], "claimed_today": result[1]})

@routes.route("/daily-bonus", methods=["POST"])
def daily_bonus():
    telegram_id = session.get("telegram_id")
    if not telegram_id:
        return jsonify({"success": False, "message": "Telegram ID not found"}), 400

    data = request.get_json()
    day = data.get("day")
    if not day:
        return jsonify({"success": False, "message": "Day not provided"}), 400

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT current_day, claimed_today FROM daily_bonus WHERE telegram_id = %s", (telegram_id,))
        result = cur.fetchone()

        if not result:
            return jsonify({"success": False, "message": "Bonus data not found"}), 404

        current_day, claimed_today = result
        if current_day != day:
            return jsonify({"success": False, "message": "Invalid day"}), 400

        if claimed_today:
            return jsonify({"success": False, "message": "Bonus already claimed today"}), 400

        # Mukofotni hisoblash
        rewards = [
            100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
            1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000,
            2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 10000
        ]
        reward = rewards[day - 1]

        # Balansni yangilash va holatni belgilash
        next_day = day + 1 if day < 30 else 1
        cur.execute("""
            UPDATE users SET balance = balance + %s WHERE telegram_id = %s;
            UPDATE daily_bonus SET current_day = %s, claimed_today = true WHERE telegram_id = %s;
        """, (reward, telegram_id, next_day, telegram_id))
        
        conn.commit()

    return jsonify({"success": True, "message": f"Bonus claimed: {reward} QODEX"})

# Friends sahifasi
@routes.route("/friends")
def friends():
    telegram_id, _, _ = get_telegram_data()
    if not telegram_id:
        return "❌ Faqat Telegram orqali kirish mumkin!", 403

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance FROM users WHERE telegram_id = %s", (telegram_id,))
            user = cur.fetchone()
            balance = user[0] if user else 0

            cur.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = %s", (telegram_id,))
            referral_count = cur.fetchone()[0]

            cur.execute("SELECT invited_user FROM referrals WHERE referrer_id = %s", (telegram_id,))
            friends = [row[0] for row in cur.fetchall()]

    referral_link = f"https://t.me/QODEX_COINBot?start={telegram_id}"
    return render_template(
        "friends.html",
        username=telegram_id,
        balance=balance,
        referral_link=referral_link,
        referral_count=referral_count,
        friends=friends,
    )

# Admin sahifasi
@routes.route("/admin")
def admin():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, telegram_id, username, first_name, last_name, balance, wallet_address FROM users"
                )
                users = [
                    {
                        "id": u[0],
                        "telegram_id": u[1] or "No Telegram ID",
                        "username": u[2] or "No username",
                        "first_name": u[3] or "No first name",
                        "last_name": u[4] or "No last name",
                        "balance": u[5] or 0,
                        "wallet_address": u[6] or "No wallet",
                    }
                    for u in cur.fetchall()
                ]
        return render_template("admin.html", users=users)
    except Exception as e:
        return f"❌ Xatolik: {str(e)}", 500

# Wallet sahifasi
@routes.route("/wallet", methods=["GET", "POST"])
def wallet():
    telegram_id, _, _ = get_telegram_data()
    if not telegram_id:
        return "❌ Faqat Telegram orqali kirish mumkin!", 403

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if request.method == "POST":
                wallet_address = request.form.get("wallet_address")
                if wallet_address:
                    cur.execute(
                        "UPDATE users SET wallet_address = %s WHERE telegram_id = %s",
                        (wallet_address, telegram_id),
                    )
                    conn.commit()

            cur.execute("SELECT balance, wallet_address FROM users WHERE telegram_id = %s", (telegram_id,))
            user = cur.fetchone()
            balance, wallet_address = user if user else (0, None)

    return render_template(
        "wallet.html",
        username=telegram_id,
        balance=balance,
        wallet_address=wallet_address,
    )

# Hamyon manzilini saqlash
@routes.route("/save-wallet", methods=["POST"])
def save_wallet():
    telegram_id, _, _ = get_telegram_data()
    if not telegram_id:
        return jsonify({"success": False, "message": "❌ Faqat Telegram orqali kirish mumkin!"}), 403

    data = request.get_json()
    wallet_address = data.get("wallet_address")
    if not wallet_address:
        return jsonify({"success": False, "message": "Hamyon manzili kiritilmagan!"}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM users WHERE telegram_id = %s", (telegram_id,))
                if not cur.fetchone():
                    return jsonify({"success": False, "message": "Foydalanuvchi topilmadi!"}), 404

                cur.execute(
                    "UPDATE users SET wallet_address = %s WHERE telegram_id = %s",
                    (wallet_address, telegram_id),
                )
                conn.commit()
        return jsonify({"success": True, "message": "✅ Hamyon manzili saqlandi!"})
    except Exception as e:
        print(f"[Xatolik] Database error: {e}")
        return jsonify({"success": False, "message": "❌ Serverda xatolik yuz berdi!"}), 500

# Farming da'vo qilish
@routes.route("/claim", methods=["POST"])
def claim():
    telegram_id, _, _ = get_telegram_data()
    if not telegram_id:
        return jsonify({"success": False, "message": "❌ Faqat Telegram orqali kirish mumkin!"}), 403

    current_time = int(time.time())
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance, farming, farming_start FROM users WHERE telegram_id = %s", (telegram_id,))
            user = cur.fetchone()
            if not user:
                return jsonify({"success": False, "message": "Foydalanuvchi topilmadi!"}), 404

            balance, farming, farming_start = user
            farming_start_timestamp = int(farming_start.timestamp()) if farming_start else 0
            remaining_time = max(0, 3600 - (current_time - farming_start_timestamp))

            if remaining_time > 0:
                return jsonify({
                    "success": False,
                    "message": f"Qayta da'vo qilish uchun {remaining_time // 60}:{remaining_time % 60:02d} kuting!",
                    "remaining_time": remaining_time,
                })

            new_balance = balance + 1000
            cur.execute(
                "UPDATE users SET balance = %s, farming = TRUE, farming_start = %s WHERE telegram_id = %s",
                (new_balance, datetime.now(), telegram_id),
            )
            conn.commit()

    return jsonify({
        "success": True,
        "message": "1000 QODEX qo‘shildi!",
        "balance": new_balance,
        "remaining_time": 3600,
    })

# Reklama ko‘rish
@routes.route("/watch-ad", methods=["POST"])
def watch_ad():
    telegram_id, _, _ = get_telegram_data()
    if not telegram_id:
        return jsonify({"success": False, "message": "❌ Faqat Telegram orqali kirish mumkin!"}), 403

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET balance = balance + 1000 WHERE telegram_id = %s RETURNING balance",
                    (telegram_id,),
                )
                new_balance = cur.fetchone()[0]
                conn.commit()
        return jsonify({
            "success": True,
            "message": "1000 QODEX qo‘shildi!",
            "balance": new_balance,
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Xatolik: {str(e)}"}), 500

# Vazifani bajarish
@routes.route("/complete-task", methods=["POST"])
def complete_task():
    telegram_id, _, _ = get_telegram_data()
    if not telegram_id:
        return jsonify({"success": False, "message": "❌ Faqat Telegram orqali kirish mumkin!"}), 403

    data = request.get_json()
    if not data or "task_id" not in data:
        return jsonify({"success": False, "message": "Task ID kiritilmagan!"}), 400

    task_id = data["task_id"]

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Vazifa allaqachon bajarilganmi?
                cur.execute(
                    "SELECT 1 FROM completed_tasks WHERE telegram_id = %s AND task_id = %s",
                    (telegram_id, task_id)
                )
                if cur.fetchone():
                    return jsonify({"success": False, "message": "Bu vazifa allaqachon bajarilgan!"})

                # Vazifani bajarilgan deb belgilash
                cur.execute(
                    "INSERT INTO completed_tasks (telegram_id, task_id) VALUES (%s, %s)",
                    (telegram_id, task_id)
                )

                # Foydalanuvchi balansini yangilash
                cur.execute(
                    "UPDATE users SET balance = balance + 1000 WHERE telegram_id = %s RETURNING balance",
                    (telegram_id,)
                )
                result = cur.fetchone()
                if not result:
                    return jsonify({"success": False, "message": "Foydalanuvchi topilmadi!"}), 404

                new_balance = result[0]
                conn.commit()

        return jsonify({
            "success": True,
            "message": "✅ Vazifa bajarildi! 1000 QODEX qo‘shildi!",
            "balance": new_balance
        })

    except Exception as e:
        print("Xato:", e)  # Logga yozish uchun
        return jsonify({"success": False, "message": "Ichki server xatosi!"}), 500

# Qo‘shimcha tangalar qo‘shish
@routes.route("/add-coins", methods=["POST"])
def add_coins():
    telegram_id, _, _ = get_telegram_data()
    if not telegram_id:
        return jsonify({"success": False, "message": "❌ Faqat Telegram orqali kirish mumkin!"}), 403

    data = request.get_json()
    coins = data.get("coins", 0)
    if not isinstance(coins, int) or coins <= 0:
        return jsonify({"success": False, "message": "Noto‘g‘ri tanga miqdori!"}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET balance = balance + %s WHERE telegram_id = %s RETURNING balance",
                    (coins, telegram_id),
                )
                new_balance = cur.fetchone()[0]
                conn.commit()
        return jsonify({
            "success": True,
            "message": f"{coins} QODEX qo‘shildi!",
            "balance": new_balance,
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Xatolik: {str(e)}"}), 500

# Admin uchun vazifa qo‘shish
@routes.route("/admin/add-task", methods=["POST"])
def add_task():
    data = request.get_json()
    name, description, link = data.get("name"), data.get("description"), data.get("link")

    if not name or not link:
        return jsonify({"success": False, "message": "Vazifa nomi va linki kiritilishi shart!"}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tasks (name, description, link) VALUES (%s, %s, %s) RETURNING id",
                    (name, description, link),
                )
                task_id = cur.fetchone()[0]
                conn.commit()
        return jsonify({"success": True, "message": "Vazifa qo‘shildi!", "task_id": task_id}), 201
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"success": False, "message": "Vazifa qo‘shishda xatolik!"}), 500

# Admin uchun vazifani tahrirlash
@routes.route("/admin/edit-task", methods=["POST"])
def edit_task():
    data = request.get_json()
    task_id, name, description, link = (
        data.get("task_id"),
        data.get("name"),
        data.get("description"),
        data.get("link"),
    )

    if not task_id:
        return jsonify({"success": False, "message": "Task ID kiritilishi shart!"}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE tasks SET name = %s, description = %s, link = %s WHERE id = %s",
                    (name, description, link, task_id),
                )
                conn.commit()
        return jsonify({"success": True, "message": "Vazifa yangilandi!"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Xatolik: {str(e)}"}), 500

# Admin uchun vazifani o‘chirish
@routes.route("/admin/delete-task", methods=["POST"])
def delete_task():
    data = request.get_json()
    task_id = data.get("task_id")

    if not task_id:
        return jsonify({"success": False, "message": "Task ID kiritilishi shart!"}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # To‘g‘ri SQL so‘rovi
                cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                conn.commit()
        return jsonify({"success": True, "message": "Vazifa o‘chirildi!"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Xatolik: {str(e)}"}), 500

# Statik fayllar
@routes.route("/tonconnect-manifest.json")
def tonconnect_manifest():
    return send_from_directory("static", "tonconnect-mani