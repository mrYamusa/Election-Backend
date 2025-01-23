from django.contrib.auth.models import User
from elections.models import *
from rest_framework import serializers
from django.conf import settings
from django.urls import reverse
from rest_framework.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    registration_number = serializers.CharField(write_only=True)
    web_mail = serializers.EmailField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'registration_number', 'web_mail']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Extract registration number and web mail
        registration_number = validated_data.pop('registration_number')
        web_mail = validated_data.pop('web_mail')

        # Verify that the registration number and web mail exist in the Student table
        try:
            student = Student.objects.get(reg_no=registration_number, web_mail=web_mail)
        except Student.DoesNotExist:
            raise ValidationError("Invalid registration number or web mail.")

        # Check if the user already exists
        if User.objects.filter(username=validated_data['username']).exists():
            raise ValidationError("A user with this username already exists.")
        if User.objects.filter(web_mail=validated_data['web_mail']).exists():
            raise ValidationError("A user with this email already exists.")

        # Create the user
        user = User.objects.create_user(**validated_data)

        # Create the UserProfile explicitly here
        UserProfile.objects.create(user=user, registration_number=registration_number, web_mail=web_mail)

        return user

    def to_representation(self, instance):
        # Customize the representation to exclude registration_number and web_mail
        representation = super().to_representation(instance)
        representation.pop('registration_number', None)
        representation.pop('web_mail', None)
        return representation


from rest_framework import serializers
from elections.models import Candidate, Position
from django.contrib.auth.models import User

class CandidateSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='candidate_name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = ['id', 'fullname', 'position_name', 'profile_picture', 'position']

    def get_profile_picture(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None


    def get_absolute_url(self, file_field):
        # Construct the absolute URL for the media file
        return f"{settings.SITE_URL}{file_field.url}"  # Ensure SITE_URL is set in your settings

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = ['id', 'name', 'start_date', 'end_date', 'status']


class VoteSerializer(serializers.Serializer):
    candidate = serializers.PrimaryKeyRelatedField(queryset=Candidate.objects.none(), required=True)

    def __init__(self, *args, **kwargs):
        # Retrieve the position_id from the URL context (passed via view)
        position_id = kwargs['context']['view'].kwargs.get('position_id')

        # If position_id is available, filter candidates by the specified position
        if position_id:
            queryset = Candidate.objects.filter(position_id=position_id)
            # Update the queryset for the candidate field
            self.fields['candidate'].queryset = queryset

        super().__init__(*args, **kwargs)

# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Validate user credentials
        user = User.objects.filter(username=username).first()
        if not user or not user.check_password(password):
            raise AuthenticationFailed('Invalid username or password')

        attrs['user'] = user
        return attrs

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'name', 'created_at']


# serializers.py
class UserVoteHistorySerializer(serializers.ModelSerializer):
    position_name = serializers.CharField(source='position.name')
    candidate_name = serializers.CharField(source='candidate.candidate_name')
    election_name = serializers.CharField(source='election.name')
    voted_at = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Vote
        fields = ['position_name', 'candidate_name', 'election_name', 'voted_at']