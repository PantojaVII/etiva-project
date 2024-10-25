from ..models import User
from credits.models import Service, UserCredit
from ..backend.backends import EmailBackend
import re
from utils.validator import Validator, status_code_error
from django.contrib.auth.hashers import check_password
from utils.common import *
from utils.common import ValidationTokenWithJwtError
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

class ValidatorUser(Validator):

    def __init__(self, data, user=None):
        self._user = user 
        self._data = data
        super().__init__()
    
    def get_data(self):
        return self._data

    def set_data(self, value):
        self._data = value
    
    def validate_Getuser(self):
        id = self.get_data().get('id')
        if not User.objects.filter(id=id).exists():

            super().set_Errors(
                {
                    'description': {
                        "error_code": status_code_error(6),
                    }
                }
            )
            return 

    """ Verifica para alteração de email """
    def validate_email(self):
        data = self.get_data()
        email = data.get('email')
        user_id = data.get('id')
        
        # Verifica se o usuário com o ID fornecido existe
        user = User.objects.filter(id=user_id).first()
        
        if user and user.email == email:
            return
        
        # Verifica se já existe algum usuário com o email fornecido
        if User.objects.filter(email=email).exists():
            # Se existir, retorna um erro
            super().set_Errors(
                {
                    'email': {
                        "error_code": status_code_error(1),
                    }
                }
            )
    def validate_email_restore(self, email):
        
        # Verifica se já existe algum usuário com o email fornecido
        if not User.objects.filter(email=email).exists():
            # Se existir, retorna um erro
            super().set_Errors(
                {
                    'email': {
                        "error_code": status_code_error(1, msg_personalize='Email não encontrado' ),
                    }
                }
            )


    def validate_format_email(self):
        email = self.get_data().get('email')
        
        padrao_email = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        if not bool(padrao_email.match(email)):
            self.set_Errors(
                {
                    'email': {
                        "error_code": status_code_error(1, 
                                                        msg_personalize="Formato de email inválido"),
                    }
                    
                }
            )
    
    def validate_name(self):
        name = self.get_data().get('name')
        if not name:
            super().set_Errors(
                {
                    'name': {
                        "error_code": status_code_error(4),
                    }
                }
            ) 
 
    def validate_avatar(self):
        avatar_file = self.get_data().get('avatar')
        if avatar_file:
            if not avatar_file.name.lower().endswith(('.png', '.jpg')):
                self.set_Errors(
                    {
                        'avatar': {
                            "error_code": status_code_error(2),
                            "error_message": "Avatar deve ter extensão .png ou .jpg"
                        }
                    }
                ) 

    def validate_Oldpassword(self):
        id = self.get_data().get('id')
        password = self.get_data().get('old_password')
        
        # Obtenha o usuário com o id fornecido
        user = User.objects.filter(id=id).first()

        # Verifique se o usuário existe e se a senha fornecida é válida
        if user and check_password(password, user.password):
            return
        else:
            # A senha fornecida não é válida ou o usuário não existe
            super().set_Errors(
                {
                    'old_password': {
                        "error_code": status_code_error(5),
                    }
                }
            )

    def validate_password(self):
        password = self.get_data().get('password')
      

        # Regras de validação
        errors = {}
        if len(password) < 6:
            errors['password'] = True
        
        if not re.search(r"[A-Z]", password):  # Verifica se há pelo menos uma letra maiúscula
            errors['password'] = True
        
        if not re.search(r"[a-z]", password):  # Verifica se há pelo menos uma letra minúscula
            errors['password'] = True
        
        if not re.search(r"[0-9]", password):  # Verifica se há pelo menos um número
            errors['password'] = True
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Verifica se há pelo menos um caractere especial
            errors['password'] = True

        if len(set(password)) < 4:  # Verifica se a senha não tem pelo menos 4 caracteres diferentes
            errors['password'] = True

        # Se houver erros, chama set_Errors
        if errors:
            super().set_Errors(
                {
                    'password': {
                        "error_code": status_code_error(3, msg_personalize="A senha deve ter pelo menos 6 caracteres, letra maiúscula, uma minúscula, conter pelo menos um número, e possuir ao menos um caractere especial."),
                    }
                }
            )  

    def validate_password_confirmation(self):
        password = self.get_data().get('password')
        password_confirmation = self.get_data().get('password_confirmation')
        if password_confirmation != password:
            super().set_Errors(
                {
                    'password confirmation': {
                        "error_code": status_code_error(3, msg_personalize="As senhas não coincidem"),
                    }
                }
            )      

    def verify_csrf(self, csrf):
        if not csrf:
            super().set_Errors(
                {
                    'validation': {
                        "error_code": status_code_error(1.3),
                    }
                }
            ) 
                
    def validate_User(self):
        self.validate_Getuser()
        return super().get_Errors()
    
    def validate_CadUser(self):
        self.validate_email()
        self.validate_format_email()
        self.validate_avatar()
        self.validate_password()
        self.validate_password_confirmation()
        #self.validate_name()

        return super().get_Errors()
    
    def validate_UpdateUser(self, authorization_header):
        self.validate_email()
        self.verify_jwt_token(authorization_header, self._user)
        if self.get_data().get('password'):
            self.validate_Oldpassword()
            self.validate_password()
            self.validate_password_confirmation()           
        return super().get_Errors()

    def validate_RestorePassword(self):
        self.verify_csrf(csrf=self.get_data().get('csrf'))
        self.validate_email_restore(email=self.get_data().get('email'))     
        return super().get_Errors()
    
    def validate_ResetPassword(self, authorization_header):
        
        self.verify_jwt_token(authorization_header, self._user)
        self.validate_password()
        self.validate_password_confirmation()           
        return super().get_Errors()
        
    """ Login """
    def validate_login_credentials(self):

        email = self.get_data().get('email')
        password = self.get_data().get('password')
        user = EmailBackend().authenticate(email=email, password=password)
        if not user:
            super().set_Errors(
                {
                    'description': {
                        "error_code": status_code_error(1.2),
                    }
                }
            )
        return super().get_Errors()

def validate_pk_hash_jwt(user_id, pk_hash):
    """
    Valida o hash enviado com o JWT armazenado no local storage do frontend.
    
    :param user_id: ID do usuário autenticado.
    :param pk_hash: Hash a ser validado.
    :raises PKHashValidationError: Se a validação falhar.
    """
    id_pk = decode_id(pk_hash)  # Decodifica o pk_hash
    if id_pk != user_id:
        print('-----erro de validação--------')  # Debug
        raise ValidationTokenWithJwtError({'verify': {'error_code': status_code_error(0.3)}})

def check_user_has_sufficient_credits(user_id, service_id):
    try:
        # Obtém o serviço pelo ID
        service = Service.objects.get(id=service_id)
        
        # Obtém os créditos do usuário
        user_credit, created = UserCredit.objects.get_or_create(user_id=user_id)
        
        
        # Verifica se o usuário tem créditos suficientes para o serviço
        if user_credit.balance >= service.cost_in_credits:
            return service
        else:
            raise ValidationTokenWithJwtError({'credit': {'error_code': status_code_error(7.1)}})
    except ObjectDoesNotExist:
        # Caso o serviço ou os créditos do usuário não sejam encontrados
        raise ValidationTokenWithJwtError({'credit': {'error_code': status_code_error(0.3)}})
