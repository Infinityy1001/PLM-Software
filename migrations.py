from app import create_app, db
from app.models import Component, Product

def update_database():
    app = create_app()
    with app.app_context():
        # Drop existing tables
        db.drop_all()
        # Create all tables with new schema
        db.create_all()
        # Add inventory and min_stock columns to Component table
        db.engine.execute('ALTER TABLE component ADD COLUMN inventory INTEGER DEFAULT 0')
        db.engine.execute('ALTER TABLE component ADD COLUMN min_stock INTEGER DEFAULT 10')

if __name__ == "__main__":
    update_database() 