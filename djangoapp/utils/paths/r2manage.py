import boto3
from django.http import HttpResponse
import os
import botocore


class R2FileManager:
    def __init__(self):
        self.s3_client = self.get_r2_client()
        self.r2_bucket_name = os.getenv('BUCKET_NAME')
    
    def get_r2_client(self):
        s3 = boto3.client(
            service_name=os.getenv('SERVICE_NAME'),
            endpoint_url=os.getenv('ENDPOINT_URL'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('REGION_NAME'),
            
        )
        return s3
    
    def get_image_data(self, request, image_url):
        print('----------')
        print(image_url)
        
        try:
            # Use o cliente S3 para baixar a imagem do R2
            response = self.s3_client.get_object(Bucket=self.r2_bucket_name, Key=image_url)
            image_data = response['Body'].read()
            
            # Criar uma resposta HTTP com os dados da imagem
            http_response = HttpResponse(image_data, content_type='image/jpeg')  # ou 'image/png', dependendo do formato
            http_response['Content-Length'] = len(image_data)
            return http_response

        except botocore.exceptions.ClientError as e:
            print(f"Erro ao obter imagem: {e}")
            return HttpResponse(status=500)

    def generate_presigned_url(self, image_key, expiration=3600):
        """Gera uma URL assinada para acessar a imagem."""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.r2_bucket_name, 'Key': image_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            print(f"Erro ao gerar URL assinada: {e}")
            return None
    
    def upload_file(self, file, path_to_file):
        try:
            # Certifique-se de que o arquivo seja um file-like object, por exemplo, abrindo o arquivo se ele for um caminho.
            if isinstance(file, str):  # Se o 'file' for uma string (caminho do arquivo), abra o arquivo
                with open(file, 'rb') as file_obj:
                    self.s3_client.upload_fileobj(file_obj, self.r2_bucket_name, path_to_file)
            else:
                # Se o 'file' já for um file-like object
                self.s3_client.upload_fileobj(file, self.r2_bucket_name, path_to_file)
            
            print("Arquivo enviado com sucesso para o R2 da Cloudflare.")
            return f"{path_to_file}"
        except Exception as e:
            print(f"Erro ao enviar arquivo para o R2 da Cloudflare via S3: {e}")
    
    def delete_file(self, path_to_file):
        try:
            self.s3_client.delete_object(Bucket=self.r2_bucket_name, Key=path_to_file)
            print("Arquivo deletado com sucesso do R2 da Cloudflare.")
        except Exception as e:
            print(f"Erro ao deletar arquivo do R2 da Cloudflare via S3: {e}")
    
    def delete_directory(self, directory_path):
        try:
            objects_to_delete = []
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.r2_bucket_name, Prefix=directory_path)
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        objects_to_delete.append({'Key': obj['Key']})
            
            if objects_to_delete:
                response = self.s3_client.delete_objects(Bucket=self.r2_bucket_name, Delete={'Objects': objects_to_delete})
                if 'Errors' in response:
                    for error in response['Errors']:
                        print(f"Erro ao excluir objeto {error['Key']}: {error['Code']}")
                else:
                    print("Diretório excluído com sucesso do R2 da Cloudflare.")
            else:
                print("Nenhum objeto encontrado no diretório para excluir.")
        except Exception as e:
            print(f"Erro ao excluir diretório do R2 da Cloudflare via S3: {e}")

