from flask import Flask, render_template, session, request, jsonify, redirect, url_for
import time
import random
import string

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Foydalanuvchilar ma'lumotlarini saqlash
users = {}

# Random ism yaratish funksiyasi
def generate_random_name():
    return "User-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/')
def home():
    """Asosiy sahifa (Token ishlash sahifasi)"""
    session.permanent = True  # Sessiyani saqlash
    
    if "user_id" not in session:
        session["user_id"] = generate_random_name()

    user_id = session["user_id"]
    
    # Agar user bo‘lmasa, avtomatik qo‘shish
    user_data = users.setdefault(user_id, {"balance": 0, "last_claim": int(time.time()), "referral": None})
    
    return render_template("home.html", username=user_id, balance=user_data["balance"])

@app.route('/earn')
def earn():
    """Referal tizimi va tasks orqali token ishlash sahifasi"""
    if "user_id" not in session:
        return redirect(url_for("home"))

    user_id = session["user_id"]
    referral_link = f"{request.host_url}refer?ref={user_id}"

    return render_template("earn.html", username=user_id, balance=users[user_id]["balance"], referral_link=referral_link)

@app.route('/claim', methods=['POST'])
def claim():
    """Har soatda token olish"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Foydalanuvchi aniqlanmadi!"})

    user_id = session["user_id"]
    current_time = int(time.time())

    last_claim = users[user_id]["last_claim"]
    elapsed_time = current_time - last_claim  # Oxirgi claimdan beri qancha vaqt o‘tdi
    remaining_time = max(0, 3600 - elapsed_time)  # 1 soat (3600 soniya) sanash

    if remaining_time == 0:
        users[user_id]["balance"] += 1000
        users[user_id]["last_claim"] = current_time
        return jsonify({"success": True, "balance": users[user_id]["balance"], "next_claim": 3600})
    
    return jsonify({"success": False, "remaining_time": remaining_time})

@app.route('/wallet')
def wallet():
    """Foydalanuvchi hamyoni"""
    if "user_id" not in session:
        return redirect(url_for("home"))
    
    user_id = session["user_id"]
    balance = users[user_id]["balance"]
    
    return render_template("wallet.html", username=user_id, balance=balance)

@app.route('/admin')
def admin():
    """Admin sahifasi - barcha foydalanuvchilarni ko‘rish"""
    if not users:
        return "Hali hech qanday foydalanuvchi yo‘q!"
    return render_template("admin.html", users=users)

@app.route('/refer', methods=['GET'])
def refer():
    """Referal orqali token olish"""
    referrer_id = request.args.get("ref")
    if not referrer_id or referrer_id not in users:
        return redirect(url_for("home"))
    
    if "user_id" not in session:
        session["user_id"] = generate_random_name()

    user_id = session["user_id"]

    # Agar user allaqachon mavjud bo‘lsa va referal olmagan bo‘lsa
    if users[user_id]["referral"] is None and user_id != referrer_id:
        users[user_id]["referral"] = referrer_id
        users[referrer_id]["balance"] += 5000  

    return redirect(url_for("home"))

@app.route('/tasks', methods=['POST'])
def tasks():
    """Vazifalarni bajarib token ishlash"""
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Foydalanuvchi aniqlanmadi!"})

    user_id = session["user_id"]
    
    # Masalan, biror kanalga obuna bo‘lsa 2000 token oladi
    users[user_id]["balance"] += 2000  

    return jsonify({"success": True, "balance": users[user_id]["balance"]})

if __name__ == "__main__":
    app.run(debug=True)