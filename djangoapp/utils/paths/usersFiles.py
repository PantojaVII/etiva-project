from .baseFileUploader import BaseFileUploader
from utils.common import decode_id, encode_id
""" Section Upload and delete medias"""
class UserFileManager(BaseFileUploader):
    
    def __init__(self, profile=None, request=None):
        self._profile = profile
        self._request = request
        self._hash_id = encode_id(profile.user.id)

    """ Paths """
    def path_user(self):
        # Define o caminho onde o arquivo será salvo baseado no hash_id
        path_user = f'users/{self._hash_id}'
        return path_user
    
    def path_avatar(self):
        # Gera o nome único do arquivo usando o método da classe pai
        unique_filename = super()._generate_unique_filename()
        
        # Define o caminho onde o arquivo será salvo
        path_avatar = f'{self.path_user()}/{unique_filename}'
        
        return path_avatar
    
    def upload_avatar(self, request):
        if 'avatar' in self._request.FILES:
            fileAvatar = self._request.FILES['avatar']
            if self._profile.picture:
                self.delete_file_local(self._profile.picture)    
            super().__init__(fileAvatar)           
            saved_path = self.upload_files_local(self.path_avatar())
            return saved_path
        return None