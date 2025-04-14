from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re

# Start Validation Functions
def validate_email_helper(value, pk):
    """ Validate and transform email """

    if value:
        updated_value = value.lower()
        if pk == None:
            if get_user_model().objects.filter(email=updated_value).filter(is_active=True).exists():
                raise serializers.ValidationError('user with this email already exists.')
        else:
            if get_user_model().objects.filter(email=updated_value).filter(is_active=True).exclude(pk=pk).exists():
                raise serializers.ValidationError('user with this email already exists.')
        return updated_value

def validate_phone_helper(value, pk):
    """ Validate phone """

    if value:
        valid_phone = re.search('^[0-9]{10}$', value)
        if not valid_phone:
            raise serializers.ValidationError("Invalid phone number entered.")
        if pk == None:
            if get_user_model().objects.filter(phone=value).filter(is_active=True).exists():
                raise serializers.ValidationError('user with this phone already exists.')
        else:
            if get_user_model().objects.filter(phone=value).filter(is_active=True).exclude(pk=pk).exists():
                raise serializers.ValidationError('user with this phone already exists.')
        return value
    return None
# End Validation Functions


class UserCreateSerializer(serializers.ModelSerializer):
    """ Serializer: Create a new user """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('pk', 'email', 'first_name', 'last_name', 'phone', 'date_of_birth', 'password',)

    def validate_email(self, value):
        return validate_email_helper(value, pk=None)

    def validate_phone(self, value):
        return validate_phone_helper(value, pk=None)
    
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """ Serializer: User Update Serializer"""

    class Meta:
        model = get_user_model()
        fields = ('pk', 'first_name', 'last_name', 'phone', 'date_of_birth')

    def validate_phone(self, value):
        pk = self.context.get('pk')
        return validate_phone_helper(value, pk)


class UserDisplaySerializer(serializers.ModelSerializer):
    """ Serializer: User display """

    class Meta:
        model = get_user_model()
        fields = (
        'pk', 'email', 'first_name', 'last_name', 'phone', 'date_of_birth', 'created', 'modified')


class UserLoginSerializer(TokenObtainPairSerializer):
    """ Serializer: Authenticate a user """

    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Email does not exist or Password did not match.")

        attrs['user'] = user
        return attrs

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claim
        token['email'] = user.email

        return token