# from rest_framework_simplejwt.tokens import RefreshToken
# class MyRefreshToken(RefreshToken):
#     @classmethod
#     def for_user(cls, user):
#         token = super().for_user(user)
#         token['user_id'] = str(user._id)  # Ensure you're using the correct field from your model
#         return token