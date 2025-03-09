
// تابع کمکی برای خواندن مقدار کوکی با نام مشخص
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // بررسی می‌کنیم که کوکی با نام مورد نظر شروع شود
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// تابع حذف درس با اضافه کردن توکن CSRF
function confirmCourseDelete(courseId) {
  const sure = confirm("Are you sure to delete this course?");
  if (sure) {
    // دریافت توکن CSRF از کوکی
    const csrfToken = getCookie('csrftoken');

    // ساخت یک فرم موقت و تنظیم فیلدهای مورد نیاز
    const form = document.createElement("form");
    form.method = "POST";
    // در صورت نیاز آدرس دقیق (action) را تنظیم کنید؛ اگر خالی بماند، فرم به URL فعلی ارسال می‌شود.
    form.action = "";

    form.innerHTML = `
      <input type="hidden" name="course_id" value="${courseId}">
      <input type="hidden" name="delete_course" value="1">
      <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
    `;
    document.body.appendChild(form);
    form.submit();
  }
}

// تابع پر کردن فرم جهت ویرایش درس
function populateCourseForm(courseID, courseName, courseCode, credits, capacity, remainingCapacity, departmentID, instructorID, classDays, startTime, endTime, examTime) {
    // مقداردهی فیلدهای فرم با توجه به آیدی‌های تولید شده توسط Django
    // فرض بر این است که فیلدها با نام‌های پیش‌فرض ساخته شده‌اند.
    if (document.getElementById("id_courseName"))
        document.getElementById("id_courseName").value = courseName;
    if (document.getElementById("id_courseCode"))
        document.getElementById("id_courseCode").value = courseCode;
    if (document.getElementById("id_credits"))
        document.getElementById("id_credits").value = credits;
    if (document.getElementById("id_capacity"))
        document.getElementById("id_capacity").value = capacity;
    if (document.getElementById("id_startTime"))
        document.getElementById("id_startTime").value = startTime;
    if (document.getElementById("id_endTime"))
        document.getElementById("id_endTime").value = endTime;
    // فیلد تاریخ امتحان دارای آیدی "examTimePicker" است
    if (document.getElementById("examTimePicker"))
        document.getElementById("examTimePicker").value = examTime;

    // ایجاد یا به‌روزرسانی فیلد مخفی course_id جهت تشخیص عملیات ویرایش در سمت سرور
    let courseIdField = document.getElementById("id_course_id");
    if (!courseIdField) {
         courseIdField = document.createElement("input");
         courseIdField.type = "hidden";
         courseIdField.name = "course_id";
         courseIdField.id = "id_course_id";
         document.querySelector("form").appendChild(courseIdField);
    }
    courseIdField.value = courseID;

    // مدیریت فیلد کد درس هم نیاز
    let coField = document.getElementById("id_co_course_code");
    if (!coField) {
         let container = document.createElement("div");
         container.id = "coCourseContainer";
         container.classList.add("form-group");
         let label = document.createElement("label");
         label.setAttribute("for", "id_co_course_code");
         label.textContent = "کد درس هم نیاز";
         coField = document.createElement("input");
         coField.type = "text";
         coField.name = "co_course_code";
         coField.id = "id_co_course_code";
         coField.classList.add("form-control");
         container.appendChild(label);
         container.appendChild(coField);
         let submitButton = document.querySelector("form button[type='submit']");
         submitButton.parentNode.insertBefore(container, submitButton);
    }
    coField.value = coCourseCode;

    // اضافه کردن فیلد "ظرفیت باقی مانده" به فرم در حالت ویرایش (در صورتی که وجود ندارد)
    let remCapField = document.getElementById("id_remainingCapacity");
    if (!remCapField) {
         let container = document.createElement("div");
         container.id = "remainingCapacityContainer";
         container.classList.add("form-group");  // اگر از Bootstrap استفاده می‌کنید

         let label = document.createElement("label");
         label.setAttribute("for", "id_remainingCapacity");
         label.textContent = "ظرفیت باقی مانده";

         remCapField = document.createElement("input");
         remCapField.type = "number";
         remCapField.name = "remainingCapacity";
         remCapField.id = "id_remainingCapacity";
         remCapField.classList.add("form-control");

         container.appendChild(label);
         container.appendChild(remCapField);

         // قرار دادن container قبل از دکمه ارسال فرم
         let submitButton = document.querySelector("form button[type='submit']");
         submitButton.parentNode.insertBefore(container, submitButton);
    }
    // مقداردهی فیلد ظرفیت باقی مانده با مقدار دریافتی
    remCapField.value = remainingCapacity;

    // تغییر دکمه ارسال به حالت "به‌روزرسانی درس"
    let submitButton = document.querySelector("form button[type='submit']");
    submitButton.name = "update_course";
    submitButton.textContent = "به‌روزرسانی درس";
}

// تابع بازنشانی فرم به حالت اولیه (ایجاد درس جدید)
function resetCourseForm() {
    if(document.getElementById("id_courseName"))
        document.getElementById("id_courseName").value = "";
    if(document.getElementById("id_courseCode"))
        document.getElementById("id_courseCode").value = "";
    if(document.getElementById("id_credits"))
        document.getElementById("id_credits").value = "";
    if(document.getElementById("id_capacity"))
        document.getElementById("id_capacity").value = "";
    if(document.getElementById("id_startTime"))
        document.getElementById("id_startTime").value = "";
    if(document.getElementById("id_endTime"))
        document.getElementById("id_endTime").value = "";
    if(document.getElementById("examTimePicker"))
        document.getElementById("examTimePicker").value = "";

    // حذف فیلد مخفی course_id (در صورت وجود)
    let courseIdField = document.getElementById("id_course_id");
    if (courseIdField) {
        courseIdField.remove();
    }

    // حذف فیلد ظرفیت باقی مانده (در صورت وجود)
    let remCapContainer = document.getElementById("remainingCapacityContainer");
    if (remCapContainer) {
        remCapContainer.remove();
    }

    // تغییر دکمه ارسال به حالت ایجاد درس جدید
    let submitButton = document.querySelector("form button[type='submit']");
    submitButton.name = "create_course";
    submitButton.textContent = "ذخیره درس";
}



// مثال: فیلتر جدول
function filterCourses() {
  const input = document.getElementById("courseSearch");
  const filter = input.value.toLowerCase();
  const rows = document.querySelectorAll("#coursesTable tbody tr");

  rows.forEach((row) => {
    const text = row.innerText.toLowerCase();
    row.style.display = text.includes(filter) ? "" : "none";
  });
}
