"""dhweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, reverse
from django.contrib.sitemaps import Sitemap, GenericSitemap
from django.contrib.sitemaps.views import index, sitemap
from django.contrib.flatpages.models import FlatPage
from abstracts import models


class CoreViewSitemap(Sitemap):
    protocol = "https"
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ["home_view", "conference_list", "standalone_conference_list"]

    def location(self, item):
        return reverse(item)


dh_sitemaps = {
    "sitemaps": {
        "series": GenericSitemap(
            {"queryset": models.ConferenceSeries.objects.all()},
            changefreq="monthly",
            priority=0.8,
            protocol="https",
        ),
        "work": GenericSitemap(
            {"queryset": models.Work.objects.all(), "date_field": "last_updated"},
            changefreq="monthly",
            priority=1.0,
            protocol="https",
        ),
        "author": GenericSitemap(
            {"queryset": models.Author.objects.all(), "date_field": "last_updated"},
            changefreq="monthly",
            priority=0.9,
            protocol="https",
        ),
        "flatpages": GenericSitemap(
            {"queryset": FlatPage.objects.all()}, changefreq="monthly", protocol="https"
        ),
        "core": CoreViewSitemap,
    }
}

urlpatterns = [
    path("", include("abstracts.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("filer/", include("filer.urls")),
    path("pages/", include("django.contrib.flatpages.urls")),
    path("sitemap.xml", index, dh_sitemaps),
    path(
        "sitemap-<section>.xml",
        sitemap,
        dh_sitemaps,
        name="django.contrib.sitemaps.views.sitemap",
    ),
]
