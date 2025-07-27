from flask import Flask, request, render_template, flash, redirect
from flask_mail import Mail, Message
import json
import os
from datetime import datetime

app = Flask(__name__)

# Load parameters from JSON file with error handling
try:
    config_path = r'D:\Portfolio App\confij.json'
    with open(config_path, 'r') as c:
        parame = json.load(c)["parame"]
except FileNotFoundError:
    print("Error: confij.json file not found!")
    print("Please create the config file with Gmail credentials")
    exit(1)
except KeyError:
    print("Error: 'parame' key not found in config file!")
    exit(1)
except json.JSONDecodeError:
    print("Error: Invalid JSON format in config file!")
    exit(1)

local_server = True
app.secret_key = 'nsluvurhozqetrxz'  # Consider using environment variable

# ✅ Mail configuration with error handling
try:
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_USERNAME=parame['Gmail_User'],
        MAIL_PASSWORD=parame['pass']
    )
except KeyError as e:
    print(f"Error: Missing key in config: {e}")
    exit(1)

mail = Mail(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    # Get form data with validation
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()
    
    # Basic validation
    if not all([name, email, message]):
        flash("All fields are required!", "danger")
        return redirect('/')
    
    # Basic email validation
    if '@' not in email or '.' not in email.split('@')[-1]:
        flash("Please enter a valid email address!", "danger")
        return redirect('/')
    
    # Length validation
    if len(name) > 100 or len(email) > 100 or len(message) > 1000:
        flash("Input too long! Please keep fields within reasonable limits.", "danger")
        return redirect('/')

    try:
        msg = Message(
            subject=f"New Message from {name}",
            sender=parame['Gmail_User'],
            recipients=[parame['Gmail_User']],
            body=f"Name: {name}\nEmail: {email}\nTime: {datetime.now()}\n\nMessage:\n{message}"
        )
        
        mail.send(msg)
        flash("Message sent successfully!", "success")
        
    except Exception as e:
        # Log the error for debugging
        print(f"Mail error: {str(e)}")
        flash("Message failed to send. Please try again later.", "danger")

    return redirect('/')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)