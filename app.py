from flask import Flask, session
from routes import routes  
from datetime import timedelta

app = Flask(__name__)

# Sessiyalarni faollashtirish va sozlash
app.secret_key = "supersecretkey"  
app.permanent_session_lifetime = timedelta(days=90)  # Sessiyalarni 90 kun saqlash

# Blueprint orqali marshrutlarni ro‘yxatdan o‘tkazish
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  # Lokal va tarmoqdan kirish uchun