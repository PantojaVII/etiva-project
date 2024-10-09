### Tabela `User`

| **Nome do Campo**     | **Tipo de Dados**         | **Descrição**                                      |
|-----------------------|---------------------------|----------------------------------------------------|
| `id`                  | `UUID` / `AutoField`      | Chave primária (gerada automaticamente pelo Django) |
| `username`            | `VARCHAR(255)`            | Nome de usuário único (indexado)                   |
| `email`               | `VARCHAR(255)`            | E-mail único (indexado)                            |
| `is_verified`         | `BOOLEAN`                 | Indica se o e-mail foi verificado (`default=False`) |
| `is_active`           | `BOOLEAN`                 | Indica se o usuário está ativo (`default=True`)    |
| `is_staff`            | `BOOLEAN`                 | Indica se o usuário tem permissão de administrador (`default=False`) |
| `created_at`          | `TIMESTAMP`               | Data de criação (`auto_now_add=True`)              |
| `updated_at`          | `TIMESTAMP`               | Data de última atualização (`auto_now=True`)       |
| `auth_method`         | `VARCHAR(20)`             | Método de autenticação escolhido (`default='seek'`) |
| `password`            | `VARCHAR(128)`            | Senha criptografada pelo Django                    |

#### Índices e Restrições
- `username` e `email` são únicos e indexados.
- O campo `auth_method` utiliza as opções definidas em `AUTH_METHOD_CHOICES`.

---

### Tabela `Profile`

| **Nome do Campo**     | **Tipo de Dados**         | **Descrição**                                      |
|-----------------------|---------------------------|----------------------------------------------------|
| `id`                  | `AutoField`               | Chave primária (gerada automaticamente pelo Django) |
| `user_id`             | `ForeignKey (UUID)`       | Chave estrangeira que referencia `User` (`OneToOne`) |
| `first_name`          | `VARCHAR(30)`             | Primeiro nome do usuário (`null=True`)             |
| `last_name`           | `VARCHAR(30)`             | Último nome do usuário (`blank=True`, `null=True`)  |
| `picture`             | `VARCHAR`                 | URL ou caminho da imagem de perfil (`blank=True`, `null=True`) |
| `phone_number`        | `VARCHAR(15)`             | Número de telefone (`blank=True`, `null=True`)     |
| `date_of_birth`       | `DATE`                    | Data de nascimento (`blank=True`, `null=True`)     |

### Relação Entre as Tabelas
- A tabela `Profile` possui uma relação `OneToOne` com a tabela `User` por meio do campo `user_id`.

### Observações

- A tabela `User` não precisa armazenar tokens JWT, pois a autenticação é gerenciada diretamente pelo mecanismo JWT.
