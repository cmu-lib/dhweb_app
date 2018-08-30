from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('version/<int:version_id>/', views.version_detail, name='version_detail')
]
