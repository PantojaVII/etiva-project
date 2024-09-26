from rest_framework import serializers
from ..models import User, Profile
from utils.common import *

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    user_email = serializers.ReadOnlyField(source='user.email')
    pk = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Profile
        fields = ['pk', 'user', 'user_email', 'first_name', 'last_name', 'picture', 'phone_number', 'date_of_birth']
        extra_kwargs = {
            'date_of_birth': {'required': False}
        }
    
    def get_pk(self, obj):
        return encode_id(obj.user.pk)

    def to_representation(self, instance):
        # Obtenha a representação original dos dados
        """A representation é um dicionário que contém a versão serializada dos dados do modelo (neste caso, do Profile). Ela é gerada automaticamente pelo serializer e usada para preparar os dados que serão enviados na resposta da API. """
        representation = super().to_representation(instance)

        # Obtenha a request a partir do context e construa a base_url
        request = self.context.get('request')
        if request is not None:
            base_url = request.build_absolute_uri('/')
            # Concatena a base_url ao campo 'picture'
            if representation['picture']:
                representation['picture'] = f"{base_url}media/{representation['picture']}"

        return representation
