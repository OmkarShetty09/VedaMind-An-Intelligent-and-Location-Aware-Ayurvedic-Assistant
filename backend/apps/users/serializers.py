from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import User, UserCondition, UserMedication


def validate_password_strength(value):
    validate_password(value)
    return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password_strength])

    class Meta:
        model = User
        fields = ["email", "name", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data, password=password)
        return user


class UserMedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMedication
        fields = ["id", "free_text", "canonical_drug_ids", "active"]


class UserConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCondition
        fields = ["id", "condition", "severity", "active"]


class MeSerializer(serializers.ModelSerializer):
    medications = UserMedicationSerializer(many=True, read_only=True)
    conditions = UserConditionSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "timezone",
            "consent_accepted",
            "consent_version",
            "medications",
            "conditions",
        ]
        read_only_fields = ["email", "consent_accepted", "consent_version"]

    def validate_timezone(self, value):
        try:
            from apps.core.validators import validate_timezone as _v

            _v(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return value


class MedsUpdateSerializer(serializers.Serializer):
    """Replace the user's active medication list (meds are guardrail input)."""

    medications = serializers.ListField(child=serializers.CharField(max_length=255), max_length=50)

    def update_user(self, user):
        user.medications.filter(active=True).update(active=False)
        for text in self.validated_data["medications"]:
            UserMedication.objects.create(user=user, free_text=text, canonical_drug_ids=[])
        return user
