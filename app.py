from flask import Flask
from routes import routes  # Yangi routes.py faylimizni yuklaymiz

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Sessiyalar uchun maxfiy kalit

# Blueprint orqali marshrutlarni ro‘yxatdan o‘tkazamiz
app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True)