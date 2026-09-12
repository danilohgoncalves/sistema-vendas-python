Aplicação web para gerenciamento de produtos, controle de estoque e registro de vendas, desenvolvida com Python e Flask.

O projeto simula algumas operações comuns de um comércio, permitindo cadastrar produtos, atualizar informações, controlar quantidades em estoque e registrar vendas através de uma interface web.

## Funcionalidades

- Cadastro de produtos
- Listagem de produtos
- Edição de produtos
- Exclusão de produtos
- Entrada e saída de estoque
- Registro de vendas
- Atualização do estoque após uma venda
- Consulta de vendas
- Cálculo do faturamento

## Tecnologias

- Python
- Flask
- SQLite
- SQL
- HTML
- CSS
- Jinja2

## Estrutura

```text
sistemas_vendas/
├── app.py
├── database.py
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── produto_form.html
│   ├── produtos.html
│   ├── estoque.html
│   └── vendas.html
└── README.md
```

## Como executar

Clone o repositório:

```bash
git clone https://github.com/danilohgoncalves/sistema-vendas-python.git
```

Entre na pasta:

```bash
cd sistema-vendas-python
```

Instale o Flask:

```bash
pip install flask
```

Execute a aplicação:

```bash
python app.py
```

Acesse no navegador:

```text
http://127.0.0.1:5000
```

## Sobre o projeto

Este projeto foi desenvolvido como parte dos meus estudos em desenvolvimento de sistemas, com o objetivo de praticar a construção de uma aplicação web utilizando backend em Python, banco de dados SQLite e integração com páginas HTML.

Durante o desenvolvimento, trabalhei com operações CRUD, manipulação de banco de dados, rotas Flask, templates Jinja2 e regras de negócio relacionadas ao controle de estoque e vendas.

## Próximos passos

- Implementar autenticação de usuários
- Adicionar relatórios de vendas
- Melhorar o dashboard
- Adicionar validações e mensagens mais completas
- Evoluir a aplicação para um ambiente de produção
