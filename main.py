import warnings
# Suprimir todos os DeprecationWarning antes de qualquer importação
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import argparse
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget,
    QSpacerItem, QSizePolicy, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import init_database, load_data_from_file, get_all_salas, get_patrimonios_by_sala

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SUAP-CD - Coletor de Dados")

        # Inicializar o banco de dados
        self.conn, self.cursor = init_database()

        # Layout principal
        layout = QVBoxLayout()
        
        # Espaçador superior reduzido
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Título
        label = QLabel("Bem-vindo ao SUAP-CD!", self)
        label.setFont(QFont("Arial", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # ComboBox para selecionar salas
        self.sala_combo = QComboBox(self)
        self.sala_combo.setFont(QFont("Arial", 12))
        self.sala_combo.addItem("Selecione uma sala", None)
        self.populate_sala_combo()
        self.sala_combo.currentIndexChanged.connect(self.update_patrimonios_table)
        layout.addWidget(self.sala_combo, alignment=Qt.AlignCenter)
        
        # Tabela para exibir patrimônios
        self.table = QTableWidget(self)
        self.table.setColumnCount(16)
        self.table.setHorizontalHeaderLabels([
            "Número", "Status", "ED", "Descrição", "Rótulos", "Carga Atual",
            "Setor Responsável", "Campus Carga", "Valor Aquisição",
            "Valor Depreciado", "Nota Fiscal", "Número de Série",
            "Data Entrada", "Data Carga", "Fornecedor", "Estado Conservação"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setFont(QFont("Arial", 10))
        layout.addWidget(self.table, stretch=1)  # Expandir a tabela verticalmente
        
        # Espaçador inferior reduzido
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Container
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def populate_sala_combo(self):
        """Popula o QComboBox com todas as salas da tabela salas."""
        salas = get_all_salas(self.cursor)
        for sala_id, sala_nome in salas:
            self.sala_combo.addItem(sala_nome, sala_id)

    def update_patrimonios_table(self):
        """Atualiza a tabela de patrimônios com base na sala selecionada."""
        sala_id = self.sala_combo.currentData()
        self.table.setRowCount(0)  # Limpar tabela
        if sala_id is None:
            return
        
        patrimonios = get_patrimonios_by_sala(self.cursor, sala_id)
        self.table.setRowCount(len(patrimonios))
        for row_idx, row_data in enumerate(patrimonios):
            # Ignorar o campo sala (índice 15) e mapear os outros 16 campos
            for col_idx in range(16):
                value = row_data[col_idx] if col_idx < 15 else row_data[col_idx + 1]
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value or "")))

    def closeEvent(self, event):
        # Fechar conexão com o banco ao fechar a janela
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    # Parsear argumentos da linha de comando
    parser = argparse.ArgumentParser(description="SUAP-CD - Coletor de Dados")
    parser.add_argument("-load", type=str, help="Caminho do arquivo CSV para carregar dados")
    args = parser.parse_args()

    if args.load:
        # Modo não gráfico: apenas carregar o CSV e sair
        conn, cursor = init_database()
        load_data_from_file(cursor, conn, args.load)
        conn.close()
        sys.exit(0)

    # Modo gráfico: abrir a interface
    # Habilitar suporte a High DPI
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Ajustar tamanho da janela para a tela do cliente
    screen = app.primaryScreen()
    size = screen.size()
    window.resize(size)
    
    # Maximizar a janela
    window.showMaximized()
    
    sys.exit(app.exec_())