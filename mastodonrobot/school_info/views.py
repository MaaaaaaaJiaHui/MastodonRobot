from django.shortcuts import render

from .models import SchoolInfo


def index(request):
    school_info_list = SchoolInfo.objects.all()
    # context = {'latest_question_list': latest_question_list}
    return render(request, 'school_info/index.html')