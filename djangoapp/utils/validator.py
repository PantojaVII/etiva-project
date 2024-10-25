from django.core.exceptions import ValidationError
import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from authentication.models import User
from utils.common import decode_id, encode_id

class Validator:
    
    def __init__(self):
        self._errors = {}

    def get_Errors(self):
        return self._errors
    
    def set_Errors(self, error):
        self._errors.update(error)
    
    def validate_Prompt_AI(self, prompt):
        prompt = prompt
        if not prompt:

            self.set_Errors(
                {
                    'prompt': {
                        "error_code": status_code_error(7.0),
                    }
                }
            )
            return 
        
    def verify_jwt_token(self, authorization_header, user):

        if not authorization_header or not authorization_header.startswith('Bearer '):
            raise AuthenticationFailed('Authorization token missing or invalid')

        # Extrai o token do cabeçalho
        token = authorization_header.split(' ')[1]

        try:
            # Decodifica o token JWT usando a SECRET_KEY do Django
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            realUser = User.objects.get(id=decoded_token['user_id'])
            print(realUser)
            
            if realUser.email != user.email:
                self.set_Errors(
                    {
                        'token': {
                            "error_code": status_code_error(0.3),
                        }
                    }
                )
                
        except jwt.ExpiredSignatureError:
            # Se existir, retorna um erro
            self.set_Errors(
                {
                    'token': {
                        "error_code": status_code_error(0.1),
                    }
                }
            )
        except jwt.InvalidTokenError:
            self.set_Errors(
                {
                    'token': {
                        "error_code": status_code_error(0.2),
                    }
                }
            )


def status_code_error(index, name_value=None, msg_personalize=None):
    # Lista de códigos de erro e mensagens correspondentes
    error_messages = {
        0: {
            "error_code": "RC0",
            "error_message": "Erro desconhecido, entre em contato com o suporte.",
        },
        0.1: {
            "error_code": "RC0.1",
            "error_message": "Token expirado.",
        },
        0.2: {
            "error_code": "RC0.2",
            "error_message": "Token inválido.",
        },
        0.3: {
            "error_code": "RC0.3",
            "error_message": "Ação inválida.",
        },
        1: {
            "error_code": "RC1",
            "error_message": "Email não está disponível.",
        },
        1.1: {
            "error_code": "RC1.1",
            "error_message": "Cadastro de perfil inválido.",
        },
        1.2: {
            "error_code": "RC1.2",
            "error_message": "Login inválido, por favor, verifique suas credênciais.",
        },
        1.3: {
            "error_code": "RC1.3",
            "error_message": "Erro de validação. por favor, Tente mais tarde, se o erro persistir, entre em contato com o suporte.",
        },
        1.4: {
            "error_code": "RC1.4",
            "error_message": "Login inválido, por favor, verifique suas credênciais.",
        },
        2: {
            "error_code": "RC2",
            "error_message": "Imagem de avatar apenas em formatos .png ou .jpg.",
        },
        3: {
            "error_code": "RC3",
            "error_message": "A senha deve conter no mínimo 6 dígitos.",
        }, 
        4: {
            "error_code": "RC4",
            "error_message": "O nome é obrigatório.",
        },
        4.1: {
            "error_code": "RC4.1",
            "error_message": "O Primeiro nome é obrigatório.",
        },
        5: {
            "error_code": "RC5",
            "error_message": "Senha de autenticação inválida.",
        },
        6: {
            "error_code": "RC6",
            "error_message": "Usuário não encontrado.",
        },
        6.1: {
            "error_code": "RC6.1",
            "error_message": "Perfil não encontrado.",
        },
        7.0: {
            "error_code": "RC7.0",
            "error_message": "Verifique o prompt, campo obrigatório.",
        },
        7.1: {
            "error_code": "RC7.1",
            "error_message": "Créditos insuficientes para realizar a operação.",
        },
    }
        # Verifica se um valor adicional foi fornecido
    if msg_personalize is not None:
        # Se um valor adicional foi fornecido, adiciona-o à mensagem de erro correspondente
        error_messages[index]["error_message"] = msg_personalize
        
    return error_messages[index]