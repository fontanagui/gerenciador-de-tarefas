# GERENCIADOR DE TAREFAS

API REST para gerenciamento de usuários e tarefas, construída com **FastAPI** e **PostgreSQL**.

O projeto utiliza autenticação via JWT e uma arquitetura separada em routers, services, schemas e models.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.x-009688?style=flat-square\&logo=fastapi\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square\&logo=postgresql\&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square)

## Features

* Cadastro e gerenciamento de usuários
* Autenticação com JWT
* Hash de senhas
* Criação e gerenciamento de tarefas
* Tarefas vinculadas ao usuário autenticado
* Validação de dados com Pydantic


## Stack

* **Python** — linguagem principal
* **FastAPI** — framework da API
* **SQLAlchemy** — ORM
* **PostgreSQL** — banco de dados
* **Pydantic** — validação e schemas
* **JWT** — autenticação
* **Uvicorn** — servidor ASGI

## Estrutura

```text
app/
├── models/
│   ├── task.py
│   └── user.py
├── routers/
│   ├── auth.py
│   ├── tasks.py
│   └── users.py
├── schemas/
│   ├── auth.py
│   ├── task.py
│   └── users.py
├── services/
│   ├── task_service.py
│   └── user_service.py
├── config.py
├── database.py
├── dependencies.py
├── security.py
└── main.py
```

A aplicação utiliza uma separação entre **rotas**, **regras de negócio**, **schemas de validação** e **modelos do banco de dados**.



As rotas de tarefas utilizam o usuário autenticado para determinar quais tarefas podem ser acessadas.

## Autenticação

Após realizar o login, a API retorna um token JWT.

As senhas dos usuários são armazenadas utilizando hash.



### Requisitos

* Python 3
* PostgreSQL

### Instalação

Clone o repositório
Crie um ambiente virtual
Instale as dependências

### Env

Crie um arquivo `.env` na raiz do projeto

```env
DATABASE_URL=postgresql://seubd
SECRET_KEY=suakey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Inicie a aplicação:

```bash
uvicorn app.main:app --reload
```

A API estará disponível em:

```text
http://127.0.0.1:8000
```

## Documentação

O FastAPI disponibiliza documentação interativa automaticamente.

**Swagger UI**

```text
http://127.0.0.1:8000/docs
```

**ReDoc**

```text
http://127.0.0.1:8000/redoc
```


**Guilherme Fontana** 

Estudante de Ciência da Computação - UFPR.

## Regras de acesso e validação

O cadastro (`POST /users/`) é público e retorna `201`. As demais rotas de
usuários exigem `Authorization: Bearer <token>`. A listagem retorna somente a
própria conta; consultar, editar ou excluir outra conta retorna `403`.
Excluir a própria conta retorna `204` e remove também suas tarefas.

O login retorna `401` com a mesma mensagem para email inexistente ou senha
incorreta. Conflitos de email retornam `409`.

No cadastro, a senha deve ter entre 8 e 128 caracteres; espaços na senha são
preservados. O nome de usuário deve ter de 1 a 70 caracteres, sem contar espaços
nas extremidades. Tarefas exigem título de 1 a 150 caracteres e aceitam descrição
de até 350 caracteres.

A atualização de tarefas usa os mesmos nomes da criação:

```json
{"title": "Estudar FastAPI", "concluida": true}
```

`PUT /tasks/{task_id}` mantém a atualização parcial: campos omitidos são
preservados. `descricao: null` limpa a descrição; `title` e `concluida` não
aceitam `null`. Campos desconhecidos são rejeitados com `422`.

`GET /tasks/?offset=0&limit=50` retorna tarefas ordenadas por ID. O limite máximo
por página é 100.

`ACCESS_TOKEN_EXPIRE_MINUTES` controla a validade do token (padrão: 30, valor
positivo). Para habilitar logs SQL no desenvolvimento, defina `SQL_ECHO=true`;
o padrão é desabilitado.

## Testes

```bash
pip install -r requirements.txt
python -m pytest -q
```

Os testes usam SQLite em memória com chaves estrangeiras habilitadas e não
acessam o banco configurado no `.env`. Para validação específica do PostgreSQL,
é necessário um ambiente de integração separado.

## Frontend · Fluxo

Interface em TypeScript, CSS e Vite, com cadastro, login, busca, filtros e CRUD
completo de tarefas. Inclui painel lateral de edição, confirmação de exclusão,
transições suaves, cores animadas e layout responsivo. A preferência do sistema
por movimento reduzido é respeitada.

Requisito: Node.js 22.12+ ou 24 LTS e npm (ou pnpm).

### Desenvolvimento

Com a API rodando em `http://127.0.0.1:8000`, abra outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Acesse `http://localhost:5173/ui/`. O Vite encaminha `/api` à API FastAPI,
sem precisar habilitar CORS. Para usar outra porta da API, altere o `target`
do proxy em `frontend/vite.config.ts`.

### Servir pelo FastAPI

```bash
cd frontend
npm install
npm run build
cd ..
uvicorn app.main:app --reload
```

Acesse `http://127.0.0.1:8000/ui/`. Reinicie a API se ela já estava rodando antes
do primeiro build. O FastAPI serve os arquivos gerados em `frontend/dist`;
as rotas da API continuam nos mesmos caminhos.

O token fica no `sessionStorage` da aba, é removido ao sair e precisa ser
renovado por um novo login quando expira. O frontend consulta todas as páginas
da API para que a busca e os filtros incluam todas as tarefas do usuário.

### Iniciar frontend e backend juntos

Depois de instalar as dependências Python na `.venv` e executar `npm install`
em `frontend/`, use um único terminal na raiz do projeto:

```bash
./dev.sh
```

Abra `http://localhost:5173/ui/`. O script inicia a API na porta 8000 e o Vite
na porta 5173, ambos com recarregamento automático. `Ctrl+C` encerra os dois.
O PostgreSQL deve estar rodando e configurado no `.env`. Encerre servidores
anteriores que já estejam usando essas portas antes de executar o script.
