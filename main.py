import sys
import warnings

# Suprimir o DeprecationWarning do SIP antes de importar PyQt5
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sip")

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SUAP-CD - Coletor de Dados")

        # Layout principal
        layout = QVBoxLayout()
        
        # Espaçador superior para centralização vertical
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Configurar o QLabel centralizado
        label = QLabel("Bem-vindo ao SUAP-CD!", self)
        label.setFont(QFont("Arial", 16))  # Fonte maior (16pt)
        label.setAlignment(Qt.AlignCenter)  # Centralizar o texto horizontalmente
        layout.addWidget(label)
        
        # Configurar o QPushButton
        button = QPushButton("Clique aqui", self)
        button.setFont(QFont("Arial", 14))  # Fonte um pouco menor (14pt)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # Garantir tamanho fixo para centralização
        layout.addWidget(button, alignment=Qt.AlignCenter)  # Centralizar o botão no layout
        
        # Espaçador inferior para centralização vertical
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Container
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def on_button_click(self):
        print("Botão clicado!")

if __name__ == "__main__":
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