from os import getenv
from os.path import join, dirname, abspath
from dotenv import load_dotenv

basedir = abspath(dirname(__name__))
load_dotenv(join(basedir, '.env'))

FLASK_APP = 'app.py'
SECRET_KEY = str(getenv('SECRET_KEY'))

#Mongo
MONDO_DBNAME = str(getenv('MONGO_DBNAME'))
MONGO_URI = str(getenv('MONGO_URI'))

#Cloudinary
CLOUDINARY_CLOUD_NAME = str(getenv('CLOUDINARY_CLOUD_NAME'))
CLOUDINARY_API_KEY = str(getenv('CLOUDINARY_API_KEY'))
CLOUDINARY_API_SECRET = str(getenv('CLOUDINARY_API_SECRET'))

