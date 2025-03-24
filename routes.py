from datetime import datetime
from flask import request, render_template, session, jsonify, Blueprint, send_from_directory
import time
import psycopg2
import os

routes = Blueprint("routes", __name__)

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL") + "?sslmode=require")

def get_telegram_data():
    return (
        session.get("telegram_id"),  # user_id o'rniga telegram_id ishlatiladi
        session.get("telegram_username"),
        session.get("telegram_first_name"),
    )

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
                    "INSERT INTO users (telegram_id, balance, farming, farming_start, username, first_name) VALUES (%s, %s, %s, %s, %s, %s)",
                    (telegram_id, 0, False, None, telegram_username, telegram_first_name),
                )
                conn.commit()
                return 0, False, None, telegram_username, telegram_first_name

            return user[0], user[1], user[2], telegram_username, telegram_first_name

@routes.route("/")
def home():
    session.permanent = True
    session.modified = True

    if request.args.get("telegram_id"):
        session["telegram_id"] = request.args["telegram_id"]
    if request.args.get("username"):
        session["telegram_username"] = request.args["username"]

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

@routes.route("/earn")
def earn():
    telegram_id, _, _ = get_telegram_data()

    if not telegram_id:
        return "❌ Faqat Telegram orqali kirish mumkin!", 403

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance FROM users WHERE telegram_id = %s", (telegram_id,))
            user = cur.fetchone()
            balance = user[0] if user else 0

    referral_link = f"https://t.me/QODEX_COINBot?start={telegram_id}"
    return render_template("earn.html", username=telegram_id, balance=balance, referral_link=referral_link)

@routes.route("/admin")
def admin():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(""" 
                    SELECT id, telegram_id, username, first_name, last_name, balance, wallet_address 
                    FROM users 
                """)
                users = [
                    {
                        "id": u[0],
                        "telegram_id": u[1] or "No Telegram ID",
                        "username": u[2] or "No username",
                        "first_name": u[3] or "No first name",
                        "last_name": u[4] or "No last name",
                        "balance": u[5] or 0,
                        "wallet_address": u[6] or "No wallet"
                    }
                    for u in cur.fetchall()
                ]

        return render_template("admin.html", users=users)

    except Exception as e:
        return f"❌ Error: {str(e)}", 500

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
                    cur.execute("UPDATE users SET wallet_address = %s WHERE telegram_id = %s", (wallet_address, telegram_id))
                    conn.commit()

            cur.execute("SELECT balance, wallet_address FROM users WHERE telegram_id = %s", (telegram_id,))
            user = cur.fetchone()
            balance, wallet_address = user if user else (0, None)

    return render_template("wallet.html", username=telegram_id, balance=balance, wallet_address=wallet_address)

@routes.route("/save-wallet", methods=["POST"])
def save_wallet():
    try:
        telegram_id, _, _ = get_telegram_data()

        if not telegram_id:
            return jsonify({"success": False, "message": "❌ Faqat Telegram orqali kirish mumkin!"}), 403

        data = request.get_json()
        wallet_address = data.get("wallet_address")

        if not wallet_address:
            return jsonify({"success": False, "message": "Hamyon manzili kiritilmagan!"}), 400

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Foydalanuvchini tekshirish
                cur.execute("SELECT 1 FROM users WHERE telegram_id = %s", (telegram_id,))
                if not cur.fetchone():
                    return jsonify({"success": False, "message": "Foydalanuvchi topilmadi!"}), 404

                # Hamyon manzilini yangilash
                cur.execute("UPDATE users SET wallet_address = %s WHERE telegram_id = %s", 
                            (wallet_address, telegram_id))
                conn.commit()

        return jsonify({"success": True, "message": "✅ Hamyon manzili saqlandi!"})

    except Exception as e:
        print(f"[Xatolik] Database error: {e}")  # Log uchun
        return jsonify({"success": False, "message": "❌ Serverda xatolik yuz berdi!"}), 500

@routes.route("/claim", methods=["POST"])
def claim():
    telegram_id, _, _ = get_telegram_data()

    if not telegram_id:
        return jsonify({"success": False, "message": "❌ Faqat Telegram orqali kirish mumkin!"})

    current_time = int(time.time())

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance, farming, farming_start FROM users WHERE telegram_id = %s", (telegram_id,))
            user = cur.fetchone()

            if not user:
                return jsonify({"success": False, "message": "Foydalanuvchi topilmadi!"})

            balance, farming, farming_start = user
            farming_start_timestamp = int(farming_start.timestamp()) if farming_start else 0
            remaining_time = max(0, 3600 - (current_time - farming_start_timestamp))

            if remaining_time > 0:
                return jsonify({
                    "success": False,
                    "message": f"Qayta bosish uchun {remaining_time // 60}:{remaining_time % 60:02d} kuting!",
                    "remaining_time": remaining_time,
                })

            new_balance = balance + 1000
            cur.execute("UPDATE users SET balance = %s, farming = TRUE, farming_start = %s WHERE telegram_id = %s",
                        (new_balance, datetime.now(), telegram_id))
            conn.commit()

    return jsonify({"success": True, "message": "1000 QODEX qo'shildi!", "balance": new_balance, "remaining_time": 3600})

# **Referal ma'lumotlarini olish**
@routes.route("/get_referral_data", methods=["GET"])
def get_referral_data():
    telegram_id = request.args.get("telegram_id")

    if not telegram_id:
        return jsonify({"error": "No telegram_id provided"}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT balance FROM users WHERE telegram_id = %s", (telegram_id,))
                user = cur.fetchone()

                if not user:
                    return jsonify({"error": "User not found"}), 404

                cur.execute("SELECT COUNT(*) FROM users WHERE user_id = %s", (telegram_id,))
                referral_count = cur.fetchone()[0]

        return jsonify({"balance": user[0], "referral_count": referral_count})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to edit an existing task
@routes.route("/admin/edit-task", methods=["POST"])
def edit_task():
    data = request.get_json()
    task_id, new_name, new_desc, new_link = data.get("task_id"), data.get("name"), data.get("description"), data.get("link")

    if not task_id:
        return jsonify({"success": False, "message": "Task ID is required!"}), 400

    query = "UPDATE tasks SET name = %s, description = %s, link = %s WHERE id = %s"

    if execute_query(query, (new_name, new_desc, new_link, task_id)):
        return jsonify({"success": True, "message": "Task updated!"}), 200
    else:
        return jsonify({"success": False, "message": "Failed to update task"}), 500

# Route to delete a task
@routes.route("/admin/delete-task", methods=["POST"])
def delete_task():
    data = request.get_json()
    task_id = data.get("task_id")

    if not task_id:
        return jsonify({"success": False, "message": "Task ID is required!"}), 400

    query = "DELETE FROM tasks WHERE id = %s"

    if execute_query(query, (task_id,)):
        return jsonify({"success": True, "message": "Task deleted!"}), 200
    else:
        return jsonify({"success": False, "message": "Failed to delete task"}), 500

# Route to add a new task
@routes.route("/admin/add-task", methods=["POST"])
def add_task():
    data = request.get_json()
    name, description, link = data.get("name"), data.get("description"), data.get("link")

    if not name or not link:
        return jsonify({"success": False, "message": "Task name and link are required!"}), 400

    query = "INSERT INTO tasks (name, description, link) VALUES (%s, %s, %s) RETURNING id"
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (name, description, link))
                task_id = cur.fetchone()[0]
                conn.commit()
        return jsonify({"success": True, "message": "Task added!", "task_id": task_id}), 201
    except Exception as e:
        print("Database error:", e)
        return jsonify({"success": False, "message": "Failed to add task"}), 500

@routes.route('/add-coins', methods=['POST'])
def add_coins():
    data = request.get_json()
    coins = data.get('coins', 0)

    if not isinstance(coins, int) or coins <= 0:
        return jsonify({'success': False, 'message': 'Invalid coin amount!'}), 400

    telegram_id, _, _ = get_telegram_data()

    if not telegram_id:
        return jsonify({'success': False, 'message': '❌ Faqat Telegram orqali kirish mumkin!'}), 403

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT balance FROM users WHERE telegram_id = %s", (telegram_id,))
                user = cur.fetchone()

                if not user:
                    return jsonify({'success': False, 'message': 'User not found!'}), 404

                new_balance = user[0] + coins
                cur.execute("UPDATE users SET balance = %s WHERE telegram_id = %s", (new_balance, telegram_id))
                conn.commit()

        return jsonify({'success': True, 'message': f'{coins} QODEX qo‘shildi!', 'balance': new_balance})

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

# **Taymerni olish**
@routes.route("/get_timer", methods=["GET"])
def get_timer():
    telegram_id = get_user_identifier()
    current_time = int(time.time())

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT farming, farming_start FROM users WHERE user_id = %s", (telegram_id,))
            user = cur.fetchone()
            remaining_time = max(0, 3600 - (current_time - user[1].timestamp())) if user and user[0] and user[1] else 0

    return jsonify({"remaining_time": remaining_time})

@routes.route("/complete-task", methods=["POST"])
def complete_task():
    telegram_id = get_user_identifier()
    data = request.get_json()
    task_id = data.get("task_id")

    if not task_id:
        return jsonify({"success": False, "message": "Task ID not provided!"})

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM completed_tasks WHERE telegram_id = %s AND task_id = %s", (telegram_id, task_id))
            if cur.fetchone():
                return jsonify({"success": False, "message": "You have already completed this task!"})

            cur.execute("INSERT INTO completed_tasks (telegram_id, task_id) VALUES (%s, %s)", (telegram_id, task_id))
            cur.execute("UPDATE users SET balance = balance + 1000 WHERE telegram_id = %s RETURNING balance", (telegram_id,))
            new_balance = cur.fetchone()[0]
            conn.commit()

    return jsonify({"success": True, "message": "Task completed!", "balance": new_balance})

@routes.route("/tonconnect-manifest.json")
def tonconnect_manifest():
    return send_from_directory("static", "tonconnect-manifest.json")

@routes.route("/watch-ad", methods=["POST"])
def watch_ad():
    telegram_id, _, _ = get_telegram_data()

    if not telegram_id:
        return jsonify({"success": False, "message": "❌ Faqat Telegram orqali kirish mumkin!"})

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET balance = balance + 1000 WHERE telegram_id = %s RETURNING balance", (telegram_id,))
            new_balance = cur.fetchone()[0]
            conn.commit()

    return jsonify({"success": True, "message": "1000 QODEX qo'shildi!", "balance": new_balance})

@routes.route('/favicon.ico')
def favicon():
    return send_from_directory('static/images', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@routes.route("/static/path:filename")
def static_files(filename): return send_from_directory("static", filename)