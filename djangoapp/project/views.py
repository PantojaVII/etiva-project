# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests  
import os
import replicate


@api_view(['GET'])
@permission_classes([AllowAny])
def test_view(request):
    # Configurar a chave da API da OpenAI
    try:
        input = {
            "image": "https://instagram.fpmw9-1.fna.fbcdn.net/v/t51.29350-15/385795091_736452681830123_1983335295362787902_n.webp?stp=dst-jpg_e35&efg=eyJ2ZW5jb2RlX3RhZyI6ImltYWdlX3VybGdlbi4xNDQweDkyMC5zZHIuZjI5MzUwLmRlZmF1bHRfaW1hZ2UifQ&_nc_ht=instagram.fpmw9-1.fna.fbcdn.net&_nc_cat=111&_nc_ohc=jXQaqQXJQ9kQ7kNvgFkj4GT&_nc_gid=582b71a973204113a7e0dc17012f21a0&edm=AP4sbd4BAAAA&ccb=7-5&ig_cache_key=MzIwNjUyMDQ3MzcxMzgwNjg1NQ%3D%3D.3-ccb7-5&oh=00_AYASFNqKIe4InloxWcwFrkos-abqtNXOtuRPWhjBS7hXsA&oe=66FA7F52&_nc_sid=7a9f4b",
            "style": "Toy",
            "prompt": "a person in a post apocalyptic war game",
            "instant_id_strength": 0.8
        }

        # Executar a chamada para o modelo
        output = replicate.run(
            "fofr/face-to-many:a07f252abbbd832009640b27f063ea52d87d7a23a185ca165bec23b5adc8deaf",
            input=input
        )

        # Retornar a saída como uma resposta
        return Response({"output": output})  # Certifique-se de retornar a resposta
    except Exception as e:
        return Response({"error": str(e)}, status=500)
