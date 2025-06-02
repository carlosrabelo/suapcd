import sqlite3
import os
import csv
import hashlib
import platform
from pathlib import Path

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.init_database()

    def get_data_dir(self):
        """Retorna o diretório de dados apropriado com base no sistema operacional."""
        if platform.system() == "Windows":
            # Usar %APPDATA%\SUAP-CD no Windows
            data_dir = Path(os.getenv("APPDATA")) / "SUAP-CD"
        else:
            # Usar /var/lib/suapcd no Linux
            data_dir = Path("/var/lib/suapcd")
        
        # Criar o diretório se não existir
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    def init_database(self):
        """Inicializa o banco de dados e armazena a conexão e o cursor."""
        data_dir = self.get_data_dir()
        db_path = data_dir / "suap.db"
        
        self.conn = sqlite3.connect(db_path, check_same_thread=True)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS salas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sala TEXT NOT NULL UNIQUE,
                codigo TEXT NOT NULL UNIQUE
            )
        ''')
        
        self.cursor.execute('''
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
                encontrado INTEGER DEFAULT 0,
                sala_id_original INTEGER,
                FOREIGN KEY (sala_id) REFERENCES salas(id),
                FOREIGN KEY (sala_id_original) REFERENCES salas(id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patrimonios_nao_cadastrados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL,
                sala_id INTEGER,
                FOREIGN KEY (sala_id) REFERENCES salas(id)
            )
        ''')
        
        self.cursor.execute("PRAGMA table_info(patrimonios)")
        columns = [col[1] for col in self.cursor.fetchall()]
        if 'encontrado' not in columns:
            self.cursor.execute('''
                ALTER TABLE patrimonios
                ADD COLUMN encontrado INTEGER DEFAULT 0
            ''')
        
        if 'sala_id_original' not in columns:
            self.cursor.execute('''
                ALTER TABLE patrimonios
                ADD COLUMN sala_id_original INTEGER
            ''')
            self.cursor.execute('''
                UPDATE patrimonios
                SET sala_id_original = sala_id
                WHERE sala_id_original IS NULL
            ''')
            self.conn.commit()
        
        self.conn.commit()

    def close(self):
        """Fecha a conexão com o banco de dados de forma segura."""
        try:
            if self.conn is not None:
                self.conn.commit()
                self.conn.close()
                self.conn = None
                self.cursor = None
        except Exception as e:
            print(f"Erro ao fechar a conexão com o banco: {e}")

    def get_all_salas(self):
        """Retorna uma lista de todas as salas (id, nome)."""
        self.cursor.execute("SELECT id, sala FROM salas ORDER BY sala")
        return self.cursor.fetchall()

    def get_patrimonios_by_sala(self, sala_id):
        """Retorna todos os patrimônios associados a uma sala específica."""
        self.cursor.execute('''
            SELECT p.numero, p.status, p.ed, p.descricao, p.rotulos, p.carga_atual,
                   p.setor_responsavel, p.campus_carga, p.numero_de_serie,
                   p.estado_de_conservacao, p.encontrado, p.sala_id_original
            FROM patrimonios p
            WHERE p.sala_id = ?
        ''', (sala_id,))
        return self.cursor.fetchall()

    def mark_patrimonio_encontrado(self, numero, sala_id):
        """Marca um patrimônio como encontrado e atualiza sala_id se necessário."""
        self.cursor.execute('''
            SELECT sala_id, sala_id_original
            FROM patrimonios
            WHERE numero = ?
        ''', (numero,))
        result = self.cursor.fetchone()
        
        if result:
            current_sala_id, current_sala_id_original = result
            if current_sala_id_original is None:
                self.cursor.execute('''
                    UPDATE patrimonios
                    SET sala_id_original = ?
                    WHERE numero = ?
                ''', (current_sala_id, numero))
            
            self.cursor.execute('''
                UPDATE patrimonios
                SET sala_id = ?, encontrado = 1
                WHERE numero = ?
            ''', (sala_id, numero))
            self.conn.commit()
            return self.cursor.rowcount > 0
        return False

    def record_unfound_patrimonio(self, numero, sala_id):
        """Registra um patrimônio não cadastrado na tabela patrimonios_nao_cadastrados."""
        self.cursor.execute('''
            INSERT INTO patrimonios_nao_cadastrados (numero, sala_id)
            VALUES (?, ?)
        ''', (numero, sala_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_unfound_patrimonios(self):
        """Retorna todos os patrimônios não cadastrados com suas salas."""
        self.cursor.execute('''
            SELECT s.id, s.sala, u.numero
            FROM patrimonios_nao_cadastrados u
            JOIN salas s ON u.sala_id = s.id
            ORDER BY s.sala, u.numero
        ''')
        return self.cursor.fetchall()

    def get_relatorio_patrimonios(self):
        """Retorna uma lista de todas as salas e seus patrimônios para relatório."""
        self.cursor.execute('''
            SELECT s.id, s.sala, p.numero, p.status, p.ed, p.descricao, p.rotulos,
                   p.carga_atual, p.setor_responsavel, p.campus_carga,
                   p.numero_de_serie, p.estado_de_conservacao, p.encontrado,
                   p.sala_id_original
            FROM salas s
            LEFT JOIN patrimonios p ON s.id = p.sala_id
            ORDER BY s.sala, p.numero
        ''')
        return self.cursor.fetchall()

def generate_unique_code(sala_text, existing_codes=None):
    """Gera um código único baseado no hash MD5 do texto da sala."""
    if not sala_text:
        return None
    hash_object = hashlib.md5(sala_text.encode('utf-8'))
    code = hash_object.hexdigest()
    if existing_codes is None or code not in existing_codes:
        return code
    raise ValueError(f"Colisão de hash MD5 para a sala: {sala_text}")

def load_data_from_file(cursor, conn, file_path):
    """Zera as tabelas, processa o CSV em memória e grava salas e patrimônios no banco."""
    cursor.execute("DELETE FROM patrimonios")
    cursor.execute("DELETE FROM patrimonios_nao_cadastrados")
    cursor.execute("DELETE FROM salas")
    conn.commit()

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

            salas_unicas = set(row['SALA'].upper() for row in reader if row['SALA'] and row['SALA'].strip())
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

            patrimonios_data = []
            csvfile.seek(0)
            next(reader)
            for row in reader:
                campus_carga = row['CAMPUS DA CARGA'].lower() if row['CAMPUS DA CARGA'] else None
                sala_text = row['SALA'].upper() if row['SALA'] and row['SALA'].strip() else None
                sala_id = sala_to_id.get(sala_text, None)
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
                    row['ESTADO DE CONSERVAÇÃO'] or None,
                    0,
                    sala_id
                ))

            for sala in sala_data:
                cursor.execute('''
                    INSERT INTO salas (id, sala, codigo)
                    VALUES (?, ?, ?)
                ''', (sala['id'], sala['sala'], sala['codigo']))

            cursor.executemany('''
                INSERT INTO patrimonios (
                    numero, status, ed, descricao, rotulos, carga_atual,
                    setor_responsavel, campus_carga, valor_aquisicao,
                    valor_depreciado, numero_nota_fiscal, numero_de_serie,
                    data_da_entrada, data_da_carga, fornecedor, sala_id,
                    estado_de_conservacao, encontrado, sala_id_original
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', patrimonios_data)

            conn.commit()
            print(f"Dados carregados com sucesso de {file_path}")
            print(f"Itens importados: {len(patrimonios_data)}")
            print(f"Salas importadas: {len(sala_data)}")
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")