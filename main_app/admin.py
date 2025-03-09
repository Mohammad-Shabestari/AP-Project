
from django.contrib import admin
from .models import (
    Department, Instructor,
    Student, Course, Classroom, CourseClassroom,
    Prerequisite, CoRequisite, Enrollment, WeeklySchedule
)

admin.site.register(Department)
admin.site.register(Instructor)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Classroom)
admin.site.register(CourseClassroom)
admin.site.register(Prerequisite)
admin.site.register(CoRequisite)
admin.site.register(Enrollment)
admin.site.register(WeeklySchedule)
