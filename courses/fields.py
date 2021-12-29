from django.db import models
from django.core.exceptions import ObjectDoesNotExist
class OrderField(models.PositiveIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields# this is an instance method.
        super().__init__(*args, **kwargs)
    def pre_save(self, model_instance, add):
        if getattr(model_instance, self.attname) is None:
# no current value
            try:
                qs = self.model.objects.all()#here we are getting all objects for the fields model.
                if self.for_fields:
# filter by objects with the same field values
# for the fields in "for_fields"
                   query = {field: getattr(model_instance, field)\
                   for field in self.for_fields}#here we are using dictionary comprehension to filter objects with the same fellds naem
                   qs = qs.filter(**query)#here we are getting the current value of the fields by filtreing. filter by the current value
# get the order of the last item
                last_item = qs.latest(self.attname)
                value = last_item.order + 1# if an order is found, ypu ad 1 to it
            except ObjectDoesNotExist:
                value = 0
            setattr(model_instance, self.attname, value)
            return value
        else:
           return super().pre_save(model_instance, add)
