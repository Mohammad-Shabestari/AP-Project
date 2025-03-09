from django import template
from persiantools.jdatetime import JalaliDateTime

register = template.Library()

@register.filter
def shamsi_exam_time(value):
    """تبدیل تاریخ میلادی به شمسی"""
    return JalaliDateTime(value).strftime("%Y-%m-%d %H:%M")
