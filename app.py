from flask import Flask
from config import Config
from models import db
from routes import bp
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)


# Register the routes
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True,port=5000)
