from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ScanWindow(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Escanear Código de Barras")
        self.db_manager = db_manager
        self.parent = parent

        # Configurar modalidade para bloquear a aplicação
        self.setWindowModality(Qt.ApplicationModal)
        self.showMaximized()

        layout = QVBoxLayout()
        
        # Espaçador superior para centralizar verticalmente
        layout.addStretch(1)
        
        # Instrução
        label = QLabel("Escaneie o número do patrimônio:")
        label.setFont(QFont("Arial", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Campo de entrada
        self.input = QLineEdit()
        self.input.setFont(QFont("Arial", 16))
        self.input.setMaximumWidth(400)
        self.input.returnPressed.connect(self.process_scan)
        layout.addWidget(self.input, alignment=Qt.AlignCenter)
        
        # Label para feedback
        self.feedback_label = QLabel("")
        self.feedback_label.setFont(QFont("Arial", 14))
        self.feedback_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.feedback_label)
        
        # Botão para fechar a janela
        close_button = QPushButton("Fechar")
        close_button.setFont(QFont("Arial", 12))
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)
        
        # Espaçador inferior
        layout.addStretch(1)
        
        self.setLayout(layout)
        self.input.setFocus()

    def process_scan(self):
        numero = self.input.text().strip()
        if not numero:
            self.feedback_label.setText("Nenhum código escaneado.")
            self.input.clear()
            return
        
        if self.db_manager.mark_patrimonio_encontrado(numero):
            self.feedback_label.setText(f"Patrimônio {numero} encontrado.")
            # Atualizar a tabela de patrimônios na janela principal
            if self.parent:
                self.parent.update_patrimonios_table()
        else:
            self.feedback_label.setText(f"Patrimônio {numero} não encontrado.")
        
        self.input.clear()
        self.input.setFocus()

    def closeEvent(self, event):
        """Evento de fechamento da ScanWindow."""
        try:
            if self.parent is not None:
                self.parent.showMaximized()
        except Exception as e:
            print(f"Erro ao restaurar a janela principal: {e}")
        event.accept()