from django.urls import path

from . import views

urlpatterns = [
    path('', views.WorkList.as_view(), name='index'),
    path('<int:pk>/', views.WorkView.as_view(), name = 'work_detail'),
    path('tag', views.TagList.as_view(), name = 'tag_list'),
    path('tag/<int:pk>', views.TagView.as_view(), name = "tag_detail"),
    path('author', views.AuthorList.as_view(), name = 'author_list'),
    path('author/<int:pk>', views.AuthorView.as_view(), name = 'author_detail'),
    path('conference', views.SubmissionList.as_view(), name = 'submission_list'),
    path('conference/<int:pk>', views.SubmissionView.as_view(), name = 'submission_detail'),
]
