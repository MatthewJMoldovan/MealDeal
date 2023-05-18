from flask import Flask
from flask_bcrypt import Bcrypt
import openai as OPENAI
import os

app = Flask(__name__)

BCRPYT = Bcrypt(app)
DATABASE  = "Meal_Deal_DB"
app.secret_key = "password"

