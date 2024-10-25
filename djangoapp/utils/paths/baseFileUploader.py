from datetime import datetime
import os
import shutil
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import boto3
from botocore.exceptions import NoCredentialsError, ClientError


""" Section Upload and delete medias"""
class BaseFileUploader:
    def __init__(self, file=None):
        self._bucket_name = os.getenv('S3_BUCKET_NAME')
        self._file = file
        self._s3_client = boto3.client('s3')

    def upload_file_to_s3(self, file_path, file_name):
        """Faz o upload de um arquivo para o S3."""
        try:
            self._s3_client.upload_file(file_path, self._bucket_name, file_name)
            print(f"Upload de {file_name} para {self._bucket_name} foi bem-sucedido.")
            return True
        except FileNotFoundError:
            print(f"O arquivo {file_path} não foi encontrado.")
            return False
        except NoCredentialsError:
            print("Credenciais não encontradas.")
            return False
        except ClientError as e:
            print(f"Ocorreu um erro: {e}")
            return False

    def delete_file_from_s3(self, file_name):
        """Exclui um arquivo do S3."""
        try:
            self._s3_client.delete_object(Bucket=self._bucket_name, Key=file_name)
            print(f"Arquivo {file_name} excluído do bucket {self._bucket_name}.")
            return True
        except ClientError as e:
            print(f"Ocorreu um erro: {e}")
            return False

    def delete_directory_from_s3(self, prefix):
        """Exclui todos os arquivos em um diretório no S3."""
        try:
            response = self._s3_client.list_objects_v2(Bucket=self._bucket_name, Prefix=prefix)

            if 'Contents' in response:
                for obj in response['Contents']:
                    self._s3_client.delete_object(Bucket=self._bucket_name, Key=obj['Key'])
                print(f"Todos os arquivos em {prefix} foram excluídos do bucket {self._bucket_name}.")
                return True
            else:
                print("Nenhum arquivo encontrado para excluir.")
                return False
        except ClientError as e:
            print(f"Ocorreu um erro: {e}")
            return False


    
    
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
