from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import Database
from datetime import datetime
import json

app = Flask(__name__)
db = Database()

# Inicializar banco de dados
db.criar_tabelas()

@app.route('/')
def index():
    return render_template('index.html')

# ============ API PRODUTOS ============
@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    produtos = db.listar_produtos()
    return jsonify(produtos)

@app.route('/api/produtos', methods=['POST'])
def adicionar_produto():
    dados = request.json
    sucesso = db.adicionar_produto(
        dados['nome'],
        dados['descricao'],
        float(dados['preco']),
        int(dados['quantidade'])
    )
    return jsonify({'sucesso': sucesso})

@app.route('/api/produtos/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    dados = request.json
    sucesso = db.atualizar_produto(
        id,
        dados['nome'],
        dados['descricao'],
        float(dados['preco']),
        int(dados['quantidade'])
    )
    return jsonify({'sucesso': sucesso})

@app.route('/api/produtos/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    sucesso = db.deletar_produto(id)
    return jsonify({'sucesso': sucesso})

# ============ API VENDAS ============
@app.route('/api/vendas', methods=['POST'])
def realizar_venda():
    dados = request.json
    sucesso = db.realizar_venda(dados['itens'])
    return jsonify({'sucesso': sucesso})

@app.route('/api/vendas', methods=['GET'])
def listar_vendas():
    vendas = db.listar_vendas()
    return jsonify(vendas)

@app.route('/api/vendas/<int:id>', methods=['GET'])
def detalhes_venda(id):
    venda = db.detalhes_venda(id)
    return jsonify(venda)

# ============ RELATÓRIOS ============
@app.route('/api/relatorios/vendas', methods=['GET'])
def relatorio_vendas():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    relatorio = db.relatorio_vendas(data_inicio, data_fim)
    return jsonify(relatorio)

@app.route('/api/relatorios/produtos', methods=['GET'])
def relatorio_produtos():
    relatorio = db.produtos_mais_vendidos()
    return jsonify(relatorio)

# Páginas
@app.route('/produtos')
def pagina_produtos():
    return render_template('produtos.html')

@app.route('/vendas')
def pagina_vendas():
    return render_template('vendas.html')

@app.route('/relatorios')
def pagina_relatorios():
    return render_template('relatorios.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
