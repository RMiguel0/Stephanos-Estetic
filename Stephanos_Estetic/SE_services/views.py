# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def services_list(request):
    # TODO: reemplazar por consulta real al modelo
    data = [
        {"id": 1, "name": "Facial Cleansing", "price": 5000},
        {"id": 2, "name": "Massage Therapy", "price": 8000},
    ]
    return Response(data)
