from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Course
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, \
DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, \
PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content
from django.views.generic.detail import DetailView
from students.forms import CourseEnrollForm



from .models import Course

# Create your views here.

class ManageCourseListView(ListView):
    model = Course
    template_name = 'manage/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)#this methode is overiding the listView class method. this implies 
        #that this our managecourselistview is a child class and the child  method we are adopting is overiding 
        #the method in the parent class. the super function allows us to call the init function of the mother class.
        #sothis method does two things, allow users to retrieve course in which they created. also allow a user to update, delete
        # and create views. # calling a super class implies that we calling on the super class to get the base querry set
        #we then filters it to ensure that courses ownened by the current user is returned or user that is logged in




class OwnerMixin(object):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)# theis method would most likely be used in dealing with form fields that contains the owner attribute
class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user# this is saving the form instance to the logged in user.
        return super().form_valid(form)# this function is taking in form. 
class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')#redirects user after a form is successfully submitted or object is created. used by create view, update view and the delete view.
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'manage/course/form.html'
class ManageCourseListView(OwnerCourseMixin, ListView):# lists all the courses created by the user
    template_name = 'manage/course/list.html'
    permission_required ='courses.view_course'
class CourseCreateView(OwnerCourseEditMixin, CreateView):# the owner courseEdit mixen is used by views with  forms. executed when the summited form is valid.# uses the fields supplied in ownercoursemixen to create
    #form. it also subclasses create view.it also uses the templates supplied in ownercourse edit mixin.
    permission_required = 'courses.add_course'
class CourseUpdateView(OwnerCourseEditMixin,UpdateView):# allows the edditing of an existing objects,uses the fields supplied in ownercoursemixin. uses  the template defined in owner
    #courseeditmixin.
    permission_required = 'courses.change_course'
class CourseDeleteView(OwnerCourseMixin, DeleteView):# it inherits from owner coursemixin. generates a specific templat_name for  a specific template to comfirm deletion.
    template_name = 'manage/course/delete.html'
    permission_required = 'courses.delete_course'        
    #generally what i learnt from class mixin is that it combined different functionality of different class to achieve a goal in a specific view.


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'manage/module/formset.html'
    course = None
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,
        data=data)
    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,
        id=pk,
        owner=request.user)
        return super().dispatch(request, pk)
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,
        'formset': formset})
    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course,'formset': formset})
        
#explaning the formset method
#1. The get_formset() method is responsible for creating a ModuleFormSet instance using the data in request.POST if it exists, or an empty instance if not.
#2. The dispatch() method ensures that the correct course instance is available to the view.
#3. The get() method is responsible for returning a bound version of the formset.
#4. The post() method is only responsible for saving the formset if it is valid.


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'manage/content/form.html'
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',model_name= model_name)
                                                    
        return None
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner','order', 'created', 'updated'])
                                                
                                                    
                                                    
        return Form(*args, **kwargs)
    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,id=module_id,course__owner=request.user)
                                
                                
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,id =id, owner= request.user)
                                                           
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
        'object': self.obj})
    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
        
        data=request.POST,
        files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
    # new content
                Content.objects.create(module=self.module,
                item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form,'object':self.obj})


class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'manage/module/content_list.html'
    def get(self, request, module_id):
        module = get_object_or_404(Module, id=module_id )
        return self.render_to_response({'module': module}) 

from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
class ModuleOrderView(CsrfExemptMixin,JsonRequestResponseMixin,View):


 def post(self, request):
  for id, order in self.request_json.items():
    Module.objects.filter(id=id,
        course__owner=request.user).update(order=order)
    return self.render_json_response({'saved':  'OK'})
class ContentOrderView(CsrfExemptMixin,JsonRequestResponseMixin,View):


  def post(self, request):
    for id, order in self.request_json.items():
      Content.objects.filter(id=id,
       module__course__owner=request.user) \
          .update(order=order)
    return self.render_json_response({'saved': 'OK'})

class CourseDetailView(DetailView):
    model = Course
    template_name = 'course/details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})
                                                   
        return context


from django.db.models import Count
from .models import Subject
from django.core.cache import cache

# class CourseListView(TemplateResponseMixin, View):
#     model = Course
#     template_name = 'course/list.html'
#     def get(self, request, subject=None):
#         subjects = cache.get('all_subjects')
#         #courses = Course.objects.annotate(total_modules=Count('modules'))
#         if not subjects:
#             subjects = Subject.objects.annotate(total_courses=Count('courses'))
#             cache.set('all_subjects', subjects)                             
#             all_courses = Course.objects.annotate(total_modules=Count('modules'))
#         if subjects:
#             subject = get_object_or_404(Subject, slug=subject)
#             key = f'subject_{subject.id}_courses'
#             courses = cache.get(key)
#             if not courses:
#                courses = all_courses.filter(subject=subject)
#                cache.set(key, courses)
#             else:
#                 courses = cache.get('all_courses')
#                 if not courses:
#                  courses = all_courses
#                  cache.set('all_courses', courses) 
#                 return self.render_to_response({'subjects': subjects,
#                        'subject': subject,
#                           'courses': courses})          
            

        




class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'course/list.html'
    def get(self, request, subject=None):
     subjects = cache.get('all_subjects')
     if not subjects:
        subjects = Subject.objects.annotate(
        total_courses=Count('courses'))
        cache.set('all_subjects', subjects)
        all_courses = Course.objects.annotate(
        total_modules=Count('modules'))
     if subject:
      subject = get_object_or_404(Subject, slug=subject)
      key = f'subject_{subject.id}_courses'
      courses = cache.get(key)
      if not courses:
        courses = all_courses.filter(subject=subject)
        cache.set(key, courses)
     else:
      courses = cache.get('all_courses')
      if not courses:
        courses = all_courses
        cache.set('all_courses', courses)
     return self.render_to_response({'subjects': subjects,
     'subject': subject,
     'courses': courses})