from flask import Flask, render_template, request, redirect, url_for, flash, session
import database as db

app = Flask(__name__)
app.secret_key = "troque-esta-chave-em-producao"


@app.before_request
def garantir_banco():
    db.init_db()

@app.before_request
def exigir_login():
    rotas_livres = ["login", "cadastro", "static"]

    if request.endpoint not in rotas_livres and "usuario_id" not in session:
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da conta.", "sucesso")
    return redirect(url_for("login"))    
@app.route("/cadastro", methods=["GET", "POST"])

def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")

        if not nome or not email or not senha:
            flash("Preencha todos os campos.", "erro")
            return render_template("cadastro.html")

        sucesso, erro = db.cadastrar_usuario(nome, email, senha)

        if sucesso:
            flash("Cadastro realizado com sucesso! Faça login.", "sucesso")
            return redirect(url_for("login"))

        flash(erro, "erro")

    return render_template("cadastro.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "")

        usuario = db.buscar_usuario_por_email(email)

        if usuario and db.verificar_senha(senha, usuario["senha"]):
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]

            flash("Login realizado com sucesso.", "sucesso")
            return redirect(url_for("index"))

        flash("E-mail ou senha inválidos.", "erro")

    return render_template("login.html")

@app.route("/")
def index():
    produtos = db.listar_produtos(session["usuario_id"])    
    total_produtos = len(produtos)
    estoque_baixo = [p for p in produtos if p["estoque"] <= 5]
    faturamento = db.ver_faturamento(session["usuario_id"])
    return render_template(
        "index.html",
        total_produtos=total_produtos,
        estoque_baixo=estoque_baixo,
        faturamento=faturamento,
    )


# ---------- PRODUTOS ----------

@app.route("/produtos")
def produtos():
    lista = db.listar_produtos(session["usuario_id"])
    return render_template("produtos.html", produtos=lista)


@app.route("/produtos/novo", methods=["GET", "POST"])
def produto_novo():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        preco_raw = request.form.get("preco", "")
        estoque_raw = request.form.get("estoque", "")

        preco, erro_preco = _parse_float(preco_raw)
        estoque, erro_estoque = _parse_int(estoque_raw)

        if erro_preco:
            flash(erro_preco, "erro")
        elif erro_estoque:
            flash(erro_estoque, "erro")
        else:
            ok, erro = db.cadastrar_produto(
                nome,
                preco,
                estoque,
                session["usuario_id"]
            )

            if ok:
                flash("Produto cadastrado com sucesso.", "sucesso")
                return redirect(url_for("produtos"))

            flash(erro, "erro")

    return render_template("produto_form.html", produto=None)


@app.route("/produtos/<int:produto_id>/editar", methods=["GET", "POST"])
def produto_editar(produto_id):
    produto = db.obter_produto(produto_id, session["usuario_id"])
    if produto is None:
        flash("Produto não encontrado.", "erro")
        return redirect(url_for("produtos"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        preco_raw = request.form.get("preco", "")
        estoque_raw = request.form.get("estoque", "")

        preco, erro_preco = _parse_float(preco_raw)
        estoque, erro_estoque = _parse_int(estoque_raw)

        if erro_preco:
            flash(erro_preco, "erro")
        elif erro_estoque:
            flash(erro_estoque, "erro")
        else:
            ok, erro = db.atualizar_produto(
                produto_id,
                nome,
                preco,
                estoque,
                session["usuario_id"]
            )

            if ok:
                flash("Produto atualizado com sucesso.", "sucesso")
                return redirect(url_for("produtos"))

            flash(erro, "erro")
            produto = db.obter_produto(produto_id, session["usuario_id"])

    return render_template("produto_form.html", produto=produto)


@app.route("/produtos/<int:produto_id>/excluir", methods=["POST"])
def produto_excluir(produto_id):
    ok, erro = db.excluir_produto(
        produto_id,
        session["usuario_id"]
    )

    flash(
        "Produto excluído com sucesso." if ok else erro,
        "sucesso" if ok else "erro"
    )

    return redirect(url_for("produtos"))


# ---------- ESTOQUE ----------

@app.route("/estoque", methods=["GET", "POST"])
def estoque():
    if request.method == "POST":
        produto_id, erro_id = _parse_int(
            request.form.get("produto_id", "")
        )

        quantidade, erro_qtd = _parse_int(
            request.form.get("quantidade", "")
        )

        tipo = request.form.get("tipo")

        if erro_id or produto_id is None:
            flash("Selecione um produto válido.", "erro")

        elif erro_qtd or quantidade is None:
            flash("Digite uma quantidade válida.", "erro")

        elif tipo == "entrada":
            ok, erro, novo_estoque = db.entrada_estoque(
                produto_id,
                quantidade,
                session["usuario_id"]
            )

            flash(
                f"Entrada registrada! Novo estoque: {novo_estoque}"
                if ok else erro,
                "sucesso" if ok else "erro"
            )

        elif tipo == "saida":
            ok, erro, novo_estoque = db.saida_estoque(
                produto_id,
                quantidade,
                session["usuario_id"]
            )

            flash(
                f"Saída registrada! Novo estoque: {novo_estoque}"
                if ok else erro,
                "sucesso" if ok else "erro"
            )

        return redirect(url_for("estoque"))

    produtos = db.listar_produtos(session["usuario_id"])

    return render_template("estoque.html", produtos=produtos)
# ---------- VENDAS ----------

@app.route("/vendas", methods=["GET", "POST"])
def vendas():
    if request.method == "POST":
        produto_id, erro_id = _parse_int(request.form.get("produto_id", ""))
        quantidade, erro_qtd = _parse_int(request.form.get("quantidade", ""))

        if erro_id or produto_id is None:
            flash("Selecione um produto válido.", "erro")
        elif erro_qtd or quantidade is None:
            flash("Digite uma quantidade válida.", "erro")
        else:
            ok, erro, valor_total = db.registrar_venda(
    produto_id,
    quantidade,
    session["usuario_id"]
)
            if ok:
                flash(f"Venda registrada! Valor total: R$ {valor_total:.2f}", "sucesso")
            else:
                flash(erro, "erro")

        return redirect(url_for("vendas"))

    produtos = db.listar_produtos(session["usuario_id"])
    lista_vendas = db.listar_vendas(session["usuario_id"])
    faturamento = db.ver_faturamento(session["usuario_id"])    
    return render_template(
        "vendas.html", produtos=produtos, vendas=lista_vendas, faturamento=faturamento
    )


# ---------- helpers ----------

def _parse_float(valor):
    try:
        return float(valor), None
    except (TypeError, ValueError):
        return None, "Digite um valor numérico válido."


def _parse_int(valor):
    try:
        return int(valor), None
    except (TypeError, ValueError):
        return None, "Digite um número inteiro válido."


if __name__ == "__main__":
    app.run(debug=True)
