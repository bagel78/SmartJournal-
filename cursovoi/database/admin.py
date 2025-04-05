from django.contrib import admin
from .models import Students, Teachers, Faculties, Departments, Specialties, Groups, Subjects, Grades, Curriculum

admin.site.register(Students)
admin.site.register(Teachers)
admin.site.register(Faculties)
admin.site.register(Departments)
admin.site.register(Specialties)
admin.site.register(Groups)
admin.site.register(Subjects)
admin.site.register(Grades)
admin.site.register(Curriculum)