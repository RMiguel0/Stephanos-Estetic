# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def sales_list(request):
    #TODO: reemplazar por consulta real al modelo
    data = [
        {"id": 1, "total": 15000, "created_at": "2025-09-27"},
    ]
    return Response(data)
