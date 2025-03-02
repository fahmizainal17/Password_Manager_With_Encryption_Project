from flask import Flask, render_template, request, redirect, url_for, flash, session
from password_manager import PasswordManager
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure secret key for session

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'logged_in' not in session:
        if request.method == 'POST':
            master_password = request.form.get('master_password')
            if master_password:
                session['master_password'] = master_password
                session['logged_in'] = True
                return redirect(url_for('index'))
        return render_template('index.html', login_page=True)
    
    # User is logged in
    password_manager = PasswordManager(session['master_password'])
    
    # Handle form submissions
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            website = request.form.get('website')
            username = request.form.get('username')
            password = request.form.get('password')
            
            if website and username and password:
                password_manager.save_password(website, username, password)
                flash('Password saved successfully!')
            else:
                flash('Please fill in all fields')
                
        elif action == 'delete':
            website = request.form.get('website')
            if password_manager.delete_password(website):
                flash(f'Password for {website} deleted!')
            else:
                flash(f'No password found for {website}')
    
    # Get all stored passwords (just the websites)
    passwords = password_manager.load_passwords()
    
    # If a website is selected, get its details
    selected_website = request.args.get('website')
    selected_password = None
    
    if selected_website:
        selected_password = password_manager.get_password(selected_website)
    
    return render_template('index.html', 
                          login_page=False, 
                          passwords=passwords, 
                          selected_website=selected_website,
                          selected_password=selected_password)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/debug')
def debug():
    if 'logged_in' not in session:
        return redirect(url_for('index'))
        
    try:
        with open('passwords.json', 'r') as f:
            raw_data = json.load(f)
            return render_template('debug.html', raw_data=raw_data)
    except (FileNotFoundError, json.JSONDecodeError):
        return "No password data found."

if __name__ == '__main__':
    app.run(debug=True)