from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # teaching assistant
    path('teaching_assistant/<int:teaching_assistant_id>', views.teaching_assistant_delete_or_update, name='teaching_assistant_delete_or_update'),
    path('teaching_assistant', views.teaching_assistant_index, name='teaching_assistant_index'),
    path('teaching_assistant_post', views.teaching_assistant_post, name='teaching_assistant_post'),

    # course template
    path('course_template/<int:course_template_id>', views.course_template_delete_or_update, name='course_template_delete_or_update'),
    path('course_template', views.course_template_index, name='course_template_index'),
    path('course_template_post', views.course_template_post, name='course_template_post'),

    # course
    path('course/<int:course_id>', views.course_delete_or_update, name='course_delete_or_update'),
    path('course', views.course_index, name='course_index'),
    path('course_post', views.course_post, name='course_post'),

    # exam
    path('exam/<int:exam_id>', views.exam_delete_or_update, name='exam_delete_or_update'),
    path('exam', views.exam_index, name='exam_index'),
    path('exam_post', views.exam_post, name='exam_post'),


    # assignment
    path('assignment/<int:assignment_id>', views.assignment_delete_or_update, name='assignment_delete_or_update'),
    path('assignment', views.assignment_index, name='assignment_index'),
    path('assignment_post', views.assignment_post, name='assignment_post'),

    # score
    path('score/<int:score_id>', views.score_delete_or_update, name='score_delete_or_update'),
    path('score', views.score_index, name='score_index'),

    # # question
    path('question/<int:question_id>', views.question_delete_or_update, name='question_delete_or_update'),
    path('question', views.question_index, name='question_index'),
    # path('question_post', views.question_post, name='question_post'),

    # query history
    path('query_history/<int:query_history_id>', views.query_history_delete_or_update, name='query_history_delete_or_update'),
    path('query_history', views.query_history_index, name='query_history_index'),
    # path('query_history_post', views.query_history_post, name='query_history_post'),

    # teacher
    path('teacher/<int:teacher_id>', views.teacher_delete_or_update, name='teacher_delete_or_update'),
    path('teacher', views.teacher_index, name='teacher_index'),
    path('teacher_post', views.teacher_post, name='teacher_post'),
]