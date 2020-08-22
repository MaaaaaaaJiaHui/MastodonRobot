from django.db import models
from django.utils import timezone

# Create your models here.
class BaseSchema(models.Model):
    created_at = models.DateTimeField("created at",auto_now_add=True)
    updated_at = models.DateTimeField("updated at",auto_now=True)
    deleted_at = models.DateTimeField("deleted at",null=True,default=None)

    def save(self, force_insert=False, force_update=False, using=None,
            update_fields=None):
        self.updated_at = timezone.now()
        super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()
    
    class Meta:
        # this means this class would be set as abstract class, it won't create a table
        # if we don't set abstract=True, it would throw exception when we call sub classes which extends from this class
        abstract = True

class SchoolInfo(BaseSchema):
    info_name = models.CharField(max_length=512)
    info_value = models.CharField(max_length=1024)

    def __str__(self):
        return self.info_name+':'+self.info_value

class CourseTemplate(BaseSchema):
    course_code = models.CharField(max_length=64)
    name = models.CharField(max_length=512)


class Teacher(BaseSchema):
    user_name = models.CharField(max_length=512)
    email = models.CharField(max_length=512)

    def __str__(self):
        return 'teacher '+self.user_name+')\'s email is '+self.email

class Course(BaseSchema):
    course_template = models.ForeignKey(
        CourseTemplate,
        on_delete=models.CASCADE,
        verbose_name="the related course template",
    )
    grade = models.CharField(max_length=64)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        verbose_name="the related teacher"
    )

    def __str__(self):
        return 'course {}(code is {}), teacher {} is teaching grade {}'.format(self.course_template.name, self.course_template.course_code, self.teacher.name, self.grade)

    def __str__(self):
        return 'course '+self.name+' code is '+self.course_code

class Exam(BaseSchema):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="the related course",
    )

    name = models.CharField(max_length=512)
    description = models.TextField()
    exam_at = models.DateTimeField("exam at",null=True,default=None)
    exam_type = models.IntegerField()
    location = models.CharField(max_length=512)
    url = models.CharField(max_length=1024)

    def __str__(self):
        return 'course '+self.course_name+' has an exam '+self.name+' at '+self.exam_at

class Assignment(BaseSchema):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="the related course",
    )

    name = models.CharField(max_length=512)
    description = models.TextField()
    deadline_at = models.DateTimeField("deadline at",null=True,default=None)
    url = models.CharField(max_length=1024)

    def __str__(self):
        return 'course '+self.course_name+' has an assignment '+self.name+' deadline is '+self.deadline_at

class Score(BaseSchema):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="the related course",
    )
    user_id = models.IntegerField()
    score = models.FloatField()
    suggestion = models.TextField()

    def __str__(self):
        return 'course '+self.course_name+' has an assignment '+self.name+' deadline is '+self.deadline_at

class Question(BaseSchema):
    user_id = models.IntegerField()
    user_name = models.CharField(max_length=512)
    question_content = models.TextField()

    def __str__(self):
        return self.user_name+' ask question:'+self.question_content

class QueryHistory(BaseSchema):
    user_id = models.IntegerField()
    query_title = models.CharField(max_length=512)
    query_content = models.TextField()

    def __str__(self):
        return 'user(id='+self.user_id+') queried info:'+self.query_content

class TeachingAssistant(BaseSchema):
    user_name = models.CharField(max_length=512)
    email = models.CharField(max_length=512)

    def __str__(self):
        return 'teaching assistant '+self.user_name+')\'s email is '+self.email