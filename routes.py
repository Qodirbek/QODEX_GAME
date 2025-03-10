from flask import Blueprint, render_template, session, request, jsonify, redirect, url_for
import time
import random
import string

routes = Blueprint('routes', __name__)

# Foydalanuvchilar ma'lumotlari
users = {}

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
    user_data = users.setdefault(user_id, {
        "balance": 0, 
        "farming": False, 
        "farming_start": None
    })

    # Taymerni hisoblash
    remaining_time = 0
    if user_data["farming"]:
        elapsed_time = int(time.time()) - user_data["farming_start"]
        remaining_time = max(3600 - elapsed_time, 0)  # 1 soat taymer

        # Agar taymer tugagan bo‘lsa, "Claim" tugmasi yana chiqadi
        if remaining_time == 0:
            user_data["farming"] = False

    return render_template("home.html", username=user_id, balance=user_data["balance"], farming=user_data["farming"], remaining_time=remaining_time)

@routes.route('/earn')
def earn():
    """Referal tizimi va tasks orqali token ishlash sahifasi"""
    if "user_id" not in session:
        return redirect(url_for("routes.home"))

    user_id = session["user_id"]
    referral_link = f"{request.host_url}refer?ref={user_id}"

    return render_template("earn.html", username=user_id, balance=users[user_id]["balance"], referral_link=referral_link)

@routes.route('/claim', methods=['POST'])
def claim():
    """Claim tugmasi bosilganda balansga 1000 QODEX qo'shish"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Foydalanuvchi aniqlanmadi!"})

    user_id = session["user_id"]
    user_data = users[user_id]

    # Taymer tekshiruvi - foydalanuvchi 1 soat kutganmi?
    if user_data["farming"]:
        elapsed_time = int(time.time()) - user_data["farming_start"]
        if elapsed_time < 3600:
            return jsonify({"success": False, "message": f"Qayta bosish uchun {3600 - elapsed_time} soniya kuting!"})

    # Agar taymer tugagan bo'lsa, balansni oshiramiz va farming boshlaymiz
    user_data["balance"] += 1000
    user_data["farming"] = True
    user_data["farming_start"] = int(time.time())

    return jsonify({"success": True, "balance": user_data["balance"], "remaining_time": 3600})

@routes.route('/wallet')
def wallet():
    """Foydalanuvchi hamyoni"""
    if "user_id" not in session:
        return redirect(url_for("routes.home"))

    user_id = session["user_id"]
    balance = users[user_id]["balance"]

    return render_template("wallet.html", username=user_id, balance=balance)

@routes.route('/admin')
def admin():
    """Admin sahifasi - barcha foydalanuvchilarni ko‘rish"""
    if not users:
        return "Hali hech qanday foydalanuvchi yo‘q!"
    return render_template("admin.html", users=users)