

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import GetCommentById_InputView,CategoryViewSet, NewsCategoryViewSet, NewsSubCategoryViewSet,LatestArticleNewsView, LanguageViewSet, CommentView, ArticleViewSet, AddNewsCategoryView, AddArticle, EditNews, EditArticle, Category_GetItemByfield_InputView, GetArticlesByDateView, GetItemByfield_InputView, GetSubCategoryById_InputView, UpdateNewsStatus, SearchNews, LatestNewsView, LoginView, ValidateOTPView, GetProfile, GetProfileById, ResendOTPView, ProfileUpdate
from .views import *
from .views import LoginView,ValidateOTPView,ResendOTPView,ProfileUpdate,GetProfile,GetProfileById
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register('category', CategoryViewSet, basename='category')
router.register('news', NewsCategoryViewSet, basename='news')
router.register('sub_category', NewsSubCategoryViewSet, basename='sub_category')
# router.register('language', LanguageViewSet,basename='language')
router.register("comment",CommentView, basename='article_comment')
router.register("news_comment",News_CommentView, basename='news_comment')
router.register("article",ArticleViewSet, basename='article')
router.register("article_category",ArticleCategoryViewSet, basename='article_category')
router.register("article_profile",GetArticleProfileViewSet, basename='article_profile')
router.register('categories_subcategories', CategoryViewSet1, basename='category_subcategory')


router.register('Staging_db',StagingNewsViewSet,basename='Staging_db')
router.register('production_db', ProductionViewSet,basename='production_db')
# router.register('staging_to_production', StagingToProductionViewSet,basename='staging_to_production')

router.register('fixed-holidays', FixedHolidayViewSet, basename='fixed-holidays')
router.register('media', MediaViewSet,basename='media')
# router.register("leader",LeaderViewSet, basename='leader')
router.register("organizations",OrganizationsViewSet, basename='organizations')
router.register("outlook_comment",Outlook_CommentView, basename='outlook_comment')
router.register("organizations_category",OrganizationCategoryViewSet, basename='organizations_category')

router.register('movie_header', MovieHeaderViewSet, basename='movie-header')
router.register('movie_platforms', MoviePlatformsViewSet, basename='movie-platforms')
router.register('movie_geners', MovieGenersViewSet, basename='movie-geners')
router.register('movie_details', MovieDetailsViewSet, basename='movie-details')
router.register('staging_movie_details', StagingMovieDetailsViewSet, basename='staging_movie-details')
router.register('language', LanguageViewSet,basename='language')
router.register('news_podcast', NewsPodcastView,basename='news_podcast')







urlpatterns = [
    path('', include(router.urls)),
    path('add_news/', AddNewsCategoryView.as_view(), name='add_news'),
    path('add_article/',AddArticle.as_view(), name='add_article'),
    path('edit_news/<str:_id>/', EditNews.as_view(), name='edit_news'),
#     path('update_news/<str:_id>/', UpdateNews.as_view(), name='update_news'),
 
    path('edit_article/<str:_id>/', EditArticle.as_view(), name='edit_article'),
    path('category_get_by_field/<str:field_name>/<str:input_value>/', Category_GetItemByfield_InputView.as_view(), name='get_category_by_field'),
    path('sub_category_by_id/<str:_id>/', GetSubCategoryById_InputView.as_view(), name="sub_category_by_id"),
    path('news-category-filter/', GetItemByfield_InputView.as_view(), name='newsgetbyfield'),
    path('articles-filter/', GetArticlesByDateView.as_view(), name='getarticlesbydate'),
    path('update_news_status/<str:_id>/', UpdateNewsStatus.as_view(), name='updatenewsstatus'),
    path('search_news/',SearchNews.as_view(), name='searchnews'),
    path('search_news_by_location/',SearchNewsByLocation.as_view(), name='search_news_by_location'),
    # path('search_news/',SearchNews.as_view(), name='searchnews'),

    path('latest_news/', LatestNewsView.as_view(), name='latest-images'),
    path('latest_news_home/', LatestNewsHomeView.as_view(), name='latest-news'),

    path('latest_articles/', LatestArticleNewsView.as_view(), name='latest_articles'),
    path('register/',LoginView.as_view(), name='register'),
    path('login/',ValidateOTPView.as_view(), name='login'),
    path('resendotp/',ResendOTPView.as_view(), name='resendotp'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/<str:id>/',ProfileUpdate.as_view(), name='profile'),
    path('profile_get/',GetProfile.as_view(), name='profileget'),
    path('profile_get_by_id/<str:id>/',GetProfileById.as_view(), name='profilegetbyid'),
    path('GetCommentById_InputView/', GetCommentById_InputView.as_view(), name='GetCommentById_InputView'),
    path('comments_like/<uuid:comment_id>/', LikeCommentView.as_view(), name='like-comment'),
    path('comments_dislike/<uuid:comment_id>/', DislikeCommentView.as_view(), name='dislike-comment'),

    path('add_article_profile/', ArticleProfilePost.as_view(), name='add_article_profile'),
    path('edit_article_profile/<str:id>/', UpdateArticleProfile.as_view(), name='edit_article_profile'),
    # path('get_article_profile/',GetArticleProfile.as_view(), name='get_article_profile'),
    # path('get_article_profile_id/<str:id>/',GetArticleProfileById.as_view(), name='get_article_profile_id'),
    path('get_author_name/',GetArticleProfileName.as_view(), name='get_author_name'),
    path('get_all_author_name/',GetAllArticleProfileName.as_view(), name='get_author_name'),#for member fprm we want the success and pending authors also
    path('get_author_name_by_id/<str:id>/',GetArticleProfileNameById.as_view(), name='get_author_name_by_id'),
    path('add_article_category/', ArticleCategoryPost.as_view(), name='add_article_category'),
    path('edit_article_category/<str:_id>/', UpdateArticleCategory.as_view(), name='edit_article_category'),
    path('update_news_production/<str:_id>/', UpdateNews_Production.as_view(), name='update_news_production'),
    path('update_news_staging/<str:_id>/', UpdateNews_Staging.as_view(), name='update_news_staging'),
    path('edit_news_production/<str:_id>/', Production_Edit.as_view(), name='edit_news_production'),




    path('staging-to-production/transfer_to_production/<str:_id>/',
         StagingToProductionViewSet.as_view({'post': 'transfer_to_production'}),
         name='transfer-to-production'),
    path('production-to-staging/transfer_to_staging/<str:_id>/',
         StagingToProductionViewSet.as_view({'post': 'transfer_to_staging'}),
         name='transfer_to_staging'),

    path('edit_news_staging/<str:_id>/', Staging_Edit.as_view(), name='edit_news_staging'),
    path('Staging_Post/', Staging_Post.as_view(), name='Staging_Post'),
 
   

    path('GetNewsCommentById_InputView/', News_GetCommentById_InputView.as_view(), name='GetNewsCommentById_InputView'),
    path('news_comments_like/<uuid:comment_id>/', News_LikeCommentView.as_view(), name='news_comments_like'),
    path('news_comments_dislike/<uuid:comment_id>/', News_DislikeCommentView.as_view(), name='news_comments_dislike'),

    path('staging-news-category-filter/', Staging_GetItemByfield_InputView.as_view(), name='stagingnewsgetbyfield'),
    # path('download_news_pdf/<str:news_id>/', NewsPDFDownloadView.as_view(), name='download_news_pdf'),

    # path('share-news/<str:news_id>/', ShareNewsView.as_view(), name='share_news'),

    path('download_news_pdf/<str:news_id>/', NewsPDFDownloadView.as_view(), name='download_news_pdf'),
    path('news_detail/<str:news_id>/', NewsDetailView.as_view(), name='news_detail'),
    path('share_news/<str:news_id>/', ShareNewsView.as_view(), name='share_news'),
    path('download_articles_pdf/<str:articles_id>/', ArticlesPDFDownloadView.as_view(), name='download_articles_pdf'),
    path('articles_detail/<str:articles_id>/', ArticlesDetailView.as_view(), name='articles_detail'),
    path('share_articles/<str:articles_id>/', ShareArticlesView.as_view(), name='share_articles'),
    path('latest-news-by-state/', LatestNewsByStateView.as_view(), name='latest-news-by-state'),
    # path('multi_lang_news/', MultiLangNews.as_view(), name='multi_lang_news'),
    # path('add_leader/', LeaderPost.as_view(), name='add_leader'),
    # path('edit_leader/<str:_id>/', LeaderUpdate.as_view(), name='edit_leader'),
    path('add_organizations/', OrganizationsPost.as_view(), name='add_organizations'),
    path('edit_organizations/<str:_id>/', OrganizationsUpdate.as_view(), name='edit_organizations'),
    path('Organization_GetItemByfield_InputView/', Organization_GetItemByfield_InputView.as_view(), name='Organization_GetItemByfield_InputView'),

    path('outlook_GetCommentById_InputView/', Outlook_GetCommentById_InputView.as_view(), name='outlook_GetCommentById_InputView'),
    path('outlook_comments_like/<uuid:comment_id>/', Outlook_LikeCommentView.as_view(), name='outlook_like-comment'),
    path('outlook_comments_dislike/<uuid:comment_id>/', Outlook_DislikeCommentView.as_view(), name='outlook_dislike-comment'),

    path('add_media/', AddMediaView.as_view(), name='add_media'),
    path('edit_media/<str:_id>/', EditMedia.as_view(), name='edit_media'),
    path('latest_organizations/', LatestOrganizationsView.as_view(), name='latest_organizations'),
    path('GetOrganizationCategoryById_InputView/', GetOrganizationCategoryById_InputView.as_view(), name='GetOrganizationCategoryById_InputView'),
    
    # path('latest-news-by-state/', LatestNewsByStateView.as_view(), name='latest-news-by-state'),
    path('polls/', PollListCreateView.as_view(), name='poll-list-create'),
    path('poll-responses/', PollResponseCreateView.as_view(), name='poll-response-create'),
    path('Media_GetItemByfield_InputView/', Media_GetItemByfield_InputView.as_view(), name='Media_GetItemByfield_InputView'),
    path("movies_filter", MovieFilterView.as_view(), name="movie-filter"),
    path("staging_movies_filter", StagingMovieFilterView.as_view(), name="movie-filter"),
    path("publish-staging/<str:staging_id>/", PublishStagingMovie.as_view()),
    path("latest_articles_home",LatestArticlePerCategoryAPIView.as_view(),name="latest-single-article"),
    path("sso_login", SSOLoginView.as_view(), name="sso-login"),


]
