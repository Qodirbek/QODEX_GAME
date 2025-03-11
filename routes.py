from flask import Blueprint, render_template, session, request, jsonify, redirect, url_for, send_from_directory
import time
import random
import string
import json
import os

# Blueprint yaratish
routes = Blueprint('routes', __name__)

# JSON fayl nomi
USER_DATA_FILE = "users.json"

# Foydalanuvchi ma'lumotlarini yuklash
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}  # Agar fayl buzilgan bo‘lsa, bo‘sh dict qaytarish
    return {}

# Foydalanuvchi ma'lumotlarini saqlash
def save_users():
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Barcha foydalanuvchilarni yuklash
users = load_users()

# Random ism yaratish funksiyasi
def generate_random_name():
    return "User-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

@routes.route('/')
def home():
    """Asosiy sahifa (Token ishlash sahifasi)"""
    session.permanent = True

    if "user_id" not in session:
        session["user_id"] = generate_random_name()

    user_id = session["user_id"]

    # Foydalanuvchi ma'lumotlarini yuklash yoki yangi yaratish
    if user_id not in users:
        users[user_id] = {
            "balance": 0,
            "farming": False,
            "farming_start": None,
            "wallet_address": None  # Wallet manzili bo‘sh
        }
        save_users()  # Yangi foydalanuvchini saqlash

    user_data = users[user_id]

    # Taymerni hisoblash
    remaining_time = 0
    if user_data["farming"] and user_data["farming_start"]:
        elapsed_time = int(time.time()) - user_data["farming_start"]
        if elapsed_time < 3600:
            remaining_time = 3600 - elapsed_time
        else:
            user_data["farming"] = False
            user_data["farming_start"] = None
            save_users()

    return render_template("home.html", 
                           username=user_id, 
                           balance=user_data["balance"], 
                           farming=user_data["farming"], 
                           remaining_time=remaining_time)

@routes.route('/claim', methods=['POST'])
def claim():
    """Claim tugmasi bosilganda balansga 1000 QODEX qo‘shish"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Foydalanuvchi aniqlanmadi!"})

    user_id = session["user_id"]
    user_data = users.get(user_id)

    if not user_data:
        return jsonify({"success": False, "message": "Foydalanuvchi topilmadi!"})

    # Agar farming boshlangan bo‘lsa, qancha vaqt qolgani
    if user_data["farming"] and user_data["farming_start"]:
        elapsed_time = int(time.time()) - user_data["farming_start"]
        if elapsed_time < 3600:
            return jsonify({"success": False, "message": f"Qayta bosish uchun {3600 - elapsed_time} soniya kuting!"})

    # Yangi token olish va farming boshlash
    user_data["balance"] += 1000
    user_data["farming"] = True
    user_data["farming_start"] = int(time.time())

    save_users()  # Ma'lumotlarni saqlash

    return jsonify({"success": True, "balance": user_data["balance"], "remaining_time": 3600})

@routes.route('/wallet', methods=['GET', 'POST'])
def wallet():
    """Foydalanuvchi hamyoni"""
    if "user_id" not in session:
        return redirect(url_for("routes.home"))

    user_id = session["user_id"]
    balance = users[user_id]["balance"]

    if request.method == 'POST':
        wallet_address = request.form.get('wallet_address')
        if wallet_address:
            users[user_id]["wallet_address"] = wallet_address
            save_users()

    wallet_address = users[user_id].get("wallet_address", "")

    return render_template("wallet.html", username=user_id, balance=balance, wallet_address=wallet_address)

@routes.route('/admin')
def admin():
    """Admin sahifasi - barcha foydalanuvchilarni ko‘rish"""
    return render_template("admin.html", users=users)

@routes.route('/earn')
def earn():
    """Earn sahifasi"""
    if "user_id" not in session:
        return redirect(url_for("routes.home"))

    user_id = session["user_id"]
    balance = users[user_id]["balance"]

    bot_username = "@QODEX_COINBot"
    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    return render_template("earn.html", 
                           username=user_id, 
                           balance=balance, 
                           referral_link=referral_link)

@routes.route('/watch-ad', methods=['POST'])
def watch_ad():
    """Reklama ko‘rish orqali 1,000 QODEX olish"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "User not found!"})

    user_id = session["user_id"]
    users[user_id]["balance"] += 1000
    save_users()

    return jsonify({"success": True, "balance": users[user_id]["balance"]})

@routes.route('/referral/<referrer_id>')
def referral(referrer_id):
    """Referal orqali qo‘shilgan foydalanuvchini ro‘yxatga olish"""
    session.permanent = True

    if "user_id" not in session:
        session["user_id"] = generate_random_name()

    user_id = session["user_id"]

    if user_id != referrer_id and user_id not in users:
        users[user_id] = {"balance": 0, "farming": False, "farming_start": None, "wallet_address": None}
        if referrer_id in users:
            users[referrer_id]["balance"] += 35000  # 35,000 QODEX bonus
        save_users()

    return redirect(url_for("routes.earn"))

@routes.route('/leaderboard')
def leaderboard():
    """Eng ko‘p QODEX ishlagan foydalanuvchilar ro‘yxati"""
    sorted_users = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)
    top_users = [{"username": user[0], "balance": user[1]["balance"]} for user in sorted_users[:10]]

    return render_template("leaderboard.html", top_users=top_users)

@routes.route('/reset', methods=['POST'])
def reset():
    """Foydalanuvchi balansini noldan boshlash"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "User not found!"})

    user_id = session["user_id"]
    users[user_id] = {"balance": 0, "farming": False, "farming_start": None, "wallet_address": None}
    save_users()

    return jsonify({"success": True, "message": "Balansingiz nollandi!", "balance": 0})

@routes.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)