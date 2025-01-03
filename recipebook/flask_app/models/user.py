from flask_app.config.mySQLconnection import connect_to_mysql
from datetime import datetime

from flask import flash

from flask_app import app
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

import re
db = "groceries"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    def __init__(self, db_data):
        self.id = db_data['id']
        self.first_name = db_data['first_name']
        self.last_name = db_data['last_name']
        self.email = db_data['email']
        self.password = db_data['password']
        self.created_at = db_data.get('created_at', datetime.now())
        self.updated_at = db_data['updated_at']

    @classmethod
    def save(cls, form_data):
        hashed_data = {
            'first_name': form_data["first_name"],
            'last_name': form_data["last_name"],
            'email': form_data["email"],
            'password': bcrypt.generate_password_hash(form_data['password'])
        }
        query = """
                INSERT INTO users (first_name,last_name,email,password)
                VALUES (%(first_name)s, %(last_name)s,%(email)s, %(password)s)
                """
        return connect_to_mysql(db).query_db(query, hashed_data)

    @classmethod
    def validate_reg(cls, form_data):
        is_valid = True
        if len(form_data['email']) < 1:
            flash("Email must not be blank", "register")
            is_valid = False
        elif not EMAIL_REGEX.match(form_data['email']):
            flash("Invalid email address", "register")
            is_valid = False
        elif User.get_by_email(form_data):
            flash("Email already in use", "register")
            is_valid = False
        if len(form_data['password']) < 8:
            flash("Password must be at least 8 characters", "register")
            is_valid = False
        if form_data['password'] != form_data['confirm_password']:
            flash("Passwords do not match", "register")
            is_valid = False        
        if len(form_data['first_name']) < 2:
            flash("First name must be at least 2 characters", "register")
            is_valid = False
        if len(form_data['last_name']) < 2:
            flash("Last name must be at least 2 characters", "register")
            is_valid = False
        return is_valid


    @staticmethod
    def validate_login(form_data):
        if not EMAIL_REGEX.match(form_data['email']):
            flash("invalid email/password", "login")
            return False
        
        user = User.get_by_email({'email': form_data['email']})
        if not user:
            flash("Invalid email/password", "login")
            return False
        
        if not bcrypt.check_password_hash(user.password, form_data['password']):
            flash("invalid email/password", "login")
            return False

        return user

    @classmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM users WHERE email = %(email)s"
        # data = {'email': email}
        result = connect_to_mysql(db).query_db(query, email)
        if not result:
            return False
        return cls(result[0])
    
    @classmethod
    def get_by_id(cls, id):
        query = "SELECT * FROM users WHERE id = %(id)s"
        data = {'id': id}
        result = connect_to_mysql(db).query_db(query, data)
        if not result or len(result) < 1:
            return False
        return cls(result[0])