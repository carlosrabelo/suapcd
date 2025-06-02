import os
import csv
import glob
import platform
from pathlib import Path

class ReportGenerator:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_report_dir(self):
        """Retorna o diretório de relatórios apropriado com base no sistema operacional."""
        if platform.system() == "Windows":
            # Usar %APPDATA%\SUAP-CD\report no Windows
            report_dir = Path(os.getenv("APPDATA")) / "SUAP-CD" / "report"
        else:
            # Usar /var/lib/suapcd/report no Linux
            report_dir = Path("/var/lib/suapcd/report")
        
        # Criar o diretório se não existir
        report_dir.mkdir(parents=True, exist_ok=True)
        return report_dir

    def generate_report(self):
        """Gera relatórios CSV com itens lidos, não lidos, divergentes e não cadastrados para cada sala e geral."""
        base_dir = self.get_report_dir()
        
        geral_dir = base_dir / "_GERAL_"
        try:
            geral_dir.mkdir(exist_ok=True)
        except Exception as e:
            print(f"Erro ao criar diretório {geral_dir}: {e}")
            return

        relatorio_data = self.db_manager.get_relatorio_patrimonios()
        salas = {}
        geral_encontrados = []
        geral_nao_encontrados = []
        geral_divergentes = []
        for row in relatorio_data:
            sala_id, sala_nome = row[0], row[1]
            if sala_id not in salas:
                salas[sala_id] = {"nome": sala_nome, "encontrados": [], "nao_encontrados": [], "divergentes": []}
            if row[2] is not None:
                patrimonio = row[2:]
                if patrimonio[-2] == 1:
                    salas[sala_id]["encontrados"].append(patrimonio)
                    geral_encontrados.append((sala_nome, *patrimonio))
                else:
                    salas[sala_id]["nao_encontrados"].append(patrimonio)
                    geral_nao_encontrados.append((sala_nome, *patrimonio))
                if patrimonio[-1] is not None and patrimonio[-1] != sala_id:
                    salas[sala_id]["divergentes"].append(patrimonio)
                    geral_divergentes.append((sala_nome, *patrimonio))

        unfound_data = self.db_manager.get_unfound_patrimonios()
        salas_unfound = {}
        geral_unfound = []
        for sala_id, sala_nome, numero in unfound_data:
            if sala_id not in salas_unfound:
                salas_unfound[sala_id] = {"nome": sala_nome, "unfound": []}
            salas_unfound[sala_id]["unfound"].append(numero)
            geral_unfound.append((sala_nome, numero))

        headers_sala = [
            "Número", "Status", "ED", "Descrição", "Rótulos", "Carga Atual",
            "Setor Responsável", "Campus Carga", "Número de Série",
            "Estado Conservação", "Encontrado", "Sala Original"
        ]

        headers_geral = [
            "Sala Atual", "Número", "Status", "ED", "Descrição", "Rótulos", "Carga Atual",
            "Setor Responsável", "Campus Carga", "Número de Série",
            "Estado Conservação", "Encontrado", "Sala Original"
        ]

        headers_unfound = ["Número"]
        headers_unfound_geral = ["Sala Atual", "Número"]

        for csv_file in glob.glob(str(geral_dir / "*.csv")):
            try:
                os.remove(csv_file)
                print(f"Arquivo removido: {csv_file}")
            except Exception as e:
                print(f"Erro ao remover arquivo {csv_file}: {e}")

        csv_path_geral_encontrados = geral_dir / "encontrados.csv"
        try:
            with open(csv_path_geral_encontrados, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers_geral)
                for sala_nome, *patrimonio in geral_encontrados:
                    row = list(patrimonio)
                    row[-2] = "Lido"
                    sala_id_original = row[-1]
                    sala_original_nome = ""
                    if sala_id_original:
                        self.db_manager.cursor.execute("SELECT sala FROM salas WHERE id = ?", (sala_id_original,))
                        result = self.db_manager.cursor.fetchone()
                        sala_original_nome = result[0] if result else ""
                    row[-1] = sala_original_nome
                    writer.writerow([sala_nome, *map(lambda x: str(x or ""), row)])
            print(f"Relatório geral de encontrados gerado: {csv_path_geral_encontrados}")
        except Exception as e:
            print(f"Erro ao escrever CSV {csv_path_geral_encontrados}: {e}")

        csv_path_geral_nao_encontrados = geral_dir / "nao_encontrados.csv"
        try:
            with open(csv_path_geral_nao_encontrados, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers_geral)
                for sala_nome, *patrimonio in geral_nao_encontrados:
                    row = list(patrimonio)
                    row[-2] = "Não Lido"
                    sala_id_original = row[-1]
                    sala_original_nome = ""
                    if sala_id_original:
                        self.db_manager.cursor.execute("SELECT sala FROM salas WHERE id = ?", (sala_id_original,))
                        result = self.db_manager.cursor.fetchone()
                        sala_original_nome = result[0] if result else ""
                    row[-1] = sala_original_nome
                    writer.writerow([sala_nome, *map(lambda x: str(x or ""), row)])
            print(f"Relatório geral de não encontrados gerado: {csv_path_geral_nao_encontrados}")
        except Exception as e:
            print(f"Erro ao escrever CSV {csv_path_geral_nao_encontrados}: {e}")

        csv_path_geral_divergentes = geral_dir / "divergente.csv"
        try:
            with open(csv_path_geral_divergentes, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers_geral)
                for sala_nome, *patrimonio in geral_divergentes:
                    row = list(patrimonio)
                    row[-2] = "Lido" if row[-2] == 1 else "Não Lido"
                    sala_id_original = row[-1]
                    sala_original_nome = ""
                    if sala_id_original:
                        self.db_manager.cursor.execute("SELECT sala FROM salas WHERE id = ?", (sala_id_original,))
                        result = self.db_manager.cursor.fetchone()
                        sala_original_nome = result[0] if result else ""
                    row[-1] = sala_original_nome
                    writer.writerow([sala_nome, *map(lambda x: str(x or ""), row)])
            print(f"Relatório geral de divergentes gerado: {csv_path_geral_divergentes}")
        except Exception as e:
            print(f"Erro ao escrever CSV {csv_path_geral_divergentes}: {e}")

        csv_path_geral_unfound = geral_dir / "nao_cadastrados.csv"
        try:
            with open(csv_path_geral_unfound, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers_unfound_geral)
                for sala_nome, numero in geral_unfound:
                    writer.writerow([sala_nome, numero])
            print(f"Relatório geral de não cadastrados (escaneados) gerado: {csv_path_geral_unfound}")
        except Exception as e:
            print(f"Erro ao escrever CSV {csv_path_geral_unfound}: {e}")

        for sala_id, sala_info in salas.items():
            sala_nome = sala_info["nome"]
            encontrados = sala_info["encontrados"]
            nao_encontrados = sala_info["nao_encontrados"]
            divergentes = sala_info["divergentes"]
            
            safe_sala_nome = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in sala_nome)
            sala_dir = base_dir / safe_sala_nome
            try:
                sala_dir.mkdir(exist_ok=True)
            except Exception as e:
                print(f"Erro ao criar diretório {sala_dir}: {e}")
                continue
            
            for csv_file in glob.glob(str(sala_dir / "*.csv")):
                try:
                    os.remove(csv_file)
                    print(f"Arquivo removido: {csv_file}")
                except Exception as e:
                    print(f"Erro ao remover arquivo {csv_file}: {e}")

            csv_path_encontrados = sala_dir / "encontrados.csv"
            try:
                with open(csv_path_encontrados, mode='w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers_sala)
                    for patrimonio in encontrados:
                        row = list(patrimonio)
                        row[-2] = "Lido"
                        sala_id_original = row[-1]
                        sala_original_nome = ""
                        if sala_id_original:
                            self.db_manager.cursor.execute("SELECT sala FROM salas WHERE id = ?", (sala_id_original,))
                            result = self.db_manager.cursor.fetchone()
                            sala_original_nome = result[0] if result else ""
                        row[-1] = sala_original_nome
                        writer.writerow([str(val or "") for val in row])
                print(f"Relatório de encontrados gerado para sala {sala_nome}: {csv_path_encontrados}")
            except Exception as e:
                print(f"Erro ao escrever CSV {csv_path_encontrados}: {e}")

            csv_path_nao_encontrados = sala_dir / "nao_encontrados.csv"
            try:
                with open(csv_path_nao_encontrados, mode='w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers_sala)
                    for patrimonio in nao_encontrados:
                        row = list(patrimonio)
                        row[-2] = "Não Lido"
                        sala_id_original = row[-1]
                        sala_original_nome = ""
                        if sala_id_original:
                            self.db_manager.cursor.execute("SELECT sala FROM salas WHERE id = ?", (sala_id_original,))
                            result = self.db_manager.cursor.fetchone()
                            sala_original_nome = result[0] if result else ""
                        row[-1] = sala_original_nome
                        writer.writerow([str(val or "") for val in row])
                print(f"Relatório de não encontrados gerado para sala {sala_nome}: {csv_path_nao_encontrados}")
            except Exception as e:
                print(f"Erro ao escrever CSV {csv_path_nao_encontrados}: {e}")

            csv_path_divergentes = sala_dir / "divergente.csv"
            try:
                with open(csv_path_divergentes, mode='w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers_sala)
                    for patrimonio in divergentes:
                        row = list(patrimonio)
                        row[-2] = "Lido" if row[-2] == 1 else "Não Lido"
                        sala_id_original = row[-1]
                        sala_original_nome = ""
                        if sala_id_original:
                            self.db_manager.cursor.execute("SELECT sala FROM salas WHERE id = ?", (sala_id_original,))
                            result = self.db_manager.cursor.fetchone()
                            sala_original_nome = result[0] if result else ""
                        row[-1] = sala_original_nome
                        writer.writerow([str(val or "") for val in row])
                print(f"Relatório de divergentes gerado para sala {sala_nome}: {csv_path_divergentes}")
            except Exception as e:
                print(f"Erro ao escrever CSV {csv_path_divergentes}: {e}")

            if sala_id in salas_unfound:
                csv_path_unfound = sala_dir / "nao_cadastrados.csv"
                try:
                    with open(csv_path_unfound, mode='w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow(headers_unfound)
                        for numero in salas_unfound[sala_id]["unfound"]:
                            writer.writerow([numero])
                    print(f"Relatório de não cadastrados (escaneados) gerado para sala {sala_nome}: {csv_path_unfound}")
                except Exception as e:
                    print(f"Erro ao escrever CSV {csv_path_unfound}: {e}")