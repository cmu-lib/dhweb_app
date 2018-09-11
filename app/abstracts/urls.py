from django.urls import path

from . import views

urlpatterns = [
    path('', views.WorkList.as_view(), name='index'),
    path('<int:pk>', views.WorkView.as_view(), name = 'work_detail'),
    path('tag', views.TagList.as_view(), name = 'tag_list'),
    path('tag/<int:pk>', views.TagView.as_view(), name = "tag_detail"),
    path('author', views.AuthorList.as_view(), name = 'author_list'),
    path('author/<int:pk>', views.AuthorView.as_view(), name = 'author_detail'),
    path('conference', views.ConferenceList.as_view(), name = 'conference_list'),
    path('conference/<int:pk>', views.ConferenceView.as_view(),
         name='conference_detail'),
    path('institution', views.InstitutionList.as_view(), name = 'institution_list'),
    path('institution/<int:pk>', views.InstitutionView.as_view(), name = 'institution_detail'),
]
