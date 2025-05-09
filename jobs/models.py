from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from unidecode import unidecode



class Company(models.Model):
    name = models.CharField(max_length=255, unique=False)
    identification_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    logo = models.ImageField(upload_to='company_logos/',blank=True, null=True)
    publish_on_job_page = models.BooleanField(default=False)
    job_page_publish_expiration_date = models.DateTimeField(blank=True, null=True)  # Expiration for job page status
    slug = models.SlugField(unique=True, blank=True, null=True)
    fb_social = models.URLField(blank=True, null=True)
    insta_social = models.URLField(blank=True, null=True)
    linkedin_social = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    is_vip = models.BooleanField(default=False)  # Add VIP status field
    vip_expiration_date = models.DateTimeField(blank=True, null=True)  # Add expiration date

    @property
    def has_logo(self):
        return bool(self.logo and getattr(self.logo, 'name', ''))

    def save(self, *args, **kwargs):
        # --- Generate Slug if it doesn't exist ---
        # Use simplified condition: checks for None or empty string
        if not self.slug:
            if self.name: # Ensure there is a name to slugify
                transliterated_name = unidecode(self.name)
                # 2. Slugify the result (lowercase, spaces to hyphens, remove invalid chars)
                base_slug = slugify(transliterated_name)
            else:
                # Fallback if name is somehow empty
                base_slug = "company" # Or generate a random/timestamped one

            # Handle cases where transliteration + slugify results in empty string
            # (e.g., name contained only symbols removed by both steps)
            if not base_slug:
                 timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
                 base_slug = f"company-{timestamp}"

            unique_slug = base_slug
            counter = 1
            # Check for uniqueness against other Company slugs
            queryset = Company.objects.all()
            # If updating an existing instance, exclude itself from the uniqueness check
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

            # Loop until a unique slug is found
            while queryset.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            # Assign the unique slug
            self.slug = unique_slug

        # # Automatically update VIP status on save
        # if self.is_vip and self.vip_expiration_date and self.vip_expiration_date < timezone.now():
        #     self.is_vip = False
        #     self.vip_expiration_date = None
        #
        # # --- NEW: Automatically update Job Page Publish status on save ---
        # if self.publish_on_job_page and self.job_page_publish_expiration_date and self.job_page_publish_expiration_date < timezone.now():
        #     self.publish_on_job_page = False
        #     self.job_page_publish_expiration_date = None  # Clear the date
        # # --- END NEW ---

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class JobCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
class Location(models.Model):
    name = models.CharField(max_length=100, unique=True) # Adjust max_length if needed
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            transliterated = unidecode(self.name)
            self.slug = slugify(transliterated)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class JobTimeType(models.Model):
    name = models.CharField(max_length=50, unique=True) # Adjust max_length if needed
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name'] # Optional

class Job(models.Model):
    # REMOVED: LOCATION_TYPES list
    # REMOVED: JOB_TIME_TYPE list

    JOB_TYPES = [
        ('ვაკანსია', 'ვაკანსია'),
        ('ტრენინგი/განათლება', 'ტრენინგი/განათლება'),
        ('ტენდერი', 'ტენდერი'),
        ('სხვა', 'სხვა'),
    ]



    title = models.CharField(max_length=255)
    description = CKEditor5Field("Description", config_name="default")
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    post_with_logo = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_jobs = models.DateTimeField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='ვაკანსია')
    category = models.ManyToManyField(JobCategory, related_name='jobs', blank=True)
    is_vip = models.BooleanField(default=False)
    vip_expiration_date = models.DateTimeField(blank=True, null=True)
    company_page_small_job_description = models.TextField(blank=True, null=True)
    has_salary = models.BooleanField(blank=True, default=False)
    is_foreign_language = models.BooleanField(blank=True, default=False)

    salary_amount = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    salary_currency = models.CharField(max_length=3, choices=[
        ('USD', 'US Dollar'),
        ('GEL', 'Georgian Lari'),
        ('EUR', 'Euro'),
    ],blank=True, null=True)

    # CHANGED: Use ManyToManyField
    locations = models.ManyToManyField(Location, related_name='jobs')
    job_time_types = models.ManyToManyField(JobTimeType, related_name='jobs')

    exact_cities = models.CharField(max_length=255, blank=True, null=True)

    slug = models.SlugField(unique=True, blank=True, max_length=255) # Added slug field

    def _generate_unique_slug(self):
        """Generates a unique, transliterated slug for the job."""
        # Only generate if the slug is not already set
        # This prevents changing slugs on every save if not needed
        if not self.slug:
            # --- START Transliteration ---
            if self.title: # Ensure there is a title
                # 1. Transliterate Georgian title to Latin characters
                transliterated_title = unidecode(self.title)

                # 2. Slugify the transliterated title (handles spaces, lowercasing, removes remaining unwanted chars)
                base_slug = slugify(transliterated_title)
            else: # Fallback if title is empty for some reason
                base_slug = "job"
            # --- END Transliteration ---

            # Handle cases where transliteration + slugify might result in an empty string
            # (e.g., title was only symbols removed by both steps)
            if not base_slug:
                # More robust fallback using timestamp or potentially ID if available
                timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
                base_slug = f"job-{timestamp}"

            unique_slug = base_slug
            counter = 1
            # Check for uniqueness across jobs (important!)
            # Use .exclude(pk=self.pk) if updating an existing object to avoid self-collision
            # But since we check 'if not self.slug', this primarily runs for new objects
            # or objects explicitly needing a new slug.
            queryset = Job.objects.all()
            if self.pk: # If the object is already saved, exclude itself from the check
                queryset = queryset.exclude(pk=self.pk)

            while queryset.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug


    def save(self, *args, **kwargs):
        # Generate slug before saving if it's not set
        # This ensures slugs are created for new objects and can be regenerated
        # if manually cleared in the admin, for instance.
        self._generate_unique_slug() # Call slug generation

        # Existing VIP expiration logic (keep this)
        if self.is_vip and self.vip_expiration_date and self.vip_expiration_date < timezone.now():
            self.is_vip = False
            self.vip_expiration_date = None

        super().save(*args, **kwargs) # Call the "real" save() method.

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Returns the canonical URL for the job detail page."""
        from django.urls import reverse
        # Use the name defined in urls.py
        return reverse('job_detail', kwargs={'id': self.id, 'job_slug': self.slug})