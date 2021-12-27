from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from django.template.loader import render_to_string


# Create your models here.





class Subject(models.Model):
    title = models.CharField(max_length= 20)
    slug = models.SlugField(max_length=300, unique=True)

  

    def __str__(self):
        return self.title

class Course(models.Model):
    owner = models.ForeignKey(User, related_name='created_courses', on_delete= models.CASCADE) 
    subject = models.ForeignKey(Subject, related_name= 'courses', on_delete=models.CASCADE)
    title = models.CharField(max_length=200 )   
    slug = models.SlugField(max_length=300, unique=True) 
    overview = models.TextField()  
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User,related_name='courses_joined',blank=True)


    class Meta:
        ordering = ['created']

    def __str__(self):
        return self.title
class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)#here we can have more than one course in a module
    title =models.CharField(max_length=300)
    description = models.TextField(blank =True)
    order = OrderField(blank=True, for_fields=['course'])

    def __str__(self):
        return f'{self.order}.{self.title}'
    class Meta:
        ordering = ['order']

class Content(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='contents')
    content_type = models.ForeignKey(ContentType, on_delete= models.CASCADE, limit_choices_to={'model__in':('text','video','image','file')})#limit choice 
    #is used limit the content type object used for the generic relation.then the 'model_in' to filter the querry to the content type
    #object with the model attribute in the parenthesis.
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id') 
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']    


# creating an abstract models below. all the child models would inherit from the itembase models. django will not create a database table for the itembasemodels.
class ItemBase(models.Model):
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete= models.CASCADE)#the class related would authomatically generate the related names for the other child models
    title = models.CharField(max_length=300)
    created= models.DateTimeField(auto_now_add=True)
    updated = models. DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True 

    def __str__(self):
        return self.title
    def render(self):
        return render_to_string(f'courses/content/{self._meta.model_name}.html',{'item': self})   
         

        
class Text(ItemBase):
    content = models.TextField
class Image(ItemBase):
      file  = models.FileField(upload_to='images')
class Video(ItemBase):
    url = models.URLField()
class File(ItemBase):
    file = models.FileField(upload_to='files')




