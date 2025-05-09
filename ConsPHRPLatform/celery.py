import os
from celery import Celery
from celery.schedules import crontab

import os
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ConsPHRPLatform.settings')

app = Celery('ConsPHRPLatform', broker=os.getenv('CELERY_BROKER_URL'))
app.conf.timezone = 'Asia/Tbilisi'
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'delete_expired_jobs_every_midnight': {
        'task': 'jobs.tasks.delete_expired_jobs',
        'schedule': crontab(minute='*/1'),
    },
    'check_company_vip_status_every_minute': {
        'task': 'jobs.tasks.check_company_vip_status',
        'schedule': crontab(minute='*/1')
    },
    'check_job_vip_status_every_minute': {
        'task': 'jobs.tasks.check_job_vip_status',
        'schedule': crontab(minute='*/1')
    },
    # --- ADDED SCHEDULE FOR THE NEW TASK ---
    'check_company_job_page_publish_status_daily': {
        'task': 'jobs.tasks.check_company_job_page_publish_status',
        'schedule': crontab(minute='*/1'),
    }
    # --- END ADDED SCHEDULE ---
}