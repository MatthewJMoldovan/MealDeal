from flask_app import app, OPENAI
from flask_app.controllers import users_controller
import os



if __name__ == "__main__":
    app.run(debug=True)
    OPENAI.api_key = os.getenv("OPENAI_API_KEY")