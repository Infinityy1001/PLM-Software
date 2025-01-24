from . import db
from .models import User, Component, Product, ComponentVersion, ProductVersion, ProductInventory
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_db():
    # Check if database is already initialized
    if User.query.first() is not None:
        return

    # Create admin and test user
    admin = User(
        username="admin",
        password=generate_password_hash("admin123"),
        role="admin"
    )
    test_user = User(
        username="user",
        password=generate_password_hash("user123"),
        role="user"
    )
    db.session.add_all([admin, test_user])
    db.session.commit()

    # Create components
    components = [
        Component(name="Premium Rose Oil", type="Fragrance Oil", description="Luxurious rose essential oil", inventory=1000, min_stock=100),
        Component(name="Lavender Extract", type="Fragrance Oil", description="Calming lavender essence", inventory=1000, min_stock=100),
        Component(name="Vanilla Bean", type="Fragrance Oil", description="Rich vanilla fragrance", inventory=1000, min_stock=100),
        Component(name="Citrus Blend", type="Fragrance Oil", description="Energizing citrus mix", inventory=1000, min_stock=100),
        Component(name="Musk Base", type="Fragrance Oil", description="Deep musk foundation", inventory=1000, min_stock=100),
        Component(name="Luxury Glass Bottle", type="Bottle", description="Premium glass bottle", inventory=500, min_stock=50),
        Component(name="Gold Cap", type="Cap", description="Premium gold-plated cap", inventory=500, min_stock=50),
        Component(name="Premium Box", type="Box", description="Luxury packaging box", inventory=500, min_stock=50),
        Component(name="Designer Label", type="Label", description="Premium label design", inventory=500, min_stock=50),
        Component(name="Alcohol Base", type="Alcohol Base", description="Premium alcohol base", inventory=2000, min_stock=200),
    ]
    
    for component in components:
        db.session.add(component)
        version = ComponentVersion(
            component=component,
            version_number="1.0.0",
            changes="Initial component creation",
            created_by=admin.id,
            is_production=True  # Set initial versions as production
        )
        db.session.add(version)
    
    db.session.commit()

    # Create finance-themed products
    products = [
        {
            "name": "Eau de Wall Street",
            "description": "A powerful blend of success and ambition. Notes of freshly printed money and morning coffee.",
            "category": "Perfume",
            "base_price": 199.99,
            "components": components[:5] + components[5:9],
            "inventory": 100
        },
        {
            "name": "L'essence du Profit",
            "description": "A sophisticated fragrance that captures the sweet scent of positive returns. For the distinguished investor.",
            "category": "Cologne",
            "base_price": 299.99,
            "components": components[1:6] + components[5:9],
            "inventory": 50
        },
        {
            "name": "Parfum de Portfolio",
            "description": "A well-balanced blend, like a perfectly diversified portfolio. Notes of blue chip stability.",
            "category": "Perfume",
            "base_price": 149.99,
            "components": components[2:7] + components[5:9],
            "inventory": 150
        },
        {
            "name": "Crypto Mist",
            "description": "An unpredictable mix of highs and lows. Volatile notes that change with market sentiment.",
            "category": "Body Spray",
            "base_price": 89.99,
            "components": components[3:8] + components[5:9],
            "inventory": 200
        },
        {
            "name": "Eau de Dividend",
            "description": "A reliable fragrance that pays off consistently. Notes of steady returns and compound interest.",
            "category": "Perfume",
            "base_price": 399.99,
            "components": components[0:5] + components[5:9],
            "inventory": 30
        },
        {
            "name": "Le Premier IPO",
            "description": "Make a strong market debut. This initial public offering will have everyone wanting shares.",
            "category": "Cologne",
            "base_price": 249.99,
            "components": components[1:6] + components[5:9],
            "inventory": 75
        },
        {
            "name": "Brut Broker",
            "description": "A classic scent for the modern trader. Bold notes of market confidence and deal-closing power.",
            "category": "Cologne",
            "base_price": 179.99,
            "components": components[2:7] + components[5:9],
            "inventory": 120
        },
        {
            "name": "Chanel No. NYSE",
            "description": "Luxury meets liquidity in this premium blend. The essence of high-frequency elegance.",
            "category": "Perfume",
            "base_price": 449.99,
            "components": components[0:5] + components[5:9],
            "inventory": 25
        }
    ]

    for product_data in products:
        product = Product(
            name=product_data["name"],
            description=product_data["description"],
            category=product_data["category"],
            base_price=product_data["base_price"]
        )
        product.components.extend(product_data["components"])
        db.session.add(product)
        db.session.flush()  # Get product.id

        # Create initial version and inventory
        version = ProductVersion(
            product_id=product.id,
            version_number="1.0.0",
            changes="Initial product launch",
            created_by=admin.id,
            is_production=True  # Set initial versions as production
        )
        inventory = ProductInventory(
            product_id=product.id,
            version="1.0.0",
            inventory=product_data["inventory"],
            price=product_data["base_price"]
        )
        db.session.add_all([version, inventory])

    db.session.commit() 