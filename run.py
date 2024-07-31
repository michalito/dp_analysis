import os
import logging
from app import create_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    env = os.environ.get('ENV', 'development')
    logger.info(f"Starting app in {env} mode")
    
    if env == 'production':
        app.run(host='0.0.0.0', port=5000)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
