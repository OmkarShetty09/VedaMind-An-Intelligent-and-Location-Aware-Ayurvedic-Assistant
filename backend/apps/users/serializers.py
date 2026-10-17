from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import User, UserCondition, UserMedication


def validate_password_strength(value):
    validate_password(value)
    return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password_strength])
    name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    timezone = serializers.CharField(max_length=64, required=False)

    class Meta:
        model = User
        fields = ["email", "name", "password", "timezone"]

    def validate_email(self, value):
        # Login lowercases the email, so accounts must be stored lowercased to be reachable.
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def validate_timezone(self, value):
        try:
            from apps.core.validators import validate_timezone as _v

            _v(value)
        except ValidationError:
            return "UTC"  # never block sign-up on a browser-reported zone we don't know
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        if not validated_data.get("name", "").strip():
            validated_data["name"] = validated_data["email"].split("@")[0]
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
    # Replaced lists are soft-deactivated, so only the active rows describe the user.
    medications = serializers.SerializerMethodField()
    conditions = serializers.SerializerMethodField()

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

    def get_medications(self, obj):
        return UserMedicationSerializer(obj.medications.filter(active=True), many=True).data

    def get_conditions(self, obj):
        return UserConditionSerializer(obj.conditions.filter(active=True), many=True).data

    def validate_timezone(self, value):
        try:
            from apps.core.validators import validate_timezone as _v

            _v(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        return value


class MedsUpdateSerializer(serializers.Serializer):
    """Replace the user's active medication list (meds are guardrail input)."""

    medications = serializers.ListField(child=serializers.CharField(max_length=255, allow_blank=True), max_length=50)

    def update_user(self, user):
        user.medications.filter(active=True).update(active=False)
        for text in self.validated_data["medications"]:
            if text.strip():
                UserMedication.objects.create(user=user, free_text=text.strip(), canonical_drug_ids=[])
        return user


class ConditionsUpdateSerializer(serializers.Serializer):
    """Replace the user's active condition list (pregnancy, diabetes, ... feed guardrail context flags)."""

    conditions = serializers.ListField(child=serializers.CharField(max_length=120, allow_blank=True), max_length=50)

    def update_user(self, user):
        user.conditions.filter(active=True).update(active=False)
        for text in self.validated_data["conditions"]:
            if text.strip():
                UserCondition.objects.create(user=user, condition=text.strip())
        return user


class LocationSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lon = serializers.FloatField(min_value=-180, max_value=180)
    accuracy = serializers.FloatField(required=False, default=0.0, min_value=0)
    source = serializers.CharField(required=False, default="gps", max_length=16)
    confidence = serializers.FloatField(required=False, default=1.0, min_value=0, max_value=1)
    # Sent when the user picked a city by name (no need to reverse-geocode it again).
    place_name = serializers.CharField(required=False, allow_blank=True, max_length=255, default="")
