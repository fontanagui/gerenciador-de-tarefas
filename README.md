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

## Authentication

Após realizar o login, a API retorna um token JWT.

As senhas dos usuários são armazenadas utilizando hash.



### Requisitos

* Python 3
* PostgreSQL

### Installation

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

## Documentation

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
