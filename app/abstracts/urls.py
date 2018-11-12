from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_view, name='home_view'),
    path('works', views.WorkList.as_view(), name='work_list'),
    path('works/<int:pk>', views.WorkView.as_view(), name = 'work_detail'),
    path('tags', views.TagList.as_view(), name = 'tag_list'),
    path('tags/<int:pk>', views.TagView.as_view(), name = "tag_detail"),
    path('authors', views.AuthorList.as_view(), name = 'author_list'),
    path('authors/<int:pk>', views.AuthorView.as_view(), name = 'author_detail'),
    path('conferences', views.ConferenceList.as_view(), name = 'conference_list'),
    path('conferences/<int:pk>', views.ConferenceView.as_view(),
         name='conference_detail'),
    path('institutions', views.InstitutionList.as_view(), name = 'institution_list'),
    path('institutions/<int:pk>', views.InstitutionView.as_view(), name = 'institution_detail'),
    path('series', views.SeriesList.as_view(), name = "series_list"),
    path('series/<int:pk>', views.SeriesView.as_view(), name = "series_detail")
]
