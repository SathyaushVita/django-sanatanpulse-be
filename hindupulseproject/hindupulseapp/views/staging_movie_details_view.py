from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models import StagingMovieDetails,MovieDetails
from ..serializers import StagingMovieDetailsSerializer,MovieDetailsSerializer
from ..utils import save_image_to_azure, save_video_to_azure
from ..enums import EntityStatus
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



# class StagingMovieDetailsViewSet(viewsets.ModelViewSet):
#     queryset = StagingMovieDetails.objects.all()
#     serializer_class = StagingMovieDetailsSerializer




#     def retrieve(self, request, *args, **kwargs):
#         try:
#             movie_id = kwargs.get("pk")

#             movie = StagingMovieDetails.objects.using("staging_db").filter(_id=movie_id).first()

#             if not movie:
#                 return Response({
#                     "message": "Movie not found in staging"
#                 }, status=status.HTTP_404_NOT_FOUND)

#             serializer = StagingMovieDetailsSerializer(movie)

#             return Response({
#                 "message": "success",
#                 "result": serializer.data
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({
#                 "message": "error",
#                 "error": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




#     def create(self, request, *args, **kwargs):
#         try:
#             poster_base64 = request.data.get("poster")
#             trailer_base64 = request.data.get("trailer")

#             if isinstance(poster_base64, list):
#                 poster_base64 = poster_base64[0]

#             if isinstance(trailer_base64, list):
#                 trailer_base64 = trailer_base64[0]

#             data_copy = request.data.copy()
#             data_copy["poster"] = None
#             data_copy["trailer"] = None

#             serializer = self.get_serializer(data=data_copy)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()

#             movie = serializer.instance
#             entity_type = "movie"

#             # ⭐ USE TITLE IN PATH (your requirement)
#             title_name = movie.title if movie.title else "untitled-movie"

#             saved_poster = None
#             saved_trailer = None

#             # ---------------- POSTER ----------------
#             if poster_base64 and poster_base64 != "null":
#                 saved_poster = save_image_to_azure(
#                     poster_base64,
#                     movie._id,
#                     title_name,     
#                     entity_type
#                 )

#             # ---------------- TRAILER ----------------
#             if trailer_base64 and trailer_base64 != "null":
#                 saved_trailer = save_video_to_azure(
#                     trailer_base64,
#                     movie._id,
#                     title_name,      
#                     entity_type
#                 )

#             if saved_poster:
#                 movie.poster = [saved_poster]

#             if saved_trailer:
#                 movie.trailer = [saved_trailer]

#             movie.save()

#             return Response({
#                 "message": "success",
#                 "result": StagingMovieDetailsSerializer(movie).data
#             }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({
#                 "message": "An error occurred",
#                 "error": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        






class StagingMovieDetailsViewSet(viewsets.ModelViewSet):
    queryset = StagingMovieDetails.objects.all()
    serializer_class = StagingMovieDetailsSerializer


    # ---------------- LIST ----------------
    def list(self, request, *args, **kwargs):
        now = timezone.now()

        queryset = StagingMovieDetails.objects.using("staging_db").filter(
            publish_at__lte=now
        )

        serializer = StagingMovieDetailsSerializer(queryset, many=True)

        return Response({
            "message": "success",
            "result": serializer.data
        }, status=status.HTTP_200_OK)


    # ---------------- RETRIEVE ----------------
    def retrieve(self, request, *args, **kwargs):
        try:
            movie_id = kwargs.get("pk")

            movie = StagingMovieDetails.objects.using("staging_db").filter(_id=movie_id).first()

            if not movie:
                return Response({
                    "message": "Movie not found in staging"
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = StagingMovieDetailsSerializer(movie)

            return Response({
                "message": "success",
                "result": serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": "error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # ---------------- CREATE ----------------
    def create(self, request, *args, **kwargs):
        try:
            poster_base64 = request.data.get("poster")
            trailer_base64 = request.data.get("trailer")

            if isinstance(poster_base64, list):
                poster_base64 = poster_base64[0]

            if isinstance(trailer_base64, list):
                trailer_base64 = trailer_base64[0]

            data_copy = request.data.copy()
            data_copy["poster"] = None
            data_copy["trailer"] = None

            serializer = self.get_serializer(data=data_copy)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            movie = serializer.instance
            entity_type = "movie"
            title_name = movie.title if movie.title else "untitled-movie"

            saved_poster = None
            saved_trailer = None

            # ------ Upload Poster ------
            if poster_base64 and poster_base64 != "null":
                saved_poster = save_image_to_azure(
                    poster_base64,
                    movie._id,
                    title_name,
                    entity_type
                )

            # ------ Upload Trailer ------
            if trailer_base64 and trailer_base64 != "null":
                saved_trailer = save_video_to_azure(
                    trailer_base64,
                    movie._id,
                    title_name,
                    entity_type
                )

            if saved_poster:
                movie.poster = [saved_poster]

            if saved_trailer:
                movie.trailer = [saved_trailer]

            movie.save()

            return Response({
                "message": "success",
                "result": StagingMovieDetailsSerializer(movie).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "message": "An error occurred",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # ---------------- UPDATE (PUT/PATCH) ----------------
    def update(self, request, *args, **kwargs):
        try:
            movie = self.get_object()

            poster_base64 = request.data.get("poster")
            trailer_base64 = request.data.get("trailer")

            if isinstance(poster_base64, list):
                poster_base64 = poster_base64[0]

            if isinstance(trailer_base64, list):
                trailer_base64 = trailer_base64[0]

            data_copy = request.data.copy()
            data_copy["poster"] = movie.poster
            data_copy["trailer"] = movie.trailer

            serializer = self.get_serializer(movie, data=data_copy, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            entity_type = "movie"
            title_name = movie.title if movie.title else "untitled-movie"

            # Upload updated poster
            if poster_base64 and not str(poster_base64).startswith("https"):
                saved_poster = save_image_to_azure(
                    poster_base64,
                    movie._id,
                    title_name,
                    entity_type
                )
                movie.poster = [saved_poster]

            # Upload updated trailer
            if trailer_base64 and not str(trailer_base64).startswith("https"):
                saved_trailer = save_video_to_azure(
                    trailer_base64,
                    movie._id,
                    title_name,
                    entity_type
                )
                movie.trailer = [saved_trailer]

            movie.save()

            return Response({
                "message": "updated successfully",
                "result": StagingMovieDetailsSerializer(movie).data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": "Update failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # ---------------- DELETE ----------------
    def destroy(self, request, *args, **kwargs):
        movie = self.get_object()
        movie.delete(using="staging_db")

        return Response({
            "message": "deleted successfully"
        }, status=status.HTTP_200_OK)









# class StagingMovieFilterView(APIView):
#     def get(self, request):
#         platform_id = request.query_params.get("platform_id")
#         header_id = request.query_params.get("header_id")
#         geners_id = request.query_params.get("geners_id")
#         search = request.query_params.get("search")

#         # Show ALL movies (no status filter)
#         queryset = StagingMovieDetails.objects.all().order_by("-_id")

#         # Apply filters
#         if platform_id:
#             queryset = queryset.filter(platform_id=platform_id)

#         if header_id:
#             queryset = queryset.filter(header_id=header_id)

#         if geners_id:
#             queryset = queryset.filter(geners_id=geners_id)

#         if search:
#             queryset = queryset.filter(title__icontains=search)

#         serializer = StagingMovieDetailsSerializer(queryset, many=True)

#         return Response({
#             "message": "success",
#             "result": serializer.data
#         }, status=status.HTTP_200_OK)


from django.utils import timezone

# class StagingMovieFilterView(APIView):
#     def get(self, request):
#         platform_id = request.query_params.get("platform_id")
#         header_id = request.query_params.get("header_id")
#         geners_id = request.query_params.get("geners_id")
#         search = request.query_params.get("search")

#         # Show ONLY movies where publish_at time reached
#         queryset = StagingMovieDetails.objects.filter(
#             publish_at__lte=timezone.now()
#         ).order_by("-_id")

#         # Apply filters
#         if platform_id:
#             queryset = queryset.filter(platform_id=platform_id)

#         if header_id:
#             queryset = queryset.filter(header_id=header_id)

#         if geners_id:
#             queryset = queryset.filter(geners_id=geners_id)

#         # Search
#         if search:
#             queryset = queryset.filter(title__icontains=search)

#         serializer = StagingMovieDetailsSerializer(queryset, many=True)

#         return Response({
#             "message": "success",
#             "count": queryset.count(),
#             "result": serializer.data
#         }, status=status.HTTP_200_OK)


class StagingMovieFilterView(APIView):
    def get(self, request):
        platform_id = request.query_params.get("platform_id")
        header_id = request.query_params.get("header_id")
        geners_id = request.query_params.get("geners_id")
        search = request.query_params.get("search")
        language = request.query_params.get("language")   # <--- NEW

        # Removed publish_at__lte filter
        queryset = StagingMovieDetails.objects.all().order_by("-_id")

        # Apply filters
        if platform_id:
            queryset = queryset.filter(platform_id=platform_id)

        if header_id:
            queryset = queryset.filter(header_id=header_id)

        if geners_id:
            queryset = queryset.filter(geners_id=geners_id)

        # MULTIPLE LANGUAGES SUPPORT
        if language:
            lang_list = [lang.strip() for lang in language.split(",")]
            queryset = queryset.filter(language__in=lang_list)

        # Search
        if search:
            queryset = queryset.filter(title__icontains=search)

        serializer = StagingMovieDetailsSerializer(queryset, many=True)

        return Response({
            "message": "success",
            "count": queryset.count(),
            "result": serializer.data
        }, status=status.HTTP_200_OK)
















# class PublishStagingMovie(APIView):
#     def post(self, request, staging_id):
#         try:
#             staging_movie = StagingMovieDetails.objects.using("staging_db").get(_id=staging_id)

#             movie = MovieDetails.objects.using("default").create(
#                 title=staging_movie.title,
#                 header_id=staging_movie.header_id,
#                 release_date=staging_movie.release_date,
#                 cast=staging_movie.cast,
#                 actions=staging_movie.actions,
#                 platform_id=staging_movie.platform_id,
#                 status="SUCCESS",
#                 geners_id=staging_movie.geners_id,
#                 user_id=staging_movie.user_id,
#                 poster=staging_movie.poster,
#                 trailer=staging_movie.trailer,
#                 language=staging_movie.language,
#                 trailer_link=staging_movie.trailer_link,
#                 publish_at=staging_movie.publish_at,
#             )

#             return Response({
#                 "message": "published successfully",
#                 "result": MovieDetailsSerializer(movie).data
#             }, status=201)

#         except StagingMovieDetails.DoesNotExist:
#             return Response({"message": "Staging movie not found"}, status=404)
#         except Exception as e:
#             return Response({"error": str(e)}, status=500)


class PublishStagingMovie(APIView):

    # GET should behave same as POST
    def get(self, request, staging_id):
        return self.post(request, staging_id)

    def post(self, request, staging_id):
        try:
            staging_movie = StagingMovieDetails.objects.using("staging_db").get(_id=staging_id)

            # FIX 1: Check if staging has platform_id or platform
            platform_value = getattr(staging_movie, "platform_id", None)
            if not platform_value:
                platform_value = getattr(staging_movie, "platform", None)

            # FIX 2: Use SAME values as staging (don't hardcode SUCCESS)
            status_value = getattr(staging_movie, "status", "SUCCESS")

            # FIX 3: actions may not exist in staging
            actions_value = getattr(staging_movie, "actions", None)

            movie = MovieDetails.objects.using("default").create(
                title=staging_movie.title,
                header_id=staging_movie.header_id,
                release_date=staging_movie.release_date,
                cast=staging_movie.cast,
                actions=actions_value,
                platform_id=platform_value,
                status=status_value,
                geners_id=staging_movie.geners_id,
                user_id=staging_movie.user_id,
                poster=staging_movie.poster,
                trailer=staging_movie.trailer,
                language=staging_movie.language,
                trailer_link=staging_movie.trailer_link,
                publish_at=staging_movie.publish_at,
            )

            return Response({
                "message": "published successfully",
                "result": MovieDetailsSerializer(movie).data
            }, status=201)

        except StagingMovieDetails.DoesNotExist:
            return Response({"message": "Staging movie not found"}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
