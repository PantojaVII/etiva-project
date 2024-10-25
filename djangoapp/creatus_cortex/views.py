from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import json
from .services.service import *
from authentication.validators.validatorsUsers import validate_pk_hash_jwt, check_user_has_sufficient_credits
from rest_framework.response import Response
from rest_framework import status
from .validators.validators_creatus import ValidatorsCreatus
from utils.paths.r2manage import R2FileManager
from utils.common import decode_id, encode_id
from openai import OpenAI
from .models import GeneratedImage
from rest_framework.pagination import PageNumberPagination
from credits.models import ServiceUsage

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def GenerateImageView(request):
    """Gera uma imagem com base no prompt fornecido pelo usuário."""
    data = json.loads(request.body.decode('utf-8'))

    # Pegando usuário
    user = request.user
    pk_hash = data.get('pk_hash')
    pk_service = decode_id(data.get('pk_service'))
    
    # Validações de usuário
    validate_pk_hash_jwt(user.id, pk_hash)

    service = check_user_has_sufficient_credits(user.id, pk_service)
    
    # Obtendo os campos do corpo da requisição
    prompt = data.get('prompt', '')
    
    # Define 1024 como valor máximo permitido
    max_size = 1024

    # Obtém os valores enviados ou usa 1024 como padrão
    width = min(data.get('width', 1024), max_size)
    height = min(data.get('height', 1024), max_size)
    
    num_outputs = data.get('num_outputs', 1)  # Padrão
    guidance_scale = data.get('guidance_scale', 7.5)  # Padrão
    apply_watermark = data.get('apply_watermark', True)  # Padrão
    negative_prompt = data.get('negativePrompt', '')  # Atualizado
    prompt_strength = data.get('promptStrength', 0.8)  # Atualizado

    # Validação de dados enviados
    validator = ValidatorsCreatus(data)
    errors = validator.validate_Creatus()
    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    # Validação de prompt
    if not prompt:
        return Response({'error': 'No prompt provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Gera a imagem usando Stable Diffusion
        image_names, image_files, statusGenerate = generate_image_stable_diffusion(
            prompt,
            num_images=num_outputs,  # Passando o número de saídas
            width=width,  # Passando a largura
            height=height,  # Passando a altura
            guidance_scale=guidance_scale,  # Passando o valor de guidance_scale
            apply_watermark=apply_watermark,  # Passando se deve aplicar watermark
            negative_prompt=negative_prompt,  # Passando o prompt negativo
            prompt_strength=prompt_strength,  # Passando a força do prompt
        )
        
        if statusGenerate == "success":
            presigned_urls = []
            r2_manager = R2FileManager()
            
            for image_name, image_file in zip(image_names, image_files):
                path_image = pathImage(pk_hash, image_name)
                
                # Upload da imagem para o R2
                r2_manager.upload_file(image_file, path_image)
                
                # Gerar URL assinada para acessar a imagem
                presigned_url = r2_manager.generate_presigned_url(path_image)
                
                # Salvar a imagem gerada no banco de dados
                GeneratedImage.objects.create(
                    user=user,
                    image_url=path_image,
                    prompt=prompt
                )
                
                presigned_urls.append(presigned_url)
            
            # Calcula o total de créditos usados
            total_credits_used = len(image_names) * service.cost_in_credits


            # Registra o uso de créditos na tabela ServiceUsage
            ServiceUsage.objects.create(
                user=user,
                service=service,
                credits_used=total_credits_used
            )

            # Retorna a lista de URLs assinadas ao cliente
            return Response({'image_urls': presigned_urls}, status=status.HTTP_200_OK)

    except Exception as e:
        # Registra o erro no console
        print(f"Ocorreu um erro: {e}")
        return Response({'error': 'Erro na geração, Por favor, tente mais tarde!'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ListGeneratedImagesView(request):
    """Retorna todas as imagens geradas pelo usuário autenticado."""
    user = request.user
    
    try:
        # Obtém todas as imagens geradas pelo usuário
        generated_images = GeneratedImage.objects.filter(user=user).order_by('-created_at')
        
        # Paginação
        paginator = PageNumberPagination()
        paginated_images = paginator.paginate_queryset(generated_images, request)

        r2_manager = R2FileManager()
        
        # Serializa os dados
        images_data = [
            {   
                "pk_image": encode_id(img.id),
                'image_url': r2_manager.generate_presigned_url(img.image_url),  # Gerar URL assinada
                'prompt': img.prompt,
                'created_at': img.created_at.isoformat()  # Formato ISO para datas
            }
            for img in paginated_images
        ]
        
        return paginator.get_paginated_response({'generated_images': images_data})
    
    except Exception as e:
        print(f"Ocorreu um erro ao listar as imagens: {e}")
        return Response({'error': 'Erro ao recuperar as imagens, tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def DeleteImagesView(request):
    """Deleta imagens geradas pelo usuário autenticado com base nos IDs fornecidos."""
    user = request.user
    data = json.loads(request.body.decode('utf-8'))
    image_ids = data.get('image_ids', [])

    if not image_ids:
        return Response({'error': 'Nenhum ID de imagem fornecido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Decodifica os IDs e obtém as imagens geradas pelo usuário
        decoded_image_ids = [decode_id(image_id) for image_id in image_ids]
        generated_images = GeneratedImage.objects.filter(id__in=decoded_image_ids, user=user)

        r2_manager = R2FileManager()
        
        for image in generated_images:
            # Deleta a imagem do R2
            r2_manager.delete_file(image.image_url)
            # Remove a entrada do banco de dados
            image.delete()

        return Response({'message': 'Imagens deletadas com sucesso'}, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        print(f"Ocorreu um erro ao deletar as imagens: {e}")
        return Response({'error': 'Erro ao deletar as imagens, tente novamente mais tarde.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

