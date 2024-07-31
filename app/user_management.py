import logging
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock user database for demonstration
# Generate the password hash for 'dragonphoenix'
hashed_password = generate_password_hash('dragonphoenix')
logger.info(f"Generated hashed password: {hashed_password}")

users = {
    'admin': {
        'password': hashed_password
    }
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

def load_user(user_id):
    if user_id in users:
        logger.info(f"User {user_id} found in database")
        return User(user_id)
    logger.warning(f"User {user_id} not found in database")
    return None
