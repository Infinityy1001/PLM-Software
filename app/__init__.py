from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Create db instance here
db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    from .models import User  # Import User here to avoid circular import
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///perfume.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'

    with app.app_context():
        # Import parts of our application
        from .models import User, Product
        from .views import auth, product

        # Register Blueprints
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(product.product_bp)

        @app.route('/')
        def home():
            return render_template('home.html')

        # Create tables and initialize data
        db.create_all()
        
        # Import and run init_db after db is created
        from .init_db import init_db
        init_db()

        return app
