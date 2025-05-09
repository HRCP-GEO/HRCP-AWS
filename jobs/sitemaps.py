# your_app/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.utils import timezone

from .models import Job, Company # Import your models
from django.urls import reverse

class JobSitemap(Sitemap):
    changefreq = "daily"  # How often job postings might change
    # priority = 0.8       # Higher priority than static pages

    def items(self):
        # Return active/non-expired jobs
        return Job.objects.filter(expired_jobs__gte=timezone.now()).order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at # Or an update timestamp if you have one

    # get_absolute_url is already defined on the model, Django uses it by default
    # If not, you'd define:
    # def location(self, obj):
    #     return reverse('job_detail', kwargs={'id': obj.id, 'job_slug': obj.slug})

class CompanySitemap(Sitemap):
    changefreq = "daily"
    # priority = 0.6

    def items(self):
        # Maybe only include companies with active job page status or VIP?
        return Company.objects.filter(publish_on_job_page=True) # Or filter as needed

    def lastmod(self, obj):
        return obj.created_at # Or an update timestamp

    # Assuming you have a URL pattern named 'jobs_by_company'
    def location(self, obj):
         # Ensure you have a URL pattern named 'jobs_by_company' taking a slug
         try:
             return reverse('jobs_by_company', kwargs={'company_slug': obj.slug})
         except: # Handle cases where URL might not exist or slug is missing
             return None


class StaticViewSitemap(Sitemap):
    # priority = 0.5
    changefreq = 'daily'

    def items(self):
        # List the names of your static views
        return ['home', 'post_job_ad', 'banner_page', 'faq_page', 'contact_page']

    def location(self, item):
        return reverse(item)