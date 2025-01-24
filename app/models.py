from flask_login import UserMixin
from . import db 
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'

# Create an association table for the many-to-many relationship
product_components = db.Table('product_components',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('component_id', db.Integer, db.ForeignKey('component.id'), primary_key=True)
)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)  # Base price for the product
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    
    # Remove inventory and current_version from here as they'll be in ProductInventory
    versions = db.relationship('ProductVersion', backref='product', lazy=True)
    components = db.relationship('Component', 
                               secondary=product_components,
                               backref=db.backref('products', lazy=True))
    inventory_entries = db.relationship('ProductInventory', backref='product', lazy=True, order_by='desc(ProductInventory.created_at)')

    @property
    def current_version(self):
        """Get the current version from the latest inventory entry"""
        latest_entry = self.inventory_entries[0] if self.inventory_entries else None
        return latest_entry.version if latest_entry else "1.0"

    @property
    def current_inventory(self):
        """Get the current inventory level from the latest entry"""
        latest_entry = self.inventory_entries[0] if self.inventory_entries else None
        return latest_entry.inventory if latest_entry else 0

    @property
    def current_price(self):
        """Get the current price from the latest entry"""
        latest_entry = self.inventory_entries[0] if self.inventory_entries else None
        return latest_entry.price if latest_entry else self.base_price

class ProductVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    version_number = db.Column(db.String(10), nullable=False)
    changes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_production = db.Column(db.Boolean, default=False)

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50), nullable=False)
    inventory = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=10)
    versions = db.relationship('ComponentVersion', backref='component', lazy=True, order_by='desc(ComponentVersion.created_at)')

    @property
    def latest_version(self):
        """Get the latest version object"""
        return self.versions[0] if self.versions else None

    @property
    def current_version(self):
        """Get the current version number from the latest version entry"""
        latest = self.latest_version
        return latest.version_number if latest else "1.0.0"

    @property
    def is_available(self):
        return len(self.products) == 0

    @property
    def stock_status(self):
        if self.inventory <= 0:
            return "out_of_stock"
        elif self.inventory < self.min_stock:
            return "low_stock"
        return "in_stock"

class ComponentVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'), nullable=False)
    version_number = db.Column(db.String(10), nullable=False)
    changes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_production = db.Column(db.Boolean, default=False)

class ProductInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    version = db.Column(db.String(10), nullable=False)
    inventory = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)  # Specific price for this version
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def stock_status(self):
        if self.inventory <= 0:
            return "out_of_stock"
        elif self.inventory < 10:
            return "low_stock"
        return "in_stock"
