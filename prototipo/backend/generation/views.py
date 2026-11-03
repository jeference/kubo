from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from generation import services
from generation.serializers import (
    CreateModelSerializer,
    CreditsSerializer,
    EditImageSerializer,
    GenerateImagesSerializer,
    ImageFileSerializer,
    ModelStatusSerializer,
    StoredImageSerializer,
)


class GenerateImagesView(APIView):
    def post(self, request):
        serializer = GenerateImagesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        images = services.generate_images(
            prompt=serializer.validated_data["prompt"],
            style=serializer.validated_data["style"],
        )
        return Response(
            StoredImageSerializer(images, many=True).data, status=status.HTTP_201_CREATED
        )


class EditImageView(APIView):
    def post(self, request, id):
        serializer = EditImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = services.edit_image(
            image_id=id, instruction=serializer.validated_data["instruction"]
        )
        return Response(StoredImageSerializer(image).data, status=status.HTTP_201_CREATED)


class UploadImageView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        serializer = ImageFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        image = services.standardize_upload(
            raw=serializer.validated_data["image"].read(),
            prompt=serializer.validated_data["prompt"],
            style=serializer.validated_data["style"],
        )
        return Response(StoredImageSerializer(image).data, status=status.HTTP_201_CREATED)


class ModelsView(APIView):
    def post(self, request):
        serializer = CreateModelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        model = services.create_model(image_id=serializer.validated_data["image_id"])
        return Response(ModelStatusSerializer(model).data, status=status.HTTP_202_ACCEPTED)


class ModelDetailView(APIView):
    def get(self, request, id):
        model = services.get_model(task_id=id)
        return Response(ModelStatusSerializer(model).data)


class CreditsView(APIView):
    def get(self, request):
        return Response(CreditsSerializer(services.get_credits()).data)
