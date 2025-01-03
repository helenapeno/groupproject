from flask import Flask, render_template, redirect, request, session, flash
from flask_app.models.user import User
from flask_app.models.recipe import Recipe
from flask_app.config import mySQLconnection
from flask_app import app

@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if 'user_id' in session:
        return redirect('/dashboard')
    
    user = User.validate_login(request.form)
    if not user:
        flash("Invalid login credentials", "login")
        return redirect('/')
    
    session['user_id'] = user.id
    return redirect('/dashboard')

@app.route('/user/login/process', methods=['POST'])
def login_process():
    logged_in_user = User.validate_login(request.form)
    if not logged_in_user:
        return redirect('/')
    session['user_id'] = logged_in_user.id
    return redirect('/dashboard')


@app.route('/register', methods=['POST'])
def register_success():
    if not User.validate_reg(request.form):
        return redirect('/')
    
    user_id = User.save(request.form)
    session['user_id'] = user_id
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')