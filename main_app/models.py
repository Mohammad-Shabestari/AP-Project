from django.contrib.auth.models import User, Group
from django.db import models
from multiselectfield import MultiSelectField


# 1) دانشکده (Departments)
class Department(models.Model):
    departmentID = models.AutoField(primary_key=True)
    departmentName = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.departmentName

# 2) استادان (Instructors)
class Instructor(models.Model):
    instructorID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    email = models.EmailField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.firstName} {self.lastName}"

# 3) دانشجو (Students)
class Student(models.Model):
    studentID = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    email = models.EmailField()
    nationalID = models.CharField(max_length=10)
    phoneNumber = models.CharField(max_length=20, blank=True)
    major = models.CharField(max_length=100, blank=True)
    year = models.IntegerField(default=1)
    maxUnits = models.IntegerField(default=24)
    studentNumber = models.CharField(max_length=9, unique=True)
    admissionYear = models.IntegerField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.firstName} {self.lastName} - {self.studentNumber}"

# 4) درس‌ها (Courses)
class Course(models.Model):
    # گزینه‌های روزهای هفته
    WEEK_DAYS = [
        ("شنبه", "شنبه"),
        ("یکشنبه", "یکشنبه"),
        ("دوشنبه", "دوشنبه"),
        ("سه‌شنبه", "سه‌شنبه"),
        ("چهارشنبه", "چهارشنبه"),
        ("پنج‌شنبه", "پنج‌شنبه"),
    ]

    # گزینه‌های زمان کلاس (اسلات‌های نیم‌ساعته از 7:00 تا 18:00)
    TIME_SLOTS = [(f"{hour:02d}:{minute:02d}", f"{hour:02d}:{minute:02d}") for hour in range(7, 19) for minute in
                  (0, 30)]

    courseID = models.AutoField(primary_key=True)
    courseName = models.CharField(max_length=100)
    courseCode = models.CharField(max_length=50, unique=True)
    credits = models.IntegerField()
    # انتخاب روزهای مشخص
    classDays = MultiSelectField(choices=WEEK_DAYS, max_length=20)

    # انتخاب زمان شروع و پایان از اسلات‌های نیم‌ساعته
    startTime = models.CharField(max_length=5, choices=TIME_SLOTS)
    endTime = models.CharField(max_length=5, choices=TIME_SLOTS)

    examTime = models.DateTimeField()   # مثلا "15:00-17:00"
    capacity = models.IntegerField()
    remainingCapacity = models.IntegerField(null=True,blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # اگر remainingCapacity مقداردهی نشده (یعنی None) باشد، آن را برابر با capacity قرار می‌دهیم.
        if self.remainingCapacity is None:
            self.remainingCapacity = self.capacity
        super().save(*args, **kwargs)

    def get_co_course_code(self):
        try:
            co_req = self.co_main_course.first()  # چون در CoRequisite از related_name='co_main_course' استفاده شده است
            if co_req:
                return co_req.requiredCourse.courseCode
            else:
                return ""
        except Exception:
            return ""

    def __str__(self):
        return f"{self.courseName} ({self.courseCode})"

# 5) کلاس‌ها (Classrooms)
class Classroom(models.Model):
    classroomID = models.AutoField(primary_key=True)
    classroomName = models.CharField(max_length=100)
    capacity = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.classroomName} - {self.department.departmentName}"

# 6) رابطهٔ درس‌ها و کلاس‌ها (CourseClassrooms)
class CourseClassroom(models.Model):
    courseClassroomID = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course.courseName} in {self.classroom.classroomName}"

# 7) پیش‌نیاز (Prerequisites)
class Prerequisite(models.Model):
    prerequisiteID = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, related_name='main_course', on_delete=models.CASCADE)
    requiredCourse = models.ForeignKey(Course, related_name='prereq_course', on_delete=models.CASCADE)

    def __str__(self):
        return f"Prerequisite: {self.requiredCourse.courseName} -> {self.course.courseName}"

# 8) هم‌نیاز (CoRequisites)
class CoRequisite(models.Model):
    coRequisiteID = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, related_name='co_main_course', on_delete=models.CASCADE)
    requiredCourse = models.ForeignKey(Course, related_name='co_required_course', on_delete=models.CASCADE)

    def __str__(self):
        return f"CoRequisite: {self.requiredCourse.courseName} & {self.course.courseName}"

# 9) ثبت انتخاب واحد (Enrollments)
class Enrollment(models.Model):
    enrollmentID = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollmentDate = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, default='active')  # یا choice field

    def __str__(self):
        return f"Enrollment: {self.student.studentNumber} -> {self.course.courseName}"

# 10) برنامهٔ هفتگی (WeeklySchedule)
class WeeklySchedule(models.Model):
    scheduleID = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"Schedule: {self.student.studentNumber} - {self.course.courseCode} "
