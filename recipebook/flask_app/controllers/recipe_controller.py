from flask_app import app
from flask import render_template, redirect, request, session, url_for, flash
from flask_app.models.user import User
from flask_app.models.recipe import Recipe
from datetime import datetime

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user = User.get_by_id(session['user_id'])
    if not user:
        return redirect('/login')
    recipes = Recipe.get_all()
    saved_recipes = Recipe.get_by_user(session['user_id'])
    return render_template('dashboard.html', user=user, recipes=recipes, saved_recipes=saved_recipes)

@app.route('/new_recipe', methods=['GET'])
def new_recipe():
    user = User.get_by_id(session['user_id'])
    if not user:
        return redirect('/login')
    return render_template('add.html', user=user)

@app.route('/add_recipe', methods=['POST'])
def make_recipe_process():
    if 'user_id' not in session:
        return redirect('/login')
    
    if not request.form["name"] or not request.form["type"]:
        flash("All fields are required", "error")
        return redirect('/new_recipe')
    
    data = {
        "name": request.form["name"],
        "type": request.form["type"],
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "user_id": session['user_id']
    }
    recipe_id = Recipe.make_recipe(data)
    data["recipe_id"] = recipe_id
    ingredients = request.form.getlist('ingredients[]') if 'ingredients[]' in request.form else []
    instructions = request.form.getlist('instructions[]') if 'instructions[]' in request.form else []

    if ingredients:
        Recipe.add_ingredients(ingredients=ingredients, data=data)
    if instructions and len(instructions) > 0:
        Recipe.add_instructions(instructions=instructions, data=data)

    return redirect('/dashboard')

@app.route('/recipe/<int:id>/edit', methods=['GET'])
def show_recipe(id):
    if 'user_id' not in session:
        return redirect('/login')
    recipe = Recipe.get_one(id)
    instructions = Recipe.get_instructions(id)
    ingredients = Recipe.get_ingredients(id)
    user = User.get_by_id(session['user_id'])
    return render_template('edit.html', recipe=recipe, user=user, instructions=instructions, ingredients=ingredients)

@app.route('/recipe/<int:id>/delete')
def delete_recipe(id):
    if 'user_id' not in session:
        return redirect('/login')
    recipe = Recipe.get_one(id)
    if not recipe or recipe.user_id != session['user_id']:
        return redirect('/dashboard')
    Recipe.delete(id)
    return redirect('/dashboard')

@app.route('/recipe/<int:id>/update', methods=['POST'])
def update_recipe(id):
    if 'user_id' not in session:
        return redirect('/login')
    recipe = Recipe.get_one(id)
    if not recipe or recipe.user_id != session['user_id']:
        return redirect('/dashboard')
    data = Recipe.get_recipe_data_from_request(id, recipe)
    Recipe.update(id, data)
    return redirect('/dashboard')

@app.route('/recipe/<int:id>/view')
def view_recipe(id):
    recipe = Recipe.get_one(id)
    ingredients = Recipe.get_ingredients(id)
    instructions = Recipe.get_instructions(id)
    return render_template('view.html',ingredients=ingredients, instructions=instructions, recipe=recipe)

@app.route('/update_instruction/<int:id>', methods=['POST'])
def update_instructions(id):
    instructions = request.form.getlist('instructions[]') if 'instructions[]' in request.form else []
    data = {
        "recipe_id": id
    }
    Recipe.update_instructions(instructions=instructions, data=data)
    return redirect('/dashboard')

@app.route('/update_ingredient/<int:id>', methods=['POST'])
def update_ingredients(id):
    ingredients = request.form.getlist('ingredients[]') if 'ingredients[]' in request.form else []
    data = {
        "recipe_id": id
    }
    Recipe.update_ingredients(ingredients=ingredients, data=data)
    return redirect('/dashboard')

@app.route('/delete_ingredient/<int:id>', methods=['POST'])
def delete_ingredient(id):
    Recipe.delete_ingredient(id)
    return redirect('/dashboard')

@app.route('/delete_instruction/<int:id>', methods=['POST'])
def delete_instruction(id):
    Recipe.delete_instruction(id)
    return redirect('/dashboard')