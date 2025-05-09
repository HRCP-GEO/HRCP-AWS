from django.urls import path
from .views import job_list, jobs_by_company, job_detail, post_job_ad, success_page, contact_page, faq_page, banner_page

urlpatterns = [
    path('', job_list, name="home"),
    path('kompania/<slug:company_slug>/', jobs_by_company, name="jobs_by_company"),
    path('vakansia/<int:id>/<slug:job_slug>/', job_detail, name='job_detail'),
    path('gancxadeba/', post_job_ad, name='post_job_ad'),
    path('success/', success_page, name='success_page'),
    path('kontakti/', contact_page, name='contact_page'),
    path('faq/', faq_page, name='faq_page'),
    path('reklama/', banner_page, name='banner_page'),

]
