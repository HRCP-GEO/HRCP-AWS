from django.contrib import admin
from .models import Job, Company, JobCategory, Location, JobTimeType


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    exclude = ('slug',)
    change_list_template = "jobs/job_change_list.html"

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context=extra_context or {})

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ('name',) # Allow searching by name
    exclude = ('slug',)
    change_list_template = "jobs/job_change_list.html"

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context=extra_context or {})

@admin.register(JobTimeType)
class JobTimeTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('id',)
    exclude = ('slug',)
    change_list_template = "jobs/job_change_list.html"

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context=extra_context or {})

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    autocomplete_fields = ['company']  # 👈 this replaces the dropdown with a searchable field
    search_fields = ['title']
    ordering = ['title']
    list_display = ('title', 'company', 'job_type', 'created_at')
    filter_horizontal = ['category','locations','job_time_types']
    exclude = ('slug',"company_page_small_job_description")
    change_list_template = "jobs/job_change_list.html"

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context=extra_context or {})

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']  # 👈 alphabetically ordered
    list_display = ('name', 'email', 'is_vip')

    change_list_template = "jobs/job_change_list.html"

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context=extra_context or {})
