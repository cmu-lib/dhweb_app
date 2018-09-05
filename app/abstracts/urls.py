from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:work_id>/', views.work_detail, name = 'work_detail'),
    path('tag', views.IndexView.as_view(), name = 'tag_list'),
    path('tag/<int:pk>', views.DetailView.as_view(), name = "tag_detail"),
    path('author', views.IndexView.as_view(), name = 'author_list'),
    path('author/<int:pk>', views.DetailView.as_view(), name = 'author_detail')
]
