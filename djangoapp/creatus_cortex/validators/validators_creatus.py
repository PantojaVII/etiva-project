from utils.validator import Validator
from django.contrib.auth.hashers import check_password
from utils.common import *


class ValidatorsCreatus(Validator):

    def __init__(self, data):
        self._data = data
        super().__init__()

    def get_data(self):
        return self._data

    def set_data(self, value):
        self._data = value

   
    def validate_Creatus(self):
        super().validate_Prompt_AI(self.get_data().get('prompt'))
        return super().get_Errors()
