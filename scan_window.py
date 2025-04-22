from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

class ScanWindow(QDialog):
    def __init__(self, db_manager, parent=None, sala_id=None):
        super().__init__(parent)
        self.setWindowTitle("Escanear Código de Barras")
        self.db_manager = db_manager
        self.parent = parent
        self.sala_id = sala_id
        self.is_processing = False  # Flag para evitar múltiplos escaneamentos simultâneos

        # Configurar modalidade para bloquear a aplicação
        self.setWindowModality(Qt.ApplicationModal)

        # Obter tamanho da tela e definir janela como 80% da tela
        screen = QApplication.primaryScreen().size()
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        self.resize(width, height)
        # Centralizar a janela na tela
        self.move(int((screen.width() - width) / 2), int((screen.height() - height) / 2))

        layout = QVBoxLayout()
        
        # Espaçador superior para centralizar verticalmente
        layout.addStretch(1)
        
        # Instrução
        label = QLabel("Escaneie o número do patrimônio:")
        label.setFont(QFont("Arial", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Label para exibir o nome da sala
        sala_nome = self.get_sala_nome()
        self.sala_label = QLabel(f"Sala: {sala_nome}")
        self.sala_label.setFont(QFont("Arial", 16))
        self.sala_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.sala_label, alignment=Qt.AlignCenter)
        
        # Campo de entrada
        self.input = QLineEdit()
        self.input.setFont(QFont("Arial", 16))
        self.input.setMaximumWidth(400)
        self.input.returnPressed.connect(self.handle_return_pressed)
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

    def get_sala_nome(self):
        """Obtém o nome da sala com base no sala_id."""
        if self.sala_id:
            self.db_manager.cursor.execute("SELECT sala FROM salas WHERE id = ?", (self.sala_id,))
            result = self.db_manager.cursor.fetchone()
            return result[0] if result else "Desconhecida"
        return "Nenhuma sala selecionada"

    def handle_return_pressed(self):
        """Manipula o sinal returnPressed para evitar múltiplas chamadas."""
        if not self.is_processing:
            self.is_processing = True
            self.input.setEnabled(False)  # Desabilitar entrada durante processamento
            QTimer.singleShot(0, self.process_scan)  # Processar no próximo ciclo do evento
            QTimer.singleShot(200, self.reset_processing)  # Redefinir após 200ms

    def reset_processing(self):
        """Redefine a flag de processamento e reativa a entrada."""
        self.is_processing = False
        self.input.setEnabled(True)
        self.input.setFocus()
        self.activateWindow()
        self.raise_()

    def process_scan(self):
        """Processa o escaneamento e mantém a janela aberta para escaneamento contínuo."""
        numero = self.input.text().strip()
        print(f"Processando escaneamento: '{numero}'")  # Log para depuração
        
        if not numero:
            self.feedback_label.setText("Nenhum código escaneado.")
            self.input.clear()
            return
        
        # Usar o sala_id passado no construtor
        if not self.sala_id:
            self.feedback_label.setText("Nenhuma sala selecionada.")
            self.input.clear()
            return
        
        if self.db_manager.mark_patrimonio_encontrado(numero, self.sala_id):
            self.feedback_label.setText(f"Patrimônio {numero} encontrado na sala {self.sala_label.text().replace('Sala: ', '')}.")
            # Atualizar a tabela de patrimônios na janela principal
            if self.parent:
                self.parent.update_patrimonios_table()
        else:
            self.feedback_label.setText(f"Patrimônio {numero} não encontrado.")
        
        self.input.clear()

    def keyPressEvent(self, event):
        """Impede que a tecla Enter ou Esc feche a janela."""
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            if not self.is_processing:
                self.handle_return_pressed()  # Chamar manipulador para Enter/Return
            event.accept()  # Impedir propagação
        elif event.key() == Qt.Key_Escape:
            event.accept()  # Impedir fechamento com Esc (ajustável)
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Evento de fechamento da ScanWindow."""
        try:
            if self.parent is not None:
                self.parent.showMaximized()  # Restaurar a janela principal apenas ao fechar
        except Exception as e:
            print(f"Erro ao restaurar a janela principal: {e}")
        event.accept()