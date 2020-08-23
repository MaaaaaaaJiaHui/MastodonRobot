import json
import datetime
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.serializers import serialize
from django.core.exceptions import ValidationError
from .models import SchoolInfo, TeachingAssistant, Course, Exam, Assignment, Question, QueryHistory, Teacher, Score, CourseTemplate

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

    # transfer all the user name capitalize
    user_name = user_name.lower()

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
        teaching_assistant.user_name = user_name.lower()
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


def generate_course_template_table():
    # transfer course_templates objects to table data
    course_templates = CourseTemplate.objects.all().filter(deleted_at__isnull=True)
    table = []
    for course_template in course_templates:
        table.append([
            course_template.course_code, 
            course_template.name,
            '<button type="button" class="btn btn-default" onclick="update_row($(this),{})">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(course_template.id, course_template.id)
        ])
    return table

@require_http_methods(["GET"])
def course_template_index(request):
    """
    Display course_template list page
    """
    content_dict = {}
    content_dict['course_templates'] = generate_course_template_table()
    content_dict['current_nav_id'] = 'nav-course-template'
    return render(request, 'course_template/index.html', content_dict)

@require_http_methods(["POST"])
def course_template_post(request):

    # get data from inputs
    course_code = request.POST.get('course_code', None)
    name = request.POST.get('name', None)

    # check if data illegal
    if course_code is None or course_code == '':
        result = {'status':'error', 'message':'Illegal course_template code!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if name is None or name == '':
        result = {'status':'error', 'message':'Illegal name!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    course_code = course_code.upper()

    # create new course_template
    course_template = CourseTemplate.objects.create(course_code=course_code, name=name)

    # transfer course_templates objects to table data
    table = generate_course_template_table()
    result = {'status':'success', 'message':'Create success!', 'data':{'table':table}}
    return HttpResponse(json.dumps(result))

@require_http_methods(["DELETE", "PUT"])
def course_template_delete_or_update(request, course_template_id):
    # get object
    course_template = CourseTemplate.objects.get(id=course_template_id, deleted_at__isnull=True)

    # check if data illegal
    if course_template is None:
        result = {'status':'error', 'message':'This course_template not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    if request.method == 'DELETE':
        # delete it
        course_template.delete()
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
        course_template.course_code = course_code.upper()
        course_template.name = name
        course_template.save()

        message = 'Update success!'

    table = generate_course_template_table()
    result = {'status':'success', 'message':message, 'data':{'table':table}}
    return HttpResponse(json.dumps(result))


def generate_course_table():
    # transfer courses objects to table data
    courses = Course.objects.all().filter(deleted_at__isnull=True)
    table = []
    for course in courses:
        table.append([
            '<span data-course_template_id="{}">{}</span>'.format(course.course_template.id, course.course_template.course_code),
            course.course_template.name,
            course.grade,
            '<span data-teacher_id="{}">{}</span>'.format(course.teacher.id, course.teacher.user_name),
            '<button type="button" class="btn btn-default" onclick="update_row($(this),{})">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(course.id, course.id)
        ])
    return table

@require_http_methods(["GET"])
def course_index(request):
    """
    Display course list page
    """
    course_templates = CourseTemplate.objects.all().filter(deleted_at__isnull=True)
    teachers = Teacher.objects.all().filter(deleted_at__isnull=True)
    content_dict = {}
    content_dict['courses'] = generate_course_table()
    content_dict['course_templates'] = course_templates
    content_dict['teachers'] = teachers
    content_dict['current_nav_id'] = 'nav-course'
    return render(request, 'course/index.html', content_dict)

@require_http_methods(["POST"])
def course_post(request):

    # get data from inputs
    grade = request.POST.get('grade', None)
    course_template_id = request.POST.get('course_template_id', None)
    teacher_id = request.POST.get('teacher_id', None)

    # check if data illegal
    if grade is None or grade == '':
        result = {'status':'error', 'message':'Illegal grade!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if course_template_id is None or course_template_id == '':
        result = {'status':'error', 'message':'Illegal course template!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if teacher_id is None or teacher_id == '':
        result = {'status':'error', 'message':'Illegal teacher!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    course_template_id = int(course_template_id)
    teacher_id = int(teacher_id)
    
    # find course template
    course_template = CourseTemplate.objects.get(id=course_template_id, deleted_at__isnull=True)
    if course_template is None:
        result = {'status':'error', 'message':'This course not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    # find teacher
    teacher = Teacher.objects.get(id=teacher_id, deleted_at__isnull=True)
    if teacher is None:
        result = {'status':'error', 'message':'This teacher not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))

    # create new course
    course = Course.objects.create(grade=grade, course_template=course_template, teacher=teacher)

    # transfer courses objects to table data
    table = generate_course_table()
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
        grade = put.get('grade', None)
        course_template_id = put.get('course_template_id', None)
        teacher_id = put.get('teacher_id', None)

        # check if data illegal
        if grade is None or grade == '':
            result = {'status':'error', 'message':'Illegal grade!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if course_template_id is None or course_template_id == '':
            result = {'status':'error', 'message':'Illegal course template!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if teacher_id is None or teacher_id == '':
            result = {'status':'error', 'message':'Illegal teacher!', 'data':{}}
            return HttpResponse(json.dumps(result))
        
        course_template_id = int(course_template_id)
        teacher_id = int(teacher_id)
        
        # find course template
        course_template = CourseTemplate.objects.get(id=course_template_id, deleted_at__isnull=True)
        if course_template is None:
            result = {'status':'error', 'message':'This course not exists!', 'data':{}}
            return HttpResponse(json.dumps(result))
        
        # find teacher
        teacher = Teacher.objects.get(id=teacher_id, deleted_at__isnull=True)
        if teacher is None:
            result = {'status':'error', 'message':'This teacher not exists!', 'data':{}}
            return HttpResponse(json.dumps(result))

        # update data
        course.course_template = course_template
        course.grade = grade
        course.teacher = teacher
        course.save()

        message = 'Update success!'

    table = generate_course_table()
    result = {'status':'success', 'message':message, 'data':{'table':table}}
    return HttpResponse(json.dumps(result))

def generate_exam_table():
    """
    Read all exam data and transfer them for display
    """
    # transfer exams objects to table data
    exams = Exam.objects.all().filter(deleted_at__isnull=True)
    table = []
    for exam in exams:
        if exam.exam_type == 0:
            display_exam_type = '<span data-exam_type="0">Offline</span>'
        else:
            display_exam_type = '<span data-exam_type="1">Online</span>'

        table.append([
            '<span data-course_id="{}">{} - {}</span>'.format(exam.course.id, exam.course.course_template.name, exam.course.grade),
            exam.name,
            exam.description,
            exam.exam_at.strftime("%Y-%m-%d %H:%M:%S"),
            display_exam_type,
            exam.location,
            exam.url,
            '<button type="button" class="btn btn-default" onclick="update_row($(this),{})">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(exam.id, exam.id)
        ])
    return table

@require_http_methods(["GET"])
def exam_index(request):
    """
    Display exam list page
    """
    courses = Course.objects.all().filter(deleted_at__isnull=True)

    content_dict = {}
    content_dict['exams'] = generate_exam_table()
    content_dict['courses'] = courses
    content_dict['current_nav_id'] = 'nav-exam'
    return render(request, 'exam/index.html', content_dict)

@require_http_methods(["POST"])
def exam_post(request):

    # get data from inputs
    name = request.POST.get('name', None)
    description = request.POST.get('description', None)
    exam_at = request.POST.get('exam_at', None)
    exam_type = int(request.POST.get('exam_type', None)) # 0: offline; 1: online
    location = request.POST.get('location', None)
    url = request.POST.get('url', None)
    course_id = request.POST.get('course_id', None)

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
    if course_id is None:
        result = {'status':'error', 'message':'Please select course!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    # transfer datetime
    exam_at = datetime.datetime.strptime(exam_at, "%Y-%m-%d %H:%M:%S")

    # find course
    course = Course.objects.get(id=course_id, deleted_at__isnull=True)
    if course is None:
        result = {'status':'error', 'message':'This course not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))

    # create new exam
    exam = Exam.objects.create(course=course, name=name, description=description, exam_at=exam_at, exam_type=exam_type, location=location, url=url)

    # transfer exams objects to table data
    table = generate_exam_table()
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
        course_id = int(put.get('course_id', None))

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
        if course_id is None:
            result = {'status':'error', 'message':'Please select course!', 'data':{}}
            return HttpResponse(json.dumps(result))

        # transfer datetime
        exam_at = datetime.datetime.strptime(exam_at, "%Y-%m-%d %H:%M:%S")

        # find course
        course = Course.objects.get(id=course_id, deleted_at__isnull=True)
        if course is None:
            result = {'status':'error', 'message':'This course not exists!', 'data':{}}
            return HttpResponse(json.dumps(result))
        
        # update data
        exam.course = course
        exam.name = name
        exam.description = description
        exam.exam_at = exam_at
        exam.exam_type = exam_type
        exam.location = location
        exam.url = url
        exam.save()

        message = 'Update success!'

    table = generate_exam_table()

    result = {'status':'success', 'message':message, 'data':{'table':table}}
    return HttpResponse(json.dumps(result))


def generate_assignment_table():
    """
    Read all exam data and transfer them for display
    """
    # transfer exams objects to table data
    assignments = Assignment.objects.all().filter(deleted_at__isnull=True)
    table = []
    for assignment in assignments:

        table.append([
            '<span data-course_id="{}">{} - {}</span>'.format(assignment.course.id, assignment.course.course_template.name, assignment.course.grade),
            assignment.name,
            assignment.description,
            assignment.deadline_at.strftime("%Y-%m-%d %H:%M:%S"),
            assignment.url,
            '<button type="button" class="btn btn-default" onclick="update_row($(this),{})">Edit</button> <button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(assignment.id, assignment.id)
        ])
    return table

@require_http_methods(["GET"])
def assignment_index(request):
    """
    Display assignment list page
    """
    courses = Course.objects.all().filter(deleted_at__isnull=True)
    content_dict = {}
    content_dict['assignments'] = generate_assignment_table()
    content_dict['courses'] = courses
    content_dict['current_nav_id'] = 'nav-assignment'
    return render(request, 'assignment/index.html', content_dict)

@require_http_methods(["POST"])
def assignment_post(request):

    # get data from inputs
    name = request.POST.get('name', None)
    description = request.POST.get('description', None)
    deadline_at = request.POST.get('deadline_at', None)
    url = request.POST.get('url', None)
    course_id = int(request.POST.get('course_id', None))

    # check if data illegal
    if name is None or name == '':
        result = {'status':'error', 'message':'Illegal name!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if description is None or description == '':
        result = {'status':'error', 'message':'Illegal description!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if deadline_at is None or deadline_at == '':
        result = {'status':'error', 'message':'Please input correct assignment time!', 'data':{}}
        return HttpResponse(json.dumps(result))
    if url is None:
        url = ''
    
    # transfer datetime
    deadline_at = datetime.datetime.strptime(deadline_at, "%Y-%m-%d %H:%M:%S")

    # find course
    course = Course.objects.get(id=course_id, deleted_at__isnull=True)
    if course is None:
        result = {'status':'error', 'message':'This course not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))

    # create new assignment
    assignment = Assignment.objects.create(course=course, name=name, description=description, deadline_at=deadline_at, url=url)

    # transfer assignments objects to table data
    table = generate_assignment_table()

    result = {'status':'success', 'message':'Create success!', 'data':{'table':table}}
    return HttpResponse(json.dumps(result))

@require_http_methods(["DELETE", "PUT"])
def assignment_delete_or_update(request, assignment_id):
    # get object
    assignment = Assignment.objects.get(id=assignment_id, deleted_at__isnull=True)

    # check if data illegal
    if assignment is None:
        result = {'status':'error', 'message':'This assignment not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    if request.method == 'DELETE':
        # delete it
        assignment.delete()
        message = 'Delete success!'
    elif request.method == 'PUT':
        from django.http import QueryDict
        put = QueryDict(request.body)

        # get data from inputs
        name = put.get('name', None)
        description = put.get('description', None)
        deadline_at = put.get('deadline_at', None)
        url = put.get('url', None)
        course_id = int(put.get('course_id', None))

        # check if data illegal
        if name is None or name == '':
            result = {'status':'error', 'message':'Illegal name!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if description is None or description == '':
            result = {'status':'error', 'message':'Illegal description!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if deadline_at is None or deadline_at == '':
            result = {'status':'error', 'message':'Please input correct assignment time!', 'data':{}}
            return HttpResponse(json.dumps(result))
        if url is None:
            url = ''
        
        # transfer datetime
        deadline_at = datetime.datetime.strptime(deadline_at, "%Y-%m-%d %H:%M:%S")

        # find course
        course = Course.objects.get(id=course_id, deleted_at__isnull=True)
        if course is None:
            result = {'status':'error', 'message':'This course not exists!', 'data':{}}
            return HttpResponse(json.dumps(result))
        
        # update data
        assignment.course = course
        assignment.name = name
        assignment.description = description
        assignment.deadline_at = deadline_at
        assignment.url = url
        assignment.save()

        message = 'Update success!'

    table = generate_assignment_table()

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
    teacher = Teacher.objects.create(user_name=user_name.lower(), email=email)

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
        teacher.user_name = user_name.lower()
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
    content_dict['current_nav_id'] = 'nav-query-history'
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

@require_http_methods(["GET"])
def score_index(request):
    """
    Display score list page
    """
    scores = Score.objects.all().filter(deleted_at__isnull=True)

    content_dict = {}
    content_dict['scores'] = scores
    content_dict['current_nav_id'] = 'nav-score'
    return render(request, 'score/index.html', content_dict)

@require_http_methods(["DELETE"])
def score_delete_or_update(request, score_id):
    # get object
    score = Score.objects.get(id=score_id, deleted_at__isnull=True)

    # check if data illegal
    if score is None:
        result = {'status':'error', 'message':'This score not exists!', 'data':{}}
        return HttpResponse(json.dumps(result))
    
    if request.method == 'DELETE':
        # delete it
        score.delete()
        message = 'Delete success!'

    scores = Score.objects.all().filter(deleted_at__isnull=True)
    table = []
    for score in scores:
        table.append([
            score.user_id, 
            score.score,
            score.suggestion,
            '<button type="button" class="btn btn-danger" onclick="delete_row({})">Delete</button>'.format(score.id)
        ])

    result = {'status':'success', 'message':message, 'data':{'table':table}}
    return HttpResponse(json.dumps(result))