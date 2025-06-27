from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "password", "first_name", "last_name")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
                "style": {"input_type": "password"},
            },
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password")
        user = super(UserSerializer, self).update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "first_name", "last_name")
