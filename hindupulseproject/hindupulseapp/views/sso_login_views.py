# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
# # from ..models import Register

# # class SSOLoginView(APIView):

# #     def get(self, request):
# #         token = request.GET.get('token')

# #         if not token:
# #             return Response({"error": "Token missing"}, status=400)

# #         try:
# #             access = AccessToken(token)

# #             # ✔ Gramadevata nunchi vachinda check
# #             if access.get('source') != 'gramadevata':
# #                 return Response({"error": "Invalid source"}, status=403)

# #             user_id = access.get('user_id')
# #             username = access.get('username')
# #             email = access.get('email')
# #             contact = access.get('contact_number')

# #             user = Register.objects.filter(id=user_id).first()

# #             if not user:
# #                 user = Register.objects.create(
# #                     id=user_id,
# #                     username=username,
# #                     email=email,
# #                     contact_number=contact,
# #                     status='ACTIVE'
# #                 )

# #             refresh = RefreshToken.for_user(user)

# #             return Response({
# #                 "refresh": str(refresh),
# #                 "access": str(refresh.access_token),
# #                 "message": "SSO Login Success"
# #             })

# #         except Exception:
# #             return Response({"error": "Invalid or expired token"}, status=401)



















# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
# from ..models import Register

# class SSOLoginView(APIView):

#     def get(self, request):
#         token = request.GET.get('token')

#         if not token:
#             return Response({"error": "Token missing"}, status=400)

#         try:
#             # 🔐 Decode token (same secret)
#             access = AccessToken(token)

#             user_id = access.get('user_id')
#             username = access.get('username')
#             email = access.get('email')
#             contact = access.get('contact_number')

#             if not user_id:
#                 return Response({"error": "Invalid token"}, status=401)

#             # 🔎 Check user exists or not
#             user = Register.objects.filter(id=user_id).first()

#             if not user:
#                 # 🆕 Auto create user
#                 user = Register.objects.create(
#                     id=user_id,
#                     username=username,
#                     email=email,
#                     contact_number=contact,
#                     status='ACTIVE'
#                 )

#             # 🔁 Generate LOCAL JWT
#             refresh = RefreshToken.for_user(user)
#             local_access = refresh.access_token

#             return Response({
#                 "refresh": str(refresh),
#                 "access": str(local_access),
#                 "message": "SSO Login Success"
#             })

#         except Exception as e:
#             return Response({"error": "Invalid or expired token"}, status=401)









from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model

User = get_user_model()

class SSOLoginView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        """
        Authorization: Bearer <Gramadevata Access Token>
        """
        user = request.user

        if not user or not user.is_authenticated:
            return Response(
                {"error": "Invalid Gramadevata token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Auto-create user if not exists
        local_user, created = User.objects.get_or_create(
            username=user.username,
            defaults={
                "email": user.email,
                "contact_number": user.contact_number,
                "status": "ACTIVE"
            }
        )

        return Response({
            "message": "SSO login successful",
            "user_id": local_user.id,
            "username": local_user.username,
            "full_name": local_user.full_name,
            "is_member": local_user.is_member
        }, status=status.HTTP_200_OK)
