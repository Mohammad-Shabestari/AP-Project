from django import forms
from django.contrib.auth.models import User
from .models import Student, Course , CoRequisite
from persiantools.jdatetime import JalaliDateTime

from multiselectfield.forms.fields import MultiSelectFormField
from django.core.exceptions import ValidationError

ROLE_CHOICES = [
    ('student', 'دانشجو'),
    ('admin', 'ادمین'),
]


class RegisterForm(forms.Form):
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="نقش کاربر",
        required=True,
        error_messages={'required': 'لطفا نقش کاربر را انتخاب کنید.'}
    )

    username = forms.CharField(
        label="نام کاربری",
        max_length=50,
        required=True,
        error_messages={
            'required': 'لطفا نام کاربری را وارد کنید.',
            'max_length': 'نام کاربری نمی‌تواند بیش از 50 کاراکتر باشد.'
        }
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput,
        required=True,
        error_messages={'required': 'لطفا رمز عبور را وارد کنید.'}
    )
    email = forms.EmailField(
        label="ایمیل",
        required=True,
        error_messages={
            'required': 'لطفا ایمیل خود را وارد کنید.',
            'invalid': 'ایمیل وارد شده معتبر نیست.'
        }
    )
    firstName = forms.CharField(
        label="نام",
        max_length=50,
        required=True,
        error_messages={
            'required': 'لطفا نام خود را وارد کنید.',
            'max_length': 'نام نمی‌تواند بیش از 50 کاراکتر باشد.'
        }
    )
    lastName = forms.CharField(
        label="نام خانوادگی",
        max_length=50,
        required=True,
        error_messages={
            'required': 'لطفا نام خانوادگی خود را وارد کنید.',
            'max_length': 'نام خانوادگی نمی‌تواند بیش از 50 کاراکتر باشد.'
        }
    )
    nationalID = forms.CharField(
        label="کد ملی",
        max_length=10,
        required=False,
        error_messages={
            'max_length': 'کد ملی نمی‌تواند بیش از 10 کاراکتر باشد.'
        }
    )

    # فیلدهای مربوط به دانشجو
    studentNumber = forms.CharField(
        label="شماره دانشجویی",
        required=False,
        max_length=9,
        error_messages={
            'required': 'لطفا شماره دانشجویی را وارد کنید.',
            'max_length': 'شماره دانشجویی نمی‌تواند بیش از 9 رقم باشد.'
        }
    )
    admissionYear = forms.IntegerField(
        label="سال پذیرش",
        required=False,
        error_messages={
            'required': 'لطفا سال پذیرش را وارد کنید.',
            'invalid': 'سال پذیرش باید یک عدد صحیح باشد.'
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        if role == 'student':
            # اگر نقش دانشجوست، این فیلدها باید پر باشند
            if not cleaned_data.get('studentNumber'):
                self.add_error('studentNumber', "برای نقش دانشجو، شماره دانشجویی اجباری است.")
            if not cleaned_data.get('admissionYear'):
                self.add_error('admissionYear', "برای نقش دانشجو، سال پذیرش اجباری است.")

        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50,label="نام کاربری")
    password = forms.CharField(widget=forms.PasswordInput,label="رمز عبور")

# نمونه فرم برای ایجاد/ویرایش درس توسط ادمین
class CourseForm(forms.ModelForm):
    # فیلد برای انتخاب روز کلاس
    classDays = MultiSelectFormField(
        choices=Course.WEEK_DAYS,
        flat_choices=Course.WEEK_DAYS,
        label="روزهای برگزاری کلاس",
        widget=forms.CheckboxSelectMultiple
    )

    # فیلد برای انتخاب زمان شروع
    startTime = forms.ChoiceField(
        choices=Course.TIME_SLOTS,
        label="زمان شروع کلاس",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    # فیلد برای انتخاب زمان پایان
    endTime = forms.ChoiceField(
        choices=Course.TIME_SLOTS,
        label="زمان پایان کلاس",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    # فیلد برای انتخاب تاریخ امتحان با تقویم فارسی
    examTime = forms.DateTimeField(
        label="زمان امتحان",
        widget=forms.TextInput(attrs={"class": "form-control", "id": "examTimePicker"})
    )

    co_course_code = forms.CharField(
        label="کد درس هم نیاز",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Course
        fields = [
            "courseName",
            "courseCode",
            "credits",
            "classDays",
            "startTime",
            "endTime",
            "examTime",
            "capacity",
            "department",
            "instructor",
        ]

        labels = {
            "courseName": "نام درس",
            "courseCode": "کد درس",
            "credits": "تعداد واحد",
            "capacity": "ظرفیت درس",
            "department": "دانشکده",
            "instructor": "استاد درس",
        }

        widgets = {
            "courseName": forms.TextInput(attrs={"class": "form-control"}),
            "courseCode": forms.TextInput(attrs={"class": "form-control"}),
            "credits": forms.NumberInput(attrs={"class": "form-control"}),
            "capacity": forms.NumberInput(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-control"}),
            "instructor": forms.Select(attrs={"class": "form-control"}),
        }

    def clean_examTime(self):
        exam_time = self.cleaned_data.get("examTime")
        exam_time = str(exam_time)

        try:
            jalali_datetime = JalaliDateTime.strptime(exam_time, "%Y-%m-%d %H:%M")
            return jalali_datetime.to_gregorian()  # تبدیل به میلادی
        except ValueError:
            raise forms.ValidationError("فرمت تاریخ نادرست است، لطفاً از تقویم استفاده کنید.")

    def save(self, commit=True):
        course = super().save(commit)
        # حذف رکورد هم‌نیاز قدیمی (اگر وجود دارد)
        CoRequisite.objects.filter(course=course).delete()
        co_code = self.cleaned_data.get("co_course_code")
        if co_code:
            try:
                required_course = Course.objects.get(courseCode=co_code)
                # ایجاد رکورد هم‌نیاز
                CoRequisite.objects.create(course=course, requiredCourse=required_course)
            except Course.DoesNotExist:
                # در صورت عدم وجود درس با آن کد، می‌توانیم خطا بدهیم یا پیام هشدار ارسال کنیم
                raise ValidationError(f"درسی با کد '{co_code}' یافت نشد.")
        return course