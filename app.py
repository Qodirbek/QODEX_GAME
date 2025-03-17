from flask import Flask, session
from routes import routes  
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# `.env` faylidagi ma'lumotlarni yuklash
load_dotenv()

app = Flask(__name__)

# Sessiyalarni faollashtirish va sozlash
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # `.env` dan olinadi yoki default
app.permanent_session_lifetime = timedelta(days=90)  # Sessiyalarni 90 kun saqlash

# Ma'lumotlar bazasi sozlamalari
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SQLAlchemy obyektini yaratish
db = SQLAlchemy(app)

# Blueprint orqali marshrutlarni ro‘yxatdan o‘tkazish
app.register_blueprint(routes)

# Ma'lumotlar bazasini yaratish (Agar yo‘q bo‘lsa)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  # Lokal va tarmoqdan kirish uchun