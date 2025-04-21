import sqlite3
import os
import csv
import hashlib

def init_database():
    """Inicializa o banco de dados e retorna a conexão e o cursor."""
    # Criar pasta 'data' se não existir
    os.makedirs("data", exist_ok=True)
    
    # Conectar ao banco de dados
    conn = sqlite3.connect("data/suap.db")
    cursor = conn.cursor()
    
    # Criar tabela de salas, se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sala TEXT NOT NULL UNIQUE,
            codigo TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Criar tabela de patrimônios, se não existir
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
            sala_id INTEGER,
            estado_de_conservacao TEXT,
            FOREIGN KEY (sala_id) REFERENCES salas(id)
        )
    ''')
    
    conn.commit()
    return conn, cursor

def generate_unique_code(sala_text, existing_codes=None):
    """
    Gera um código único baseado no hash MD5 do texto da sala.
    O código é determinístico, produzindo o mesmo resultado para o mesmo texto.
    """
    if not sala_text:
        return None
    hash_object = hashlib.md5(sala_text.encode('utf-8'))
    code = hash_object.hexdigest()
    if existing_codes is None or code not in existing_codes:
        return code
    raise ValueError(f"Colisão de hash MD5 para a sala: {sala_text}")

def load_data_from_file(cursor, conn, file_path):
    """Zera as tabelas, processa o CSV em memória e grava salas e patrimônios no banco."""
    # Zerar as tabelas apenas quando um novo arquivo é carregado
    cursor.execute("DELETE FROM patrimonios")
    cursor.execute("DELETE FROM salas")
    conn.commit()

    # Ler e processar o arquivo CSV
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

            # Montar array temporário para salas
            salas_unicas = set(row['SALA'] for row in reader if row['SALA'])
            sala_data = []
            existing_codes = set()
            sala_to_id = {}
            next_id = 1
            for sala in salas_unicas:
                codigo = generate_unique_code(sala, existing_codes)
                existing_codes.add(codigo)
                sala_data.append({'id': next_id, 'sala': sala, 'codigo': codigo})
                sala_to_id[sala] = next_id
                next_id += 1

            # Armazenar registros de patrimônios em memória
            patrimonios_data = []
            csvfile.seek(0)
            next(reader)  # Pular o cabeçalho
            for row in reader:
                campus_carga = row['CAMPUS DA CARGA'].lower() if row['CAMPUS DA CARGA'] else None
                sala_id = sala_to_id.get(row['SALA'], None)
                patrimonios_data.append((
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
                    sala_id,
                    row['ESTADO DE CONSERVAÇÃO'] or None
                ))

            # Inserir salas no banco
            for sala in sala_data:
                cursor.execute('''
                    INSERT INTO salas (id, sala, codigo)
                    VALUES (?, ?, ?)
                ''', (sala['id'], sala['sala'], sala['codigo']))

            # Inserir patrimônios no banco
            cursor.executemany('''
                INSERT INTO patrimonios (
                    numero, status, ed, descricao, rotulos, carga_atual,
                    setor_responsavel, campus_carga, valor_aquisicao,
                    valor_depreciado, numero_nota_fiscal, numero_de_serie,
                    data_da_entrada, data_da_carga, fornecedor, sala_id,
                    estado_de_conservacao
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', patrimonios_data)

            conn.commit()
            print(f"Dados carregados com sucesso de {file_path}")
            print(f"Itens importados: {len(patrimonios_data)}")
            print(f"Salas importadas: {len(sala_data)}")
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")

def get_all_salas(cursor):
    """Retorna uma lista de todas as salas (id, nome)."""
    cursor.execute("SELECT id, sala FROM salas ORDER BY sala")
    return cursor.fetchall()

def get_patrimonios_by_sala(cursor, sala_id):
    """Retorna todos os patrimônios associados a uma sala específica."""
    cursor.execute('''
        SELECT p.numero, p.status, p.ed, p.descricao, p.rotulos, p.carga_atual,
               p.setor_responsavel, p.campus_carga, p.valor_aquisicao,
               p.valor_depreciado, p.numero_nota_fiscal, p.numero_de_serie,
               p.data_da_entrada, p.data_da_carga, p.fornecedor, s.sala,
               p.estado_de_conservacao
        FROM patrimonios p
        LEFT JOIN salas s ON p.sala_id = s.id
        WHERE p.sala_id = ?
    ''', (sala_id,))
    return cursor.fetchall()