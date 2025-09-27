# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def donations_list(request):
    # TODO: reemplazar por consulta real al modelo
    data = [
        {"id": 1, "amount": 10000, "created_at": "2025-09-27"},
        {"id": 2, "amount": 25000, "created_at": "2025-09-26"},
    ]
    return Response(data)
