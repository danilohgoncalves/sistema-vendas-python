import sqlite3
import os

CAMINHO_BANCO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banco.db")


def get_conexao():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def init_db():
    """Cria as tabelas caso ainda não existam (mesma estrutura do script original)."""
    conexao = get_conexao()
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            quantidade INTEGER,
            valor_total REAL,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)
    conexao.commit()
    conexao.close()


# ---------- PRODUTOS ----------

def listar_produtos():
    conexao = get_conexao()
    produtos = conexao.execute("SELECT * FROM produtos ORDER BY nome").fetchall()
    conexao.close()
    return produtos


def obter_produto(produto_id):
    conexao = get_conexao()
    produto = conexao.execute(
        "SELECT * FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()
    conexao.close()
    return produto


def cadastrar_produto(nome, preco, estoque):
    erro = _validar_produto(nome, preco, estoque)
    if erro:
        return False, erro

    conexao = get_conexao()
    conexao.execute(
        "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)",
        (nome, preco, estoque),
    )
    conexao.commit()
    conexao.close()
    return True, None


def atualizar_produto(produto_id, nome, preco, estoque):
    erro = _validar_produto(nome, preco, estoque)
    if erro:
        return False, erro

    conexao = get_conexao()
    produto = conexao.execute(
        "SELECT id FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()
    if produto is None:
        conexao.close()
        return False, "Produto não encontrado."

    conexao.execute(
        "UPDATE produtos SET nome = ?, preco = ?, estoque = ? WHERE id = ?",
        (nome, preco, estoque, produto_id),
    )
    conexao.commit()
    conexao.close()
    return True, None


def excluir_produto(produto_id):
    conexao = get_conexao()
    produto = conexao.execute(
        "SELECT id FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()
    if produto is None:
        conexao.close()
        return False, "Produto não encontrado."

    conexao.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conexao.commit()
    conexao.close()
    return True, None


def _validar_produto(nome, preco, estoque):
    if not nome or nome.strip() == "":
        return "O nome do produto não pode ficar vazio."
    if preco is None or preco < 0:
        return "O preço não pode ser negativo."
    if estoque is None or estoque < 0:
        return "O estoque não pode ser negativo."
    return None


# ---------- ESTOQUE ----------

def entrada_estoque(produto_id, quantidade):
    if quantidade <= 0:
        return False, "A quantidade deve ser maior que zero.", None

    conexao = get_conexao()
    produto = conexao.execute(
        "SELECT estoque FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()
    if produto is None:
        conexao.close()
        return False, "Produto não encontrado.", None

    novo_estoque = produto["estoque"] + quantidade
    conexao.execute(
        "UPDATE produtos SET estoque = ? WHERE id = ?", (novo_estoque, produto_id)
    )
    conexao.commit()
    conexao.close()
    return True, None, novo_estoque


def saida_estoque(produto_id, quantidade):
    if quantidade <= 0:
        return False, "A quantidade deve ser maior que zero.", None

    conexao = get_conexao()
    produto = conexao.execute(
        "SELECT estoque FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()
    if produto is None:
        conexao.close()
        return False, "Produto não encontrado.", None

    if quantidade > produto["estoque"]:
        conexao.close()
        return False, "Estoque insuficiente.", None

    novo_estoque = produto["estoque"] - quantidade
    conexao.execute(
        "UPDATE produtos SET estoque = ? WHERE id = ?", (novo_estoque, produto_id)
    )
    conexao.commit()
    conexao.close()
    return True, None, novo_estoque


# ---------- VENDAS ----------

def registrar_venda(produto_id, quantidade):
    if quantidade <= 0:
        return False, "A quantidade deve ser maior que zero.", None

    conexao = get_conexao()
    produto = conexao.execute(
        "SELECT preco, estoque FROM produtos WHERE id = ?", (produto_id,)
    ).fetchone()
    if produto is None:
        conexao.close()
        return False, "Produto não encontrado.", None

    if quantidade > produto["estoque"]:
        conexao.close()
        return False, "Estoque insuficiente.", None

    valor_total = produto["preco"] * quantidade
    novo_estoque = produto["estoque"] - quantidade

    conexao.execute(
        "INSERT INTO vendas (produto_id, quantidade, valor_total) VALUES (?, ?, ?)",
        (produto_id, quantidade, valor_total),
    )
    conexao.execute(
        "UPDATE produtos SET estoque = ? WHERE id = ?", (novo_estoque, produto_id)
    )
    conexao.commit()
    conexao.close()
    return True, None, valor_total


def listar_vendas():
    conexao = get_conexao()
    vendas = conexao.execute("""
        SELECT vendas.id, produtos.nome, vendas.quantidade, vendas.valor_total
        FROM vendas
        JOIN produtos ON vendas.produto_id = produtos.id
        ORDER BY vendas.id DESC
    """).fetchall()
    conexao.close()
    return vendas


def ver_faturamento():
    conexao = get_conexao()
    total = conexao.execute("SELECT SUM(valor_total) AS total FROM vendas").fetchone()["total"]
    conexao.close()
    return total or 0
