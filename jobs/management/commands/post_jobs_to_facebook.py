import os
import logging
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse
from jobs.models import FacebookPost

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Post latest 5 jobs to Facebook Page using Graph API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--api-url",
            dest="api_url",
            default=None,
            help="Override jobs API URL (defaults to SITE_URL + /api/jobs/latest/)",
        )
        parser.add_argument(
            "--page-id",
            dest="page_id",
            default=None,
            help="Facebook Page ID (overrides env/settings)",
        )
        parser.add_argument(
            "--token",
            dest="access_token",
            default=None,
            help="Facebook Page access token (overrides env/settings)",
        )

    def handle(self, *args, **options):
        api_url = options.get("api_url")
        page_id = options.get("page_id") or os.getenv("FACEBOOK_PAGE_ID", getattr(settings, "FACEBOOK_PAGE_ID", None))
        access_token = options.get("access_token") or os.getenv("FACEBOOK_ACCESS_TOKEN", getattr(settings, "FACEBOOK_ACCESS_TOKEN", None))

        if not api_url:
            site_url = os.getenv("SITE_URL", getattr(settings, "SITE_URL", "")).rstrip("/")
            if not site_url:
                logger.error("SITE_URL is not set (env or settings). Use --api-url to override.")
                return
            api_url = f"{site_url}{reverse('latest_jobs_api')}"

        if not page_id or not access_token:
            logger.error("Missing FACEBOOK_PAGE_ID or FACEBOOK_ACCESS_TOKEN.")
            return

        logger.info("Fetching jobs from: %s", api_url)
        try:
            resp = requests.get(api_url, timeout=20)
            resp.raise_for_status()
            jobs = resp.json()
            if not isinstance(jobs, list):
                logger.error("API did not return a list.")
                return
        except Exception as e:
            logger.exception("Failed to fetch jobs from API: %s", e)
            return

        # Build set of already-posted job IDs
        posted_ids = set(FacebookPost.objects.values_list('job_id', flat=True))

        # Filter only new jobs
        new_jobs = [j for j in jobs if j.get('id') not in posted_ids]

        if not new_jobs:
            logger.info("No new jobs to post.")
            return

        fb_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        posted, failed = 0, 0
        for job in new_jobs:
            title = job.get("title", "")
            company = job.get("company", "")
            url = job.get("url", "")
            job_id = job.get("id")
            message = f"{company} - {title}\n{url}"
            data = {"message": message, "link": url, "access_token": access_token}
            try:
                r = requests.post(fb_url, data=data, timeout=20)
                if r.status_code == 200:
                    # Save record to avoid reposting next runs
                    try:
                        fb_post_id = (r.json() or {}).get('id')
                    except Exception:
                        fb_post_id = None
                    FacebookPost.objects.get_or_create(job_id=job_id, defaults={"facebook_post_id": fb_post_id})
                    logger.info("Posted job to Facebook: %s - %s", title, company)
                    posted += 1
                else:
                    logger.warning("Facebook API error %s posting %s - %s: %s", r.status_code, title, company, r.text)
                    failed += 1
            except Exception as e:
                logger.exception("Unexpected error posting job '%s' to Facebook: %s", title, e)
                failed += 1

        logger.info("Facebook posting complete. Posted: %s, Failed: %s", posted, failed)


