from django import template
from django.contrib.humanize.templatetags.humanize import intcomma as django_intcomma
import jdatetime

register = template.Library()

@register.filter(name='to_jalali')
def to_jalali(value):
    """تبدیل تاریخ میلادی به شمسی"""
    if not value:
        return ''
    try:
        jalali_date = jdatetime.datetime.fromgregorian(datetime=value)
        return jalali_date.strftime('%Y/%m/%d - %H:%M')
    except Exception as e:
        return str(value)

@register.filter(name='intcomma')
def intcomma_filter(value):
    """فرمت کردن اعداد با جداکننده هزارگان"""
    try:
        return django_intcomma(int(value))
    except Exception:
        return value
