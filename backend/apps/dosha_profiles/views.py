from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DoshaAssessment, DoshaProfile
from .scoring import score
from .serializers import DoshaAssessmentSerializer, DoshaProfileSerializer, DoshaSubmitSerializer


class AssessView(APIView):
    """POST /api/v1/dosha/assess - run the quiz, persist assessment + update profile."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DoshaSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        normalized_answers = serializer.validated_data["answers"]
        result = score(normalized_answers)
        assessment = DoshaAssessment.objects.create(
            user=request.user,
            answers=serializer.validated_data["answers"],
            results=result,
        )
        profile, _ = DoshaProfile.objects.get_or_create(user=request.user)
        profile.vikriti_scores = result["scores"]
        profile.dominant_dosha = result["dominant_dosha"]
        profile.save(update_fields=["vikriti_scores", "dominant_dosha", "updated_at"])
        return Response(DoshaAssessmentSerializer(assessment).data)


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/dosha/profile - read/update prakriti + vikriti."""

    serializer_class = DoshaProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = DoshaProfile.objects.get_or_create(user=self.request.user)
        return profile
