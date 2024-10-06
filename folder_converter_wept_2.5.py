import os
import glob
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                             QWidget, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QProgressBar, QFileDialog, 
                             QHBoxLayout, QSizePolicy, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PIL import Image

class WorkerThread(QThread):
    progress = pyqtSignal(int, int)
    
    def __init__(self, input_folder, output_folder):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.total_images = 0
        self.completed_images = 0

    def run(self):
        images = glob.glob(os.path.join(self.input_folder, "*.jpg"))  
        self.total_images = len(images)

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        for image_path in images:
            img = Image.open(image_path)
            img = img.convert("RGBA")  
            output_path = os.path.join(self.output_folder, os.path.basename(image_path).replace(".jpg", ".webp"))
            img.save(output_path, "WEBP", quality=65)  
            self.completed_images += 1
            self.progress.emit(self.completed_images, self.total_images)  

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Folder Converter to WebP")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(layout)

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Percorso Cartella", "Immagini Convertite", "Immagini Totali", "Progresso", "Apri la cartella di output"])  # Modifica del titolo della colonna

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  
        header.setStretchLastSection(True)

        # Rimuovi l'intestazione verticale
        self.table.verticalHeader().setVisible(False)

        # Modifica dello stile del titolo delle colonne
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: transparent;
                color: #A0A0A0;  /* Colore grigio per i titoli */
                border: none;
                font-weight: normal;  /* Regular */
            }
            QHeaderView::section:first-child {
                color: black;  /* Colore nero per il titolo della prima colonna */
                font-weight: bold;  /* Grassetto */
            }
        """)
        
        # Alternanza di colore per le righe
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                alternate-background-color: #f0f0f0;  
            }
            QTableWidget::item {
                background-color: transparent;
                color: #A0A0A0; 
            }
        """)

        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  
        layout.addWidget(self.table)

        # Layout orizzontale per i pulsanti
        button_layout = QHBoxLayout()
        
        self.add_folder_button = QPushButton("Aggiungi Cartella")
        self.add_folder_button.setStyleSheet("""
            QPushButton {
                background-color: white; 
                color: #007AFF; 
                border-radius: 5px; 
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #007AFF; 
                color: white;
            }
        """)
        self.add_folder_button.setFixedHeight(40)
        self.add_folder_button.setCursor(Qt.PointingHandCursor)
        self.add_folder_button.clicked.connect(self.add_folder)
        button_layout.addWidget(self.add_folder_button)

        self.close_button = QPushButton("Chiudi")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: black; 
                color: white; 
                border: none; 
                border-radius: 5px; 
                padding: 10px;
            }
            QPushButton:hover {
                background-color: red;
            }
        """)
        self.close_button.setFixedHeight(40)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)  

        # Abilitazione del drag and drop
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            folder = url.toLocalFile()
            if os.path.isdir(folder):
                self.process_folder(folder)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleziona Cartella")
        if folder:
            self.process_folder(folder)

    def process_folder(self, folder):
        output_folder = os.path.join(folder, "convertite")
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        # Imposta i parametri della tabella
        relative_path = os.path.relpath(folder)  
        
        # Crea un nuovo QTableWidgetItem per la prima colonna
        item = QTableWidgetItem(relative_path)  
        item.setFlags(Qt.ItemIsEnabled)  
        item.setForeground(Qt.black)  # Colore nero per la prima colonna
        font = item.font()
        font.setBold(False)  # Regular
        item.setFont(font)  # Imposta il font aggiornato
        self.table.setItem(row_position, 0, item)  

        self.table.setItem(row_position, 1, QTableWidgetItem("0"))  
        self.table.item(row_position, 1).setFlags(Qt.ItemIsEnabled)  
        self.table.setItem(row_position, 2, QTableWidgetItem(str(len(glob.glob(os.path.join(folder, "*.jpg"))))))  
        self.table.item(row_position, 2).setFlags(Qt.ItemIsEnabled)  

        # Crea un widget contenitore per la barra di progresso
        progress_widget = QWidget()
        progress_layout = QVBoxLayout()
        progress_layout.setAlignment(Qt.AlignCenter)  
        progress_widget.setLayout(progress_layout)

        progress_bar = QProgressBar(self)
        progress_bar.setAlignment(Qt.AlignCenter)
        progress_bar.setMaximumHeight(20)  
        progress_bar.setTextVisible(False)  
        progress_bar.setStyleSheet("""
            QProgressBar {
                border-radius: 10px; 
                background-color: #e0e0e0; 
            }
            QProgressBar::chunk {
                background-color: #007AFF; 
                border-radius: 10px; 
            }
        """)

        progress_layout.addWidget(progress_bar)  
        self.table.setCellWidget(row_position, 3, progress_widget)  

        # Pulsante per aprire la cartella di output
        open_button = QPushButton("Vai!")  # Modifica del testo del pulsante
        open_button.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                color: #007AFF; 
                border: 0.5px solid #007AFF; 
                border-radius: 5px; 
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #007AFF; 
                color: white;
            }
        """)
        open_button.clicked.connect(lambda: subprocess.run(["open", output_folder]))  
        self.table.setCellWidget(row_position, 4, open_button)  

        # Avvia il thread di lavoro
        self.worker_thread = WorkerThread(folder, output_folder)
        self.worker_thread.progress.connect(lambda completed, total: self.update_progress(row_position, completed, total))
        self.worker_thread.start()

    def update_progress(self, row_position, completed, total):
        progress_bar = self.table.cellWidget(row_position, 3).findChild(QProgressBar)
        progress_value = int((completed / total) * 100)  
        progress_bar.setValue(progress_value)  
        self.table.item(row_position, 1).setText(str(completed))  

        if progress_value == 100:
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border-radius: 10px; 
                    background-color: #e0e0e0; 
                }
                QProgressBar::chunk {
                    background-color: #90EE90;  
                    border-radius: 10px; 
                }
            """)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
