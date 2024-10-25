# services.py
from openai import OpenAI
import requests
from io import BytesIO
import replicate
from datetime import datetime

def pathImage(pk_hash, image):
 return f"users/{pk_hash}/creatus_cortex/images/{image}"

def generate_image(prompt):
    openai = OpenAI()
    model = "dall-e-3"
    
    # Gerar uma imagem com o modelo DALL·E 3
    response = openai.images.generate(
        prompt=prompt, 
        model=model,
        size="1024x1024",
        quality="standard",
        n=1
    )

    # Obter o URL da imagem gerada
    image_url = response.data[0].url
    image_name = image_url.split("/")[-1]

    # Baixar a imagem usando requests
    image_response = requests.get(image_url)

    # Verifique se a imagem foi baixada corretamente
    if image_response.status_code == 200:
        # Convertendo o conteúdo da imagem para um objeto file-like
        image_file = BytesIO(image_response.content)
        image_file.seek(0)  # Garantir que o ponteiro esteja no início do arquivo
        return image_name, image_file, "success"
    else:
        raise Exception('Error downloading the image')

def generate_image_stable_diffusion(prompt, num_images=1, width=1024, height=1024, guidance_scale=7.5, apply_watermark=True, negative_prompt="", prompt_strength=0.8):
    try:
        # Define os parâmetros de entrada
        input = {
            "width": width,
            "height": height,
            "prompt": prompt,
            "scheduler": "KarrasDPM",
            "num_outputs": num_images,
            "guidance_scale": guidance_scale,
            "apply_watermark": apply_watermark,
            "negative_prompt": negative_prompt,
            "prompt_strength": prompt_strength,
            "num_inference_steps": 20,
        }

        output = replicate.run(
            "datacte/proteus-v0.2:06775cd262843edbde5abab958abdbb65a0a6b58ca301c9fd78fa55c775fc019",
            input=input, safety_checker=None
        )

        # output deve ser uma lista com as URLs das imagens geradas
        image_urls = output  # Assume que o output é uma lista de URLs

        image_names = []
        image_files = []

        for image_url in image_urls:
            # Baixar a imagem a partir da URL
            image_response = requests.get(image_url)

            # Verificar se o download foi bem-sucedido
            if image_response.status_code != 200:
                raise Exception(f"Erro ao baixar a imagem: {image_url}")

            # Converte o conteúdo da imagem para um arquivo binário em memória
            image_file = BytesIO(image_response.content)
            
            image_name = image_url.split("/")[-1]

            # Obtém a data e hora atuais, incluindo milissegundos
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Formato: AAAAMMDD_HHMMSS_milissegundos

            # Atualiza o nome da imagem para incluir a data, hora e milissegundos
            image_name_with_timestamp = f"{timestamp}_{image_name}"
            image_names.append(image_name_with_timestamp)
            image_files.append(image_file)

        return image_names, image_files, "success"
    
    except Exception as e:
        # Se ocorrer um erro, você pode retornar o erro ou um status de falha
        return None, None, f"Erro: {str(e)}"