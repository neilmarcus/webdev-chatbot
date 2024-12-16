from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('new-post/', views.post_new, name="new-post"),
]
