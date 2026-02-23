# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from ..models import MovieDetails
# from ..serializers import MovieDetailsSerializer
# from ..utils import save_image_to_azure, save_video_to_azure

# class MovieDetailsViewSet(viewsets.ModelViewSet):
#     queryset = MovieDetails.objects.all()
#     serializer_class = MovieDetailsSerializer


#     def list(self, request, *args, **kwargs):
#         queryset = MovieDetails.objects.filter(status="SUCCESS")
#         serializer = MovieDetailsSerializer(queryset, many=True)

#         return Response({
#             "message": "success",
#             "result": serializer.data
#         }, status=status.HTTP_200_OK)



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
#                 "result": MovieDetailsSerializer(movie).data
#             }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({
#                 "message": "An error occurred",
#                 "error": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





from ..enums import EntityStatus

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models import MovieDetails, StagingMovieDetails
from ..serializers import MovieDetailsSerializer, StagingMovieDetailsSerializer
from ..utils import save_image_to_azure, save_video_to_azure

from django.db.models import Q

from ..serializers import MovieDetailsSerializer
from ..utils import save_image_to_azure, save_video_to_azure
import uuid
from django.utils import timezone

class MovieDetailsViewSet(viewsets.ModelViewSet):
    queryset = MovieDetails.objects.all()
    serializer_class = MovieDetailsSerializer


    # ---------------- LIST ----------------
    def list(self, request, *args, **kwargs):
        queryset = MovieDetails.objects.filter(status="SUCCESS")
        serializer = MovieDetailsSerializer(queryset, many=True)

        return Response({
            "message": "success",
            "result": serializer.data
        }, status=status.HTTP_200_OK)


    # ---------------- RETRIEVE ----------------
    def retrieve(self, request, *args, **kwargs):
        movie = self.get_object()
        serializer = MovieDetailsSerializer(movie)
        return Response({
            "message": "success",
            "result": serializer.data
        })


    # ---------------- CREATE ----------------
    def create(self, request, *args, **kwargs):
        try:
            poster_base64 = request.data.get("poster")
            trailer_base64 = request.data.get("trailer")

            if isinstance(poster_base64, list):
                poster_base64 = poster_base64[0]

            if isinstance(trailer_base64, list):
                trailer_base64 = trailer_base64[0]

            # Save MovieDetails without files
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

            if poster_base64 and poster_base64 != "null":
                saved_poster = save_image_to_azure(
                    poster_base64, movie._id, title_name, entity_type
                )

            if trailer_base64 and trailer_base64 != "null":
                saved_trailer = save_video_to_azure(
                    trailer_base64, movie._id, title_name, entity_type
                )

            if saved_poster:
                movie.poster = [saved_poster]

            if saved_trailer:
                movie.trailer = [saved_trailer]

            movie.save()

            # Save into staging DB
            StagingMovieDetails.objects.using("staging_db").create(
                _id=movie._id,
                title=movie.title,
                header_id=movie.header_id,
                poster=movie.poster,
                release_date=movie.release_date,
                cast=movie.cast,
                trailer=movie.trailer,
                actions=movie.actions,
                platform_id=movie.platform_id,
                status="STAGING",
                geners_id=movie.geners_id,
                user_id=movie.user_id,
                language=getattr(movie, "language", None),
                publish_at=movie.publish_at,
                trailer_link=movie.trailer_link
            )

            return Response({
                "message": "success",
                "result": MovieDetailsSerializer(movie).data
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

            # Upload new poster if sent
            if poster_base64 and not poster_base64.startswith("https"):
                saved_poster = save_image_to_azure(
                    poster_base64, movie._id, title_name, entity_type
                )
                movie.poster = [saved_poster]

            # Upload new trailer if sent
            if trailer_base64 and not trailer_base64.startswith("https"):
                saved_trailer = save_video_to_azure(
                    trailer_base64, movie._id, title_name, entity_type
                )
                movie.trailer = [saved_trailer]

            movie.save()

            # UPDATE staging DB
            StagingMovieDetails.objects.using("staging_db").filter(_id=movie._id).update(
                title=movie.title,
                header_id=movie.header_id,
                poster=movie.poster,
                release_date=movie.release_date,
                cast=movie.cast,
                trailer=movie.trailer,
                actions=movie.actions,
                platform_id=movie.platform_id,
                status="UPDATED",
                geners_id=movie.geners_id,
                user_id=movie.user_id,
                language=getattr(movie, "language", None),
                publish_at=movie.publish_at,
                trailer_link=movie.trailer_link
            )

            return Response({
                "message": "updated successfully",
                "result": MovieDetailsSerializer(movie).data
            })

        except Exception as e:
            return Response({
                "message": "Update failed",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # ---------------- DELETE ----------------
    def destroy(self, request, *args, **kwargs):
        movie = self.get_object()

        movie.delete()

        # Delete from staging DB also
        StagingMovieDetails.objects.using("staging_db").filter(_id=movie._id).delete()

        return Response({
            "message": "deleted successfully"
        }, status=status.HTTP_200_OK)





# class MovieDetailsViewSet(viewsets.ModelViewSet):
#     queryset = MovieDetails.objects.all()
#     serializer_class = MovieDetailsSerializer


#     # ---------------- LIST ----------------
#     def list(self, request, *args, **kwargs):
#         queryset = MovieDetails.objects.filter(status="SUCCESS")
#         serializer = MovieDetailsSerializer(queryset, many=True)

#         return Response({
#             "message": "success",
#             "result": serializer.data
#         }, status=status.HTTP_200_OK)



#     # ---------------- CREATE ----------------
#     def create(self, request, *args, **kwargs):
#         try:
#             poster_base64 = request.data.get("poster")
#             trailer_base64 = request.data.get("trailer")

#             # If list, take first item
#             if isinstance(poster_base64, list):
#                 poster_base64 = poster_base64[0]

#             if isinstance(trailer_base64, list):
#                 trailer_base64 = trailer_base64[0]

#             # First save MovieDetails WITHOUT files
#             data_copy = request.data.copy()
#             data_copy["poster"] = None
#             data_copy["trailer"] = None

#             serializer = self.get_serializer(data=data_copy)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()

#             movie = serializer.instance
#             entity_type = "movie"

#             title_name = movie.title if movie.title else "untitled-movie"

#             saved_poster = None
#             saved_trailer = None

#             # -------- Upload Poster --------
#             if poster_base64 and poster_base64 != "null":
#                 saved_poster = save_image_to_azure(
#                     poster_base64,
#                     movie._id,
#                     title_name,
#                     entity_type
#                 )

#             # -------- Upload Trailer --------
#             if trailer_base64 and trailer_base64 != "null":
#                 saved_trailer = save_video_to_azure(
#                     trailer_base64,
#                     movie._id,
#                     title_name,
#                     entity_type
#                 )

#             # Update movie with uploaded paths
#             if saved_poster:
#                 movie.poster = [saved_poster]

#             if saved_trailer:
#                 movie.trailer = [saved_trailer]

#             movie.save()

#             # ---------------------------------------------------
#             # 🚀 NOW SAVE SAME DATA INTO STAGING DATABASE
#             # ---------------------------------------------------
#             StagingMovieDetails.objects.using("staging_db").create(
#                 _id=movie._id,
#                 title=movie.title,
#                 header_id=movie.header_id,
#                 poster=movie.poster,
#                 release_date=movie.release_date,
#                 cast=movie.cast,
#                 trailer=movie.trailer,
#                 actions=movie.actions,
#                 platform_id=movie.platform_id,
#                 status="STAGING",
#                 geners_id=movie.geners_id,
#                 user_id=movie.user_id,
#                 language=getattr(movie, "language", None),
#                 publish_at=movie.publish_at,
#                 trailer_link=movie.trailer_link
#             )

#             return Response({
#                 "message": "success",
#                 "result": MovieDetailsSerializer(movie).data
#             }, status=status.HTTP_201_CREATED)


#         except Exception as e:
#             return Response({
#                 "message": "An error occurred",
#                 "error": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








# class MovieFilterView(APIView):
#     def get(self, request):
#         platform_id = request.query_params.get("platform_id")
#         header_id = request.query_params.get("header_id")
#         geners_id = request.query_params.get("geners_id")
#         search = request.query_params.get("search")   # <-- search added

#         # Only SUCCESS movies
#         queryset = MovieDetails.objects.filter(status="SUCCESS").order_by("-_id")

#         # Apply filters
#         if platform_id:
#             queryset = queryset.filter(platform_id=platform_id)

#         if header_id:
#             queryset = queryset.filter(header_id=header_id)

#         if geners_id:
#             queryset = queryset.filter(geners_id=geners_id)

#         # ----------- SEARCH FILTER (title only) -----------
#         if search:
#             queryset = queryset.filter(title__icontains=search)

#         serializer = MovieDetailsSerializer(queryset, many=True)

#         return Response({
#             "message": "success",
#             "count": queryset.count(),
#             "result": serializer.data
#         }, status=status.HTTP_200_OK)








# class MovieFilterView(APIView):
#     def get(self, request):
#         platform_id = request.query_params.get("platform_id")
#         header_id = request.query_params.get("header_id")
#         geners_id = request.query_params.get("geners_id")
#         search = request.query_params.get("search")

#         # Only SUCCESS movies + publish_at reached
#         queryset = MovieDetails.objects.filter(
#             status="SUCCESS",
#             publish_at__lte=timezone.now()   # <-- Added
#         ).order_by("-_id")

#         # Apply filters
#         if platform_id:
#             queryset = queryset.filter(platform_id=platform_id)

#         if header_id:
#             queryset = queryset.filter(header_id=header_id)

#         if geners_id:
#             queryset = queryset.filter(geners_id=geners_id)

#         # Search by title
#         if search:
#             queryset = queryset.filter(title__icontains=search)

#         serializer = MovieDetailsSerializer(queryset, many=True)

#         return Response({
#             "message": "success",
#             "count": queryset.count(),
#             "result": serializer.data
#         }, status=status.HTTP_200_OK)






class MovieFilterView(APIView):
    def get(self, request):
        platform_id = request.query_params.get("platform_id")
        header_id = request.query_params.get("header_id")
        geners_id = request.query_params.get("geners_id")
        search = request.query_params.get("search")
        language = request.query_params.get("language")   # <--- NEW

        # Removed publish_at__lte
        queryset = MovieDetails.objects.filter(
            status="SUCCESS"
        ).order_by("-_id")

        # Apply filters
        if platform_id:
            queryset = queryset.filter(platform_id=platform_id)

        if header_id:
            queryset = queryset.filter(header_id=header_id)

        if geners_id:
            queryset = queryset.filter(geners_id=geners_id)

        # MULTIPLE LANGUAGE FILTER SUPPORT
        if language:
            lang_list = [lang.strip() for lang in language.split(",")]
            queryset = queryset.filter(language__in=lang_list)

        # Search by title
        if search:
            queryset = queryset.filter(title__icontains=search)

        serializer = MovieDetailsSerializer(queryset, many=True)

        return Response({
            "message": "success",
            "count": queryset.count(),
            "result": serializer.data
        }, status=status.HTTP_200_OK)
