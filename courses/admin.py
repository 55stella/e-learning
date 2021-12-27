from django.contrib import admin

# Register your models here.
from .models import User, Subject, Course, Module, Content
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display =['title','slug']
    prepopulated_fields ={'slug':('title',)}
class ModuleInline(admin.StackedInline) :
    model = Module  
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'created']
    list_filter = ['created', 'subject']   
    search_fields =['title', 'overview']
    prepopulated_fileds={'slug':('title',)}# this is a field that is authomatically filled using a field from other fields.
    inlines = [ModuleInline] #the inline is used to connect to the module model simply because the are related. a user can access the module model through the course model

admin.site.register(Content)
admin.site.index_template = 'memcache_status/admin_index.html'

