from flask import render_template, redirect,request,session, flash
from flask_app import app, OPENAI
from flask_app.models.user_model import User
import os




@app.route('/')
def index():
    return render_template("index.html")

@app.route('/create_user', methods = ['POST'])
def create_user():
    
    if not User.validate(request.form):
        return redirect('/')
        
    User.create_user(request.form)
    return redirect('/')

@app.route('/secure_login', methods = ['POST'])
def secure_login():
    logged_in_user = User.validate_login(request.form)
    if not logged_in_user:
        return redirect('/')
        
    session['uid'] = logged_in_user.id
    return redirect('/user')

@app.route('/user')
def user():
    if not 'uid' in session:
        flash("Access Denied! Login First!")
        return redirect('/')
    
    logged_in_user = User.get_user_by_id(session['uid'])

    return render_template("show_user.html",user = logged_in_user)

@app.route('/edit_user')
def edit_user():
    if not 'uid' in session:
        flash("Access Denied! Login First!")
        return redirect('/')
    logged_in_user = User.get_user_by_id(session['uid'])
    return render_template("edit_user.html",user = logged_in_user)

@app.route('/save_edit', methods = ['POST'])
def save_edit():
    if not User.validate_user(request.form):
        return redirect('/edit_user')
    User.edit_user(request.form)
    return redirect('/user')



@app.route('/get_meal')
def get_meal():
    if not 'uid' in session:
        flash("Access Denied! Login First!")
        return redirect('/')
    
    logged_in_user = User.get_user_by_id(session['uid'])
    return render_template("get_meal.html",user = logged_in_user)

@app.route('/process_meal', methods = ['POST'])
def process_meal():
    logged_in_user = User.get_user_by_id(session['uid'])
    print(logged_in_user.get_daily_caloric_intake())
    
    meal_calories = int(logged_in_user.get_daily_caloric_intake())
    print(request.form)
    meal_type = request.form
    if meal_type["meal_type"] == "Breakfast":
        meal_calories = meal_calories * .20
    elif  meal_type["meal_type"] == "Lunch":
        meal_calories = meal_calories * .20
    elif  meal_type["meal_type"] == "Dinner":
        meal_calories = meal_calories * .30
    else:
        return meal_calories

    response = OPENAI.Completion.create(
        model="text-davinci-003",
        prompt=f"Give me a close to {meal_calories} calorie {meal_type['meal_type']} recipe that is moderate in protein that which includes cooking instructions, nutritional breakdown and measurements. be mindful of the listed alleregens and dislikes - {meal_type['preferences']}. Include the following ingredients in the meal - {meal_type['include']} ",
        temperature=1,
        max_tokens = 1000
        )
    session['output'] = response['choices'][0]['text']
    return redirect('/show_meal')

@app.route('/show_meal')
def show_meal():
    if not 'uid' in session:
        flash("Access Denied! Login First!")
        return redirect('/')

    logged_in_user = User.get_user_by_id(session['uid'])
    return render_template("show_meal.html",user = logged_in_user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')