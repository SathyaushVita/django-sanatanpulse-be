# from celery import current_app
# from celery.schedules import crontab
# from datetime import date
# from .models import FixedHoliday

# def schedule_dynamic_tasks():
#     today = date.today()
#     holidays = FixedHoliday.objects.filter(date__gte=today)
#     holiday_dates = [holiday.date for holiday in holidays]

#     if not holiday_dates:
#         print("No holidays today. Skipping dynamic task scheduling.")
#         return

#     # Calculate holiday duration
#     duration = (max(holiday_dates) - today).days + 1

#     # Set the interval and batch size dynamically
#     if duration == 1:
#         interval_hours = 1
#         batch_size = 5
#     elif duration == 2:
#         interval_hours = 2
#         batch_size = 3
#     else:
#         interval_hours = 3
#         batch_size = 2

#     # Adjust Celery Beat schedule dynamically
#     app = current_app._get_current_object()
#     app.conf.beat_schedule = {
#         'dynamic-news-publishing': {
#             'task': 'hindupulseapp.tasks.publish_news',
#             'schedule': crontab(minute=0, hour=f'*/{interval_hours}'),
#             'args': (batch_size,),
#         }
#     }
#     print(f"Scheduled task every {interval_hours} hours to publish {batch_size} articles.")
