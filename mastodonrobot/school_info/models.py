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