from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from users.models import User


class UserRegistrationSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'nid', 'medical_history', 'specialization',
                  'contact_details', 'profile_picture']

    def create(self, validated_data):
        role = validated_data.get('role')
        if role == User.Role.PATIENT:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                role=role,
                nid=validated_data.get('nid'),
                medical_history=validated_data.get('medical_history')
            )
        elif role == User.Role.DOCTOR:
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                role=role,
                specialization=validated_data.get('specialization'),
                contact_details=validated_data.get('contact_details'),
                profile_picture=validated_data.get('profile_picture')
            )
        else:
            raise serializers.ValidationError("Invalid role")
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.Role.choices)
    remember_me = serializers.BooleanField(default=False)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')

        try:
            user = User.objects.get(username=username, role=role)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid username or role")

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        data['user'] = user
        return data


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'nid', 'medical_history', 'specialization', 'contact_details',
                  'profile_picture']
        read_only_fields = ['id', 'username', 'email', 'role']

    def update(self, instance, validated_data):
        role = instance.role
        if role == User.Role.PATIENT:
            instance.nid = validated_data.get('nid', instance.nid)
            instance.medical_history = validated_data.get('medical_history', instance.medical_history)
        elif role == User.Role.DOCTOR:
            instance.specialization = validated_data.get('specialization', instance.specialization)
            instance.contact_details = validated_data.get('contact_details', instance.contact_details)
            instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("New passwords do not match")
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'date_joined']
        read_only_fields = ['id', 'username', 'email', 'role', 'is_active', 'date_joined']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['role_display'] = instance.get_role_display()
        return representation


class CurrentUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'nid', 'medical_history', 'specialization', 'contact_details',
                  'profile_picture', 'is_active', 'date_joined', 'last_login']
        read_only_fields = ['id', 'username', 'email', 'role', 'is_active', 'date_joined', 'last_login']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['role_display'] = instance.get_role_display()
        return representation


class EmailResendSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=User.Role.choices)


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(required=True)
    role = serializers.ChoiceField(choices=User.Role.choices)


class UserStatusUpdateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ['is_active']
