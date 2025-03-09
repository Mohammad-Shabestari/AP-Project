
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone

from .models import Student, Course, Enrollment, WeeklySchedule, Department,CoRequisite
from .forms import RegisterForm, LoginForm, CourseForm
from django.contrib.auth.models import User , Group

from persiantools.jdatetime import JalaliDateTime
def get_shamsi_exam_time(course):
    return JalaliDateTime(course.examTime).strftime("%Y-%m-%d %H:%M")

def time_str_to_minutes(time_str):
    # time_str = "HH:MM"
    h, m = time_str.split(':')
    return int(h) * 60 + int(m)


def home_view(request):
    return render(request, "home.html")

# -- ثبت نام کاربر (دانشجو یا ادمین) --
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data["role"]

            if role == "student":
                username = form.cleaned_data["studentNumber"]
            else:
                username = form.cleaned_data["username"]

            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]
            firstName = form.cleaned_data["firstName"]
            lastName = form.cleaned_data["lastName"]
            nationalID = form.cleaned_data.get("nationalID", "")

            studentNumber = form.cleaned_data.get("studentNumber")  # اگر بخواهیم
            admissionYear = form.cleaned_data.get("admissionYear")

            # چک تکراری نبودن یوزرنیم
            if User.objects.filter(username=username).exists():
                messages.error(request, "نام کاربری تکراری است.")
                return redirect("register")

            # ساخت User جنگو
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=firstName,
                last_name=lastName
            )

            if role == 'student':
                # ساخت شیء Student
                Student.objects.create(
                    user=user,
                    firstName=firstName,
                    lastName=lastName,
                    email=email,
                    nationalID=nationalID,
                    studentNumber=studentNumber,
                    admissionYear=admissionYear
                )
                student_group = Group.objects.get(pk=1)
                user.groups.add(student_group)
                user.save()
                messages.success(request, "ثبت‌نام دانشجو با موفقیت انجام شد.")

            elif role == 'admin':
                # کاربر ادمین
                admin_group = Group.objects.get(pk=2)
                user.groups.add(admin_group)
                user.is_staff = True
                user.is_superuser = False
                user.save()
                messages.success(request, "ثبت‌نام ادمین با موفقیت انجام شد.")

            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

# -- ورود کاربر --
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "ورود موفق.")
                return redirect("home")
            else:
                messages.error(request, "نام کاربری یا رمز عبور وارد شده اشتباه است.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})

# -- خروج --
def logout_view(request):
    logout(request)
    messages.info(request, "از حساب کاربری خود خارج شدید.")
    return redirect("home")

# -- صفحه لیست دروس و انتخاب واحد --
@login_required
def courses_list_view(request):
    # دریافت پارامتر دانشکده از GET (نام پارامتر دلخواه، مثلاً "department")
    department_id = request.GET.get("department", "")

    # دریافت همه دروس به صورت پیش‌فرض
    courses = Course.objects.all().order_by("courseCode")
    if department_id:
        courses = courses.filter(department__departmentID=department_id)

    student = None
    if hasattr(request.user, "student"):
        student = request.user.student

    # محاسبه تعداد واحدهای انتخاب شده (تعداد واحدهای دروس ثبت شده)
    if student:
        enrolled_courses = Enrollment.objects.filter(student=student).select_related('course')
        current_credits = sum(enrollment.course.credits for enrollment in enrolled_courses)
    else:
        current_credits = 0

    if request.method == "POST":
        course_id = request.POST.get("course_id")
        action = request.POST.get("action")
        if student:
            course_obj = get_object_or_404(Course, courseID=course_id)
            if action == "add":
                # ... (بررسی سقف واحد و ظرفیت) ...
                if current_credits + course_obj.credits > student.maxUnits:
                    messages.error(request, "محدودیت حداکثر تعداد واحدهای مجاز")
                elif course_obj.remainingCapacity <= 0:
                    messages.error(request, "ظرفیت درس تکمیل است.")
                else:
                    # 1) بررسی تداخل زمانی کلاس
                    already_enrolled = Enrollment.objects.filter(student=student).select_related('course')

                    new_course_days = set(course_obj.classDays)  # روزهای کلاس درس جدید
                    new_start = time_str_to_minutes(course_obj.startTime)
                    new_end = time_str_to_minutes(course_obj.endTime)

                    for enrollment_item in already_enrolled:
                        existing_course = enrollment_item.course
                        existing_days = set(existing_course.classDays)

                        # آیا روز مشترکی وجود دارد؟
                        if new_course_days.intersection(existing_days):
                            # تبدیل زمان رشته‌ای درس قبلی به دقیقه
                            ex_start = time_str_to_minutes(existing_course.startTime)
                            ex_end = time_str_to_minutes(existing_course.endTime)

                            # اگر بازه‌های زمانی هم‌پوشانی داشته باشند، تداخل است.
                            # (به عبارت دیگر: اگر new_start < ex_end و ex_start < new_end)
                            if not (new_end <= ex_start or new_start >= ex_end):
                                messages.error(request, "تلاقی درس با سایر دروس اخذ شده")
                                # از ثبت جلوگیری کرده و ری‌دایرکت
                                return redirect(
                                    f"{request.path}?department={department_id}" if department_id else "courses_list")

                    # 2) بررسی تداخل زمانی امتحان
                    for enrollment_item in already_enrolled:
                        existing_course = enrollment_item.course

                        if course_obj.examTime == existing_course.examTime:
                            messages.error(request, "تلاقی زمان امتحان درس انتخابی با دروس اخذ شده")
                            return redirect(
                                f"{request.path}?department={department_id}" if department_id else "courses_list")

                    # اگر به اینجا رسیدیم یعنی تداخلی وجود ندارد
                    # حالا می‌توانیم عمل ثبت را ادامه بدهیم
                    Enrollment.objects.create(student=student, course=course_obj)
                    WeeklySchedule.objects.create(course=course_obj, student=student)
                    course_obj.remainingCapacity -= 1
                    course_obj.save(update_fields=['remainingCapacity'])
                    messages.success(request, f"درس {course_obj.courseName} به لیست شما اضافه شد.")

                    # بررسی هم نیازی (co-requisite)
                    co_req = CoRequisite.objects.filter(course=course_obj).first()
                    if co_req:
                        if not Enrollment.objects.filter(student=student, course=co_req.requiredCourse).exists():
                            messages.warning(
                                request,
                                f"برای رعایت هم نیازی، باید درس {co_req.requiredCourse.courseName} را نیز به برنامه خود اضافه نمایید."
                            )
            elif action == "remove":
                enrollment = Enrollment.objects.filter(student=student, course=course_obj).first()
                schedule = WeeklySchedule.objects.filter(course=course_obj, student=student).first()
                if enrollment:
                    enrollment.delete()
                    schedule.delete()
                    course_obj.remainingCapacity += 1
                    course_obj.save(update_fields=['remainingCapacity'])
                    messages.success(request, f"درس {course_obj.courseName} حذف شد.")
        else:
            messages.error(request, "شما دانشجو نیستید.")
        # حفظ فیلتر دانشکده هنگام ریدایرکت (اضافه کردن پارامتر به URL)
        if department_id:
            return redirect(f"{request.path}?department={department_id}")
        else:
            return redirect("courses_list")

    # به‌روز رسانی تعداد واحدهای انتخاب شده پس از عملیات (در صورت دانشجو بودن)
    if student:
        enrolled_courses = Enrollment.objects.filter(student=student).select_related('course')
        total_credits = sum(enrollment.course.credits for enrollment in enrolled_courses)
    else:
        total_credits = 0

    # دریافت لیست دانشکده‌ها برای نمایش در منوی کشویی
    departments = Department.objects.all().order_by("departmentName")

    return render(request, "courses_list.html", {
        "courses": courses,
        "enrolled_course_ids": Enrollment.objects.filter(student=student).values_list("course_id", flat=True) if student else [],
        "get_shamsi_exam_time": get_shamsi_exam_time,
        "departments": departments,
        "selected_department": department_id,
        "total_credits": total_credits,
        "max_units": student.maxUnits if student else 0,
    })


# -- صفحه برنامهٔ هفتگی --
@login_required
def weekly_schedule_view(request):
    if not hasattr(request.user, "student"):
        messages.error(request, "شما دانشجو نیستید(دسترسی به این بخش برای شما ممکن نیست).")
        return redirect("home")

    days = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه"]
    time_slots = [f"{hour:02d}:{minute:02d}" for hour in range(7, 19) for minute in (0, 30)]
    student = request.user.student

    # همه‌ی دروس این دانشجو
    weekly_schedules = WeeklySchedule.objects.filter(student=student).select_related('course')

    # برای راحتی، تابعی برای پیدا کردن ایندکس یک زمان در لیست time_slots:
    def get_slot_index(time_str):
        # اگر زمان در time_slots بود، همان ایندکس را بدهد وگرنه -1
        # یا می‌توانید خطایابی کنید
        try:
            return time_slots.index(time_str)
        except ValueError:
            return -1

    # ساختن ساختار برای نگهداری اطلاعات جدول:
    # schedule_map[day] = آرایه‌ای به طول len(time_slots)
    # هر خانه یا None است یا شامل {"course": فلان, "rowspan": تعداد سطرهایی که می‌پوشاند, "skip": False}
    # یا اگر در محدوده ی پوشش یک درسِ قبلاً ثبت‌شده باشیم، {"skip": True}
    schedule_map = {day: [None]*len(time_slots) for day in days}

    for sch in weekly_schedules:
        c = sch.course
        for day in c.classDays:  # ممکن است چندین روز داشته باشد
            start_i = get_slot_index(c.startTime)
            end_i   = get_slot_index(c.endTime)
            if start_i != -1 and end_i != -1 and end_i > start_i:
                # این خانه را پر می‌کنیم
                schedule_map[day][start_i] = {
                    "course": c,
                    "rowspan": end_i - start_i,  # مثلاً اگر 07:00 تا 08:30 است، end_i-start_i = 3 اسلات
                    "skip": False
                }
                # بقیه اسلات‌ها را علامت بزنیم skip
                for j in range(start_i+1, end_i):
                    schedule_map[day][j] = {"skip": True}

    # حالا یک ساختار داده برای ارسال به تمپلیت می‌سازیم:
    # می‌خواهیم برای هر سطر i، اطلاعات هر روز را داشته باشیم
    table_rows = []
    for i, ts in enumerate(time_slots):
        row_data = {
            "time": ts,
            "cells": []
        }
        for day in days:
            cell_info = schedule_map[day][i]
            if cell_info is None:
                # یعنی هیچ درسی در این اسلات شروع نمی‌شود و جزو اسلات پوشانده‌شده هم نیست
                row_data["cells"].append({
                    "type": "empty",  # یا هرچه
                    "course": None,
                    "rowspan": 1
                })
            elif "skip" in cell_info and cell_info["skip"] == True:
                # یعنی درسی از سطر قبل ادامه دارد
                row_data["cells"].append({
                    "type": "skip"
                })
            else:
                # یعنی اینجا یک درس شروع می‌شود
                # course و rowspan داریم
                row_data["cells"].append({
                    "type": "course",
                    "course": cell_info["course"],
                    "rowspan": cell_info["rowspan"]
                })
        table_rows.append(row_data)

    context = {
        "days": days,
        "time_slots": time_slots,
        "table_rows": table_rows,
    }
    return render(request, "weekly_schedule.html", context)



# -- صفحه مدیریت دروس (ادمین) --
@user_passes_test(lambda u: u.is_staff)  # یا هر شرط دیگر
def admin_courses_view(request):
    # ابتدا همه دروس را بر اساس courseCode مرتب می‌کنیم
    courses = Course.objects.all().order_by("courseCode")

    # بررسی فیلتر دریافتی از GET
    filter_param = request.GET.get("filter", "")
    if filter_param == "full":
        courses = courses.filter(remainingCapacity=0)
    elif filter_param == "empty":
        courses = courses.filter(remainingCapacity__gt=0)

        # جستجو
    search_query = request.GET.get("search", "")
    if search_query:
        courses = courses.filter(
            Q(courseName__icontains=search_query) |
            Q(courseCode__icontains=search_query) |
            Q(department__departmentName__icontains=search_query)
        )

    if request.method == "POST":
        # حذف درس
        if "delete_course" in request.POST:
            course_id = request.POST.get("course_id")
            course_obj = get_object_or_404(Course, courseID=course_id)
            course_obj.delete()
            messages.success(request, "درس حذف شد.")
            return redirect("admin_courses")
        # به‌روزرسانی درس (ویرایش)
        elif "update_course" in request.POST:
            course_id = request.POST.get("course_id")
            course_obj = get_object_or_404(Course, courseID=course_id)
            form = CourseForm(request.POST, instance=course_obj)
            if form.is_valid():
                # دریافت مقدار ظرفیت باقی مانده از درخواست (در حالت ویرایش، این فیلد به صورت داینامیک به فرم اضافه می‌شود)
                rem_cap = request.POST.get("remainingCapacity")
                if rem_cap is not None and rem_cap != "":
                    try:
                        course_obj.remainingCapacity = int(rem_cap)
                    except ValueError:
                        course_obj.remainingCapacity = course_obj.capacity
                form.save()
                messages.success(request, "درس با موفقیت به روزرسانی شد.")
                return redirect("admin_courses")
            else:
                messages.error(request, "مشکلی در آپدیت درس رخ داده است.")
        # ایجاد درس جدید (در صورتی که فیلد مخفی course_id وجود نداشته باشد)
        elif "create_course" in request.POST:
            if not request.POST.get("course_id"):
                form = CourseForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, "درس جدید با موفقیت ایجاد شد.")
                    return redirect("admin_courses")
                else:
                    messages.error(request, "مشکلی در ساخت درس جدید رخ داده است.")
            else:
                course_id = request.POST.get("course_id")
                course_obj = get_object_or_404(Course, courseID=course_id)
                form = CourseForm(request.POST, instance=course_obj)
                if form.is_valid():
                    form.save()
                    messages.success(request, "درس با موفقیت به روزرسانی شد.")
                    return redirect("admin_courses")
                else:
                    messages.error(request, "مشکلی در به روز رسانی درس رخ داده است.")
    else:
        form = CourseForm()

    return render(request, "admin_courses.html", {
        "courses": courses,
        "form": form,
        "current_filter": filter_param,  # برای نمایش وضعیت فیلتر (اختیاری)
    })


@user_passes_test(lambda u: u.is_staff)
def admin_users_view(request):
    users = User.objects.filter(student__isnull=False).order_by('username')

    if request.method == 'POST':
        # حذف کاربر
        if 'delete_user' in request.POST:
            user_id = request.POST.get('user_id')
            user_to_delete = get_object_or_404(User, pk=user_id)
            # اطمینان حاصل کنید که ادمین نمی‌تواند خودش را حذف کند
            if user_to_delete == request.user:
                messages.error(request, "شما نمی‌توانید خودتان را حذف کنید.")
            else:
                user_to_delete.delete()
                messages.success(request, "کاربر حذف شد.")
            return redirect('admin_users')

        # به‌روزرسانی کاربر
        elif 'update_user' in request.POST:
            user_id = request.POST.get('user_id')
            user_to_update = get_object_or_404(User, pk=user_id)
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password = request.POST.get('password')  # اگر رمز وارد شده باشد
            user_to_update.username = username
            user_to_update.email = email
            user_to_update.first_name = first_name
            user_to_update.last_name = last_name
            if password:  # به‌روزرسانی رمز تنها در صورت وارد کردن
                user_to_update.set_password(password)
            user_to_update.save()
            messages.success(request, "اطلاعات کاربر به روز شد.")
            return redirect('admin_users')

        # ایجاد کاربر جدید
        elif 'create_user' in request.POST:
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password = request.POST.get('password')
            role = request.POST.get('role', 'student')
            if User.objects.filter(username=username).exists():
                messages.error(request, "نام کاربری تکراری است.")
            else:
                new_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                # تعیین نقش کاربر
                if role == 'admin':
                    admin_group = Group.objects.get(pk=2)  # فرض کنید گروه ادمین با pk=2 باشد
                    new_user.groups.add(admin_group)
                    new_user.is_staff = True
                    new_user.save()
                messages.success(request, "کاربر جدید ایجاد شد.")
            return redirect('admin_users')

    return render(request, 'admin_users.html', {'users': users})