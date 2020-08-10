# Generated by Django 3.0 on 2020-08-10 01:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school_info', '0003_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('deleted_at', models.DateTimeField(default=None, null=True, verbose_name='deleted at')),
                ('course_code', models.CharField(max_length=64)),
                ('name', models.CharField(max_length=512)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameField(
            model_name='course',
            old_name='course_code',
            new_name='grade',
        ),
        migrations.RemoveField(
            model_name='course',
            name='name',
        ),
        migrations.AddField(
            model_name='course',
            name='teacher',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='school_info.Teacher', verbose_name='the related teacher'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='course_template',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='school_info.CourseTemplate', verbose_name='the related course template'),
            preserve_default=False,
        ),
    ]
