from datetime import datetime
import os
import shutil
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
""" Section Upload and delete medias"""
class BaseFileUploader():
   
    def __init__(self, file=None):
         self._file = file

    """ Generate unique name for file """
    def _generate_unique_filename(self):
        # Obtém o nome do arquivo e a extensão
        file_name, file_extension = os.path.splitext(self._file.name)
        
        # Cria um nome único com base na data e hora atual
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Combina o nome base do arquivo com o timestamp e a extensão
        unique_filename = f'{file_name}_{timestamp}{file_extension}'
        
        return unique_filename

    """ Local """
    def upload_files_local(self, file_path):
        # Salva o arquivo usando o caminho fornecido
        saved_path = default_storage.save(file_path, ContentFile(self._file.read()))
        return saved_path

    def delete_file_local(self, path_to_file):
        try:
            full_directory_file = f'{settings.MEDIA_ROOT }/{path_to_file}'
            os.remove(full_directory_file)
            print("Arquivo excluído com sucesso localmente.")
        except Exception as e:
            print(f"Erro ao excluir arquivo localmente: {e}")
    
    def delete_directory_local(self, directory_path):
        diretorio = f'{settings.MEDIA_ROOT }/{directory_path}'

        try:
            # Construa o caminho completo do diretório usando MEDIA_URL
            full_directory_path = f'{settings.MEDIA_ROOT }/{directory_path}'
            
            # Verifique se o diretório existe antes de tentar excluí-lo
            if os.path.exists(full_directory_path):
                # Exclui o diretório e todos os seus conteúdos
                shutil.rmtree(full_directory_path)
                print("Diretório e todos os seus conteúdos excluídos com sucesso localmente.")
            else:
                print("O diretório não existe.")
        except Exception as e:
            print(f"Erro ao excluir diretório localmente: {e}")

    """ Cloud - S3, R2 etc """            
    def upload_files_cloud(file_path, file):

        path = default_storage.save(file_path, ContentFile(file.read()))
        
        return True
