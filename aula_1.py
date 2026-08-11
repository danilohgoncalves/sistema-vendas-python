import sqlite3

def cadastrar_produto():
    nome = input("Nome do produto: ")
    if nome.strip() == "":
        print("O nome do produto não pode ficar vazio!")
        return
    try:
        preco = float(input("Preço: "))
    except ValueError:
        print("Digite um preço válido!")
        return


    try:
        estoque = int(input("Estoque: "))
    except ValueError:
        print("Digite um estoque valido!")
        return

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    if preco < 0:
        print("O preço não pode ser negativo!")
        return

    if estoque < 0:
        print("O estoque não pode ser negativo!")
        return
    cursor.execute("""
    INSERT INTO produtos (nome, preco, estoque)
    VALUES (?, ?, ?)
    """, (nome, preco, estoque))

    conexao.commit()
    conexao.close()

    print("Produto cadastrado com sucesso!")

def listar_produtos():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    for produto in produtos:
        print(f"\nID: {produto[0]}")
        print(f"Produto: {produto[1]}")
        print(f"Preço: R$ {produto[2]:.2f}")
        print(f"Estoque: {produto[3]}")

    conexao.close()

def atualizar_produto():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    id_produto = int(input("ID do produto: "))

    cursor.execute(
        "SELECT id FROM produtos WHERE id = ?",
        (id_produto,)
    )

    produto = cursor.fetchone()

    if produto is None:
        print("Produto não encontrado!")
        conexao.close()
        return

    nome = input("Novo nome: ")

    try:
        preco = float(input("Novo preço: "))
    except ValueError:
        print("Digite um preço válido!")
        return

    if preco < 0:
        print("O preço não pode ser negativo!")
        return

    try:
        estoque = int(input("Novo estoque: "))
    except ValueError:
        print("Digite um estoque válido!")
        return

    if estoque < 0:
        print("O estoque não pode ser negativo!")
        return

    cursor.execute("""
    UPDATE produtos
    SET nome = ?, preco = ?, estoque = ?
    WHERE id = ?
    """, (nome, preco, estoque, id_produto))

    conexao.commit()
    conexao.close()

    print("Produto atualizado com sucesso!")

def excluir_produto():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    id_produto = int(input("ID do produto que deseja excluir: "))

    cursor.execute(
        "SELECT id FROM produtos WHERE id = ?",
        (id_produto,)
    )

    produto = cursor.fetchone()

    if produto is None:
        print("Produto não encontrado!")
        conexao.close()
        return

    cursor.execute(
        "DELETE FROM produtos WHERE id = ?",
        (id_produto,)
    )

    conexao.commit()
    conexao.close()

    print("Produto excluído com sucesso!")

def registrar_venda():
    produto_id = int(input("ID do produto: "))
    quantidade = int(input("Quantidade vendida: "))

    if quantidade <= 0:
        print("A quantidade deve ser maior que zero!")
        return

    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT preco, estoque FROM produtos WHERE id = ?",
        (produto_id,)
    )

    produto = cursor.fetchone()

    if produto is None:
        print("Produto não encontrado!")
        conexao.close()
        return

    preco = produto[0]
    estoque = produto[1]

    if quantidade > estoque:
        print("Estoque insuficiente!")
        conexao.close()
        return

    valor_total = preco * quantidade
    novo_estoque = estoque - quantidade

    cursor.execute("""
    INSERT INTO vendas (produto_id, quantidade, valor_total)
    VALUES (?, ?, ?)
    """, (produto_id, quantidade, valor_total))

    cursor.execute("""
    UPDATE produtos
    SET estoque = ?
    WHERE id = ?
    """, (novo_estoque, produto_id))

    conexao.commit()

    print("\nVenda registrada com sucesso!")
    print(f"Valor total: R$ {valor_total:.2f}")
    print(f"Estoque restante: {novo_estoque}")

    conexao.close()

def criar_tabela_vendas ():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        quantidade INTEGER,
        valor_total REAL
    )
    """)
    conexao.commit()
    conexao.close()

def ver_faturamento ():
    conexao =sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    cursor.execute ("SELECT SUM (valor_total) FROM vendas")
    total = cursor.fetchone() [0]
    if total is None:
        total = 0
    print (f"\nFaturamento total: R$ {total:.2f}")
    conexao.close()

def listar_vendas ():
    conexao =sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    
    cursor.execute("""
        SELECT produtos.nome,
               vendas.quantidade,
               vendas.valor_total
        FROM vendas
        JOIN produtos
        ON vendas.produto_id = produtos.id
    """)

    vendas = cursor.fetchall()

    if len(vendas) == 0:
        print("\nNenhuma venda cadastrada.")
    else:
        print("\n===== LISTA DE VENDAS =====")

        for venda in vendas:
            print(f"Produto: {venda[0]}")
            print(f"Quantidade: {venda[1]}")
            print(f"Valor Total: R$ {venda[2]:.2f}")
            print("-" * 30)

    conexao.close()

def entrada_estoque():
    conexao = sqlite3.connect("banco.db")
    cursor = conexao.cursor()

    id_produto = int(input("ID do produto: "))
    quantidade = int(input("Quantidade de entrada: "))

    if quantidade <= 0:
        print("A quantidade deve ser maior que zero!")
        conexao.close()
        return

    cursor.execute(
        "SELECT estoque FROM produtos WHERE id = ?",
        (id_produto,)
    )

    produto = cursor.fetchone()

    if produto is None:
        print("Produto não encontrado!")
        conexao.close()
        return

    estoque_atual = produto[0]
    novo_estoque = estoque_atual + quantidade

    cursor.execute("""
        UPDATE produtos
        SET estoque = ?
        WHERE id = ?
    """, (novo_estoque, id_produto))

    conexao.commit()
    conexao.close()

    print(f"Entrada registrada! Novo estoque: {novo_estoque}")

def saida_estoque():
    conexao =sqlite3.connect("banco.db")
    cursor = conexao.cursor()
    
    id_produto = int(input("ID do produto: "))
    quantidade = int(input("Quantidade de saida: "))

    if quantidade <= 0:
        print("A quantidade deve ser maior que zero!")
        conexao.close()
        return
    cursor.execute(
        "SELECT estoque FROM produtos WHERE id = ?",
        (id_produto,)
        )
    produto = cursor.fetchone()
    if produto is None:
            print("Produto não encontrado!")
            conexao.close()
            return
    estoque_atual = produto[0]

    if quantidade > estoque_atual:
        print("Estoque insuficiente!")
        conexao.close()
        return
    
    novo_estoque = estoque_atual - quantidade
    cursor.execute("""
            UPDATE produtos
            SET estoque = ?
            WHERE id = ?
        """, (novo_estoque, id_produto))
    conexao.commit()
    conexao.close()
    
    print(f"Saida Registrada! Novo estoque: {novo_estoque}")

while True: 
    print("\n=== SISTEMA DE VENDAS ===")
    print("1 - Cadastrar produto")
    print("2 - Listar produtos")
    print("3 - Atualizar produto")
    print("4 - Excluir produto")
    print("5 - Registrar Venda")
    print("6 - Entrada de Estoque")
    print("7 - Saída de Estoque")
    print("8 - Ver faturamento")
    print("9 - listar_vendas")
    print("0 - Sair")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        cadastrar_produto()

    elif opcao == "2":
        listar_produtos()

    elif opcao == "3":
        atualizar_produto()

    elif opcao == "4":
        excluir_produto()

    elif opcao == "5":
        registrar_venda()
        
    elif opcao =="6":
        entrada_estoque()

    elif opcao =="7":
        saida_estoque()

    elif opcao == "8":
        ver_faturamento()

    elif opcao == "9":
        listar_vendas()
    
    elif opcao == "0":
        print("Você saiu")
        break
    
    else:
        print("Opção inválida!")