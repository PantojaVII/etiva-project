import hashlib
import uuid
from datetime import datetime
from hashids import Hashids
from rest_framework.relations import HyperlinkedIdentityField
from django.middleware.csrf import get_token
from django.http import JsonResponse



hashids = Hashids(min_length=8, salt="your_secret_salt")

"""  hash Section """
def encode_id(id):
    return hashids.encode(id)

def decode_id(hashid):
    decoded = hashids.decode(hashid)
    return decoded[0] if decoded else None

def generate_hash():
    # Gera um UUID aleatório
    random_uuid = uuid.uuid4()

    # Obtém a data e hora atual
    current_datetime = datetime.now()

    # Converte a data e hora em uma string formatada
    datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    # Concatena o UUID e a string formatada da data e hora
    combined_str = f"{random_uuid}-{datetime_str}"

    # Gera um hash usando SHA-256
    hashed_value = hashlib.sha256(combined_str.encode()).hexdigest()

    return hashed_value[:15] 

""" Hiperlinks serializers section """
class CustomHyperlinkedIdentityField(HyperlinkedIdentityField):
    def get_url(self, obj, view_name, request, format):
        # Obtenha a URL original usando o método da classe pai
        url = super().get_url(obj, view_name, request, format)
        if url and obj.pk:
            # Codifique o ID
            encoded_id = encode_id(obj.pk)
            # Divida a URL em partes para substituir corretamente o ID
            url_parts = url.split('/')
            # Assuma que o último componente da URL é o ID
            url_parts[-2] = encoded_id  # Substitua o penúltimo componente da URL pelo encoded_id
            url = '/'.join(url_parts)
        return url

""" Generate csrf token """
def generate_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({"csrfToken": csrf_token})


""" Group Policies section  """
#decodificar lista hash de grupos de políticas 
def groups_policies_decoded(encoded_list):

    decoded_list = [decode_id(encoded_id) for encoded_id in encoded_list]
    return decoded_list

    







