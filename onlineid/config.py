import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
INSTANCE_FOLDER = os.path.join(BASE_DIR, 'instance')
DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_FOLDER, 'app.db')}"
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
SECRET_KEY = os.environ.get('ONLINEID_SECRET_KEY', 'onlineid-secret-key-2024')
ADMIN_ROUTE = 'julisunkan'
