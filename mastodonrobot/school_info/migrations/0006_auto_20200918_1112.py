# Generated by Django 3.1 on 2020-09-18 03:12

from django.db import migrations

def init_school_info(apps, schema_editor):
    example_url = 'https://www.google.com'
    init_rows = [
        'school_newbie_info', 'school_official_website', 'school_contact_info', 'school_f_and_q'
    ]
    SchoolInfo = apps.get_model('school_info', 'SchoolInfo')
    for info_name in init_rows:
        SchoolInfo.objects.create(info_name=info_name, info_value=example_url)

class Migration(migrations.Migration):

    dependencies = [
        ('school_info', '0005_queryhistory_query_title'),
    ]

    operations = [
        migrations.RunPython(init_school_info),
    ]
