from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from ..models import Product, db, Component, ComponentVersion, ProductVersion, User, ProductInventory

product_bp = Blueprint('product', __name__, url_prefix='/product')

# Custom decorator for admin-only routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need admin privileges to access this page.')
            return redirect(url_for('product.index'))
        return f(*args, **kwargs)
    return decorated_function

@product_bp.route('/')
@login_required
def index():
    products = Product.query.all()
    available_components = Component.query.all()
    return render_template('product/index.html', 
                         products=products,
                         available_components=available_components)

@product_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        # Get form data
        component_ids = request.form.getlist('components')
        initial_inventory = int(request.form.get('inventory', 0))
        version = "1.0.0"  # Start with the new version format
        price = float(request.form.get('price'))
        
        # Check components availability
        components_available = True
        component_quantities = {}
        
        for component_id in component_ids:
            component = Component.query.get(component_id)
            if component:
                needed_quantity = initial_inventory
                if component.inventory < needed_quantity:
                    components_available = False
                    flash(f'Not enough {component.name} in stock. Need {needed_quantity}, but only have {component.inventory}.', 'error')
                component_quantities[component] = needed_quantity

        if not component_ids:
            flash('Please select at least one component for the product.', 'error')
            return redirect(url_for('product.index'))
            
        if not components_available:
            return redirect(url_for('product.index'))

        # Check if product already exists
        product = Product.query.filter_by(name=request.form.get('name')).first()
        
        if not product:
            # Create new product if it doesn't exist
            product = Product(
                name=request.form.get('name'),
                base_price=price,
                description=request.form.get('description'),
                category=request.form.get('category')
            )
            db.session.add(product)
            db.session.flush()  # Get product.id

        # Create inventory entry for this version
        inventory_entry = ProductInventory(
            product_id=product.id,
            version=version,
            inventory=initial_inventory,
            price=price
        )
        db.session.add(inventory_entry)

        # Add components if it's a new product
        if not product.components:
            for component, quantity in component_quantities.items():
                product.components.append(component)
                component.inventory -= quantity

        # Create version record
        version_record = ProductVersion(
            product_id=product.id,
            version_number=version,
            changes=request.form.get('changes', 'Initial product creation'),
            created_by=current_user.id
        )
        db.session.add(version_record)
        
        try:
            db.session.commit()
            flash('Product added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error creating product. Please try again.', 'error')
            
        return redirect(url_for('product.index'))
        
    return render_template('product/add_product.html')

@product_bp.route('/edit/<int:id>/<string:version>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product_inventory(id, version):
    inventory_entry = ProductInventory.query.filter_by(
        product_id=id, 
        version=version
    ).first_or_404()
    
    if request.method == 'POST':
        new_inventory = int(request.form.get('inventory', 0))
        inventory_change = new_inventory - inventory_entry.inventory
        
        if inventory_change > 0:
            # Check component availability
            components_available = True
            for component in inventory_entry.product.components:
                if component.inventory < inventory_change:
                    components_available = False
                    flash(f'Not enough {component.name} in stock for inventory increase.', 'error')
                    break
            
            if not components_available:
                return render_template('product/edit_inventory.html', entry=inventory_entry)
            
            # Update component inventory
            for component in inventory_entry.product.components:
                component.inventory -= inventory_change
        
        elif inventory_change < 0:
            # Return components to inventory
            for component in inventory_entry.product.components:
                component.inventory += abs(inventory_change)
        
        # Update inventory entry
        inventory_entry.inventory = new_inventory
        inventory_entry.price = float(request.form.get('price', inventory_entry.price))
        
        try:
            db.session.commit()
            flash('Product inventory updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating inventory. Please try again.', 'error')
            
        return redirect(url_for('product.inventory'))
        
    return render_template('product/edit_inventory.html', entry=inventory_entry)

@product_bp.route('/delete/<int:id>')
@login_required
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!')
    return redirect(url_for('product.index'))

@product_bp.route('/inventory')
@login_required
def inventory():
    products = Product.query.all()
    components = Component.query.all()
    return render_template('product/inventory.html', 
                         products=products, 
                         components=components)

@product_bp.route('/product/<int:id>/components')
@login_required
def view_components(id):
    product = Product.query.get_or_404(id)
    return render_template('product/components.html', product=product)

@product_bp.route('/component/<int:id>/versions')
@login_required
def component_versions(id):
    component = Component.query.get_or_404(id)
    return render_template('product/component_versions.html', component=component, User=User)

@product_bp.route('/component/<int:id>/new-version', methods=['GET', 'POST'])
@login_required
@admin_required
def new_component_version(id):
    component = Component.query.get_or_404(id)
    
    if request.method == 'POST':
        changes = request.form.get('changes', '')
        change_type = request.form.get('change_type', 'minor')
        is_production = request.form.get('is_production') == 'true'
        
        # Get the latest version using the new property
        latest_version = component.current_version
        new_version = increment_version(latest_version, change_type)
        
        # Create new version
        version = ComponentVersion(
            component_id=component.id,
            version_number=new_version,
            changes=changes,
            created_by=current_user.id,
            is_production=is_production
        )
        
        # Update all affected products with new versions
        for product in component.products:
            # Only create new product versions if this is a production component version
            if is_production:
                product_change_type = 'medium' if change_type in ['major', 'medium'] else 'minor'
                
                latest_product_version = product.current_version
                new_product_version = increment_version(latest_product_version, product_change_type)
                
                product_version = ProductVersion(
                    product_id=product.id,
                    version_number=new_product_version,
                    changes=f"Updated component {component.name} from {latest_version} to {new_version} ({change_type} change)",
                    created_by=current_user.id,
                    is_production=True
                )
                
                inventory = ProductInventory(
                    product_id=product.id,
                    version=new_product_version,
                    inventory=0,
                    price=product.base_price
                )
                
                db.session.add_all([product_version, inventory])
        
        db.session.add(version)
        
        try:
            db.session.commit()
            if is_production:
                flash(f'Component production version updated to {new_version}. Affected products have been updated.', 'success')
            else:
                flash(f'Component development version {new_version} created.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating version. Please try again.', 'error')
        
        return redirect(url_for('product.component_versions', id=id))
    
    return render_template('product/component_versions.html', component=component, User=User)

def increment_version(version, change_type):
    """
    Increment version based on change type: major, medium, or minor
    Version format: major.medium.minor (e.g., 1.0.0)
    """
    try:
        major, medium, minor = map(int, version.split('.'))
    except ValueError:
        # Handle legacy versions or invalid formats
        return "1.0.0"
    
    if change_type == 'major':
        major += 1
        medium = 0
        minor = 0
    elif change_type == 'medium':
        medium += 1
        minor = 0
    else:  # minor
        minor += 1
    
    return f"{major}.{medium}.{minor}"

@product_bp.route('/product/<int:id>/add_component', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product_component(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        # First create and commit the component
        component = Component(
            name=request.form.get('name'),
            description=request.form.get('description'),
            product_id=product.id,
            current_version="1.0"  # Initial version
        )
        
        db.session.add(component)
        db.session.commit()  # Commit first to get the component.id
        
        # Now create the component version with the valid component.id
        version = ComponentVersion(
            component_id=component.id,  # Now component.id exists
            version_number="1.0",
            changes="Initial component creation",
            created_by=current_user.id
        )
        
        db.session.add(version)
        db.session.commit()
        
        flash('Component added successfully!')
        return redirect(url_for('product.view_components', id=id))
    return render_template('product/add_component.html', product=product)

@product_bp.route('/product/<int:id>/versions')
@login_required
def view_versions(id):
    product = Product.query.get_or_404(id)
    return render_template('product/versions.html', product=product, User=User)

@product_bp.route('/product/<int:id>/new_version', methods=['GET', 'POST'])
@login_required
@admin_required
def new_version(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        changes = request.form.get('changes', '')
        change_type = request.form.get('change_type', 'minor')
        is_production = request.form.get('is_production') == 'true'
        
        # Get the latest version and increment it
        latest_version = product.current_version
        new_version = increment_version(latest_version, change_type)
        
        # Create new version
        version = ProductVersion(
            product_id=product.id,
            version_number=new_version,
            changes=changes,
            created_by=current_user.id,
            is_production=is_production
        )
        
        # Only create inventory entry for production versions
        if is_production:
            inventory = ProductInventory(
                product_id=product.id,
                version=new_version,
                inventory=0,  # Start with 0 inventory
                price=product.base_price  # Use base price for new version
            )
            db.session.add(inventory)
        
        db.session.add(version)
        
        try:
            db.session.commit()
            if is_production:
                flash(f'New production version {new_version} created. Add inventory as needed.', 'success')
            else:
                flash(f'Development version {new_version} created.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating version. Please try again.', 'error')
        
        return redirect(url_for('product.view_versions', id=id))
    
    return render_template('product/new_version.html', product=product)

@product_bp.route('/components')
@login_required
def list_components():
    components = Component.query.all()
    return render_template('product/component_list.html', components=components)

@product_bp.route('/component/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_standalone_component():
    if request.method == 'POST':
        # Create and commit the component
        component = Component(
            name=request.form.get('name'),
            description=request.form.get('description'),
            type=request.form.get('type'),
            inventory=int(request.form.get('inventory', 0)),
            min_stock=int(request.form.get('min_stock', 10))
        )
        
        db.session.add(component)
        db.session.commit()  # Commit first to get the component.id
        
        # Create the component version
        version = ComponentVersion(
            component_id=component.id,
            version_number="1.0",
            changes="Initial component creation",
            created_by=current_user.id
        )
        
        db.session.add(version)
        db.session.commit()
        
        flash('Component added successfully!', 'success')
        return redirect(url_for('product.list_components'))
    return render_template('product/add_component.html')

@product_bp.route('/component/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_component(id):
    component = Component.query.get_or_404(id)
    if request.method == 'POST':
        component.inventory = int(request.form.get('inventory', 0))
        component.min_stock = int(request.form.get('min_stock', 10))
        db.session.commit()
        flash('Component inventory updated successfully!', 'success')
        return redirect(url_for('product.inventory'))
    return render_template('product/edit_component.html', component=component)

@product_bp.route('/product/<int:id>/version/<string:version>/add-inventory', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product_inventory(id, version):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        quantity = int(request.form.get('quantity', 0))
        
        # Check component availability
        components_available = True
        for component in product.components:
            if component.inventory < quantity:
                components_available = False
                flash(f'Not enough {component.name} in stock. Need {quantity}, but only have {component.inventory}.', 'error')
                break
        
        if not components_available:
            return redirect(url_for('product.inventory'))
        
        # Create or update inventory entry
        inventory_entry = ProductInventory.query.filter_by(
            product_id=id, 
            version=version
        ).first()
        
        if inventory_entry:
            inventory_entry.inventory += quantity
        else:
            # Get price from latest version if exists, otherwise use base price
            latest_entry = product.inventory_entries[0] if product.inventory_entries else None
            price = latest_entry.price if latest_entry else product.base_price
            
            inventory_entry = ProductInventory(
                product_id=id,
                version=version,
                inventory=quantity,
                price=price
            )
            db.session.add(inventory_entry)
        
        # Update component inventory
        for component in product.components:
            component.inventory -= quantity
        
        try:
            db.session.commit()
            flash(f'Added {quantity} units to product version {version}', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating inventory. Please try again.', 'error')
        
        return redirect(url_for('product.inventory'))
    
    return render_template('product/add_inventory.html', product=product, version=version)
