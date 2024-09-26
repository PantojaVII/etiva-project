from ..models import User, Profile
from ..backend.backends import EmailBackend
import re
from utils.validator import Validator, status_code_error
from django.contrib.auth.hashers import check_password
from utils.common import *


class ValidatorsProfiles(Validator):

    def __init__(self, data):
        self._data = data
        super().__init__()

    def get_data(self):
        return self._data

    def set_data(self, value):
        self._data = value

    def validate_GetProfile(self):
        id = self.get_data().get('id')
        if not Profile.objects.filter(user_id=id).exists():

            super().set_Errors(
                {
                    'description': {
                        "error_code": status_code_error(6),
                    }
                }
            )
            return 
    
    def validate_firs_name(self):
        first_name = self.get_data().get('first_name')
        if not first_name:
            super().set_Errors(
                {
                    'first_name': {
                        "error_code": status_code_error(4.1),
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
                            #"error_message": "Avatar deve ter extensão .png ou .jpg"
                        }
                    }
                ) 


        return super().get_Errors()
    
    def validate_Profile(self):
        self.validate_GetProfile()
        return super().get_Errors()
    
    def validate_UserWithProfile(self):
        user_id = self.get_data().get('user')
        
        # Verifica se o Profile existe sem levantar exceção
        if Profile.objects.filter(user_id=user_id).exists():
            super().set_Errors(
                {
                    'first_name': {
                        "error_code": status_code_error(1.1),
                    }
                }
            )
        
        return super().get_Errors()
    
    def validate_CadProfile(self):
        self.validate_firs_name()
        self.validate_UserWithProfile()
        self.validate_avatar()
        return super().get_Errors()
    
    def validate_UpdateProfile(self):
        self.validate_avatar()
        return super().get_Errors()
