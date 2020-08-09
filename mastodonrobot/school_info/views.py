import json
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.serializers import serialize
from django.core.exceptions import ValidationError
from .models import SchoolInfo, TeachingAssistant, Course, Exam, Assignment, Question, QueryHistory, Teacher

@require_http_methods(["GET","POST"])
def index(request):
    school_info_list = SchoolInfo.objects.all().filter(deleted_at__isnull=True)
    school_info_dict = {}
    for info in school_info_list:
        school_info_dict[info.info_name] = info.info_value
    
    # if POST something, we would update info
    message = ''
    if request.method == 'POST':
        updated_data = {}
        for info in school_info_list:
            info_id = info.id
            info_name = info.info_name
            old_data = info.info_value

            new_data = request.POST.get(info_name, None)
            # if data is None or empty string, just continue
            if new_data is None or new_data == '':
                continue
            # if data is the same as old, just continue
            if new_data == old_data:
                continue

            # update data
            info.info_value = new_data
            info.save()
            message = 'Update done!'
            school_info_dict[info_name] = new_data

    content_dict = {}
    content_dict['school_info_dict'] = school_info_dict
    content_dict['message'] = message
    content_dict['current_nav_id'] = 'nav-school-info'

    return render(request, 'school_info/index.html', content_dict)

@require_http_methods(["GET"])
def teaching_assistant_index(request):
    """
    Display teaching assistant list page
    """
    teaching_assistants = TeachingAssistant.objects.all().filter(deleted_at__isnull=True)

    content_dict = {}
    content_dict['teaching_assistants'] = teaching_assistants
    content_dict['current_nav_id'] = 'nav-teaching-assistant'
    return render(request, 'teaching_assistant/index.html', content_dict)

@require_http_methods(["POST"])
def teaching_assistant_post(request):

    # get data from inputs
    user_name = request.POST.get('user_name', None)
    email = request.POST.get('email', None)

    # check if data illegal
    if user_name is None or user_name == '':
        result = {'status':'error', 'message':'Illegal name!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if email is None or email == '':
        result = {'status':'error', 'message':'Illegal email!', 'data':{}}
        return HttpResponse(json.dumps(result))

    # create new teaching assistant
    teaching_assistant = TeachingAssistant.objects.create(user_name=user_name, email=email)

    # transfer teaching assistants objects to table data
    teaching_assistants = TeachingAssistant.objects.all().filter(deleted_at__isnull=True)
    table = []
    for teaching_assistant in teaching_assistants:
        table.append([
            teaching_assistant.user_name, 
            teaching_assistant.email,
            '<button type="button" class="btn btn-default">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(teaching_assistant.id)
        ])

    result = {'status':'success', 'message':'Create success!', 'data':{'table':table}}
    return HttpResponse(json.dumps(result))

@require_http_methods(["DELETE", "PUT"])
def teaching_assistant_delete_or_update(request, teaching_assistant_id):

    # get object
    teaching_assistant = TeachingAssistant.objects.get(id=teaching_assistant_id, deleted_at__isnull=True)

    # check if data illegal
    if teaching_assistant is None:
        result = {'status':'error', 'message':'This teaching assistant not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    if request.method == 'DELETE':
        # delete it
        teaching_assistant.delete()
        message = 'Delete success!'
    elif request.method == 'PUT':
        from django.http import QueryDict
        put = QueryDict(request.body)

        # get data from inputs
        user_name = put.get('user_name', None)
        email = put.get('email', None)

        # check if data illegal
        if user_name is None or user_name == '':
            result = {'status':'error', 'message':'Illegal name!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if email is None or email == '':
            result = {'status':'error', 'message':'Illegal email!', 'data':{}}
            return HttpResponse(json.dumps(result))
        
        # update data
        teaching_assistant.user_name = user_name
        teaching_assistant.email = email
        teaching_assistant.save()

        message = 'Update success!'

    teaching_assistants = TeachingAssistant.objects.all().filter(deleted_at__isnull=True)
    table = []
    for teaching_assistant in teaching_assistants:
        table.append([
            teaching_assistant.user_name, 
            teaching_assistant.email,
            '<button type="button" class="btn btn-default">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(teaching_assistant.id)
        ])

    result = {'status':'success', 'message':message, 'data':{'table':table}}
    return HttpResponse(json.dumps(result))


@require_http_methods(["GET"])
def course_index(request):
    """
    Display course list page
    """
    courses = Course.objects.all().filter(deleted_at__isnull=True)

    content_dict = {}
    content_dict['courses'] = courses
    content_dict['current_nav_id'] = 'nav-course'
    return render(request, 'course/index.html', content_dict)

@require_http_methods(["POST"])
def course_post(request):

    # get data from inputs
    course_code = request.POST.get('course_code', None)
    name = request.POST.get('name', None)

    # check if data illegal
    if course_code is None or course_code == '':
        result = {'status':'error', 'message':'Illegal course code!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if name is None or name == '':
        result = {'status':'error', 'message':'Illegal name!', 'data':{}}
        return HttpResponse(json.dumps(result))

    # create new course
    course = Course.objects.create(course_code=course_code, name=name)

    # transfer courses objects to table data
    courses = Course.objects.all().filter(deleted_at__isnull=True)
    table = []
    for course in courses:
        table.append([
            course.course_code, 
            course.name,
            '<button type="button" class="btn btn-default">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(course.id)
        ])

    result = {'status':'success', 'message':'Create success!', 'data':{'table':table}}
    return HttpResponse(json.dumps(result))

@require_http_methods(["DELETE", "PUT"])
def course_delete_or_update(request, course_id):
    # get object
    course = Course.objects.get(id=course_id, deleted_at__isnull=True)

    # check if data illegal
    if course is None:
        result = {'status':'error', 'message':'This course not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    if request.method == 'DELETE':
        # delete it
        course.delete()
        message = 'Delete success!'
    elif request.method == 'PUT':
        from django.http import QueryDict
        put = QueryDict(request.body)

        # get data from inputs
        course_code = put.get('course_code', None)
        name = put.get('name', None)

        # check if data illegal
        if course_code is None or course_code == '':
            result = {'status':'error', 'message':'Illegal name!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if name is None or name == '':
            result = {'status':'error', 'message':'Illegal name!', 'data':{}}
            return HttpResponse(json.dumps(result))
        
        # update data
        course.course_code = course_code
        course.name = name
        course.save()

        message = 'Update success!'

    courses = Course.objects.all().filter(deleted_at__isnull=True)
    table = []
    for course in courses:
        table.append([
            course.course_code, 
            course.name,
            '<button type="button" class="btn btn-default">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(course.id)
        ])

    result = {'status':'success', 'message':message, 'data':{'table':table}}
    return HttpResponse(json.dumps(result))


@require_http_methods(["GET"])
def exam_index(request):
    """
    Display exam list page
    """
    exams = Exam.objects.all().filter(deleted_at__isnull=True)

    content_dict = {}
    content_dict['exams'] = exams
    content_dict['current_nav_id'] = 'nav-exam'
    return render(request, 'exam/index.html', content_dict)

@require_http_methods(["POST"])
def exam_post(request):

    # get data from inputs
    name = request.POST.get('name', None)
    description = request.POST.get('description', None)
    exam_at = request.POST.get('exam_at', None)
    exam_type = int(request.POST.get('exam_type', None)) # 0: real; 1: online
    location = request.POST.get('location', None)
    url = request.POST.get('url', None)

    # check if data illegal
    if name is None or name == '':
        result = {'status':'error', 'message':'Illegal name!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if description is None or description == '':
        result = {'status':'error', 'message':'Illegal description!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if exam_at is None or exam_at == '':
        result = {'status':'error', 'message':'Please input correct exam time!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if exam_type is None:
        result = {'status':'error', 'message':'Illegal exam type!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if exam_type == 0 and (location is None or location == ''):
        result = {'status':'error', 'message':'Please input location!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if url is None:
        url = ''

    # create new exam
    exam = Exam.objects.create(name=name, description=description, exam_at=exam_at, exam_type=exam_type, location=location, url=url)

    # transfer exams objects to table data
    exams = Exam.objects.all().filter(deleted_at__isnull=True)
    table = []
    for exam in exams:
        table.append([
            exam.name,
            exam.description,
            exam.exam_at,
            exam.exam_type,
            exam.location,
            exam.url,
            '<button type="button" class="btn btn-default">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(exam.id)
        ])

    result = {'status':'success', 'message':'Create success!', 'data':{'table':table}}
    return HttpResponse(json.dumps(result))

@require_http_methods(["DELETE", "PUT"])
def exam_delete_or_update(request, exam_id):
    # get object
    exam = Exam.objects.get(id=exam_id, deleted_at__isnull=True)

    # check if data illegal
    if exam is None:
        result = {'status':'error', 'message':'This exam not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    if request.method == 'DELETE':
        # delete it
        exam.delete()
        message = 'Delete success!'
    elif request.method == 'PUT':
        from django.http import QueryDict
        put = QueryDict(request.body)

        # get data from inputs
        name = put.get('name', None)
        description = put.get('description', None)
        exam_at = put.get('exam_at', None)
        exam_type = int(put.get('exam_type', None)) # 0: real; 1: online
        location = put.get('location', None)
        url = put.get('url', None)

        # check if data illegal
        if name is None or name == '':
            result = {'status':'error', 'message':'Illegal name!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if description is None or description == '':
            result = {'status':'error', 'message':'Illegal description!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if exam_at is None or exam_at == '':
            result = {'status':'error', 'message':'Please input correct exam time!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if exam_type is None:
            result = {'status':'error', 'message':'Illegal exam type!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if exam_type == 0 and (location is None or location == ''):
            result = {'status':'error', 'message':'Please input location!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if url is None:
            url = ''
        
        # update data
        exam.name = name
        exam.description = description
        exam.exam_at = exam_at
        exam.exam_type = exam_type
        exam.exam_type = exam_type
        exam.url = url
        exam.save()

        message = 'Update success!'

    exams = Exam.objects.all().filter(deleted_at__isnull=True)
    table = []
    for exam in exams:
        table.append([
            exam.name,
            exam.description,
            exam.exam_at,
            exam.exam_type,
            exam.location,
            exam.url,
            '<button type="button" class="btn btn-default">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(exam.id)
        ])

    result = {'status':'success', 'message':message, 'data':{'table':table}}
    return HttpResponse(json.dumps(result))

@require_http_methods(["GET"])
def teacher_index(request):
    """
    Display teacher list page
    """
    teachers = Teacher.objects.all().filter(deleted_at__isnull=True)

    content_dict = {}
    content_dict['teachers'] = teachers
    content_dict['current_nav_id'] = 'nav-teacher'
    return render(request, 'teacher/index.html', content_dict)

@require_http_methods(["POST"])
def teacher_post(request):

    # get data from inputs
    user_name = request.POST.get('user_name', None)
    email = request.POST.get('email', None)

    # check if data illegal
    if user_name is None or user_name == '':
        result = {'status':'error', 'message':'Illegal name!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if email is None or email == '':
        result = {'status':'error', 'message':'Illegal email!', 'data':{}}
        return HttpResponse(json.dumps(result))

    # create new teacher
    teacher = Teacher.objects.create(user_name=user_name, email=email)

    # transfer teachers objects to table data
    teachers = Teacher.objects.all().filter(deleted_at__isnull=True)
    table = []
    for teacher in teachers:
        table.append([
            teacher.user_name,
            teacher.email,
            '<button type="button" class="btn btn-default">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(teacher.id)
        ])

    result = {'status':'success', 'message':'Create success!', 'data':{'table':table}}
    return HttpResponse(json.dumps(result))

@require_http_methods(["DELETE", "PUT"])
def teacher_delete_or_update(request, teacher_id):
    # get object
    teacher = Teacher.objects.get(id=teacher_id, deleted_at__isnull=True)

    # check if data illegal
    if teacher is None:
        result = {'status':'error', 'message':'This teacher not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    if request.method == 'DELETE':
        # delete it
        teacher.delete()
        message = 'Delete success!'
    elif request.method == 'PUT':
        from django.http import QueryDict
        put = QueryDict(request.body)

        # get data from inputs
        user_name = put.get('user_name', None)
        email = put.get('email', None)

        # check if data illegal
        if user_name is None or user_name == '':
            result = {'status':'error', 'message':'Illegal name!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if email is None or email == '':
            result = {'status':'error', 'message':'Illegal email!', 'data':{}}
            return HttpResponse(json.dumps(result))
        
        # update data
        teacher.user_name = user_name
        teacher.email = email
        teacher.save()

        message = 'Update success!'

    teachers = Teacher.objects.all().filter(deleted_at__isnull=True)
    table = []
    for teacher in teachers:
        table.append([
            teacher.name,
            teacher.email,
            '<button type="button" class="btn btn-default">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(teacher.id)
        ])

    result = {'status':'success', 'message':message, 'data':{'table':table}}
    return HttpResponse(json.dumps(result))

@require_http_methods(["GET"])
def question_index(request):
    """
    Display question list page
    """
    questions = Question.objects.all().filter(deleted_at__isnull=True)

    content_dict = {}
    content_dict['questions'] = questions
    content_dict['current_nav_id'] = 'nav-question'
    return render(request, 'question/index.html', content_dict)

@require_http_methods(["DELETE"])
def question_delete_or_update(request, question_id):
    # get object
    question = Question.objects.get(id=question_id, deleted_at__isnull=True)

    # check if data illegal
    if question is None:
        result = {'status':'error', 'message':'This question not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    if request.method == 'DELETE':
        # delete it
        question.delete()
        message = 'Delete success!'

    questions = Question.objects.all().filter(deleted_at__isnull=True)
    table = []
    for question in questions:
        table.append([
            question.user_id, 
            question.user_name,
            question.question_content,
            '<button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(question.id)
        ])

    result = {'status':'success', 'message':message, 'data':{'table':table}}
    return HttpResponse(json.dumps(result))

@require_http_methods(["GET"])
def query_history_index(request):
    """
    Display query_history list page
    """
    query_history_list = QueryHistory.objects.all().filter(deleted_at__isnull=True)

    content_dict = {}
    content_dict['query_history_list'] = query_history_list
    content_dict['current_nav_id'] = 'nav-query_history'
    return render(request, 'query_history/index.html', content_dict)

@require_http_methods(["DELETE"])
def query_history_delete_or_update(request, query_history_id):
    # get object
    query_history = QueryHistory.objects.get(id=query_history_id, deleted_at__isnull=True)

    # check if data illegal
    if query_history is None:
        result = {'status':'error', 'message':'This query_history not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    if request.method == 'DELETE':
        # delete it
        query_history.delete()
        message = 'Delete success!'

    query_history_list = QueryHistory.objects.all().filter(deleted_at__isnull=True)
    table = []
    for query_history in query_history_list:
        table.append([
            query_history.user_id, 
            query_history.query_content,
            '<button type="button" class="btn btn-default">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(query_history.id)
        ])

    result = {'status':'success', 'message':message, 'data':{'table':table}}
    return HttpResponse(json.dumps(result))