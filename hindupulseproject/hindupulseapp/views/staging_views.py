
# # getting the images in th list

# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from ..models import StagingModel
# from ..serializers import StagingSerializer1,StagingSerializer
# import requests
# from bs4 import BeautifulSoup
# import uuid
# from urllib.parse import urljoin
# import requests
# from io import BytesIO
# from PIL import Image
# from ..utils import save_image_from_url,save_image_to_azure_v2,save_audio_to_azure
# from rest_framework import generics, permissions
# from django.shortcuts import get_object_or_404
# # from ..utils import save_image_to_folder
# from django.http import JsonResponse
# from ..pagination.pagination import CustomPagination 



# class Staging_Post(generics.GenericAPIView):
#     serializer_class = StagingSerializer
   

#     def post(self, request, *args, **kwargs):
        
#         audio_location = request.data.get('audio_location')  # New audio location
#         image_location = request.data.get('image_location', [])
#         if not isinstance(image_location, list):
#             return JsonResponse({"error": "Image location must be a list"}, status=400)

#         # Make a mutable copy of request.data
#         mutable_data = request.data.copy()
#         mutable_data['image_location'] = []
#         mutable_data['audio_location'] = "null"  # Set audio initially to null


#         # Instantiate the serializer with the mutable copy
#         serializer = self.get_serializer(data=mutable_data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         saved_image_paths = []
#         for idx, image_data in enumerate(image_location):
#             if image_data:
#                 saved_location = save_image_to_azure_v2(image_data, serializer.instance._id, 'news', f'image{idx + 1}')
#                 if saved_location:
#                     saved_image_paths.append(saved_location)

#         if saved_image_paths:
#             serializer.instance.image_location = saved_image_paths
#             serializer.instance.save()

#         if audio_location and audio_location != "null":  # Handle audio upload
#             saved_audio_location = save_audio_to_azure(audio_location, serializer.instance._id, serializer.instance.category_id.name, "news")
#             if saved_audio_location:
#                 serializer.instance.audio_location = saved_audio_location
#                 serializer.instance.save()
      

       
#         return Response({
#             "message": "success",
#             "result": serializer.data
#         })
    


# class Staging_Edit(generics.GenericAPIView):
#     serializer_class = StagingSerializer

   

#     def put(self, request, _id):
       
#         # Retrieve the instance
#         instance = get_object_or_404(StagingModel, _id=_id)

#         # Retrieve image_location from request data

#         audio_location = request.data.get('audio_location')  # New audio location
#         image_location = request.data.get('image_location', [])
#         if not isinstance(image_location, list):
#             return JsonResponse({"error": "Image location must be a list"}, status=400)

#         # Make a mutable copy of request.data
#         mutable_data = request.data.copy()
#         mutable_data['image_location'] = instance.image_location  # Preserve existing image locations
#         mutable_data['audio_location'] = "null"  # Set audio initially to null


#         # Instantiate the serializer with the mutable copy and instance
#         serializer = self.get_serializer(instance, data=mutable_data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         saved_image_paths = []
#         for idx, image_data in enumerate(image_location):
#             if image_data and image_data != "null":
#                 saved_location = save_image_to_azure_v2(image_data, serializer.instance._id, 'news', f'image{idx + 1}')
#                 if saved_location:
#                     saved_image_paths.append(saved_location)

#         # Update the instance with new image locations if any images were saved
#         if saved_image_paths:
#             serializer.instance.image_location = saved_image_paths
#             serializer.instance.save()

#         if audio_location and audio_location != "null":  # Handle audio upload
#             saved_audio_location = save_audio_to_azure(audio_location, serializer.instance._id, serializer.instance.category_id.name, "news")
#             if saved_audio_location:
#                 serializer.instance.audio_location = saved_audio_location
#                 serializer.instance.save()

     
      
#         return Response({
#             "message": "success",
#             "result": serializer.data
#         })



from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from ..models import StagingModel,Language
from ..serializers import StagingSerializer1,StagingSerializer
import requests
from bs4 import BeautifulSoup
import uuid
from urllib.parse import urljoin
import requests
from io import BytesIO
from PIL import Image
from ..utils import save_image_from_url,save_image_to_azure_v2,save_audio_to_azure
from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
# from ..utils import save_image_to_folder
from django.http import JsonResponse
from ..pagination.pagination import CustomPagination 

from rest_framework.permissions import IsAuthenticated
from ..enums.member_status_enum import MemberStatus
from ..models import Register









# class Staging_Post(generics.GenericAPIView):
#     serializer_class = StagingSerializer
#     permission_classes = []

#     def get_permissions(self):
#         if self.request.method in ['POST', 'PUT']:
#             return [IsAuthenticated()]
#         return super().get_permissions()

#     def post(self, request, *args, **kwargs):
#         user_id = request.user.id
#         try:
#             user = Register.objects.get(id=user_id)
#             if user.is_member != MemberStatus.true.value:
#                 return JsonResponse({"error": "User is not a member"}, status=400)
#         except Register.DoesNotExist:
#             return JsonResponse({"error": "User not found"}, status=404)
#         audio_location = request.data.get('audio_location')
#         image_location = request.data.get('image_location', [])
        
#         # Validate that image_location is a list
#         if not isinstance(image_location, list):
#             return JsonResponse({"error": "Image location must be a list"}, status=400)
#         if len(image_location) > 3:
#             return JsonResponse({"error": "You cannot upload more than three images"}, status=400)

#         # Prepare data for serializer
#         mutable_data = request.data.copy()
#         mutable_data['image_location'] = []
#         mutable_data['audio_location'] = "null"  # Set audio to null initially

#         # Create and validate serializer
#         serializer = self.get_serializer(data=mutable_data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         # Process and save images
#         saved_image_paths = []
#         for idx, image_data in enumerate(image_location):
#             if image_data:
#                 saved_location = save_image_to_azure_v2(image_data, serializer.instance._id, 'news', f'image{idx + 1}')
#                 if saved_location:
#                     saved_image_paths.append(saved_location)

#         if saved_image_paths:
#             serializer.instance.image_location = saved_image_paths
#             serializer.instance.save()

#         # Handle audio upload
#         if audio_location and audio_location != "null":
#             saved_audio_location = save_audio_to_azure(audio_location, serializer.instance._id, serializer.instance.category_id.name, "news")
#             if saved_audio_location:
#                 serializer.instance.audio_location = saved_audio_location
#                 serializer.instance.save()

#         # Return the response with the original data
#         return Response({
#             "message": "success",
#             "result": {
#                 "entered_data": mutable_data,  # Return exactly what was entered
#                 "saved_data": serializer.data,  # Return saved serializer data
#             }
#         })


import requests
from django.conf import settings
from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from ..enums import LanguageEnum
from ..utils import save_translations_for_other_languages,save_audio_to_azure,translate_text_sarvam
import base64
from uuid import UUID


# class Staging_Post(generics.GenericAPIView):
#     serializer_class = StagingSerializer
#     permission_classes = []

#     def get_permissions(self):
#         if self.request.method in ['POST', 'PUT']:
#             return [IsAuthenticated()]
#         return super().get_permissions()

#     def post(self, request, *args, **kwargs):
#         user = request.user
#         language_requested = request.data.get("language", "ENGLISH").upper()

#         # -----------------------------------------
#         # Build a map: { "ENGLISH": "en", "HINDI": "hi", ... }
#         # -----------------------------------------
#         LANG_MAP = {k: v.value for k, v in LanguageEnum.__members__.items()}
#         # Also allow user to send: en, hi, te...
#         REVERSE_LANG_MAP = {v: k for k, v in LANG_MAP.items()}

#         # Normalize selected language
#         if language_requested in LANG_MAP:  
#             selected_lang_key = language_requested
#             selected_lang_code = LANG_MAP[language_requested]

#         elif language_requested.lower() in REVERSE_LANG_MAP:
#             selected_lang_key = REVERSE_LANG_MAP[language_requested.lower()]
#             selected_lang_code = language_requested.lower()

#         else:
#             return JsonResponse({
#                 "error": "Invalid language selected",
#                 "valid_language_keys": list(LANG_MAP.keys()),
#                 "valid_language_codes": list(REVERSE_LANG_MAP.keys())
#             }, status=400)

#         # -----------------------------------------
#         # Validate Member
#         # -----------------------------------------
#         try:
#             reg = Register.objects.get(id=user.id)
#             if reg.is_member != MemberStatus.true.value:
#                 return JsonResponse({"error": "User is not a member"}, status=400)
#         except Register.DoesNotExist:
#             return JsonResponse({"error": "User not found"}, status=404)

#         # -----------------------------------------
#         # Validate Images
#         # -----------------------------------------
#         image_location = request.data.get('image_location', [])
#         if not isinstance(image_location, list):
#             return JsonResponse({"error": "Image location must be a list"}, status=400)

#         if len(image_location) > 3:
#             return JsonResponse({"error": "You cannot upload more than three images"}, status=400)

#         # -----------------------------------------
#         # Save base data
#         # -----------------------------------------
#         record_id = request.data.get('_id')
#         if StagingModel.objects.filter(_id=record_id).exists():
#             return JsonResponse({"error": "Record already exists in staging"}, status=400)

#         mutable_data = request.data.copy()
#         mutable_data['image_location'] = []
#         mutable_data['audio_location'] = "null"

#         serializer = self.get_serializer(data=mutable_data)
#         serializer.is_valid(raise_exception=True)

#         with transaction.atomic():
#             saved_instance = serializer.save()

#             # Upload images
#             saved_image_paths = []
#             for idx, img in enumerate(image_location):
#                 if img and img != "null":
#                     path = save_image_to_azure_v2(img, saved_instance._id, 'news', f'image{idx+1}')
#                     if path:
#                         saved_image_paths.append(path)

#             saved_instance.image_location = saved_image_paths
#             saved_instance.save()

#             # Upload audio
#             audio_data = request.data.get('audio_location')
#             if audio_data and audio_data != "null":
#                 audio_path = save_audio_to_azure(audio_data, saved_instance._id, "politics", "news")
#                 saved_instance.audio_location = audio_path
#                 saved_instance.save()

#         # ==============================================
#         # TRANSLATE ONLY SELECTED LANGUAGE
#         # ==============================================

#         headline = mutable_data.get("headline", "")
#         desc = mutable_data.get("desc", "")

#         translated_headline = translate_text_sarvam(headline, selected_lang_code)
#         translated_desc = translate_text_sarvam(desc, selected_lang_code)

#         # DB save format
#         desc_translation_list = [
#             {"language": selected_lang_key, "desc": translated_desc}
#         ]

#         desc_translations = {selected_lang_key: translated_desc}

#         # Save translations
#         save_translations_for_other_languages(
#             instance=saved_instance,
#             headline=headline,
#             desc_translations=desc_translations,
#             desc_translation_list=desc_translation_list,
#             user_id=user.id,
#             category=request.data.get("category_id"),
#             short_description=request.data.get("short_description"),
#             location=request.data.get("location"),
#             news_sub_category=request.data.get("news_sub_category_id"),
#             image_location=saved_image_paths,
#             publish_at=request.data.get("publish_at"),
#             status=request.data.get("status"),
#             is_published=request.data.get("is_published")
#         )

#         # Final response
#         return Response({
#             "message": "success",
#             "converted_language": {
#                 "key": selected_lang_key,
#                 "code": selected_lang_code
#             },
#             "result": {
#                 "original": {
#                     "headline": headline,
#                     "desc": desc
#                 },
#                 "translation": {
#                     "headline": translated_headline,
#                     "desc": translated_desc
#                 },
#                 "saved_data": StagingSerializer(saved_instance).data
#             }
#         })

# class Staging_Post(generics.GenericAPIView):
#     serializer_class = StagingSerializer
#     permission_classes = []

#     def get_permissions(self):
#         if self.request.method in ['POST', 'PUT']:
#             return [IsAuthenticated()]
#         return super().get_permissions()

#     def post(self, request, *args, **kwargs):
#         user = request.user
#         language_id = request.data.get("language")  # UUID string

#         if not language_id:
#             return JsonResponse({"error": "language_id is required"}, status=400)

#         # --------------------------
#         # Validate Member
#         # --------------------------
#         try:
#             reg = Register.objects.get(id=user.id)
#             if reg.is_member != MemberStatus.true.value:
#                 return JsonResponse({"error": "User is not a member"}, status=400)
#         except Register.DoesNotExist:
#             return JsonResponse({"error": "User not found"}, status=404)

#         # --------------------------
#         # Validate language UUID
#         # --------------------------
#         try:
#             language_obj = Language.objects.get(_id=language_id)
#         except Language.DoesNotExist:
#             return JsonResponse({"error": "Invalid language_id"}, status=400)

#         # Map language name to Sarvam code
#         try:
#             target_lang_code = LanguageEnum[language_obj.name.upper()].value
#         except KeyError:
#             return JsonResponse({
#                 "error": "Language not supported for translation",
#                 "supported_languages": list(LanguageEnum.__members__.keys())
#             }, status=400)

#         # --------------------------
#         # Validate Images
#         # --------------------------
#         image_location = request.data.get('image_location', [])
#         if not isinstance(image_location, list):
#             return JsonResponse({"error": "Image location must be a list"}, status=400)
#         if len(image_location) > 3:
#             return JsonResponse({"error": "You cannot upload more than three images"}, status=400)

#         # --------------------------
#         # Prepare serializer data
#         # --------------------------
#         record_id = request.data.get('_id')
#         if StagingModel.objects.filter(_id=record_id).exists():
#             return JsonResponse({"error": "Record already exists in staging"}, status=400)

#         mutable_data = request.data.copy()
#         mutable_data['image_location'] = []
#         mutable_data['audio_location'] = "null"
#         mutable_data['language_id'] = language_obj  # save FK

#         serializer = self.get_serializer(data=mutable_data)
#         serializer.is_valid(raise_exception=True)

#         # --------------------------
#         # Save base instance
#         # --------------------------
#         with transaction.atomic():
#             saved_instance = serializer.save()

#             # Upload images
#             saved_image_paths = []
#             for idx, img in enumerate(image_location):
#                 if img and img != "null":
#                     path = save_image_to_azure_v2(img, saved_instance._id, 'news', f'image{idx+1}')
#                     if path:
#                         saved_image_paths.append(path)

#             saved_instance.image_location = saved_image_paths
#             saved_instance.save()

#             # Upload audio
#             audio_data = request.data.get('audio_location')
#             if audio_data and audio_data != "null":
#                 audio_path = save_audio_to_azure(audio_data, saved_instance._id, "politics", "news")
#                 saved_instance.audio_location = audio_path
#                 saved_instance.save()

#         # --------------------------
#         # Translate only selected language
#         # --------------------------
#         headline = mutable_data.get("headline", "")
#         desc = mutable_data.get("desc", "")

#         translated_headline = translate_text_sarvam(headline, target_lang_code)
#         translated_desc = translate_text_sarvam(desc, target_lang_code)

#         desc_translation_list = [{"language": language_obj.name, "desc": translated_desc}]
#         desc_translations = {language_obj.name: translated_desc}

#         # Save translations
#         save_translations_for_other_languages(
#             instance=saved_instance,
#             headline=headline,
#             desc_translations=desc_translations,
#             desc_translation_list=desc_translation_list,
#             user_id=user.id,
#             category=request.data.get("category_id"),
#             short_description=request.data.get("short_description"),
#             location=request.data.get("location"),
#             news_sub_category=request.data.get("news_sub_category_id"),
#             image_location=saved_image_paths,
#             publish_at=request.data.get("publish_at"),
#             status=request.data.get("status"),
#             is_published=request.data.get("is_published")
#         )

#         # --------------------------
#         # Response
#         # --------------------------
#         return Response({
#             "message": "success",
#             "converted_language": {
#                 "id": str(language_obj._id),
#                 "name": language_obj.name,
#                 "code": target_lang_code
#             },
#             "result": {
#                 "original": {"headline": headline, "desc": desc},
#                 "translation": {"headline": translated_headline, "desc": translated_desc},
#                 "saved_data": StagingSerializer(saved_instance).data
#             }
#         })




###### mutli language post ##########

class Staging_Post(generics.GenericAPIView):
    serializer_class = StagingSerializer
    permission_classes = []

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT']:
            from rest_framework.permissions import IsAuthenticated
            return [IsAuthenticated()]
        return super().get_permissions()

    def post(self, request, *args, **kwargs):
        user = request.user
        language_id = request.data.get("language")  

        if not language_id:
            return JsonResponse({"error": "language_id is required"}, status=400)

        # Validate Member
        try:
            reg = Register.objects.get(id=user.id)
            if reg.is_member != MemberStatus.true.value:
                return JsonResponse({"error": "User is not a member"}, status=400)
        except Register.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        # Validate Language UUID
        try:
            language_obj = Language.objects.get(_id=language_id)
        except Language.DoesNotExist:
            return JsonResponse({"error": "Invalid language_id"}, status=400)

        # Get language code from Enum
        try:
            target_lang_code = LanguageEnum[language_obj.name.upper()].value
        except KeyError:
            return JsonResponse({
                "error": "Language not supported",
                "supported_languages": list(LanguageEnum.__members__.keys())
            }, status=400)

        # Validate Images
        image_location = request.data.get('image_location', [])
        if not isinstance(image_location, list):
            return JsonResponse({"error": "Image location must be a list"}, status=400)
        if len(image_location) > 3:
            return JsonResponse({"error": "You cannot upload more than three images"}, status=400)

        record_id = request.data.get('_id')
        if StagingModel.objects.filter(_id=record_id).exists():
            return JsonResponse({"error": "Record already exists"}, status=400)

        # Prepare Serializer Data
        mutable_data = request.data.copy()
        mutable_data['image_location'] = []
        mutable_data['audio_location'] = "null"
        mutable_data['language_id'] = language_obj  

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)

        # Save Data & Upload Files
        with transaction.atomic():
            saved_instance = serializer.save()

            saved_image_paths = []
            for idx, img in enumerate(image_location):
                if img and img != "null":
                    path = save_image_to_azure_v2(img, saved_instance._id, 'news', f'image{idx+1}')
                    if path:
                        saved_image_paths.append(path)
            saved_instance.image_location = saved_image_paths
            saved_instance.save()

            audio_data = request.data.get('audio_location')
            if audio_data and audio_data != "null":
                audio_path = save_audio_to_azure(audio_data, saved_instance._id, "politics", "news")
                saved_instance.audio_location = audio_path
                saved_instance.save()

        # Translate headline, desc, short_desc
        headline = mutable_data.get("headline", "")
        desc = mutable_data.get("desc", "")
        short_desc = mutable_data.get("short_description", "")

        translated_headline = translate_text_sarvam(headline, target_lang_code)
        translated_desc = translate_text_sarvam(desc, target_lang_code)
        translated_short_desc = translate_text_sarvam(short_desc, target_lang_code)

        desc_translation_list = [{
            "language": language_obj.name,
            "headline": translated_headline,
            "desc": translated_desc,
            "short_description": translated_short_desc
        }]

        desc_translations = {
            language_obj.name: {
                "headline": translated_headline,
                "desc": translated_desc,
                "short_description": translated_short_desc
            }
        }

        save_translations_for_other_languages(
            instance=saved_instance,
            headline=headline,
            desc_translations=desc_translations,
            desc_translation_list=desc_translation_list,
            user_id=user.id,
            category=request.data.get("category_id"),
            short_description=short_desc,
            location=request.data.get("location"),
            news_sub_category=request.data.get("news_sub_category_id"),
            image_location=saved_image_paths,
            publish_at=request.data.get("publish_at"),
            status=request.data.get("status"),
            is_published=request.data.get("is_published")
        )

        return Response({
            "message": "success",
            "converted_language": {
                "id": str(language_obj._id),
                "name": language_obj.name,
                "code": target_lang_code
            },
            "result": {
                "original": {
                    "headline": headline,
                    "desc": desc,
                    "short_description": short_desc
                },
                "translation": {
                    "headline": translated_headline,
                    "desc": translated_desc,
                    "short_description": translated_short_desc
                },
                "saved_data": StagingSerializer(saved_instance).data
            }
        })
import base64
from ..models import StagingModel, Category, NewsSubCategory, Register


# ===============================================================
# SAFE BASE64 AUDIO DECODER
# ===============================================================
def clean_and_decode_base64_audio(data: str):
    if not data or data in ["null", "None"]:
        return None
    if "," in data:
        data = data.split(",", 1)[1]
    data = data.strip()
    missing_padding = len(data) % 4
    if missing_padding:
        data += "=" * (4 - missing_padding)
    try:
        return base64.b64decode(data, validate=False)
    except Exception:
        return None


# ===============================================================
# MAIN STAGING EDIT VIEW
# ===============================================================
# -----------------------------
# Helper: clean and decode audio
# -----------------------------


def clean_and_decode_base64_audio(data):
    """
    Accepts:
    - Raw base64 string
    - Base64 with prefix (data:audio/mp3;base64,)
    - Missing padding
    Returns: decoded bytes or None
    """
    if not data or data in ["null", "None"]:
        return None

    if isinstance(data, bytes):
        return data  # already bytes

    if not isinstance(data, str):
        return None  # invalid type

    # Remove prefix
    if "," in data:
        data = data.split(",", 1)[1]

    data = data.strip()

    # Fix missing padding
    missing_padding = len(data) % 4
    if missing_padding:
        data += "=" * (4 - missing_padding)

    try:
        return base64.b64decode(data, validate=True)
    except Exception:
        return None


# -----------------------------
# Main Staging Edit API
# -----------------------------

class Staging_Edit(generics.GenericAPIView):
    serializer_class = StagingSerializer

    def put(self, request, _id):
        instance = get_object_or_404(StagingModel, _id=_id)
        data = request.data.copy()

        # -----------------------------
        # FK parser (safe)
        # -----------------------------


        def parse_fk(field, old_fk, model_class):
            val = data.get(field)

            if val in [None, "", "null", "undefined", "string"]:
                return old_fk  # keep old FK

            if isinstance(val, model_class):
                return val

            try:
                if model_class in [Category, NewsSubCategory, StagingModel]:
                    from uuid import UUID
                    uuid_val = UUID(str(val))
                    return model_class.objects.get(_id=uuid_val)
                elif model_class == Register:
                    # integer id lookup
                    return model_class.objects.get(id=int(val))
            except (ValueError, model_class.DoesNotExist):
                return old_fk




        data["category_id"] = parse_fk("category_id", instance.category_id, Category)
        data["news_sub_category_id"] = parse_fk("news_sub_category_id", instance.news_sub_category_id, NewsSubCategory)
        data["user"] = parse_fk("user", instance.user, Register)

        # -----------------------------
        # Images
        # -----------------------------
        image_list = request.data.get("image_location", [])
        if not isinstance(image_list, list):
            image_list = []

        data["image_location"] = instance.image_location

        # -----------------------------
        # Audio
        # -----------------------------
        audio_input = data.get("audio_location")
        uploaded_audio_url = None

        if audio_input and audio_input not in ["null", "None"]:
            if str(audio_input).startswith("http"):
                uploaded_audio_url = audio_input
            else:
                decoded_audio = clean_and_decode_base64_audio(audio_input)
                if not decoded_audio:
                    # skip or log invalid audio
                    print("Invalid audio input, skipping upload")
                else:
                    uploaded_audio_url = save_audio_to_azure(
                        decoded_audio,
                        instance._id,
                        instance.category_id.name if instance.category_id else "news",
                        "news"
                    )

        # -----------------------------
        # Serializer validation
        # -----------------------------
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            saved = serializer.save()

            # Save new images
            new_images = []
            for idx, img in enumerate(image_list):
                if img and img != "null":
                    uploaded = save_image_to_azure_v2(img, saved._id, "news", f"image{idx+1}")
                    if uploaded:
                        new_images.append(uploaded)

            if new_images:
                saved.image_location = new_images

            # Save audio
            if uploaded_audio_url:
                saved.audio_location = uploaded_audio_url

            saved.save()

            # -----------------------------
            # Translation + TTS
            # -----------------------------
            headline_text = data.get("headline", "")
            desc_text = data.get("desc", "")

            headline_out = []
            desc_out = []
            speech_out = []

            for lang in LanguageEnum:
                t_head = self.translate_text_sarvam(headline_text, lang.value)
                t_desc = self.translate_text_sarvam(desc_text, lang.value)

                headline_out.append({"lang": lang.value, "text": t_head})
                desc_out.append({"lang": lang.value, "text": t_desc})

                audio_url = self.generate_speech_sarvam(desc_text, lang.value)
                speech_out.append({"lang": lang.value, "audio": audio_url})

            # Save translations to DB
            save_translations_for_other_languages(
                instance=saved,
                headline=headline_text,
                desc_translation_list=desc_out,
                user_id=saved.user.id if saved.user else None,
                category_id=saved.category_id.id if saved.category_id else None,
                short_description=saved.short_description,
                location=saved.location,
                news_sub_category_id=saved.news_sub_category_id.id if saved.news_sub_category_id else None,
                image_location=saved.image_location,
                publish_at=saved.publish_at,
                status=saved.status,
                is_published=saved.is_published
            )

        return Response({
            "message": "success",
            "result": {
                "saved_data": StagingSerializer(saved).data,
                "translations": {
                    "headline": headline_out,
                    "desc": desc_out,
                    "speech": speech_out
                }
            }
        })

    # -----------------------------
    # SARVAM Translation
    # -----------------------------
    def translate_text_sarvam(self, text, lang):
        try:
            r = requests.post(
                settings.SARVAM_TRANSLATE_URL,
                headers={
                    "api-subscription-key": settings.SARVAM_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "mode": "formal",
                    "model": "sarvam-translate:v1",
                    "numerals_format": "native",
                    "speaker_gender": "Male",
                    "target_language": lang,
                    "input": text,
                    "enable_preprocessing": False
                }
            )
            if r.status_code == 200:
                return r.json().get("output_text", "")
        except Exception as e:
            print("Translate Error:", e)
        return text

    # -----------------------------
    # SARVAM TTS
    # -----------------------------
    def generate_speech_sarvam(self, text, lang):
        try:
            r = requests.post(
                "https://api.sarvam.ai/tts",
                headers={
                    "api-subscription-key": settings.SARVAM_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "input": text,
                    "model": "sarvam-tts:v1",
                    "target_language": lang,
                    "speaker_gender": "Male",
                }
            )
            if r.status_code == 200:
                return r.json().get("audio_url")
        except:
            pass
        return None








class Staging_Edit(generics.GenericAPIView):
    serializer_class = StagingSerializer
    # permission_classes = []

    # def get_permissions(self):
    #     if self.request.method in ['POST', 'PUT']:
    #         return [IsAuthenticated()]
    #     return super().get_permissions()

    def put(self, request, _id):
        # Retrieve the instance
        instance = get_object_or_404(StagingModel, _id=_id)

        # Retrieve image_location and audio_location from request data
        audio_location = request.data.get('audio_location')
        image_location = request.data.get('image_location', [])
        
        # Validate that image_location is a list
        if not isinstance(image_location, list):
            return JsonResponse({"error": "Image location must be a list"}, status=400)
        if len(image_location) > 3:
            return JsonResponse({"error": "You cannot upload more than three images"}, status=400)

        # Prepare mutable data for serializer
        mutable_data = request.data.copy()
        mutable_data['image_location'] = instance.image_location  # Preserve existing images
        mutable_data['audio_location'] = "null"  # Set audio to null initially

        # Create and validate serializer
        serializer = self.get_serializer(instance, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Process and save new images
        saved_image_paths = []
        for idx, image_data in enumerate(image_location):
            if image_data and image_data != "null":
                saved_location = save_image_to_azure_v2(image_data, serializer.instance._id, 'news', f'image{idx + 1}')
                if saved_location:
                    saved_image_paths.append(saved_location)

        # Update instance with new image locations if any were saved
        if saved_image_paths:
            serializer.instance.image_location = saved_image_paths
            serializer.instance.save()

        # Handle audio upload
        if audio_location and audio_location != "null":
            saved_audio_location = save_audio_to_azure(audio_location, serializer.instance._id, serializer.instance.category_id.name, "news")
            if saved_audio_location:
                serializer.instance.audio_location = saved_audio_location
                serializer.instance.save()

        # Return the response with the original data
        return Response({
            "message": "success",
            "result": {
                "entered_data": request.data,  # Return exactly what was entered
                "saved_data": serializer.data,  # Return saved serializer data
            }
        })





class UpdateNews_Staging(generics.GenericAPIView):
    serializer_class = StagingSerializer

    # def is_email(self, username):
    #     return re.match(r"[^@]+@gmail\.com$", username)

    # def send_email(self, email, subject, message):
    #     from_email = settings.EMAIL_HOST_USER
    #     recipient_list = [email]
    #     try:
    #         send_mail(subject, message, from_email, recipient_list)
    #         print("Email sent successfully")
    #     except Exception as e:
    #         print(f"Failed to send email: {e}")

    # def get_user_details(self, user_id):
    #     try:
    #         user = Register.objects.get(id=user_id)
    #         return {
    #             "user_id": user.id,
    #             "surname": user.surname,
    #             "full_name": user.full_name,
    #             "contact_number": user.contact_number,
    #         }
    #     except Register.DoesNotExist:
    #         return None

    def put(self, request, _id):
        # user_id = request.data.get('user')
        # if not user_id:
        #     return Response({"error": "User ID is required"}, status=400)
        
        # user_details = self.get_user_details(user_id)
        # if not user_details:
        #     return Response({"error": "User not found"}, status=404)

        # Retrieve the instance
        instance = get_object_or_404(StagingModel, _id=_id)
        instance.created_at = timezone.now()

        audio_location = request.data.get('audio_location')  # New audio location

        # Retrieve image_location from request data
        image_location = request.data.get('image_location', [])
        if not isinstance(image_location, list):
            return JsonResponse({"error": "Image location must be a list"}, status=400)
        if len(image_location) > 3:
            return JsonResponse({"error": "You cannot upload more than three images"}, status=400)

        # Make a mutable copy of request.data
        mutable_data = request.data.copy()
        mutable_data['image_location'] = instance.image_location  # Preserve existing image locations
        mutable_data['audio_location'] = "null"  # Set audio initially to null


        # Instantiate the serializer with the mutable copy and instance
        serializer = self.get_serializer(instance, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        saved_image_paths = []
        for idx, image_data in enumerate(image_location):
            if image_data and image_data != "null":
                saved_location = save_image_to_azure_v2(image_data, serializer.instance._id, 'news', f'image{idx + 1}')
                if saved_location:
                    saved_image_paths.append(saved_location)

        # Update the instance with new image locations if any images were saved
        if saved_image_paths:
            serializer.instance.image_location = saved_image_paths
            serializer.instance.save()

        if audio_location and audio_location != "null":  # Handle audio upload
            saved_audio_location = save_audio_to_azure(audio_location, serializer.instance._id, serializer.instance.category_id.name, "news")
            if saved_audio_location:
                serializer.instance.audio_location = saved_audio_location
                serializer.instance.save()

     
        # Send email with the required information
        # subject = '📢 Edit News Added'
        # message = f"""User Details:
        # User ID: {user_details['user_id']}
        # First Name: {user_details['surname']}
        # Last Name: {user_details['full_name']}
        # Contact Number: {user_details['contact_number']}
        # Details: {serializer.data}
        # """
        # recipient_email = 'sathayushtechsolutions@gmail.com'  # replace with your email
        # self.send_email(recipient_email, subject, message)

        return Response({
            "message": "success",
            "result": {
                "entered_data": request.data,  # Return exactly what was entered
                "saved_data": serializer.data,  # Return saved serializer data
            }
        })







# class UpdateNews_Staging(generics.GenericAPIView):
#     serializer_class = StagingSerializer

#     def put(self, request, _id):
#         instance = get_object_or_404(StagingModel, _id=_id)
#         instance.created_at = timezone.now()

#         record_id = request.data.get('_id')
#         if StagingModel.objects.filter(_id=record_id).exists():
#             return JsonResponse({"error": "This record already exists in the staging database."}, status=400)

#         audio_location = request.data.get('audio_location')
#         image_location = request.data.get('image_location', [])

#         if not isinstance(image_location, list):
#             return JsonResponse({"error": "Image location must be a list"}, status=400)

#         # Prepare mutable data
#         mutable_data = request.data.copy()
#         mutable_data['image_location'] = instance.image_location
#         mutable_data['audio_location'] = "null"

#         serializer = self.get_serializer(instance, data=mutable_data, partial=True)
#         serializer.is_valid(raise_exception=True)

#         with transaction.atomic():
#             saved_instance = serializer.save()

#             # Save images
#             saved_image_paths = []
#             for idx, image_data in enumerate(image_location):
#                 if image_data and image_data != "null":
#                     saved_location = save_image_to_azure_v2(
#                         image_data,
#                         saved_instance._id,
#                         'news',
#                         f'image{idx + 1}'
#                     )
#                     if saved_location:
#                         saved_image_paths.append(saved_location)

#             if saved_image_paths:
#                 saved_instance.image_location = saved_image_paths

#             # Save audio (original)
#             saved_audio_location = None
#             if audio_location and audio_location != "null":
#                 saved_audio_location = save_audio_to_azure(
#                     audio_location,
#                     saved_instance._id,
#                     saved_instance.category_id.name,
#                     "news"
#                 )
#             if saved_audio_location:
#                 saved_instance.audio_location = saved_audio_location

#             saved_instance.save()

#             # =============================
#             # SARVAM MULTILINGUAL TRANSLATION
#             # =============================

#             headline = mutable_data.get("headline")
#             desc = mutable_data.get("desc")

#             SARVAM_URL = settings.SARVAM_TRANSLATE_URL
#             API_KEY = settings.SARVAM_API_KEY

#             def translate_text_sarvam(text, target_lang):
#                 payload = {
#                     "mode": "formal",
#                     "model": "sarvam-translate:v1",
#                     "numerals_format": "native",
#                     "speaker_gender": "Male",
#                     "target_language": target_lang,
#                     "input": text,
#                     "enable_preprocessing": False
#                 }
#                 try:
#                     res = requests.post(
#                         SARVAM_URL,
#                         headers={
#                             "api-subscription-key": API_KEY,
#                             "Content-Type": "application/json"
#                         },
#                         json=payload
#                     )
#                     if res.status_code == 200:
#                         return res.json().get("output_text", "")
#                     return None
#                 except Exception as e:
#                     print("Sarvam Translation Error:", str(e))
#                     return None

#             headline_translations = []
#             desc_translations = []

#             for lang in LanguageEnum1:
#                 translated_headline = translate_text_sarvam(headline, lang.value)
#                 translated_desc = translate_text_sarvam(desc, lang.value)

#                 headline_translations.append({
#                     "lang": lang.value,
#                     "text": translated_headline
#                 })

#                 desc_translations.append({
#                     "lang": lang.value,
#                     "text": translated_desc
#                 })

#             # =============================
#             # SARVAM MULTILINGUAL SPEECH (TTS)
#             # =============================

#             def generate_speech_sarvam(text, lang):
#                 tts_url = "https://api.sarvam.ai/tts"
#                 tts_payload = {
#                     "input": text,
#                     "model": "sarvam-tts:v1",
#                     "target_language": lang,
#                     "speaker_gender": "Male",
#                 }
#                 try:
#                     res = requests.post(
#                         tts_url,
#                         headers={
#                             "api-subscription-key": API_KEY,
#                             "Content-Type": "application/json"
#                         },
#                         json=tts_payload
#                     )
#                     if res.status_code == 200:
#                         return res.json().get("audio_url")
#                     return None
#                 except:
#                     return None

#             speech_outputs = []
#             for lang in LanguageEnum1:
#                 audio_url = generate_speech_sarvam(desc, lang.value)
#                 speech_outputs.append({
#                     "lang": lang.value,
#                     "audio": audio_url
#                 })

#             # Save translations
#             save_translations_for_other_languages(
#                 saved_instance,
#                 headline_translations,
#                 desc_translations,
#                 saved_instance.user_id,
#                 saved_instance.category_id,
#                 saved_instance.short_description,
#                 saved_instance.location,
#                 saved_instance.news_sub_category_id,
#                 saved_instance.image_location,
#                 desc_translations,
#                 saved_instance.publish_at,
#                 saved_instance.status,
#                 saved_instance.is_published
#             )

#             saved_instance.save()

#         return Response({
#             "message": "success",
#             "result": {
#                 "entered_data": mutable_data,
#                 "saved_data": StagingSerializer(saved_instance).data,
#                 "translations": {
#                     "headline": headline_translations,
#                     "desc": desc_translations,
#                     "speech": speech_outputs
#                 },
#             }
#         })






from rest_framework.views import APIView
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils.timezone import make_aware,get_current_timezone
from django.utils.timezone import make_aware, is_naive, get_current_timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from pytz import timezone
from django.utils.timezone import make_aware, get_current_timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone


class Staging_GetItemByfield_InputView(APIView):
    serializer_class = StagingSerializer1
    pagination_class = CustomPagination

    def get(self, request, *args, **kwargs):
        queryset = StagingModel.objects.filter(status='SUCCESS',is_published='PUBLISHED').order_by('-created_at')
        # queryset = NewsCategory.objects.filter(status='SUCCESS', publish_at__lte=timezone.now()).order_by('-publish_at')

        category_id = request.query_params.get('category_id')
        news_sub_category_id = request.query_params.get('news_sub_category_id')
        created_at = request.query_params.get('created_at')
        language = request.query_params.get('language')
   


        # Filter by category_id if provided
        if category_id:
            queryset = queryset.filter(
                Q(category_id=category_id) | Q(news_sub_category_id=category_id)
            )

        # Filter by news_sub_category_id if provided
        if news_sub_category_id:
            queryset = queryset.filter(news_sub_category_id=news_sub_category_id)
        if language:
            queryset = queryset.filter(language=language)



        if created_at:
            try:
                if created_at.lower() == 'today':
                    start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
                elif created_at.lower() == 'yesterday':
                    start_date = (timezone.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                elif created_at.lower() in ['1 week ago', '2 weeks ago', '3 weeks ago', 'this month', 'last month',
                                            '1 month ago', '2 months ago', '3 months ago', '4 months ago', '5 months ago']:
                    # Handle specific date ranges
                    start_date, end_date = self.get_date_range(created_at)
                else:
                    # Handle specific date format YYYY-MM-DD
                    start_date = timezone.make_aware(datetime.strptime(created_at, '%Y-%m-%d'), timezone.get_current_timezone())
                    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)

                # Check if start_date is older than 4 months from now
                if start_date < timezone.now() - timedelta(days=120):
                    return Response({
                        'message': 'No data available older than 4 months. All data has been cleared.',
                        'status': 204  # Custom status code indicating no content
                    }, status=status.HTTP_204_NO_CONTENT)

            except ValueError:
                return Response({
                    'message': 'Invalid date format',
                    'status': 400
                }, status=status.HTTP_400_BAD_REQUEST)

            queryset = queryset.filter(created_at__range=(start_date, end_date))

        # Pagination
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = StagingSerializer1(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def get_date_range(self, created_at):
        """ Helper function to get date range based on relative date string """
        if created_at.lower() == 'today':
            start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        elif created_at.lower() == 'yesterday':
            start_date = (timezone.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif created_at.lower() == '1 week ago':
            start_date = (timezone.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        elif created_at.lower() == '2 weeks ago':
            start_date = (timezone.now() - timedelta(days=14)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        elif created_at.lower() == '3 weeks ago':
            start_date = (timezone.now() - timedelta(days=21)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        elif created_at.lower() == 'this month':
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now().replace(day=datetime.now().day, hour=23, minute=59, second=59, microsecond=999999)
        elif created_at.lower() == 'last month':
            last_month_end_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            last_month_start_date = last_month_end_date.replace(day=1)
            start_date = last_month_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = last_month_end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif created_at.lower() == '1 month ago':
            start_date = (timezone.now() - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        elif created_at.lower() == '2 months ago':
            start_date = (timezone.now() - timedelta(days=60)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        elif created_at.lower() == '3 months ago':
            start_date = (timezone.now() - timedelta(days=90)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        elif created_at.lower() == '4 months ago':
            start_date = (timezone.now() - timedelta(days=120)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        elif created_at.lower() == '5 months ago':
            start_date = (timezone.now() - timedelta(days=150)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            raise ValueError("Invalid relative date string")

        return start_date, end_date
 

class StagingNewsViewSet(viewsets.ModelViewSet):
    queryset = StagingModel.objects.all().order_by('-created_at')
    serializer_class = StagingSerializer1
    pagination_class = CustomPagination
    

    def get_serializer_class(self):
        if self.action == 'update':
            return StagingSerializer
        return super().get_serializer_class()
    pagination_class = CustomPagination

    @action(detail=False, methods=['get'])
    def fetch_news(self, request=None):
        urls = request.GET.getlist('url', [
            'https://apnews.com/', 'https://www.cnbc.com/world/?region=world',
            'https://www.news24.com/news24/southafrica/feel_good/', 'https://www.nbcnews.com/world/', 'https://www.abc.net.au/news/justin',
            'https://www.bbc.com/news', 'https://edition.cnn.com/world', 'https://www.aljazeera.com/asia/',
            'https://asia.nikkei.com/', 'https://www.euronews.com/just-in', 'https://www.ft.com/world',
            'https://timesofindia.indiatimes.com/','https://www.scmp.com/live?module=oneline_menu_section_int&pgtype=homepage',
            'https://www.nytimes.com/section/world','https://allafrica.com/','https://www.premiumtimesng.com/',
            'https://www.nzherald.co.nz/latest-news/','https://news.sky.com/','https://www.sbs.com.au/news'
        ]) if request else [
            'https://apnews.com/', 'https://www.cnbc.com/world/?region=world',
            'https://www.news24.com/news24/southafrica/feel_good/', 'https://www.nbcnews.com/world/', 'https://www.abc.net.au/news/justin',
            'https://www.bbc.com/news', 'https://edition.cnn.com/world', 'https://www.aljazeera.com/asia/',
            'https://asia.nikkei.com/', 'https://www.euronews.com/just-in', 'https://www.ft.com/world',
            'https://timesofindia.indiatimes.com/','https://www.scmp.com/live?module=oneline_menu_section_int&pgtype=homepage',
            'https://www.nytimes.com/section/world','https://allafrica.com/','https://www.premiumtimesng.com/',
            'https://www.nzherald.co.nz/latest-news/','https://news.sky.com/','https://www.sbs.com.au/news'
        ]

        all_news_data = []

        for url in urls:
            fetch_method = getattr(self, f'fetch_{self.get_source_name(url)}', None)
            if fetch_method:
                news_data = fetch_method(url)
                if news_data is not None:
                    print(f"{self.get_source_name(url).upper()} News Data:")
                    all_news_data.extend(news_data)
                else:
                    print(f"No data returned from {self.get_source_name(url).upper()}")

        response_data = self.process_news_data(all_news_data)
        # Apply pagination
        page = self.paginate_queryset(response_data)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(response_data, status=status.HTTP_200_OK)

    def get_source_name(self, url):
        sources = {
            'apnews.com': 'apnews',
            'cnbc.com': 'cbncnews',
            'news24.com': 'news24',
            'nbcnews.com': 'nbcnews',
            'abc.net.au': 'abcnews',
            'bbc.com': 'bbcnews',
            'cnn.com': 'cnnnews',
            'aljazeera.com': 'aljazeera',
            'asia.nikkei.com': 'asianikkei',
            'euronews.com': 'euronews',
            'ft.com': 'ftnews',
            'timesofindia.indiatimes.com':'timesofindianews',
            'scmp.com':'scmpnews',
            'nytimes.com':'nytimesnews',
            'allafrica.com':'allafricanews',
            'premiumtimesng.com': 'premiumtimesng',
            'nzherald.co.nz':'nzheraldnews',
            'news.sky.com' : 'newssky',
            'sbs.com.' : 'sbsnews',
        }
        for key, value in sources.items():
            if key in url:
                return value
        return 'unknown'

    def process_news_data(self, all_news_data):
        response_data = []
        for article in all_news_data:
            headline = article.get('Headline')
            desc = article.get('Desc')

            # Check if at least one of Headline or Description is present
            if headline or desc:
                unique_id = str(uuid.uuid4())
                obj, created = StagingModel.objects.update_or_create(
                    _id=unique_id,
                    defaults={
                        'headline': headline,
                        'desc': desc,
                        # 'url': article.get('Url'),
                        # 'image_location': article.get('Image_location')
                    }
                )
                response_data.append({
                    '_id': obj._id,
                    'Headline': obj.headline,
                    'Desc': obj.desc,
                    # 'Image_location': obj.image_location,
                    # 'Url': obj.url,
                })
        return response_data
    

    def fetch_apnews(self, url):
        return self.fetch_news_from_site(url, 'div', 'PageList-items', 'h3', 'PagePromo-title', 'div', 'PagePromo', 'img', 'Image')

    def fetch_cbncnews(self, url):
        return self.fetch_news_from_site(url, 'div', 'Card-standardBreakerCard', 'a', 'Card-title', 'div', 'PagePromo', 'img', 'Card-mediaContainerInner')

    def fetch_news24(self, url):
        return self.fetch_news_from_site(url,'div', 'article-item--container','div', 'article-item__title','div', 'article-item__synopsis','img', 'article-item__image')

    def fetch_nbcnews(self, url):
        return self.fetch_news_from_site(url, 'div', 'wide-tease-item__wrapper','h2', 'wide-tease-item__headline','div', 'wide-tease-item__description','div a picture img', 'wide-tease-item__image')
    
    def fetch_abcnews(self, url):
        return self.fetch_news_from_site(url, 'div', 'CardList_gridItem__aujmN', 'h3', 'CardHeading_cardHeading__FpsU_', 'div', 'GenericCard_synopsis__mgnzs', 'img', 'Image_image__5tFYM')

    def fetch_bbcnews(self, url):
        return self.fetch_news_from_site(url, 'div', 'sc-35aa3a40-2 cVXNac', 'h2', 'sc-4fedabc7-3 zTZri', 'p', 'sc-b8778340-4 kYtujW', 'img', 'sc-814e9212-0 hIXOPW')

    def fetch_cnnnews(self, url):
        return self.fetch_news_from_site(url, 'div', 'container__field-links container_lead-plus-headlines__field-links', 'span', 'container__headline-text', 'div', 'PagePromo', 'img', 'image__dam-img')

    def fetch_aljazeera(self, url):
        return self.fetch_news_from_site(url, 'article', 'gc u-clickable-card gc--type-post gc--list gc--with-image', 'h3', 'gc__title', 'div', 'gc__excerpt', 'img', 'article-card__image')
 

    def fetch_asianikkei(self, url):
        return self.fetch_news_from_site(url, 'div', 'landing-page__block block_collection', 'a', 'article-block__primary-tag', 'span', 'ezstring-field', 'img', 'img-fluid')    
    
    def fetch_euronews(self, url):
        return self.fetch_news_from_site(url, 'li', 'js-timeline-item', 'h3', 'm-object__title', 'div', 'm-object__description', 'img', 'm-img')
 
    def fetch_ftnews(self, url):
        return self.fetch_news_from_site(url, 'li','o-teaser-collection__item','div','o-teaser__heading','p','o-teaser__standfirst','img','o-teaser__image')

    def fetch_timesofindianews(self, url):
        return self.fetch_news_from_site(url, 'div', 'col_l_6', 'figcaption', '', 'h2', 'sortDec', 'img', 'thumb')
    
    def fetch_scmpnews(self, url):
        return self.fetch_news_from_site(url,'div', 'e1ofzbgq6 css-1wydqy6 e10emkcr6','span', 'css-0 e298i0d2','p', 'css-onn2v5 e1nmpk500','img', 'css-uxj1ib e445x7d0' )
    
    def fetch_allafricanews(self, url):
        return self.fetch_news_from_site(url,'div', 'row no-gutter items',  'span', 'headline','p', 'teaser-image-large_paragraph text-block','img', 'img-responsive')
    
    def fetch_nytimesnews(self, url):
        return self.fetch_news_from_site(url,'li', 'css-18yolpw','h3', 'css-1j88qqx e15t083i0','p', 'css-1pga48a e15t083i1','img', 'css-rq4mmj')
    
    def fetch_premiumtimesng(self, url):
        return self.fetch_news_from_site(url, 'div', 'jeg_block_container', 'h3', 'jeg_post_title', '', '', 'img', 'attachment-jnews-120x86 size-jnews-120x86 wp-post-image lazyautosizes lazyloaded')
   
    def fetch_nzheraldnews(self, url):
        return self.fetch_news_from_site(url, 'div', 'section-chain__wrapper', 'h3', 'story-card__heading', 'p','story-card__deck','a', 'story-card__image-link')
    def fetch_newssky(self, url):
        return self.fetch_news_from_site(url, 'div', 'grid-areas', 'div', 'ui-story-headline', '', '', 'img', 'ui-story-image', )
    
    def fetch_sbsnews(self, url):
        return self.fetch_news_from_site(url, 'div', 'MuiBox-root css-0', 'h3', 'MuiTypography-root MuiTypography-subtitle1 e1o065bq2 css-11beddl', 'p', 'MuiTypography-root MuiTypography-body1 css-1du8xgl', 'img', 'css-0')

    def fetch_news_from_site(self, url, container_tag, container_class, headline_tag, headline_class, description_tag, description_class, image_tag, image_class):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                return None
    
            soup = BeautifulSoup(response.content, 'html.parser')
            news_items = soup.find_all(container_tag, class_=container_class)
            print(f"Found news items: {len(news_items)}")
    
            news_data = []
            for item in news_items:
                # Extract headline
                headline_element = item.find(headline_tag, class_=headline_class)
                headline = headline_element.get_text(strip=True) if headline_element else None
                
                # Extract description
                desc_element = item.find(description_tag, class_=description_class)
                desc = desc_element.get_text(strip=True) if desc_element else None
    
                # Extract images
                # image_tags = item.find_all(image_tag)  # Find all image tags
                # image_paths = []
                # for image in image_tags:
                #     image_url = image.get('src')
                #       # Get the src attribute
                #     if image_url:
                #         # Print image URL for debugging
                #         print(f"Found image URL: {image_url}")
                #         # Generate unique image path (assuming save_image_from_url is implemented)
                #         image_path = save_image_from_url(image_url, str(uuid.uuid4()), 'news', 'news')
                #         if image_path:
                #             image_paths.append(image_path)
                # image_paths = image_paths if image_paths else None
                    

                # Extract article URL
                anchor_tag = item.find('a')
                full_url = urljoin(url, anchor_tag['href']) if anchor_tag and 'href' in anchor_tag.attrs else url
    
                news_data.append({
                    'Headline': headline,
                    'Desc': desc,
                    # 'Image_location': image_paths,  # Store images as a list
                    # 'Url': full_url,
                })
    
            return news_data
        except requests.RequestException as e:
            print(f"Failed to fetch news from {url}: {str(e)}")
            return None
    






 