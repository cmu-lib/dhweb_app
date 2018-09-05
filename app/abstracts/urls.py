from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('version/<int:version_id>/', views.version_detail, name='version_detail'),
    path('<int:work_id>/', views.work_detail, name = 'work_detail'),
    path('tag/<int:pk>', views.DetailView.as_view(), name = "detail")
]
