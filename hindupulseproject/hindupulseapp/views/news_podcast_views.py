from rest_framework import viewsets, status
from rest_framework.response import Response
from ..models import NewsPodcast
from ..serializers import NewsPodcastSerializer, NewsPodcastSerializer1
from ..utils import save_image_to_azure


class NewsPodcastView(viewsets.ModelViewSet):
    queryset = NewsPodcast.objects.all()
    serializer_class = NewsPodcastSerializer1
    def get_queryset(self):
        return NewsPodcast.objects.filter(status="SUCCESS").order_by("-_id")
    # --------------------------
    # CREATE (POST CALL)
    # --------------------------
    def create(self, request, *args, **kwargs):

        # Use write serializer for POST
        serializer = NewsPodcastSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Save object first (without image)
        podcast = serializer.save()

        # ---- IMAGE PROCESSING ----
        image_data = request.data.get("image_location")
        saved_image_url = None

        if image_data and image_data != "null":
            entity_type = "news_podcast"

            saved_image_url = save_image_to_azure(
                image_data,
                podcast._id,
                podcast.name,
                entity_type
            )

            if saved_image_url:
                podcast.image_location = saved_image_url
                podcast.save()

        # Return formatted output using serializer1
        output_serializer = NewsPodcastSerializer1(podcast)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)








# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from ..models import NewsPodcast
# from ..serializers import NewsPodcastSerializer, NewsPodcastSerializer1
# from ..utils import save_image_to_azure, save_video_to_azure



# class NewsPodcastView(viewsets.ModelViewSet):
#     queryset = NewsPodcast.objects.all()
#     serializer_class = NewsPodcastSerializer1

#     def get_queryset(self):
#         return NewsPodcast.objects.filter(status="SUCCESS").order_by("-_id")

#     def create(self, request, *args, **kwargs):
#         print("🔥 REQUEST DATA =>", request.data)

#         serializer = NewsPodcastSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         podcast = serializer.save()

#         # IMAGE
#         image_data = request.data.get("image_location")
#         print("🖼 IMAGE DATA =>", bool(image_data))

#         if image_data and str(image_data).lower() != "null":
#             podcast.image_location = save_image_to_azure(
#                 image_data, podcast._id, podcast.name, "news_podcast"
#             )

#         # VIDEO
#         video_data = request.data.get("video_location")
#         print("🎥 VIDEO DATA =>", video_data)

#         if video_data and str(video_data).lower() != "null":
#             podcast.video_location = save_video_to_azure(
#                 video_data, podcast._id, podcast.name, "news_podcast"
#             )
#         else:
#             print("❌ VIDEO NOT RECEIVED FROM REQUEST")

#         podcast.save()
#         return Response(NewsPodcastSerializer1(podcast).data, status=201)