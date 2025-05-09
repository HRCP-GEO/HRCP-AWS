from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

app = Celery('ConsPHRPLatform', broker=os.getenv('CELERY_BROKER_URL'))
