from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User , Account
from config import Config
from sqlalchemy.exc import IntegrityError
from decorators import role_required

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Create database tables
with app.app_context():
    db.create_all()

# Signup endpoint
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        # Check if the username already exists before trying to add
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"error": "Username already exists"}), 400

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username already exists due to database constraint"}), 400
    except Exception as e:
        # Log the exception and rollback the session
        print(f"Error during signup: {e}")
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred during signup"}), 500

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token), 200

        return jsonify({"error": "Invalid username or password"}), 401

    except Exception as e:
        # Log the exception for debugging
        print(f"Error during login: {e}")
        return jsonify({"error": "An unexpected error occurred during login"}), 500

# Protected profile endpoint
@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at
        }), 200

    except Exception as e:
        # Log the exception for debugging
        print(f"Error retrieving profile: {e}")
        return jsonify({"error": "An unexpected error occurred while fetching the profile"}), 500

# accounts
@app.route('/accounts', methods=['POST'])
@jwt_required()
@role_required('admin')
def add_account():
    try:
        print('Adding account')
        current_user_id = get_jwt_identity()
        print(current_user_id)
        
        # Retrieve the current user by ID
        user = User.query.filter_by(id=current_user_id).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Get request data
        data = request.get_json()
        email = data.get('email')

        if not email or not data.get('name') or not data.get('contact_number'):
            return jsonify({'message': 'Missing required fields: name, email, or contact number'}), 400

        # Check if an account with the same email and added_by already exists
        existing_account = Account.query.filter_by(email=email, added_by=user.id).first()
        if existing_account:
            return jsonify({'message': 'Account with this email already exists'}), 409

        # Create a new account if it doesn't already exist
        new_account = Account(
            name=data['name'],
            email=email,
            contact_number=data['contact_number'],
            added_by=user.id  # Set the added_by field to the current user's ID
        )
        db.session.add(new_account)
        db.session.commit()
        print(new_account.id)
        return jsonify({'message': 'Account created successfully', 'account_id': new_account.id}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'A database integrity error occurred'}), 500
    except Exception as e:
        # Log the exception and provide a consistent error response
        print(f"Error adding account: {e}")
        db.session.rollback()
        return jsonify({'message': 'An unexpected error occurred while adding the account'}), 500


# accounts/<int:id>
@app.route('/accounts/<int:id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_account(id):
    try:
        data = request.get_json()
        
        # Find the account by ID
        account = Account.query.get(id)
        if not account:
            return jsonify({'message': 'Account not found'}), 404
        
        # Check if the new email already exists in the database (excluding the current account)
        new_email = data.get('email')
        if new_email and new_email != account.email:
            existing_account = Account.query.filter_by(email=new_email).first()
            if existing_account:
                return jsonify({'message': 'Email already exists'}), 409
        
        # Update account fields
        account.name = data.get('name', account.name)
        account.email = new_email if new_email else account.email
        account.contact_number = data.get('contact_number', account.contact_number)
        
        # Commit the changes
        db.session.commit()
        return jsonify({'message': 'Account updated successfully'}), 200
    
    except Exception as e:
        # Log the exception and return an error response
        print(f"Error updating account: {e}")
        db.session.rollback()
        return jsonify({'message': 'An error occurred while updating the account'}), 500

# delete /accounts/<int:id>
@app.route('/accounts/<int:id>', methods=['GET', 'DELETE'])
@jwt_required()
def manage_account(id):
    try:
        # Fetch account by ID for both GET and DELETE requests
        account = Account.query.get(id)
        if not account:
            return jsonify({'message': 'Account not found'}), 404

        if request.method == 'GET':
            # Return account details in response
            return jsonify({
                'id': account.id,
                'name': account.name,
                'email': account.email,
                'contact_number': account.contact_number,
                'added_by': account.added_by,
                'created_at': account.created_at
            }), 200

        elif request.method == 'DELETE':
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or user.role != 'admin':
                return jsonify({"message": "Access forbidden: Admin role required to delete account"}), 403

            # Delete account
            db.session.delete(account)
            db.session.commit()
            return jsonify({'message': 'Account deleted successfully'}), 200

    except Exception as e:
        # Log the exception and rollback the session
        print(f"Error managing account: {e}")
        db.session.rollback()
        return jsonify({'message': 'An error occurred while processing the request'}), 500


@app.route('/accounts', methods=['GET'])
@jwt_required()
# @role_required('admin')  # Only allow admins to view all accounts; adjust as needed
def get_accounts():
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)

        # Filtering, searching, and sorting parameters
        email_filter = request.args.get('email')
        search_name = request.args.get('search')
        sort_by = request.args.get('sort', 'name')  # Default sorting by 'name'
        sort_order = request.args.get('order', 'asc')  # Default order ascending

        # Start building the query
        query = Account.query

        # Apply filtering
        if email_filter:
            query = query.filter(Account.email.ilike(f"%{email_filter}%"))

        # Apply searching
        if search_name:
            query = query.filter(Account.name.ilike(f"%{search_name}%"))

        # Apply sorting
        if sort_by == 'name':
            if sort_order == 'desc':
                query = query.order_by(Account.name.desc())
            else:
                query = query.order_by(Account.name.asc())
        elif sort_by == 'email':
            if sort_order == 'desc':
                query = query.order_by(Account.email.desc())
            else:
                query = query.order_by(Account.email.asc())

        # Paginate the results
        accounts_query = query.paginate(page=page, per_page=limit, error_out=False)

        # Prepare response data
        accounts = [
            {
                "id": account.id,
                "name": account.name,
                "email": account.email,
                "contact_number": account.contact_number,
                # "added_by": account.added_by,
                "created_at": account.created_at
            }
            for account in accounts_query.items
        ]

        response = {
            "accounts": accounts,
            "total_records": accounts_query.total,
            "total_pages": accounts_query.pages,
            "current_page": accounts_query.page,
            "page_size": accounts_query.per_page
        }
        return jsonify(response), 200

    except Exception as e:
        # Log the exception and provide a consistent error response
        print(f"Error retrieving accounts: {e}")
        return jsonify({'message': 'An error occurred while retrieving accounts'}), 500


# Super Admin
@app.route('/user/<int:id>', methods=['PATCH'])
def update_user_role(id):
    try:
        # Verify Super Admin key from headers
        api_key = request.headers.get('Authorization')
        if api_key != Config.SU_ADMIN_ID:
            return jsonify({"error": "Unauthorized access"}), 403

        # Extract role from request data
        data = request.get_json()
        new_role = data.get('role')

        # Ensure the role is valid
        if new_role not in ["admin", "client"]:
            return jsonify({"error": "Invalid role. Must be 'admin' or 'client'."}), 400

        # Fetch user from database
        user = User.query.get(id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update the user role
        user.role = new_role
        db.session.commit()

        return jsonify({"message": f"User role updated to {new_role} successfully"}), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "A database integrity error occurred"}), 500
    except Exception as e:
        # Log the exception and return a consistent error response
        print(f"Error updating user role: {e}")
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred while updating the user role"}), 500


if __name__ == '__main__':
    app.run(debug=True)
