from django.urls import path

from . import views
from .feeds import LatestPostsFeed

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),  # Function Based View
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),  # Function Based View with tags
    # path('', views.PostListView.as_view(), name='post_list'),  # Class Based View
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('<int:post_id>/comment/', views.post_comment, name='post_comment'),
    # Feed URLs
    path('feed/', LatestPostsFeed(), name='post_feed'),
    # Search URL
    path('search/', views.post_search, name='post_search'),
]
