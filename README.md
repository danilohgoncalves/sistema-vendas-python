Sistema de Vendas

Aplicação web para gerenciamento de produtos, controle de estoque e registro de vendas, desenvolvida com Python e Flask.

O projeto simula operações comuns de um comércio, permitindo cadastrar produtos, controlar o estoque, registrar vendas e gerenciar o acesso de usuários através de uma interface web.

Funcionalidades
Cadastro de usuários
Login e autenticação de usuários
Cadastro de produtos
Listagem de produtos
Edição de produtos
Exclusão de produtos
Entrada e saída de estoque
Registro de vendas
Atualização automática do estoque após uma venda
Consulta de vendas
Cálculo do faturamento
Mensagens de feedback para o usuário
Tecnologias
Python
Flask
SQLite
SQL
HTML
CSS
Jinja2
Werkzeug
Estrutura
sistemas_vendas/
├── app.py
├── database.py
├── banco.db
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── cadastro.html
│   ├── produto_form.html
│   ├── produtos.html
│   ├── estoque.html
│   └── vendas.html
└── README.md
Como executar

Clone o repositório:

git clone https://github.com/danilohgoncalves/sistema-vendas-python.git

Entre na pasta:

cd sistema-vendas-python

Instale o Flask:

pip install flask

Execute a aplicação:

python app.py

Acesse no navegador:

http://127.0.0.1:5000
Sobre o projeto

Este projeto foi desenvolvido como parte dos meus estudos em Desenvolvimento de Sistemas, com o objetivo de praticar a construção de uma aplicação web utilizando backend em Python, banco de dados SQLite e integração com páginas HTML.

Durante o desenvolvimento, trabalhei com:

Operações CRUD
Rotas e métodos HTTP no Flask
Templates com Jinja2
Manipulação de banco de dados SQLite
Autenticação e gerenciamento de sessões
Hash de senhas
Regras de negócio para estoque e vendas
Organização de uma aplicação web em camadas

O projeto também representa uma evolução prática dos meus conhecimentos em backend, banco de dados e desenvolvimento de sistemas.

Próximos passos
Adicionar relatórios de vendas
Melhorar o dashboard
Implementar diferentes níveis de acesso
Adicionar validações mais completas
Melhorar a experiência visual da aplicação
Evoluir a aplicação para um ambiente de produção
