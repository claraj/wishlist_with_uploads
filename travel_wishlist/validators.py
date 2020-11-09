from django.core.exceptions import ValidationError
from datetime import date, datetime

def validate_date_today_or_in_past(value):
    if value > date.today():
        raise ValidationError(f'Date {value} is not today or in the past', params={'value': value})