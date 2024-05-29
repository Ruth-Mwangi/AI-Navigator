import datetime
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '../../')
sys.path.append(src_path)

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.models.user import User
from app.utils.util import create_mysql_connection, get_jwt_details
from app.models.token import TokenData
from app.models.user_in_db import UserInDB
from passlib.context import CryptContext  # For password hashing
import mysql.connector
import jwt


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """
    Verify the plain password against the hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Generate a hashed password.
    """
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    """
    Authenticate the user with the provided username and password.
    """
    conn=create_mysql_connection()
    user = get_user(conn, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    user.hashed_password=""
    return user

def get_user(db, username: str):
    """
    Get user details from the database by username.
    """
    # Connect to MySQL database
    conn = db
    if conn:
        try:
            # Create cursor
            cursor = conn.cursor(dictionary=True)
            
            # Execute query to fetch user by username
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            
            # Fetch user data
            user_data = cursor.fetchone()
            
            # Check if user exists
            if user_data:
                return UserInDB(**user_data)
            else:
                return None
        except mysql.connector.Error as e:
            print("Error fetching user:", e)
            return None
        finally:
            # Close connection
            conn.close()
    else:
        return None
    

def create_user(user_data: UserInDB):
        """
        Create a new user in the database.
        """
        print("here")
        conn=create_mysql_connection()
        
        if conn:
            try:
                cursor = conn.cursor()

                # Generate hashed password
                hashed_password = get_password_hash(user_data.hashed_password)

                # Execute query to insert new user
                query = "INSERT INTO users (username, email, full_name, hashed_password, disabled) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(query, (user_data.username, user_data.email, user_data.full_name, hashed_password, user_data.disabled))

                # Commit changes to database
                conn.commit()

                # Return the created user
                return UserInDB(username=user_data.username, email=user_data.email, full_name=user_data.full_name, hashed_password="", disabled=user_data.disabled)
            except mysql.connector.Error as e:
                print("Error creating user:", e)
                return None
            finally:
                # Close connection
                conn.close()
        else:
            return None


def create_access_token(username: str) -> str:
    jwt_details=get_jwt_details()
    SECRET_KEY = jwt_details.get('secret_key')
    ALGORITHM = jwt_details.get('algorithm')
    ACCESS_TOKEN_EXPIRE_MINUTES = jwt_details.get('access_token_expire_minutes')

    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> str:
    jwt_details = get_jwt_details()
    SECRET_KEY = jwt_details.get('secret_key')
    ALGORITHM = jwt_details.get('algorithm')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        # Check if the username exists in the database
        conn=create_mysql_connection()
        user = get_user(conn, username)
        if user:
            return username
        return None
    except jwt.PyJWKError:
        return None
    except jwt.ExpiredSignatureError:
        # Handle expired token error
        return None
    except Exception as e:
        # Log other exceptions for debugging purposes
        return None