import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='sisvenda.db'):
        self.db_name = db_name
    
    def conectar(self):
        return sqlite3.connect(self.db_name)
    
    def criar_tabelas(self):
        conn = self.conectar()
        cursor = conn.cursor()
        
        # Tabela Produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco REAL NOT NULL,
                quantidade INTEGER NOT NULL DEFAULT 0,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela Vendas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                valor_total REAL NOT NULL,
                quantidade_itens INTEGER NOT NULL
            )
        ''')
        
        # Tabela Itens da Venda
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itens_venda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venda_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (venda_id) REFERENCES vendas (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ============ PRODUTOS ============
    def listar_produtos(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produtos ORDER BY nome')
        produtos = []
        for row in cursor.fetchall():
            produtos.append({
                'id': row[0],
                'nome': row[1],
                'descricao': row[2],
                'preco': row[3],
                'quantidade': row[4],
                'data_criacao': row[5]
            })
        conn.close()
        return produtos
    
    def adicionar_produto(self, nome, descricao, preco, quantidade):
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO produtos (nome, descricao, preco, quantidade)
                VALUES (?, ?, ?, ?)
            ''', (nome, descricao, preco, quantidade))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao adicionar produto: {e}")
            return False
    
    def atualizar_produto(self, id, nome, descricao, preco, quantidade):
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE produtos 
                SET nome=?, descricao=?, preco=?, quantidade=?
                WHERE id=?
            ''', (nome, descricao, preco, quantidade, id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao atualizar produto: {e}")
            return False
    
    def deletar_produto(self, id):
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM produtos WHERE id=?', (id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao deletar produto: {e}")
            return False
    
    # ============ VENDAS ============
    def realizar_venda(self, itens):
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            valor_total = 0
            quantidade_total = 0
            
            for item in itens:
                produto_id = item['produto_id']
                quantidade = item['quantidade']
                
                # Buscar produto
                cursor.execute('SELECT * FROM produtos WHERE id=?', (produto_id,))
                produto = cursor.fetchone()
                
                if not produto or produto[4] < quantidade:
                    raise Exception(f"Estoque insuficiente para produto {produto_id}")
                
                preco_unitario = produto[3]
                subtotal = preco_unitario * quantidade
                valor_total += subtotal
                quantidade_total += quantidade
                
                # Atualizar estoque
                novo_estoque = produto[4] - quantidade
                cursor.execute('UPDATE produtos SET quantidade=? WHERE id=?', 
                             (novo_estoque, produto_id))
            
            # Criar venda
            cursor.execute('''
                INSERT INTO vendas (valor_total, quantidade_itens)
                VALUES (?, ?)
            ''', (valor_total, quantidade_total))
            
            venda_id = cursor.lastrowid
            
            # Inserir itens da venda
            for item in itens:
                produto_id = item['produto_id']
                quantidade = item['quantidade']
                
                cursor.execute('SELECT preco FROM produtos WHERE id=?', (produto_id,))
                preco_unitario = cursor.fetchone()[0]
                subtotal = preco_unitario * quantidade
                
                cursor.execute('''
                    INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (venda_id, produto_id, quantidade, preco_unitario, subtotal))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao realizar venda: {e}")
            conn.rollback()
            conn.close()
            return False
    
    def listar_vendas(self):
        conn = self.conectar()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, COUNT(iv.id) as total_itens
            FROM vendas v
            LEFT JOIN itens_venda iv ON v.id = iv.venda_id
            GROUP BY v.id
            ORDER BY v.data_venda DESC
        ''')
        vendas = []
        for row in cursor.fetchall():
            vendas.append({
                'id': row[0],
                'data_venda': row[1],
                'valor_total': row[2],
                'quantidade_itens': row[3]
            })
        conn.close()
        return vendas
    
    def detalhes_venda(self, venda_id):
        conn = self.conectar()
        cursor = conn.cursor()
        
        # Buscar venda
        cursor.execute('SELECT * FROM vendas WHERE id=?', (venda_id,))
        venda = cursor.fetchone()
        
        if not venda:
            conn.close()
            return None
        
        # Buscar itens
        cursor.execute('''
            SELECT iv.*, p.nome as produto_nome
            FROM itens_venda iv
            JOIN produtos p ON iv.produto_id = p.id
            WHERE iv.venda_id = ?
        ''', (venda_id,))
        
        itens = []
        for row in cursor.fetchall():
            itens.append({
                'id': row[0],
                'produto_nome': row[6],
                'quantidade': row[3],
                'preco_unitario': row[4],
                'subtotal': row[5]
            })
        
        conn.close()
        return {
            'venda': {
                'id': venda[0],
                'data_venda': venda[1],
                'valor_total': venda[2],
                'quantidade_itens': venda[3]
            },
            'itens': itens
        }
    
    # ============ RELATÓRIOS ============
    def relatorio_vendas(self, data_inicio=None, data_fim=None):
        conn = self.conectar()
        cursor = conn.cursor()
        
        query = '''
            SELECT DATE(data_venda) as data, 
                   COUNT(*) as total_vendas,
                   SUM(valor_total) as total_valor
            FROM vendas
        '''
        
        params = []
        if data_inicio and data_fim:
            query += ' WHERE DATE(data_venda) BETWEEN ? AND ?'
            params = [data_inicio, data_fim]
        
        query += ' GROUP BY DATE(data_venda) ORDER BY data DESC'
        
        cursor.execute(query, params)
        
        relatorio = []
        for row in cursor.fetchall():
            relatorio.append({
                'data': row[0],
                'total_vendas': row[1],
                'total_valor': row[2]
            })
        
        conn.close()
        return relatorio
    
    def produtos_mais_vendidos(self):
        conn = self.conectar()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.nome, 
                   SUM(iv.quantidade) as total_quantidade,
                   SUM(iv.subtotal) as total_valor
            FROM itens_venda iv
            JOIN produtos p ON iv.produto_id = p.id
            GROUP BY p.id
            ORDER BY total_quantidade DESC
            LIMIT 10
        ''')
        
        produtos = []
        for row in cursor.fetchall():
            produtos.append({
                'nome': row[0],
                'total_quantidade': row[1],
                'total_valor': row[2]
            })
        
        conn.close()
        return produtos
