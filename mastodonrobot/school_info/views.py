import json
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.serializers import serialize
from django.core.exceptions import ValidationError
from .models import SchoolInfo, TeachingAssistant

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


@require_http_methods(["PUT"])
def teaching_assistant_put(request, id):

    

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