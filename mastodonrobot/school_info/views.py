from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import SchoolInfo

@require_http_methods(["GET","POST"])
def index(request):
    school_info_list = SchoolInfo.objects.all()
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
            if new_data is None or new_data is '':
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

    return render(request, 'school_info/index.html', content_dict)