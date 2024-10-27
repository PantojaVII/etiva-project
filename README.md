# Projeto Base em Docker e Django

Este repositório fornece uma base para iniciar um projeto utilizando **Docker** e **Django**, incluindo um sistema de API com gerenciamento de usuários. Ideal para desenvolvedores que desejam acelerar o desenvolvimento de suas aplicações.

## Instalação

### 🗝️ Gere os Certificados Iniciais

Para garantir a segurança da sua aplicação, você precisa gerar certificados SSL. Siga os passos abaixo:

1. Crie um diretório na raiz do projeto chamado `certs`.

2. Utilize o comando a seguir para criar as chaves SSL:

    ```bash
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem
    ```

   Responda `ENTER` para as perguntas que aparecerem, pois você poderá alterar os certificados posteriormente.

3. O comando acima gerará duas chaves não assinadas dentro do diretório `certs`. Você poderá substituí-las por certificados assinados adquiridos em serviços como Cloudflare ou outros provedores.

### 🐋 Iniciando o Projeto

1. Copie o arquivo `env-example` do diretório `dotenv_files` para a raiz do projeto e renomeie para `.env`.

2. Edite o arquivo `.env` e altere as variáveis conforme necessário. **Importante:** Não altere a variável `POSTGRES_HOST`, pois isso é crítico para a configuração do banco de dados.

3. Para iniciar a aplicação, execute o seguinte comando:

    ```bash
    docker compose up
    ```

   Ou, se preferir rodar em segundo plano (detached):

    ```bash
    docker compose up -d
    ```

### 🚀 Funcionalidades

- **API RESTful:** Sistema de API completo para gerenciar usuários e autenticação.
- **Gerenciamento de Usuários:** Criação, edição e remoção de usuários através da API.
- **Docker:** Contêineres para isolamento e fácil gerenciamento de dependências.

### 🛠️ Tecnologias Utilizadas

- **Django:** Framework web em Python.
- **Docker:** Plataforma para desenvolver, enviar e executar aplicações em contêineres.
- **PostgreSQL:** Sistema de gerenciamento de banco de dados relacional.

### 📚 Como Contribuir

Sinta-se à vontade para contribuir para este projeto. Siga as etapas:

1. Faça um fork deste repositório.
2. Crie uma nova branch (`git checkout -b feature/YourFeature`).
3. Faça suas alterações e commit (`git commit -m 'Add some feature'`).
4. Envie para o repositório remoto (`git push origin feature/YourFeature`).
5. Abra um Pull Request.
