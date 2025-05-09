from celery import shared_task
from jobs.models import Job, Company
from django.utils import timezone

import logging # Import logging

logger = logging.getLogger(__name__) # Setup logger

@shared_task
def delete_expired_jobs():
    expired_jobs = Job.objects.filter(expired_jobs__lt=timezone.now())
    count = expired_jobs.count()
    expired_jobs.delete()
    return f"Deleted {count} expired jobs."

@shared_task
def check_company_vip_status():
    expired_vips = Company.objects.filter(
        is_vip=True,
        vip_expiration_date__lt=timezone.now()
    )
    for company in expired_vips:
        company.is_vip = False
        company.vip_expiration_date = None
        company.save()
    return f"Checked and updated {expired_vips.count()} companies' VIP status."

@shared_task
def check_job_vip_status():
    expired_job_vips = Job.objects.filter(
        is_vip=True,
        vip_expiration_date__lt=timezone.now()
    )
    for job in expired_job_vips:
        job.is_vip = False
        job.vip_expiration_date = None
        job.save()
    return f"Checked and updated {expired_job_vips.count()} jobs' VIP status."

# --- NEW TASK matching the requested pattern ---
@shared_task
def check_company_job_page_publish_status():
    """
    Checks for companies whose job page publication status has expired
    and updates them using individual .save() calls (matching user's existing pattern).
    """
    now = timezone.now()
    # Filter for companies needing update
    expired_companies = Company.objects.filter(
        publish_on_job_page=True,
        job_page_publish_expiration_date__isnull=False, # Check date exists
        job_page_publish_expiration_date__lt=now      # Check date is past
    )

    count = 0 # Keep track of updated count
    for company in expired_companies: # Loop through results
        try:
            company.publish_on_job_page = False
            company.job_page_publish_expiration_date = None
            company.save() # Individual save() call
            count += 1
        except Exception as e:
            # Log error if save fails for a specific company
            logger.error(f"Error updating company {company.id} job page status: {e}", exc_info=True)

    if count > 0:
        logger.info(f"Checked and updated {count} companies' job page publish status using individual saves.")

    # Return count or a descriptive string
    return f"Checked and updated {count} companies' job page publish status."
# --- END NEW TASK ---