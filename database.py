import sqlite3
import os
import csv

def init_database():
    """Inicializa o banco de dados e retorna a conexão e o cursor."""
    # Criar pasta 'data' se não existir
    os.makedirs("data", exist_ok=True)
    
    # Conectar ao banco de dados
    conn = sqlite3.connect("data/suap.db")
    cursor = conn.cursor()
    
    # Criar tabela de patrimônios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patrimonios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            status TEXT,
            ed TEXT,
            descricao TEXT,
            rotulos TEXT,
            carga_atual TEXT,
            setor_responsavel TEXT,
            campus_carga TEXT,
            valor_aquisicao REAL,
            valor_depreciado REAL,
            numero_nota_fiscal TEXT,
            numero_de_serie TEXT,
            data_da_entrada TEXT,
            data_da_carga TEXT,
            fornecedor TEXT,
            sala TEXT,
            estado_de_conservacao TEXT
        )
    ''')
    conn.commit()
    
    return conn, cursor

def load_data_from_file(cursor, conn, file_path):
    """Zera a tabela patrimonios e carrega dados de um arquivo CSV."""
    # Zerar a tabela
    cursor.execute("DELETE FROM patrimonios")
    conn.commit()

    # Ler e inserir dados do arquivo CSV
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            expected_columns = [
                '#', 'NUMERO', 'STATUS', 'ED', 'DESCRICAO', 'RÓTULOS',
                'CARGA ATUAL', 'SETOR DO RESPONSÁVEL', 'CAMPUS DA CARGA',
                'VALOR AQUISIÇÃO', 'VALOR DEPRECIADO', 'NUMERO NOTA FISCAL',
                'NÚMERO DE SÉRIE', 'DATA DA ENTRADA', 'DATA DA CARGA',
                'FORNECEDOR', 'SALA', 'ESTADO DE CONSERVAÇÃO'
            ]
            if reader.fieldnames != expected_columns:
                print(f"Erro: O arquivo CSV deve ter exatamente as colunas: {expected_columns}")
                return

            for row in reader:
                # Converter CAMPUS DA CARGA para minúsculas
                campus_carga = row['CAMPUS DA CARGA'].lower() if row['CAMPUS DA CARGA'] else None

                cursor.execute('''
                    INSERT INTO patrimonios (
                        numero, status, ed, descricao, rotulos, carga_atual,
                        setor_responsavel, campus_carga, valor_aquisicao,
                        valor_depreciado, numero_nota_fiscal, numero_de_serie,
                        data_da_entrada, data_da_carga, fornecedor, sala,
                        estado_de_conservacao
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['NUMERO'],
                    row['STATUS'] or None,
                    row['ED'] or None,
                    row['DESCRICAO'] or None,
                    row['RÓTULOS'] or None,
                    row['CARGA ATUAL'] or None,
                    row['SETOR DO RESPONSÁVEL'] or None,
                    campus_carga,
                    float(row['VALOR AQUISIÇÃO']) if row['VALOR AQUISIÇÃO'] else None,
                    float(row['VALOR DEPRECIADO']) if row['VALOR DEPRECIADO'] else None,
                    row['NUMERO NOTA FISCAL'] or None,
                    row['NÚMERO DE SÉRIE'] or None,
                    row['DATA DA ENTRADA'] or None,
                    row['DATA DA CARGA'] or None,
                    row['FORNECEDOR'] or None,
                    row['SALA'] or None,
                    row['ESTADO DE CONSERVAÇÃO'] or None
                ))
            conn.commit()
            print(f"Dados carregados com sucesso de {file_path}")
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")