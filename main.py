import warnings
# Suprimir todos os DeprecationWarning relacionados ao SIP antes de qualquer importação
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import argparse
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget,
    QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from database import init_database, load_data_from_file

class MainWindow(QMainWindow):
    def __init__(self, load_file=None):
        super().__init__()
        self.setWindowTitle("SUAP-CD - Coletor de Dados")

        # Inicializar o banco de dados
        self.conn, self.cursor = init_database()

        # Se um arquivo foi passado via -load, zerar e carregar dados
        if load_file:
            load_data_from_file(self.cursor, self.conn, load_file)

        # Layout principal
        layout = QVBoxLayout()
        
        # Espaçador superior para centralização vertical
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Configurar o QLabel centralizado
        label = QLabel("Bem-vindo ao SUAP-CD!", self)
        label.setFont(QFont("Arial", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Botão de teste
        test_button = QPushButton("Clique aqui", self)
        test_button.setFont(QFont("Arial", 14))
        test_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        test_button.clicked.connect(self.on_button_click)
        layout.addWidget(test_button, alignment=Qt.AlignCenter)
        
        # Espaçador inferior para centralização vertical
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Container
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_button_click(self):
        print("Botão clicado!")

    def closeEvent(self, event):
        # Fechar conexão com o banco ao fechar a janela
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    # Habilitar suporte a High DPI
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Parsear argumentos da linha de comando
    parser = argparse.ArgumentParser(description="SUAP-CD - Coletor de Dados")
    parser.add_argument("-load", type=str, help="Caminho do arquivo CSV para carregar dados")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = MainWindow(load_file=args.load)
    
    # Ajustar tamanho da janela para a tela do cliente
    screen = app.primaryScreen()
    size = screen.size()
    window.resize(size)
    
    # Maximizar a janela
    window.showMaximized()
    
    sys.exit(app.exec_())