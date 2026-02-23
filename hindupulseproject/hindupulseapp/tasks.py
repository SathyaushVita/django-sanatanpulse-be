# # # your_app/tasks.py
# # from celery import shared_task
# # from .models import NewsCategory
# # from .enums import IsPublish

# # @shared_task
# # def post_news_articles(batch_size=5):
# #     # Get the next batch of articles that are not yet published
# #     articles = NewsCategory.objects.filter(is_published=IsPublish.NOT_PUBLISHED.value).order_by('created_at')[:batch_size]
# #     for article in articles:
# #         publish_article(article)
# #         article.is_published = IsPublish.PUBLISHED.value  # Mark as published
# #         article.save()

# # def publish_article(article):
# #     # Implement your logic to publish the article
# #     print(f"Published article: {article.headline}")

# # tasks.py
# # tasks.py
# from celery import shared_task
# from .models import NewsCategory  # Import your NewsCategory model
# from .enums import IsPublish

# @shared_task
# def publish_news(*args, **kwargs):
#     batch_size = kwargs.get('batch_size', 5)  # Default batch_size to 5 if not provided
    
#     # Get the next batch of articles that are not yet published
#     articles = NewsCategory.objects.filter(is_published=IsPublish.NOT_PUBLISHED.value).order_by('created_at')[:batch_size]
#     for article in articles:
#         publish_article(article)
#         article.is_published = IsPublish.PUBLISHED.value  # Mark as published
#         article.save()

# def publish_article(article):
#     # Implement your logic to publish the article
#     print(f"Published article: {article.headline}")









# from celery import shared_task
# from datetime import date
# from .models import NewsCategory, FixedHoliday
# from .enums import IsPublish

# @shared_task
# def publish_news(*args, **kwargs):
#     today = date.today()

#     # Check if today is a fixed holiday or weekend (Saturday, Sunday)
#     is_fixed_holiday = FixedHoliday.objects.filter(date=today).exists()
#     is_weekend = today.weekday() >= 5  # 5 = Saturday, 6 = Sunday

#     if not (is_fixed_holiday or is_weekend):
#         print(f"{today} is not a fixed holiday or weekend. Skipping task.")
#         return

#     print(f"{today} is a holiday or weekend. Processing articles...")
#     batch_size = kwargs.get('batch_size', 5)

#     # Fetch and publish articles
#     articles = NewsCategory.objects.filter(is_published=IsPublish.NOT_PUBLISHED.value).order_by('created_at')[:batch_size]
#     for article in articles:
#         publish_article(article)
#         article.is_published = IsPublish.PUBLISHED.value
#         article.save()

# def publish_article(article):
#     # Logic to publish the article
#     print(f"Published article: {article.headline}")












# from celery import shared_task
# from datetime import date
# from .models import NewsCategory, FixedHoliday
# from .enums import IsPublish

# @shared_task
# def publish_news(batch_size=5, *args, **kwargs):
#     today = date.today()

#     # Check if today is a fixed holiday or weekend (Sunday)
#     is_fixed_holiday = FixedHoliday.objects.filter(date=today).exists()
#     is_weekend = today.weekday() == 6  # Sunday

#     if not (is_fixed_holiday or is_weekend):
#         print(f"{today} is not a fixed holiday or weekend. Skipping task.")
#         return

#     print(f"{today} is a holiday or weekend. Publishing articles...")

#     # Fetch and publish articles
#     articles = NewsCategory.objects.filter(is_published=IsPublish.NOT_PUBLISHED.value).order_by('created_at')[:batch_size]
#     for article in articles:
#         publish_article(article)
#         article.is_published = IsPublish.PUBLISHED.value
#         article.save()

# def publish_article(article):
#     # Logic to publish the article
#     print(f"Published article: {article.headline}")







# from celery import shared_task
# from django.utils.timezone import now
# from .models import NewsCategory
# from .enums import IsPublish

# @shared_task
# def publish_scheduled_news():
#     current_time = now()

#     # Get articles scheduled for publishing
#     articles = NewsCategory.objects.filter(
#         publish_at__lte=current_time,  # Publish if the scheduled time has passed
#         is_published=IsPublish.NOT_PUBLISHED.value
#     )

#     for article in articles:
#         publish_article(article)
#         article.is_published = IsPublish.PUBLISHED.value
#         article.save()

# def publish_article(article):
#     # Logic to handle publishing the article
#     print(f"Published article: {article.headline}")





# from celery import shared_task
# from django.utils.timezone import now
# from .models import NewsCategory
# from .enums import IsPublish
# from datetime import timedelta
# from datetime import datetime


# @shared_task
# def publish_scheduled_news():
#     """
#     Task to publish news articles only at the exact `publish_at` time.
#     """
#     current_time = datetime.now()
    
#     # Fetch news articles where `publish_at` matches `current_time`
#     articles_to_publish = NewsCategory.objects.filter(
#         is_published=IsPublish.NOT_PUBLISHED.value,
#         publish_at=current_time  # Exact match condition
#     )

#     # Update the `is_published` status to `PUBLISHED`
#     for article in articles_to_publish:
#         article.is_published = IsPublish.PUBLISHED.value
#         article.save()





from celery import shared_task
from django.utils.timezone import now
from .models import NewsCategory
from .enums import IsPublish
import logging


logger = logging.getLogger(__name__)

@shared_task
def publish_scheduled_news():
    """
    Task to publish news articles when their `publish_at` time matches the current minute.
    """
    current_time = now()
    start_of_minute = current_time.replace(second=0, microsecond=0)
    end_of_minute = current_time.replace(second=59, microsecond=999999)

    logger.info(f"Checking articles to publish at {current_time}")

    articles_to_publish = NewsCategory.objects.filter(
        is_published=IsPublish.NOT_PUBLISHED.value,
        publish_at__gte=start_of_minute,
        publish_at__lte=end_of_minute
    )

    for article in articles_to_publish:
        logger.info(f"Publishing article: {article.headline}")
        article.is_published = IsPublish.PUBLISHED.value
        article.save()

# @shared_task
# def publish_scheduled_news():
#     """
#     Task to publish news articles when their publish_at time is reached.
#     """
#     current_time = now()
#     # Fetch news articles that are not published and their publish_at time has passed
#     articles_to_publish = NewsCategory.objects.filter(
#         is_published=IsPublish.NOT_PUBLISHED.value,
#         publish_at__lte=current_time
#     )

#     # Update the `is_published` status to `PUBLISHED`
#     for article in articles_to_publish:
#         article.is_published = IsPublish.PUBLISHED.value
#         article.save()

# @shared_task
# def publish_scheduled_news():
#     # Get the current time, rounded to the nearest minute (seconds and microseconds ignored)
#     current_time = now().replace(second=0, microsecond=0)

#     # Allow a small margin of time to ensure we capture articles published within the current minute
#     time_margin = timedelta(minutes=1)  # Margin of 1 minute, adjust as necessary

#     # Fetch articles that need to be published around the current time
#     articles = NewsCategory.objects.filter(
#         publish_at__gte=current_time - time_margin,  # publish_at should be within the last minute
#         publish_at__lte=current_time + time_margin,  # and within the next minute
#         is_published=IsPublish.NOT_PUBLISHED.value  # Ensure the article is not published yet
#     )

#     for article in articles:
#         # Only publish the article if the publish_at time matches the current time's minute
#         if article.publish_at.replace(second=0, microsecond=0) == current_time:
#             publish_article(article)
#             article.is_published = IsPublish.PUBLISHED.value
#             article.publish_at = current_time  # Set publish_at to the current time when it's published
#             article.save()

# def publish_article(article):
#     # Logic to handle publishing the article
#     print(f"Published article: {article.headline}")




