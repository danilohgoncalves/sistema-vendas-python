import sqlite3
import os

CAMINHO_BANCO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "banco.db")


def get_conexao():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def init_db():
    """Cria as tabelas caso ainda não existam."""
    conexao = get_conexao()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL,
            usuario_id INTEGER
        )
    """)

    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN usuario_id INTEGER")
    except sqlite3.OperationalError:
        pass

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

from werkzeug.security import generate_password_hash, check_password_hash


def cadastrar_usuario(nome, email, senha):
    senha_hash = generate_password_hash(senha)

    conexao = get_conexao()

    try:
        conexao.execute(
            """
            INSERT INTO usuarios (nome, email, senha)
            VALUES (?, ?, ?)
            """,
            (nome, email, senha_hash),
        )
        conexao.commit()
        return True, None

    except sqlite3.IntegrityError:
        return False, "Este e-mail já está cadastrado."

    finally:
        conexao.close()


def buscar_usuario_por_email(email):
    conexao = get_conexao()

    usuario = conexao.execute(
        "SELECT * FROM usuarios WHERE email = ?",
        (email,),
    ).fetchone()

    conexao.close()
    return usuario


def verificar_senha(senha_digitada, senha_hash):
    return check_password_hash(senha_hash, senha_digitada)
# ---------- PRODUTOS ----------

def listar_produtos(usuario_id):
    conexao = get_conexao()

    produtos = conexao.execute(
        """
        SELECT * FROM produtos
        WHERE usuario_id = ?
        ORDER BY nome
        """,
        (usuario_id,)
    ).fetchall()

    conexao.close()
    return produtos


def obter_produto(produto_id, usuario_id):
    conexao = get_conexao()

    produto = conexao.execute(
        """
        SELECT * FROM produtos
        WHERE id = ? AND usuario_id = ?
        """,
        (produto_id, usuario_id)
    ).fetchone()

    conexao.close()
    return produto

def cadastrar_produto(nome, preco, estoque, usuario_id):
    erro = _validar_produto(nome, preco, estoque)

    if erro:
        return False, erro

    conexao = get_conexao()

    conexao.execute(
        """
        INSERT INTO produtos (nome, preco, estoque, usuario_id)
        VALUES (?, ?, ?, ?)
        """,
        (nome, preco, estoque, usuario_id),
    )

    conexao.commit()
    conexao.close()

    return True, None


def atualizar_produto(produto_id, nome, preco, estoque, usuario_id):
    erro = _validar_produto(nome, preco, estoque)

    if erro:
        return False, erro

    conexao = get_conexao()

    produto = conexao.execute(
        """
        SELECT id FROM produtos
        WHERE id = ? AND usuario_id = ?
        """,
        (produto_id, usuario_id)
    ).fetchone()

    if produto is None:
        conexao.close()
        return False, "Produto não encontrado."

    conexao.execute(
        """
        UPDATE produtos
        SET nome = ?, preco = ?, estoque = ?
        WHERE id = ? AND usuario_id = ?
        """,
        (nome, preco, estoque, produto_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    return True, None


def excluir_produto(produto_id, usuario_id):
    conexao = get_conexao()

    produto = conexao.execute(
        """
        SELECT id FROM produtos
        WHERE id = ? AND usuario_id = ?
        """,
        (produto_id, usuario_id)
    ).fetchone()

    if produto is None:
        conexao.close()
        return False, "Produto não encontrado."

    conexao.execute(
        """
        DELETE FROM produtos
        WHERE id = ? AND usuario_id = ?
        """,
        (produto_id, usuario_id)
    )

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

def entrada_estoque(produto_id, quantidade, usuario_id):
    if quantidade <= 0:
        return False, "A quantidade deve ser maior que zero.", None

    conexao = get_conexao()

    produto = conexao.execute(
        """
        SELECT estoque FROM produtos
        WHERE id = ? AND usuario_id = ?
        """,
        (produto_id, usuario_id)
    ).fetchone()

    if produto is None:
        conexao.close()
        return False, "Produto não encontrado.", None

    novo_estoque = produto["estoque"] + quantidade

    conexao.execute(
        """
        UPDATE produtos
        SET estoque = ?
        WHERE id = ? AND usuario_id = ?
        """,
        (novo_estoque, produto_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    return True, None, novo_estoque


def saida_estoque(produto_id, quantidade, usuario_id):
    if quantidade <= 0:
        return False, "A quantidade deve ser maior que zero.", None

    conexao = get_conexao()

    produto = conexao.execute(
        """
        SELECT estoque FROM produtos
        WHERE id = ? AND usuario_id = ?
        """,
        (produto_id, usuario_id)
    ).fetchone()

    if produto is None:
        conexao.close()
        return False, "Produto não encontrado.", None

    if quantidade > produto["estoque"]:
        conexao.close()
        return False, "Estoque insuficiente.", None

    novo_estoque = produto["estoque"] - quantidade

    conexao.execute(
        """
        UPDATE produtos
        SET estoque = ?
        WHERE id = ? AND usuario_id = ?
        """,
        (novo_estoque, produto_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    return True, None, novo_estoque

# ---------- VENDAS ----------

def registrar_venda(produto_id, quantidade, usuario_id):
    if quantidade <= 0:
        return False, "A quantidade deve ser maior que zero.", None

    conexao = get_conexao()

    produto = conexao.execute(
        """
        SELECT preco, estoque
        FROM produtos
        WHERE id = ? AND usuario_id = ?
        """,
        (produto_id, usuario_id)
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
        """
        INSERT INTO vendas (produto_id, quantidade, valor_total)
        VALUES (?, ?, ?)
        """,
        (produto_id, quantidade, valor_total),
    )

    conexao.execute(
        """
        UPDATE produtos
        SET estoque = ?
        WHERE id = ? AND usuario_id = ?
        """,
        (novo_estoque, produto_id, usuario_id)
    )

    conexao.commit()
    conexao.close()

    return True, None, valor_total


def listar_vendas(usuario_id):
    conexao = get_conexao()

    vendas = conexao.execute(
        """
        SELECT produtos.nome,
               vendas.quantidade,
               vendas.valor_total
        FROM vendas
        JOIN produtos
            ON vendas.produto_id = produtos.id
        WHERE produtos.usuario_id = ?
        ORDER BY vendas.id DESC
        """,
        (usuario_id,)
    ).fetchall()

    conexao.close()
    return vendas


def ver_faturamento(usuario_id):
    conexao = get_conexao()

    total = conexao.execute(
        """
        SELECT SUM(vendas.valor_total) AS total
        FROM vendas
        JOIN produtos
            ON vendas.produto_id = produtos.id
        WHERE produtos.usuario_id = ?
        """,
        (usuario_id,)
    ).fetchone()["total"]

    conexao.close()

    return total or 0
