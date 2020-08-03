from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('teaching_assistant/<int:teaching_assistant_id>', views.teaching_assistant_delete_or_update, name='teaching_assistant_delete_or_update'),
    path('teaching_assistant', views.teaching_assistant_index, name='teaching_assistant_index'),
    path('teaching_assistant_post', views.teaching_assistant_post, name='teaching_assistant_post'),
]