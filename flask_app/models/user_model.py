from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE,BCRPYT 
from flask import flash, session
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    def __init__(self,data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.sex = data['sex']
        self.age = data['age']
        self.height = data['height']
        self.weight = data['weight']
        self.body_fat = data['body_fat']
        self.activity_level = data['activity_level']
        self.goal = data['goal']
        self.preferences = data['preferences']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']


# This creates a user
    @classmethod
    def create_user(cls,form):
        hashed_pw = BCRPYT.generate_password_hash(form['password'])
        data = {
            **form,
            "password" : hashed_pw
        }
        query = """INSERT INTO users (first_name,last_name,email,password,sex,age,height,weight,body_fat,activity_level,goal,preferences)
                VALUES(%(first_name)s,%(last_name)s,%(email)s,%(password)s,%(sex)s,%(age)s,%(height)s,%(weight)s,%(body_fat)s,%(activity_level)s,%(goal)s,%(preferences)s)"""
        return connectToMySQL(DATABASE).query_db(query,data)
    
# These get one user by a certain value
    @classmethod
    def get_user_by_email(cls, email):
        data = {
            'email' : email
        }
        query = "SELECT * FROM users WHERE email = %(email)s"
        results = connectToMySQL(DATABASE).query_db(query,data)
        if results:
            found_user = cls(results[0])
            return found_user
        else:
            return False

    @classmethod
    def get_user_by_id(cls, id):
        data = {
            'id' : id
        }
        query = "SELECT * FROM users WHERE id = %(id)s"
        results = connectToMySQL(DATABASE).query_db(query,data)
        if results:
            found_user = cls(results[0])
            return found_user
        else:
            return False

    @classmethod
    def edit_user(cls,data):
        query = """"UPDATE users
        SET sex = %(sex)s,age = %(age)s,height = %(height)s,weight = %(weight)s,body_fat = %(body_fat)s,activity_level = %(activity_level)s,goal = %(goal)s,preferences = %(preferences)s
        WHERE id = %(id)s"""
        results = connectToMySQL(DATABASE).query_db(query,data)
        return results
    
    @classmethod
    def get_daily_caloric_intake(cls):
        found_user = cls.get_user_by_id(session['uid'])
        weight_in_kg = int(found_user.weight)/2.2
        height_in_cm = int(found_user.height)*2.54
        HB = (66.47+(13.37*weight_in_kg)+(5*height_in_cm)-(6.75*int(found_user.age)))
        MSJ = ((10*weight_in_kg)+(6.25*height_in_cm)-(4.92*int(found_user.age))+5)
        FM = weight_in_kg*(int(found_user.body_fat)/100)
        FFM = weight_in_kg-FM
        NELSON = (25.8*FFM)+(4.04*FM)

        if (int(found_user.activity_level == 1)):
            activiy_level = 1.0
        elif int(found_user.activity_level == 2):
            activiy_level = 1.12
        elif int(found_user.activity_level == 3):
            activiy_level = 1.25
        elif int(found_user.activity_level == 4):
            activiy_level = 1.48
        else:
            activiy_level = 1.60

        dci = ((HB+MSJ+NELSON)*activiy_level)/3

        if (int(found_user.goal == 1)):
            dci = dci - 200
        elif int(found_user.goal == 2):
            dci = dci + 200
        elif int(found_user.goal == 3):
            dci = dci - 100
        else:
            dci = dci

        return dci
        


# These are validations for login and registration
    @classmethod
    def validate_login(cls,form):
        is_valid = True
        found_user = cls.get_user_by_email(form['email'])
        if not cls.get_user_by_email(form['email']):
            flash('Invalid Login!')
            return False
        else: 
            if not BCRPYT.check_password_hash(found_user.password, form['password']):
                flash("Invalid Login!")
                return False
        return found_user

    @staticmethod
    def validate(data):
        is_valid = True
        if len(data['first_name']) < 2:
            flash("First name is too short!")
            is_valid = False

        if len(data['last_name']) < 2:
            flash("Last name is too short!")
            is_valid = False

        if len(data['password']) < 4:
            flash("Password is too short!")
            is_valid = False

        if not EMAIL_REGEX.match(data['email']):
            flash("Email must be vaild!")
            is_valid = False

        if User.get_user_by_email(data['email']):
            flash("Email already in use!")
            is_valid = False

        if data['password'] != data['confirm_password']:
            flash("Your passwords don't match!")
            is_valid = False

        return is_valid
    

    @staticmethod
    def validate_user(data):
        is_valid = True
        if len(data['age']) < 1:
            flash("Please enter your age!")
        if len(data['height']) < 1:
            flash("Please enter your height!")
            is_valid = False
        if len(data['weight']) < 1:
            flash("Please enter your weight!")
            is_valid = False
        if len(data['body_fat']) < 1:
            flash("Please enter your body fat percentage")
            is_valid = False
        if len(data['preferences']) < 1:
            flash('Please enter any allergens or dislikes. If none please state "none"')
            is_valid = False

        return is_valid
