from flask_app.config.mySQLconnection import connect_to_mysql
from flask_app.models.user import User
from flask import flash, session, request
from datetime import datetime

db = "recipebook"
class Recipe:
    def __init__(self, db_data):
        self.id = db_data['id']
        self.name = db_data.get('name', '')
        self.type = db_data.get('type', '')
        self.user_id = db_data.get('user_id', None)
        self.creator = None

    @classmethod
    def get_all(cls):
        query = """
        SELECT recipes.*, users.first_name, users.last_name, users.email, users.password, users.created_at, users.updated_at
        FROM recipes
        JOIN users ON recipes.user_id = users.id;
        """
        data = {
            "user_id": session['user_id']
        }
        results = connect_to_mysql(db).query_db(query, data)
        results = connect_to_mysql(db).query_db(query)
        print(results)
        recipes = []
        if results:
            for row in results:
                recipe = cls(row)
                user_data = {
                    "id": row["user_id"],
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                    "password": row["password"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                recipe.creator = User(user_data)
                recipes.append(recipe)
        return recipes
    
    @classmethod
    def get_by_user(cls, id):
        query = """
        SELECT *
        FROM recipes
        JOIN users ON recipes.user_id = users.id
        WHERE recipes.user_id = %(id)s;
        """
        data = {
            "id": id
        }
    
        results = connect_to_mysql(db).query_db(query, data)
        recipes = []
        for row in results:
            recipe = cls(row)
            user_data = {
                "id": row["user_id"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "email": row["email"],
                "password": row["password"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
            recipe.creator = User(user_data)
            recipes.append(recipe)
        return recipes
    @classmethod
    def make_recipe(cls, form_data):
        query = """ INSERT INTO recipes (name, type, user_id, created_at)
        VALUES (%(name)s, %(type)s, %(user_id)s, %(created_at)s);"""
        if 'need' not in form_data:
            form_data['need'] = False
        if 'date_added' not in form_data:
            form_data['date_added'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 'user_id' in session:
            form_data['user_id'] = session['user_id']
        if 'user_id' not in session:
            flash("User not logged in", "error")
            return False
        return connect_to_mysql(db).query_db(query, form_data)

    
    @classmethod
    def get_recipe_data_from_request(cls, id, recipe):
        return {
            "name": request.form["name"],
            "type": request.form["type"],
            "user_id": session['user_id']
        }

    @classmethod
    def update(cls, id, data):
        query = """UPDATE recipes 
                SET name=%(name)s, type=%(type)s, user_id=%(user_id)s 
                WHERE id = %(id)s;"""
        data["id"] = id
        return connect_to_mysql(db).query_db(query, data)


    @classmethod
    def delete(cls, id):
        query = "DELETE FROM recipes WHERE id = %(id)s"
        data = {
        "id": id
        }
        return connect_to_mysql(db).query_db(query, data)
    
    @classmethod
    def add_ingredients(cls, data, ingredients):
        query = """
        INSERT INTO ingredients (ingredient, created_at, recipe_id, user_id)
        VALUES (%(ingredient)s, %(created_at)s, %(recipe_id)s, %(user_id)s);
        """
        if 'user_id' in session:
            data["user_id"] = session['user_id']
        else:
            flash("User not logged in", "error")
            return False

        for ingredient in ingredients:
            data["ingredient"] = ingredient
            data["created_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            connect_to_mysql(db).query_db(query, data)
    
    @classmethod 
    def add_instructions(cls, data, instructions):
        query = """
        INSERT INTO instructions (instruction, created_at, recipe_id, user_id)
        VALUES (%(instruction)s, %(created_at)s, %(recipe_id)s, %(user_id)s);
        """
        if 'user_id' in session:
            data["user_id"] = session['user_id']
        else:
            flash("User not logged in", "error")
            return False

        for instruction in instructions:
            data["instruction"] = instruction
            data["created_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            connect_to_mysql(db).query_db(query, data)

    @classmethod
    def get_last_inserted_id(cls):
        query = "SELECT LAST_INSERT_ID() as id;"
        result = connect_to_mysql(db).query_db(query)
        return result[0]['id'] if result else None
    
    @classmethod
    def get_by_id(cls, id):
        query = "SELECT * FROM recipes WHERE id = %(id)s;"
        data = {
            "id": id
        }
        result = connect_to_mysql(db).query_db(query, data)
        if not result:
            return None
        return cls(result[0])
    
    @classmethod
    def get_one(cls, id):
        query = """
        SELECT *
        FROM recipes
        JOIN users ON recipes.user_id = users.id
        WHERE recipes.id = %(id)s;
        """
        data = {
            "id": id
        }
        result = connect_to_mysql(db).query_db(query, data)
        if not result:
            return None
        return cls(result[0])

    @classmethod
    def get_instructions(cls,id):
        query = "SELECT * FROM instructions WHERE recipe_id = %(id)s;"
        data = {
        "id": id
        }
        results = connect_to_mysql(db).query_db(query, data)
        instructions = []
        for row in results:
            instructions.append(row)
        return instructions

    @classmethod
    def get_ingredients(cls,id):
        query = "SELECT * FROM ingredients WHERE recipe_id = %(id)s;"
        data = {
            "id": id
        }
        results = connect_to_mysql(db).query_db(query, data)
        ingredients = []
        for row in results:
            ingredients.append(row)
        return ingredients
    
    @classmethod
    def update_instructions(cls, data, instructions):
        query = """
        UPDATE instructions
        SET instruction = %(instruction)s
        WHERE recipe_id = %(recipe_id)s;
        """
        for instruction in instructions:
            data["instruction"] = instruction
            connect_to_mysql(db).query_db(query, data)

    @classmethod
    def update_ingredients(cls, data, ingredients):
        query = """
        UPDATE ingredient
        SET ingredient = %(ingredient)s
        WHERE recipe_id = %(recipe_id)s;
        """
        for ingredient in ingredients:
            data["ingredient"] = ingredient
            connect_to_mysql(db).query_db(query, data)
    
    @classmethod
    def delete_instruction(cls, id):
        query = "DELETE FROM instructions WHERE instruction_id = %(id)s;"
        data = {
            "id": id
        }
        connect_to_mysql(db).query_db(query, data)

    @classmethod
    def delete_ingredient(cls, id):
        query = "DELETE FROM ingredients WHERE ingredient_id = %(id)s;"
        data = {
            "id": id
        }
        connect_to_mysql(db).query_db(query, data)