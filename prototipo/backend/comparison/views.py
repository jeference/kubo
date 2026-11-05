from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from comparison import services
from comparison.serializers import CatalogModelSerializer, CreateRunSerializer, RunSerializer


class CatalogView(APIView):
    def get(self, request):
        return Response(CatalogModelSerializer(services.get_catalog(), many=True).data)


class RunsView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        serializer = CreateRunSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = services.create_run(
            raw=serializer.validated_data["image"].read(),
            model_keys=serializer.validated_data["models"],
        )
        return Response(RunSerializer(run).data, status=status.HTTP_202_ACCEPTED)


class RunDetailView(APIView):
    def get(self, request, id):
        return Response(RunSerializer(services.get_run(run_id=id)).data)
