from flask import Flask, request, render_template, flash, redirect
from flask_mail import Mail, Message
import json
import os
from datetime import datetime

app = Flask(__name__)

# Load config from JSON (relative path for deployment)
config_path = os.path.join(os.path.dirname(__file__), 'confij.json')
parame = {}

try:
    with open(config_path, 'r') as c:
        parame = json.load(c).get("parame", {})
except Exception as e:
    print(f"[Config Error] {str(e)}")

# Secret key
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default-secret-key")

# Mail Configuration
try:
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_USERNAME=parame.get('Gmail_User'),
        MAIL_PASSWORD=parame.get('pass')
    )
    mail = Mail(app)
except Exception as e:
    print(f"[Mail Config Error] {str(e)}")

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()

    # Basic validation
    if not all([name, email, message]):
        flash("All fields are required!", "danger")
        return redirect('/')
    
    if '@' not in email or '.' not in email.split('@')[-1]:
        flash("Please enter a valid email address!", "danger")
        return redirect('/')
    
    if len(name) > 100 or len(email) > 100 or len(message) > 1000:
        flash("Input too long! Please keep fields within reasonable limits.", "danger")
        return redirect('/')

    try:
        msg = Message(
            subject=f"New Message from {name}",
            sender=parame.get('Gmail_User'),
            recipients=[parame.get('Gmail_User')],
            body=f"Name: {name}\nEmail: {email}\nTime: {datetime.now()}\n\nMessage:\n{message}"
        )
        mail.send(msg)
        flash("Message sent successfully!", "success")
    except Exception as e:
        print(f"[Mail Send Error] {str(e)}")
        flash("Message failed to send. Please try again later.", "danger")

    return redirect('/')

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Don't run app here in production — WSGI server handles it (e.g., on PythonAnywhere)
if __name__ == "__main__":
    app.run(debug=True)
