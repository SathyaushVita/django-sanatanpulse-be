from django.conf import settings
import base64
import os
import re
import string
import requests
from django.core.mail import send_mail
import random
import uuid
from azure.storage.blob import BlobServiceClient



from azure.storage.blob import BlobServiceClient, ContentSettings

def save_pdf_to_azure(pdf_file, _id, name, entity_type):
    # Handle base64 or raw PDF file
    if isinstance(pdf_file, str):
        try:
            decoded_pdf = base64.b64decode(pdf_file)
        except base64.binascii.Error:
            raise ValueError("Invalid base64 PDF data.")
    elif hasattr(pdf_file, 'read'):  # Assuming file-like object (e.g. uploaded file)
        decoded_pdf = pdf_file.read()
    else:
        raise ValueError("Unsupported PDF format. Provide base64 string or file object.")
    
    # Create folder name based on _id and entity_type
    folder_name = str(_id)
    
    # Generate unique PDF name
    pdf_name = f"{name}_{uuid.uuid4().hex[:8]}.pdf"
    
    # Azure Blob Storage settings
    container_name = 'sathayush'
    folder_path = f"{entity_type}/{folder_name}/"  # Example: 'article/1234/'
    blob_name = f"{folder_path}{pdf_name}"  # Full path for the PDF in Azure Blob Storage
    
    # Initialize BlobServiceClient using connection string from settings
    try:
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Set content type and content disposition to open in the browser
        content_settings = ContentSettings(content_type='application/pdf', content_disposition='inline')
        
        # Upload the PDF to Azure Blob Storage with content settings
        blob_client.upload_blob(decoded_pdf, blob_type="BlockBlob", overwrite=True, content_settings=content_settings)
        
        # Get the full URL of the uploaded PDF
        blob_url = blob_client.url
        
        return blob_name
    
    except Exception as e:
        # Log the error and re-raise for further handling
        raise RuntimeError(f"Error uploading PDF to Azure: {str(e)}")
    





def image_path_to_binary(filename):
    img_url = settings.FILE_URL
    print(img_url,"img_url")
    img_path = os.path.join(img_url, filename)  # Assuming settings.MEDIA_ROOT contains the directory where your images are stored
    # print(img_path, "---------------------------------")
    # if os.path.exists(img_path):
    #     with open(img_path, "rb") as image_file:
    #         image_data = image_file.read()
    #         base64_encoded_image = base64.b64encode(image_data)
    return img_path
    # else:
    #     # print("File not found:", img_path)
    #     return None
   






def save_image_from_url(image_url, _id, name, entity_type):
    try:
        # Make a request to fetch the image
        response = requests.get(image_url)
        if response.status_code == 200:
            image_data = response.content
            
            # Generate a unique image name
            unique_name = f"{name}_{uuid.uuid4().hex[:8]}.jpg"
            
            # Create the relative folder path (without E://)
            folder_name = str(_id)
            relative_folder_path = os.path.join(entity_type, folder_name)  # This will be 'news/uuid'
            
            # Create the full path to store the image using MEDIA_ROOT or hardcoded base path
            base_path = "E://news"  # You can also use settings.MEDIA_ROOT if configured in Django
            full_folder_path = os.path.join(base_path, relative_folder_path)  # Full path: 'E://news/news/uuid'
            
            # Create the directory if it does not exist
            if not os.path.exists(full_folder_path):
                os.makedirs(full_folder_path)
            
            # Define the full image path
            full_image_path = os.path.join(full_folder_path, unique_name)  # Full path to save the image
            
            # Save the image to the defined path
            with open(full_image_path, "wb") as image_file:
                image_file.write(image_data)
            
            # Return the relative path like 'news/uuid/filename.jpg'
            relative_image_path = os.path.join(entity_type, folder_name, unique_name)  # 'news/uuid/filename.jpg'
            return relative_image_path.replace("\\", "/")  # Ensure path is in Unix format (slashes)
        
        else:
            print(f"Failed to download image from {image_url}. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error saving image from {image_url}: {str(e)}")
        return None








def save_image_to_azure(image_file, _id, name, entity_type):
    # Handle base64 or raw image file
    if isinstance(image_file, str):
        try:
            decoded_image = base64.b64decode(image_file)
        except base64.binascii.Error:
            raise ValueError("Invalid base64 image data.")
    elif hasattr(image_file, 'read'):  # Assuming file-like object (e.g. uploaded file)
        decoded_image = image_file.read()
    else:
        raise ValueError("Unsupported image format. Provide base64 string or file object.")
    
    # Create folder name based on _id and entity_type
    folder_name = str(_id)
    
    # Generate unique image name
    image_name = f"{name}_{uuid.uuid4().hex[:8]}.jpg"
    
    # Azure Blob Storage settings
    container_name = 'sathayush'
    folder_path = f"{entity_type}/{folder_name}/"  # Example: 'temple/1234/'
    blob_name = f"{folder_path}{image_name}"  # Full path for the image in Azure Blob Storage
    
    # Initialize BlobServiceClient using connection string from settings
    try:
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Upload the image to Azure Blob Storage
        blob_client.upload_blob(decoded_image, blob_type="BlockBlob", overwrite=True)
        
        # Get the full URL of the uploaded image
        blob_url = blob_client.url
        
        return blob_name
    
    except Exception as e:
        # Log the error and re-raise for further handling
        raise RuntimeError(f"Error uploading image to Azure: {str(e)}")

def generate_otp(length = 4):
    characters = string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp



def save_image_to_azure_v2(image_data, _id, entity_type, name):
    # Decode base64 image
    decoded_image = base64.b64decode(image_data)
    
    # Generate unique folder name and image name
    folder_name = str(_id)
    image_name = f"{name}_{uuid.uuid4().hex[:8]}.jpg"
    
    # Azure Blob Storage settings
    container_name = 'sathayush'
    folder_path = f"{entity_type}/{folder_name}/"  # Example: 'temple/1234/'
    blob_name = f"{folder_path}{image_name}"  # Full path for the image in Azure Blob Storage
    
    # Initialize BlobServiceClient using connection string from settings
    blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    
    # Upload the image to Azure Blob Storage
    blob_client.upload_blob(decoded_image, blob_type="BlockBlob", overwrite=True)
    
    # Get the full URL of the uploaded image
    blob_url = blob_client.url
    
    return blob_name



def image_path_to_binary1(filenames):
    if not isinstance(filenames, list):
        filenames = [filenames]
        print("lkjmnhbgvfcfd",filenames)
    
    base64_images = []
    img_url = settings.FILE_URL

    print("hhhhhhhhhhhhhhhhh",img_url)

    if isinstance(img_url, list):
        img_url = img_url[0]

    for filename in filenames:
        print(";oilujmhf",filename)
        if isinstance(img_url, str):
            img_path = os.path.join(img_url+ filename)
            print("wwwwwwwwwww",img_path)
            if os.path.exists(img_path):
                with open(img_path, "rb") as image_file:
                    image_data = image_file.read()
                    base64_encoded_image = base64.b64encode(image_data).decode('utf-8')
                    base64_images.append(base64_encoded_image)
            else:
                base64_images.append(None)
        else:
            raise TypeError("settings.FILE_URL should be a string or a list of strings")
    
    return img_path



# def save_audio_to_azure(audio_file, _id, name, entity_type):
#     # Handle base64 or raw audio file
#     if isinstance(audio_file, str):
#         try:
#             decoded_audio = base64.b64decode(audio_file)
#         except base64.binascii.Error:
#             raise ValueError("Invalid base64 audio data.")
#     elif hasattr(audio_file, 'read'):  # Assuming file-like object (e.g., uploaded file)
#         decoded_audio = audio_file.read()
#     else:
#         raise ValueError("Unsupported audio format. Provide base64 string or file object.")
#     # Create folder name based on _id and entity_type
#     folder_name = str(_id)
#     # Generate unique audio name
#     audio_name = f"{name}_{uuid.uuid4().hex[:8]}.mp3"
#     # Azure Blob Storage settings
#     container_name = 'sathayush'
#     folder_path = f"{entity_type}/{folder_name}/"  # Example: 'temple/1234/'
#     blob_name = f"{folder_path}{audio_name}"  # Full path for the audio in Azure Blob Storage
#     # Initialize BlobServiceClient using connection string from settings
#     try:
#         blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
#         blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
#         # Upload the audio to Azure Blob Storage
#         blob_client.upload_blob(decoded_audio, blob_type="BlockBlob", overwrite=True)
#         # Get the full URL of the uploaded audio
#         blob_url = blob_client.url
#         return blob_name
#     except Exception as e:
#         # Log the error and re-raise for further handling
#         raise RuntimeError(f"Error uploading audio to Azure: {str(e)}")




from azure.storage.blob import BlobServiceClient, ContentSettings
import base64
import uuid
from django.conf import settings

# def save_audio_to_azure(audio_file, _id, name, entity_type):
#     # Handle base64 or raw audio file
#     if isinstance(audio_file, str):
#         try:
#             decoded_audio = base64.b64decode(audio_file)
#         except base64.binascii.Error:
#             raise ValueError("Invalid base64 audio data.")
#     elif hasattr(audio_file, 'read'):  # Assuming file-like object (e.g., uploaded file)
#         decoded_audio = audio_file.read()
#     else:
#         raise ValueError("Unsupported audio format. Provide base64 string or file object.")

#     # Create folder name based on _id and entity_type
#     folder_name = str(_id)

#     # Generate unique audio name
#     audio_name = f"{name}_{uuid.uuid4().hex[:8]}.mp3"

#     # Azure Blob Storage settings
#     container_name = 'sathayush'
#     folder_path = f"{entity_type}/{folder_name}/"  # Example: 'news/1234/'
#     blob_name = f"{folder_path}{audio_name}"  # Full path for the audio in Azure Blob Storage

#     # Initialize BlobServiceClient using connection string from settings
#     try:
#         blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
#         blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

#         # Upload the audio to Azure Blob Storage with proper Content-Type
#         blob_client.upload_blob(
#             decoded_audio, 
#             blob_type="BlockBlob", 
#             overwrite=True, 
#             content_settings=ContentSettings(content_type="audio/mpeg")  # Set Content-Type
#         )

#         # Get the full URL of the uploaded audio
#         blob_url = blob_client.url
#         return blob_name
#     except Exception as e:
#         # Log the error and re-raise for further handling
#         raise RuntimeError(f"Error uploading audio to Azure: {str(e)}")

def save_audio_to_azure(audio_file, _id, name, entity_type): 
    # Handle base64 or raw audio file
    if isinstance(audio_file, str):
        try:
            decoded_audio = base64.b64decode(audio_file)
        except base64.binascii.Error:
            raise ValueError("Invalid base64 audio data.")
    elif hasattr(audio_file, 'read'):
        decoded_audio = audio_file.read()
    else:
        raise ValueError("Unsupported audio format. Provide base64 string or file object.")

    folder_name = str(_id)

    audio_name = f"{name}_{uuid.uuid4().hex[:8]}.mp3"

    container_name = 'sathayush'
    folder_path = f"{entity_type}/{folder_name}/"
    blob_name = f"{folder_path}{audio_name}"

    try:
        blob_service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        blob_client = blob_service_client.get_blob_client(
            container=container_name, 
            blob=blob_name
        )

        blob_client.upload_blob(
            decoded_audio,
            blob_type="BlockBlob",
            overwrite=True,
            content_settings=ContentSettings(content_type="audio/mpeg")
        )

        return blob_name  # <-- Correct
    except Exception as e:
        raise RuntimeError(f"Error uploading audio to Azure: {str(e)}")








# import PyPDF2


# import re
# import fitz
# def extract_pdf_content(pdf_path):
#     # Open the PDF and extract content
#     with open(pdf_path, "rb") as pdf_file:
#         pdf_reader = PyPDF2.PdfReader(pdf_file)
#         content = {}

#         # Iterate through each page
#         text_counter = 1  # Counter for numbering texts
#         image_counter = 1
#         for page in pdf_reader.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 # Remove unwanted newlines between words using regex
#                 cleaned_text = re.sub(r'\s*\n\s*', ' ', page_text.strip())

#                 # Split cleaned text into paragraphs by double newline or tabs
#                 paragraphs = re.split(r'\n\n|\t', cleaned_text)
#                 for para in paragraphs:
#                     para_cleaned = para.strip()
#                     if para_cleaned:  # Avoid empty paragraphs
#                         content[f"text{text_counter}"] = para_cleaned
#                         text_counter += 1

#         pdf_document = fitz.open(pdf_path)
#         for page_number in range(len(pdf_document)):
#             page = pdf_document.load_page(page_number)
#             images = page.get_images(full=True)
            
#             for img in images:
#                 xref = img[0]
#                 base_image = pdf_document.extract_image(xref)
#                 if base_image:
#                     image_bytes = base_image["image"]
#                     image_base64 = base64.b64encode(image_bytes).decode("utf-8")
#                     content[f"image{image_counter}"] = image_base64
#                     image_counter += 1
        
#         pdf_document.close()
        
#         return content


# def download_pdf(url, local_path):
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             with open(local_path, 'wb') as file:
#                 file.write(response.content)
#             return local_path
#     except Exception as e:
#         print(f"Error downloading PDF: {e}")
#     return None



def save_video_to_azure(video_data, _id, name, entity_type):
    try:
        # Decode base64 video
        decoded_video = base64.b64decode(video_data)

        # Generate unique video name
        video_name = f"{name}_{uuid.uuid4().hex[:8]}.mp4"

        # Azure settings
        container_name = "sathayush"
        folder_path = f"{entity_type}/{_id}/"  # Example: movie/1234/
        blob_name = f"{folder_path}{video_name}"

        # Upload to Azure
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(decoded_video, blob_type="BlockBlob", overwrite=True)

        # Return FULL AZURE URL (same as poster)
        return f"https://sathayushstorage.blob.core.windows.net/{container_name}/{blob_name}"

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None




def video_path_to_binary(filename):
    if not filename:  # Check if filename is None or empty
        return None

    video_url = settings.FILE_URL

    def get_base64_encoded_video(video_path):
        if os.path.exists(video_path):
            with open(video_path, "rb") as video_file:
                video_data = video_file.read()
                base64_encoded_video = base64.b64encode(video_data)
                return base64_encoded_video.decode('utf-8')  # Return the base64 string
        else:
            return None


# def save_translations_for_other_languages(instance, headline, desc_translations, user_id,
#                                           category, short_description, location, news_sub_category,
#                                           image_location, desc_translation_list, publish_at, status, is_published):
#     """
#     Stub function to save translations.
#     You can implement this to save in a TranslationModel or JSONField.
#     """
#     print(f"Saving translations for record {instance._id}")
#     print("Translations:", desc_translations)
#     # For now, do nothing
#     return True


# import requests

# # ---------- SARVAM API Config ----------
# SARVAM_TRANSLATE_URL = "https://api.sarvam.ai/translate"
# SARVAM_API_KEY = "sk_9eddidq9_YOg5lIfG9v9ElQI9yx2O7w4g"

# def translate_text_sarvam(text, target_language_code):
#     """
#     Translate text using SARVAM API.
#     target_language_code: 'te' for Telugu, 'hi' for Hindi, etc.
#     """
#     if not text:
#         return text

#     payload = {
#         "input": text,
#         "source_language_code": "en-IN",           # Original language is English
#         "target_language_code": f"{target_language_code}-IN",
#         "mode": "formal",
#         "model": "sarvam-translate:v1",
#         "numerals_format": "native",
#         "speaker_gender": "Male",
#         "enable_preprocessing": False
#     }

#     headers = {
#         "api-subscription-key": SARVAM_API_KEY,
#         "Content-Type": "application/json"
#     }

#     try:
#         response = requests.post(SARVAM_TRANSLATE_URL, json=payload, headers=headers)
#         if response.status_code == 200:
#             result = response.json()
#             print("Full API Response:", result)
#             return result.get("translated_text", text)
#         else:
#             print("SARVAM API Error:", response.status_code, response.text)
#             return text
#     except Exception as e:
#         print("Exception:", e)
#         return text


# # ---------- TEST ----------
# if __name__ == "__main__":
#     text_to_translate = "How are you?"
#     target_lang = "te"  # Telugu. Use 'hi' for Hindi, 'ta' for Tamil, etc.

#     translated_text = translate_text_sarvam(text_to_translate, target_lang)
#     print("Original Text:", text_to_translate)
#     print("Translated Text:", translated_text)


# Fallback mapping if sarvam_code not present in Language model
# SARVAM_TRANSLATE_URL = "https://api.sarvam.ai/translate"
# SARVAM_API_KEY = "sk_qx6p6792_SOvGOC8x2UWqVJifw8HiKxpu"
# SARVAM_TTS_URL = "https://api.sarvam.ai/tts"

# def translate_text_sarvam(text, target_language_code):
#     if not text:
#         return text

#     sarvam_target = f"{target_language_code}-IN" if target_language_code != "en" else "en-IN"

#     payload = {
#         "input": text,
#         "source_language_code": "en-IN",
#         "target_language_code": sarvam_target,
#         "mode": "formal",
#         "model": "sarvam-translate:v1",
#         "numerals_format": "native",
#         "speaker_gender": "Male",
#         "enable_preprocessing": True
#     }

#     headers = {
#         "api-subscription-key": SARVAM_API_KEY,
#         "Content-Type": "application/json"
#     }

#     try:
#         response = requests.post(SARVAM_TRANSLATE_URL, json=payload, headers=headers)
#         print("SARVAM Response:", response.text)
#         if response.status_code == 200:
#             data = response.json()
#             if "translated_text" in data:
#                 return data["translated_text"]
#             if "output" in data and len(data["output"]) > 0:
#                 return data["output"][0].get("translated_text", text)
#     except Exception as e:
#         print("Translation Error:", e)

#     return text
# def translate_text_sarvam(text, target_language_code):
#     if not text:
#         return text

#     sarvam_target = f"{target_language_code}-IN" if target_language_code != "en" else "en-IN"

#     payload = {
#         "input": text,
#         "source_language_code": "auto",          # auto-detect
#         "target_language_code": sarvam_target,
#         "model": "sarvam-translate:v1",          # ✅ Correct model
#         "mode": "formal"
#     }

#     headers = {
#         "API-Subscription-Key": SARVAM_API_KEY,
#         "Content-Type": "application/json"
#     }

#     try:
#         r = requests.post(SARVAM_TRANSLATE_URL, json=payload, headers=headers)
#         print("TRANSLATE RAW:", r.text)

#         if r.status_code == 200:
#             data = r.json()
#             # Sarvam returns output as list of dicts
#             if "output" in data and len(data["output"]) > 0:
#                 return data["output"][0].get("translated_text", text)
#             if "translated_text" in data:
#                 return data["translated_text"]
#     except Exception as e:
#         print("TRANSLATE EXCEPTION:", e)

#     return text




# def generate_speech_sarvam(text, target_language_code):
#     if not text:
#         return None

#     sarvam_lang = f"{target_language_code}-IN" if target_language_code != "en" else "en-IN"

#     payload = {
#         "model": "sarvam-tts-v1",                # ✅ Correct TTS model
#         "input": [
#             {
#                 "text": text,
#                 "language_code": sarvam_lang,
#                 "speaker": "male"               # male or female
#             }
#         ]
#     }

#     headers = {
#         "API-Subscription-Key": SARVAM_API_KEY,
#         "Content-Type": "application/json"
#     }

#     try:
#         r = requests.post(SARVAM_TTS_URL, json=payload, headers=headers)
#         print("TTS RAW:", r.text)

#         if r.status_code == 200:
#             data = r.json()
#             if "output" in data and len(data["output"]) > 0:
#                 return data["output"][0].get("audio_url")
#             if "audio_url" in data:
#                 return data["audio_url"]
#     except Exception as e:
#         print("TTS EXCEPTION:", e)

#     return None

import requests

SARVAM_TRANSLATE_URL = "https://api.sarvam.ai/translate"
SARVAM_API_KEY = "sk_9e0skwia_zrpuG5KvmjicCUAyxqjwpuA4"
SARVAM_TTS_URL = "https://api.sarvam.ai/tts"


def translate_text_sarvam(text, target_language_code):
    if not text:
        return text

    sarvam_target = f"{target_language_code}-IN" if target_language_code != "en" else "en-IN"

    payload = {
        "input": text,
        "source_language_code": "en-IN",
        "target_language_code": sarvam_target,
        "mode": "formal",
        "model": "sarvam-translate:v1",
        "numerals_format": "native",
        "speaker_gender": "Male",
        "enable_preprocessing": True
    }

    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(SARVAM_TRANSLATE_URL, json=payload, headers=headers)
        data = response.json()

        # Sarvam returns translated_text directly OR inside output list
        if "translated_text" in data:
            return data["translated_text"]
        elif "output" in data and len(data["output"]) > 0:
            return data["output"][0].get("translated_text", text)

    except Exception as e:
        print("Translation Error:", e)

    return text  # fallback


def generate_speech_sarvam(text, target_language_code):
    if not text:
        return None

    sarvam_lang = f"{target_language_code}-IN" if target_language_code != "en" else "en-IN"

    payload = {
        "model": "sarvam-tts-v1",
        "input": [
            {
                "text": text,
                "language_code": sarvam_lang,
                "speaker": "male"
            }
        ]
    }

    headers = {
        "API-Subscription-Key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(SARVAM_TTS_URL, json=payload, headers=headers)
        data = r.json()

        # Sarvam may return audio URL inside output array
        if "output" in data and len(data["output"]) > 0:
            return data["output"][0].get("audio_url")

        # fallback
        if "audio_url" in data:
            return data["audio_url"]

    except Exception as e:
        print("TTS EXCEPTION:", e)

    return None
def translate_long_text(self, text, target_lang):
    """Translate long text by splitting into smaller chunks to avoid API limits"""
    max_len = 1000
    translated = ""
    for i in range(0, len(text), max_len):
        chunk = text[i:i+max_len]
        translated_chunk = translate_text_sarvam(chunk, target_lang)
        translated += translated_chunk or chunk
    return translated


def save_translations_for_other_languages(
    instance, headline, desc_translations, desc_translation_list,
    user_id, category, short_description, location, news_sub_category,
    image_location, publish_at, status, is_published
):
    print(f"Saving translations for record {instance._id}")
    print("Translations:", desc_translations)
    return True
