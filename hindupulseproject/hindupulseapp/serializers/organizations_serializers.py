from rest_framework import serializers
from ..models import *
from ..utils import image_path_to_binary

class OrganizationsSerializer(serializers.ModelSerializer):
    organization_link = serializers.ListField(child=serializers.CharField(), required=False)
    class Meta:
        model = Organizations
        fields = '__all__'
    
class OrganizationsSerializer1(serializers.ModelSerializer):

    profile_pic = serializers.SerializerMethodField()
    organization_category = serializers.SerializerMethodField()
    def get_organization_category(self, instance):
        organization_category = instance.organization_category
        if organization_category is not None:
            return {
            '_id': organization_category._id,
            'name': organization_category.name,
        }
        return None

   
    def get_profile_pic(self, instance):
        filename = instance.profile_pic
        if filename:
            # Assuming image_path_to_binary is a utility function you have defined
            format = image_path_to_binary(filename)
            return format
        return []

    class Meta:
        model = Organizations
        fields = '__all__'
