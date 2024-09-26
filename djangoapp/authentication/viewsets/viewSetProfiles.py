from ..models import Profile, User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from ..serializers.serializerProfiles import ProfileSerializer
from ..validators.validatorsProfiles import ValidatorsProfiles
from utils.common import decode_id
from utils.paths.usersFiles import UserFileManager



class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_object(self, pk):
        # Decodifica o hash para obter o ID
        decoded_id = decode_id(pk)
        """ Validando user"""
        data = {"id": decoded_id}
        validator = ValidatorsProfiles(data)
        errors = validator.validate_Profile()
        if errors:
            raise ValidationError(errors)

        return Profile.objects.get(user_id=decoded_id)

    def retrieve(self, request, pk=None, *args, **kwargs):
        profile = self.get_object(pk)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """ Pegando DADOS ENVIADOS """
        encoded_id = request.data.get('user')
        decoded_id = decode_id(encoded_id)
        
        # Substitui o valor de 'user' em request.data com o decoded_id
        request.data['user'] = decoded_id
        
        data = request.data
        
        """ Validações """
        validator = ValidatorsProfiles(data)
        errors = validator.validate_CadProfile()
        
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Se um novo arquivo de avatar foi enviado
        if 'avatar' in request.FILES:
            file = request.FILES['avatar']
            uploader = UserFileManager(file=file, hash_id=encoded_id)
            # Salva o arquivo localmente
            saved_path = uploader.upload_files_local(uploader.path_avatar())
            
            data['picture'] = saved_path

        # Crie uma instância do serializer com os dados enviados
        serializer = self.serializer_class(data=data, context={'request': request})
       
        """ Salvando """
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop('password_confirmation', None)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, pk=None, *args, **kwargs):
        profile = self.get_object(pk)

        # Acesse os dados diretamente, sem copiar
        data = {key: value for key, value in request.data.items() if key != 'avatar'}
        
        # Verifique se o arquivo está em request.FILES
        avatar = request.FILES.get('avatar')
        if avatar:
            data['avatar'] = avatar 

        # Valida dados enviados
        validator = ValidatorsProfiles(data)
        errors = validator.validate_UpdateProfile()
        
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Envia o avatar
        fileManager = UserFileManager(request=request, profile=profile)
        picture_path = fileManager.upload_avatar(request)
        if picture_path:
          
            data['picture'] = f"{picture_path}"

        serializer = self.serializer_class(profile, data=data, context={'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object(pk)
        
        uploader = UserFileManager(hash_id=pk)
        uploader.delete_directory_local(uploader.path_user())
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)