from rest_framework import serializers
from ..models import Poll, PollResponse

class PollSerializer(serializers.ModelSerializer):
    yes_count = serializers.SerializerMethodField()
    no_count = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = ['_id', 'other_category', 'question', 'created_at', 'yes_count', 'no_count']

    def get_yes_count(self, obj):
        return obj.responses.filter(response='YES').count()

    def get_no_count(self, obj):
        return obj.responses.filter(response='NO').count()

# class PollResponseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PollResponse
#         fields = ['_id', 'poll', 'user', 'response', 'created_at']
#         read_only_fields = ['created_at']

class PollResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollResponse
        fields = ['_id', 'poll', 'user', 'response', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        # Check if a response from this user to the same poll already exists
        if PollResponse.objects.filter(poll=data['poll'], user=data['user']).exists():
            raise serializers.ValidationError({"error": "You have already responded to this poll."})
        return data