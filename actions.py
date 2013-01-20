import datetime

from auth import models as auth_models

from app import db


def get_time_records(username, days=7):
    today = datetime.date.today()
    delta = datetime.timedelta(days=days)
    cutoff_date = today - delta
    return auth_models.TimeRecord.objects(date__gt=cutoff_date).order_by('date')

