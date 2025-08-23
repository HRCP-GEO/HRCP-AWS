from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from jobs.sitemaps import JobSitemap, CompanySitemap, StaticViewSitemap
handler404 = 'jobs.views.custom_404'
sitemaps = {
    'jobs': JobSitemap,
    'companies': CompanySitemap,
    'static': StaticViewSitemap,
}
urlpatterns = [


    path('admin/', admin.site.urls),
    path('', include('jobs.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt",content_type="text/plain"))

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)