Div Solution API Documentation

# Div Solution API Documentation

## Overview

The Div Solution API is designed to facilitate secure and efficient user authentication, account management, and role-based access control. This API is developed using Flask and PostgreSQL, leveraging JWT tokens for session handling and bcrypt for secure password hashing. It is built to ensure scalability and robust handling of user data and roles.

### Key Features:

- **User Authentication**: Secure login and signup endpoints.
- **Account Management**: Admin-level functionalities to manage accounts.
- **Role-Based Access Control**: Ensures users have the appropriate permissions based on their roles.

## Project Structure

- **Flask**: A lightweight web framework used to build the API.
- **PostgreSQL**: A reliable and powerful database system for storing user and account data.
- **JWT (JSON Web Tokens)**: Used for secure and stateless user sessions.
- **bcrypt**: Implements password hashing for secure credential storage.

## How to Run the App

### Prerequisites:

Ensure you have Python installed along with `pip`.

1.  **Clone the repository**:

        git clone https://github.com/username/div-solution-api.git
        cd div-solution-api

2.  **Install dependencies**:

        pip install -r requirements.txt

3.  **Run the application**:

        python app.py

4.  **Access the API**:

    By default, the API will be available at `http://localhost:5000`.

### Environment Variables:

Configure the environment variables needed for the API in a `.env` file or set them in your environment:

- `SECRET_KEY`
- `DATABASE_URL`
- `JWT_SECRET_KEY`

## API Endpoints

### 1\. Authentication

#### POST /signup

**Description**: Registers a new user with a unique username and hashed password.

**Request Body**:

    {
      "username": "string",
      "password": "string"
    }

**Responses**:

- `201 Created`: User created successfully.
- `400 Bad Request`: Missing username or password, or the username already exists.

#### POST /login

**Description**: Authenticates a user and provides a JWT token.

**Request Body**:

    {
      "username": "string",
      "password": "string"
    }

**Responses**:

- `200 OK`: Returns an access token.
- `401 Unauthorized`: Invalid credentials.

### 2\. Admin Endpoints

#### POST /accounts

**Description**: Creates a new account managed by the current admin.

**Request Body**:

    {
      "name": "string",
      "email": "string",
      "contact_number": "string"
    }

**Responses**:

- `201 Created`: Account created successfully.
- `400 Bad Request`: Missing required fields.
- `409 Conflict`: An account with this email already exists.

#### PUT /accounts/<id>

**Description**: Updates an existing account's information.

**Request Body**:

    {
      "name": "string",
      "email": "string",
      "contact_number": "string"
    }

**Responses**:

- `200 OK`: Account updated successfully.
- `404 Not Found`: Account not found.
- `409 Conflict`: Email already exists.

#### GET /accounts/<id>

**Description**: Retrieves details of a specific account.

**Responses**:

- `200 OK`: Returns account details.
- `404 Not Found`: Account not found.

#### DELETE /accounts/<id>

**Description**: Deletes a specific account.

**Responses**:

- `200 OK`: Account deleted successfully.
- `404 Not Found`: Account not found.

### 3\. Super Admin Endpoint

#### PATCH /user/<id>

**Description**: Allows a super admin to update a user's role.

**Headers**:

    Authorization: Super Admin Key

**Request Body**:

    {
      "role": "admin" | "client"
    }

**Responses**:

- `200 OK`: User role updated successfully.
- `403 Forbidden`: Unauthorized access.
- `400 Bad Request`: Invalid role.

## Additional Information

### JWT Authentication

The API uses JWT tokens for secure access to endpoints. After logging in, users receive a token to include in the request headers:

    Authorization: Bearer <token>

### Role-Based Access Control

The API includes role-based access control to manage user permissions:

- **Client**: Basic access with limited permissions.
- **Admin**: Permissions to manage accounts.
- **Super Admin**: Permissions to modify user roles and access levels.

### Database Models

#### User Model

- **username**: Unique identifier for the user.
- **password**: Securely hashed using bcrypt.
- **role**: Defines user access (e.g., admin, client).
- **created_at**: Timestamp of user creation.
- **updated_at**: Timestamp of last update.

#### Account Model

- **name**: Name associated with the account.
- **email**: Unique email for communication.
- **contact_number**: Phone number for the account.
- **added_by**: Refers to the admin who created the account.
- **created_at**: Timestamp of account creation.
