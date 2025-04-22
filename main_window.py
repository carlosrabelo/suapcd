import warnings
# Suprimir todos os DeprecationWarning antes de qualquer importação
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import csv
import glob
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout,
    QSpacerItem, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QBrush, QColor

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.setWindowTitle("SUAP-CD - Coletor de Dados")
        self.db_manager = db_manager

        # Layout principal
        layout = QVBoxLayout()
        
        # Espaçador superior reduzido
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Título
        label = QLabel("Bem-vindo ao SUAP-CD!", self)
        label.setFont(QFont("Arial", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Layout horizontal para botões
        button_layout = QHBoxLayout()
        
        # Botão para abrir janela de escaneamento
        scan_button = QPushButton("Escanear Patrimônios")
        scan_button.setFont(QFont("Arial", 12))
        scan_button.clicked.connect(self.open_scan_window)
        button_layout.addWidget(scan_button)
        
        # Botão para gerar relatório
        report_button = QPushButton("Gerar Relatório")
        report_button.setFont(QFont("Arial", 12))
        report_button.clicked.connect(self.generate_report)
        button_layout.addWidget(report_button)
        
        layout.addLayout(button_layout)
        
        # Campo de filtro para salas
        self.filter_input = QLineEdit()
        self.filter_input.setFont(QFont("Arial", 12))
        self.filter_input.setPlaceholderText("Filtrar salas...")
        self.filter_input.textChanged.connect(self.filter_salas)
        layout.addWidget(self.filter_input)
        
        # Tabela para selecionar salas
        self.sala_table = QTableWidget(self)
        self.sala_table.setColumnCount(1)
        self.sala_table.setHorizontalHeaderLabels(["Nome da Sala"])
        self.sala_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sala_table.setFont(QFont("Arial", 10))
        self.sala_table.setSelectionMode(QTableWidget.SingleSelection)
        self.sala_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sala_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Impedir edição
        self.populate_sala_table("")  # Inicializar sem filtro
        self.sala_table.clicked.connect(self.update_patrimonios_table)
        layout.addWidget(self.sala_table, stretch=1)  # Ocupa metade do espaço
        
        # Tabela para exibir patrimônios
        self.patrimonio_table = QTableWidget(self)
        self.patrimonio_table.setColumnCount(11)
        self.patrimonio_table.setHorizontalHeaderLabels([
            "Número", "Status", "ED", "Descrição", "Rótulos", "Carga Atual",
            "Setor Responsável", "Campus Carga", "Número de Série", "Estado Conservação",
            "Encontrado"
        ])
        self.patrimonio_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.patrimonio_table.setFont(QFont("Arial", 10))
        self.patrimonio_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Impedir edição
        layout.addWidget(self.patrimonio_table, stretch=1)  # Ocupa metade do espaço
        
        # Labels para estatísticas
        self.total_label = QLabel("Total de Patrimônios: 0")
        self.total_label.setFont(QFont("Arial", 12))
        self.total_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.total_label)
        
        self.encontrados_label = QLabel("Patrimônios Encontrados: 0")
        self.encontrados_label.setFont(QFont("Arial", 12))
        self.total_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.encontrados_label)
        
        # Espaçador inferior reduzido
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Container
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def populate_sala_table(self, filter_text):
        """Popula a QTableWidget com salas, aplicando o filtro especificado."""
        salas = self.db_manager.get_all_salas()
        # Filtrar salas com base no texto (case-insensitive)
        filtered_salas = [
            (sala_id, sala_nome) for sala_id, sala_nome in salas
            if filter_text.lower() in sala_nome.lower()
        ]
        self.sala_table.setRowCount(len(filtered_salas))
        for row_idx, (sala_id, sala_nome) in enumerate(filtered_salas):
            item = QTableWidgetItem(sala_nome)
            item.setData(Qt.UserRole, sala_id)  # Armazenar sala_id como dado associado
            self.sala_table.setItem(row_idx, 0, item)

    def filter_salas(self):
        """Atualiza a tabela de salas com base no texto do filtro."""
        filter_text = self.filter_input.text().strip()
        self.populate_sala_table(filter_text)

    def update_patrimonios_table(self):
        """Atualiza a tabela de patrimônios com base na sala selecionada na tabela de salas."""
        selected_items = self.sala_table.selectedItems()
        if not selected_items:
            self.patrimonio_table.setRowCount(0)
            self.total_label.setText("Total de Patrimônios: 0")
            self.encontrados_label.setText("Patrimônios Encontrados: 0")
            return
        
        # Obter o sala_id do item selecionado
        sala_id = selected_items[0].data(Qt.UserRole)
        
        # Limpar tabela de patrimônios
        self.patrimonio_table.setRowCount(0)
        
        # Buscar e preencher patrimônios
        patrimonios = self.db_manager.get_patrimonios_by_sala(sala_id)
        self.patrimonio_table.setRowCount(len(patrimonios))
        
        # Calcular estatísticas
        total_patrimonios = len(patrimonios)
        encontrados = sum(1 for row_data in patrimonios if row_data[-1] == 1)
        
        # Atualizar labels
        self.total_label.setText(f"Total de Patrimônios: {total_patrimonios}")
        self.encontrados_label.setText(f"Patrimônios Encontrados: {encontrados}")
        
        # Preencher tabela
        for row_idx, row_data in enumerate(patrimonios):
            # Mapear os 11 campos: numero, status, ed, descricao, rotulos, carga_atual,
            # setor_responsavel, campus_carga, numero_de_serie, estado_de_conservacao, encontrado
            for col_idx, value in enumerate(row_data[:-1]):  # Excluir encontrado dos valores
                item = QTableWidgetItem(str(value or ""))
                # Destacar linha se encontrado = 1
                if row_data[-1] == 1:  # Último campo é encontrado
                    item.setBackground(QBrush(QColor(144, 238, 144)))  # Verde claro
                self.patrimonio_table.setItem(row_idx, col_idx, item)
            # Coluna Encontrado
            encontrado_text = "Sim" if row_data[-1] == 1 else "Não"
            item = QTableWidgetItem(encontrado_text)
            if row_data[-1] == 1:
                item.setBackground(QBrush(QColor(144, 238, 144)))  # Verde claro
            self.patrimonio_table.setItem(row_idx, 10, item)

    def open_scan_window(self):
        """Abre a janela de escaneamento de código de barras como diálogo modal."""
        self.hide()
        from scan_window import ScanWindow
        self.scan_window = ScanWindow(self.db_manager, self)
        self.scan_window.showMaximized()  # Abrir em tela cheia
        self.showMaximized()  # Restaurar a janela principal após fechar

    def generate_report(self):
        """Gera relatórios CSV com itens lidos e não lidos para cada sala e geral."""
        # Criar diretório base para relatórios
        base_dir = "report"
        try:
            os.makedirs(base_dir, exist_ok=True)
        except Exception as e:
            print(f"Erro ao criar diretório {base_dir}: {e}")
            return

        # Criar diretório geral
        geral_dir = os.path.join(base_dir, "_geral")
        try:
            os.makedirs(geral_dir, exist_ok=True)
        except Exception as e:
            print(f"Erro ao criar diretório {geral_dir}: {e}")
            return

        # Obter dados do relatório
        relatorio_data = self.db_manager.get_relatorio_patrimonios()
        
        # Organizar dados por sala e geral
        salas = {}
        geral_encontrados = []
        geral_nao_encontrados = []
        for row in relatorio_data:
            sala_id, sala_nome = row[0], row[1]
            if sala_id not in salas:
                salas[sala_id] = {"nome": sala_nome, "encontrados": [], "nao_encontrados": []}
            if row[2] is not None:  # Ignorar linhas sem patrimônios
                patrimonio = row[2:]
                if patrimonio[-1] == 1:  # encontrado = 1
                    salas[sala_id]["encontrados"].append(patrimonio)
                    geral_encontrados.append((sala_nome, *patrimonio))
                else:  # encontrado = 0
                    salas[sala_id]["nao_encontrados"].append(patrimonio)
                    geral_nao_encontrados.append((sala_nome, *patrimonio))

        # Cabeçalhos do CSV para relatórios por sala
        headers_sala = [
            "Número", "Status", "ED", "Descrição", "Rótulos", "Carga Atual",
            "Setor Responsável", "Campus Carga", "Número de Série",
            "Estado Conservação", "Encontrado"
        ]

        # Cabeçalhos do CSV para relatórios gerais (com coluna Sala)
        headers_geral = [
            "Sala", "Número", "Status", "ED", "Descrição", "Rótulos", "Carga Atual",
            "Setor Responsável", "Campus Carga", "Número de Série",
            "Estado Conservação", "Encontrado"
        ]

        # Limpar arquivos CSV existentes na pasta geral
        for csv_file in glob.glob(os.path.join(geral_dir, "*.csv")):
            try:
                os.remove(csv_file)
                print(f"Arquivo removido: {csv_file}")
            except Exception as e:
                print(f"Erro ao remover arquivo {csv_file}: {e}")

        # Gerar CSV geral para encontrados
        csv_path_geral_encontrados = os.path.join(geral_dir, "encontrados.csv")
        try:
            with open(csv_path_geral_encontrados, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers_geral)
                for sala_nome, *patrimonio in geral_encontrados:
                    row = list(patrimonio)
                    row[-1] = "Lido"
                    writer.writerow([sala_nome, *map(lambda x: str(x or ""), row)])
            print(f"Relatório geral de encontrados gerado: {csv_path_geral_encontrados}")
        except Exception as e:
            print(f"Erro ao escrever CSV {csv_path_geral_encontrados}: {e}")

        # Gerar CSV geral para não encontrados
        csv_path_geral_nao_encontrados = os.path.join(geral_dir, "nao_encontrados.csv")
        try:
            with open(csv_path_geral_nao_encontrados, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers_geral)
                for sala_nome, *patrimonio in geral_nao_encontrados:
                    row = list(patrimonio)
                    row[-1] = "Não Lido"
                    writer.writerow([sala_nome, *map(lambda x: str(x or ""), row)])
            print(f"Relatório geral de não encontrados gerado: {csv_path_geral_nao_encontrados}")
        except Exception as e:
            print(f"Erro ao escrever CSV {csv_path_geral_nao_encontrados}: {e}")

        # Gerar CSVs para cada sala
        for sala_id, sala_info in salas.items():
            sala_nome = sala_info["nome"]
            encontrados = sala_info["encontrados"]
            nao_encontrados = sala_info["nao_encontrados"]
            
            # Criar pasta da sala (substituir caracteres inválidos)
            safe_sala_nome = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in sala_nome)
            sala_dir = os.path.join(base_dir, safe_sala_nome)
            try:
                os.makedirs(sala_dir, exist_ok=True)
            except Exception as e:
                print(f"Erro ao criar diretório {sala_dir}: {e}")
                continue
            
            # Limpar arquivos CSV existentes na pasta da sala
            for csv_file in glob.glob(os.path.join(sala_dir, "*.csv")):
                try:
                    os.remove(csv_file)
                    print(f"Arquivo removido: {csv_file}")
                except Exception as e:
                    print(f"Erro ao remover arquivo {csv_file}: {e}")

            # Gerar CSV para encontrados
            csv_path_encontrados = os.path.join(sala_dir, "encontrados.csv")
            try:
                with open(csv_path_encontrados, mode='w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers_sala)
                    for patrimonio in encontrados:
                        row = list(patrimonio)
                        row[-1] = "Lido"
                        writer.writerow([str(val or "") for val in row])
                print(f"Relatório de encontrados gerado para sala {sala_nome}: {csv_path_encontrados}")
            except Exception as e:
                print(f"Erro ao escrever CSV {csv_path_encontrados}: {e}")

            # Gerar CSV para não encontrados
            csv_path_nao_encontrados = os.path.join(sala_dir, "nao_encontrados.csv")
            try:
                with open(csv_path_nao_encontrados, mode='w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers_sala)
                    for patrimonio in nao_encontrados:
                        row = list(patrimonio)
                        row[-1] = "Não Lido"
                        writer.writerow([str(val or "") for val in row])
                print(f"Relatório de não encontrados gerado para sala {sala_nome}: {csv_path_nao_encontrados}")
            except Exception as e:
                print(f"Erro ao escrever CSV {csv_path_nao_encontrados}: {e}")

    def closeEvent(self, event):
        """Evento de fechamento da janela principal."""
        event.accept()