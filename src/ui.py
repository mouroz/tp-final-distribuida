# -*- coding: utf-8 -*-
"""
UI Module - PyQt6 interface for the distributed messaging system.
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit, QMessageBox,
    QSplitter, QFrame, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Add comm folder to path for imports
comm_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comm")
grpc_dir = os.path.join(comm_dir, "grpc_messenger")
if comm_dir not in sys.path:
    sys.path.insert(0, comm_dir)
if grpc_dir not in sys.path:
    sys.path.insert(0, grpc_dir)

import client as cli


class ServerConfigWindow(QMainWindow):
    """Window for configuring server connections before entering chat."""
    
    def __init__(self):
        super().__init__()
        self.servers = []
        self.connections = []
        self.user_email = ""
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Configuração de Servidores")
        self.setMinimumSize(500, 400)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Sistema de Mensagens Distribuído")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Server input section
        server_frame = QFrame()
        server_frame.setFrameShape(QFrame.Shape.StyledPanel)
        server_layout = QVBoxLayout(server_frame)
        
        server_label = QLabel("Adicionar Servidor:")
        server_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        server_layout.addWidget(server_label)
        
        input_layout = QHBoxLayout()
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("IP (ex: localhost)")
        self.ip_input.setText("localhost")
        input_layout.addWidget(self.ip_input, 2)
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Porta (ex: 50051)")
        self.port_input.setText("50051")
        input_layout.addWidget(self.port_input, 1)
        
        self.add_btn = QPushButton("Adicionar")
        self.add_btn.clicked.connect(self.add_server)
        input_layout.addWidget(self.add_btn)
        
        server_layout.addLayout(input_layout)
        layout.addWidget(server_frame)
        
        # Server list
        list_label = QLabel("Servidores Adicionados:")
        list_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(list_label)
        
        self.server_list = QListWidget()
        layout.addWidget(self.server_list)
        
        # Remove button
        self.remove_btn = QPushButton("Remover Selecionado")
        self.remove_btn.clicked.connect(self.remove_server)
        layout.addWidget(self.remove_btn)
        
        # Email input
        email_layout = QHBoxLayout()
        email_label = QLabel("Seu Email:")
        email_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        email_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("seu_email@exemplo.com")
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)
        
        # Connect button
        self.connect_btn = QPushButton("Conectar")
        self.connect_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.connect_btn.setMinimumHeight(40)
        self.connect_btn.clicked.connect(self.connect_to_servers)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.connect_btn)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    def add_server(self):
        ip = self.ip_input.text().strip()
        port = self.port_input.text().strip()
        
        if not ip or not port:
            QMessageBox.warning(self, "Aviso", "Preencha IP e Porta.")
            return
        
        address = f"{ip}:{port}"
        if address not in self.servers:
            self.servers.append(address)
            self.server_list.addItem(address)
            self.port_input.clear()
    
    def remove_server(self):
        current = self.server_list.currentRow()
        if current >= 0:
            self.servers.pop(current)
            self.server_list.takeItem(current)
    
    def connect_to_servers(self):
        if not self.servers:
            QMessageBox.warning(self, "Aviso", "Adicione ao menos um servidor.")
            return
        
        email = self.email_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Aviso", "Digite seu email.")
            return
        
        self.status_label.setText("Conectando...")
        self.status_label.setStyleSheet("color: orange;")
        QApplication.processEvents()
        
        connections, failed = cli.connect_to_servers(self.servers)
        
        if not connections:
            self.status_label.setText("Falha: Nenhum servidor disponível.")
            self.status_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "Erro", 
                f"Não foi possível conectar a nenhum servidor.\nFalhas: {', '.join(failed)}")
            return
        
        if failed:
            QMessageBox.warning(self, "Aviso", 
                f"Alguns servidores falharam: {', '.join(failed)}")
        
        self.connections = connections
        self.user_email = email
        self.status_label.setText(f"Conectado a {len(connections)} servidor(es)!")
        self.status_label.setStyleSheet("color: green;")
        
        # Open chat window
        self.chat_window = ChatWindow(self.connections, self.user_email)
        self.chat_window.show()
        self.hide()


class ChatWindow(QMainWindow):
    """Main chat window for sending and receiving messages."""
    
    def __init__(self, connections: list[cli.ServerConnection], user_email: str):
        super().__init__()
        self.connections = connections
        self.user_email = user_email
        self.message_id_counter = 1
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Chat - {self.user_email}")
        self.setMinimumSize(600, 500)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_layout = QHBoxLayout()
        
        user_label = QLabel(f"Logado como: {self.user_email}")
        user_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header_layout.addWidget(user_label)
        
        header_layout.addStretch()
        
        servers_label = QLabel(f"Servidores conectados: {len(self.connections)}")
        servers_label.setStyleSheet("color: green;")
        header_layout.addWidget(servers_label)
        
        layout.addLayout(header_layout)
        
        # Inbox section
        inbox_label = QLabel("Caixa de Entrada:")
        inbox_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(inbox_label)
        
        self.inbox_list = QListWidget()
        self.inbox_list.setMinimumHeight(200)
        layout.addWidget(self.inbox_list)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Atualizar Inbox")
        self.refresh_btn.clicked.connect(self.refresh_inbox)
        layout.addWidget(self.refresh_btn)
        
        # Compose section
        compose_label = QLabel("Enviar Mensagem:")
        compose_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(compose_label)
        
        dest_layout = QHBoxLayout()
        dest_label = QLabel("Para:")
        dest_layout.addWidget(dest_label)
        self.dest_input = QLineEdit()
        self.dest_input.setPlaceholderText("email_destinatario@exemplo.com")
        dest_layout.addWidget(self.dest_input)
        layout.addLayout(dest_layout)
        
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Digite sua mensagem...")
        self.message_input.setMaximumHeight(100)
        layout.addWidget(self.message_input)
        
        # Send button
        self.send_btn = QPushButton("📤 Enviar")
        self.send_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.send_btn.setMinimumHeight(35)
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        layout.addWidget(self.send_btn)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    def refresh_inbox(self):
        self.status_label.setText("Atualizando...")
        self.status_label.setStyleSheet("color: orange;")
        QApplication.processEvents()
        
        try:
            inbox_responses = cli.receive_all_messages(self.connections, self.user_email)
            unique_messages = cli.extract_receive_all_unique_responses(inbox_responses)
            
            self.inbox_list.clear()
            
            if not unique_messages:
                self.inbox_list.addItem("(Nenhuma mensagem)")
            else:
                for msg_id, msg_text, sender_email, dest_email in unique_messages:
                    item_text = f"📧 De: {sender_email}\n   {msg_text}"
                    item = QListWidgetItem(item_text)
                    self.inbox_list.addItem(item)
            
            self.status_label.setText(f"Inbox atualizado: {len(unique_messages)} mensagem(s)")
            self.status_label.setStyleSheet("color: green;")
            
        except Exception as e:
            self.status_label.setText(f"Erro: {str(e)}")
            self.status_label.setStyleSheet("color: red;")
    
    def send_message(self):
        dest_email = self.dest_input.text().strip()
        message = self.message_input.toPlainText().strip()
        
        if not dest_email:
            QMessageBox.warning(self, "Aviso", "Digite o email do destinatário.")
            return
        
        if not message:
            QMessageBox.warning(self, "Aviso", "Digite uma mensagem.")
            return
        
        self.status_label.setText("Enviando...")
        self.status_label.setStyleSheet("color: orange;")
        QApplication.processEvents()
        
        try:
            failed_servers = cli.send_messages(
                id=self.message_id_counter,
                connections=self.connections,
                dest_message=message,
                self_email=self.user_email,
                dest_email=dest_email
            )
            
            self.message_id_counter += 1
            
            if failed_servers:
                self.status_label.setText(f"Enviado (falha em {len(failed_servers)} servidor(es))")
                self.status_label.setStyleSheet("color: orange;")
            else:
                self.status_label.setText("Mensagem enviada com sucesso!")
                self.status_label.setStyleSheet("color: green;")
                self.message_input.clear()
                
        except Exception as e:
            self.status_label.setText(f"Erro: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def closeEvent(self, event):
        """Handle window close - close all connections."""
        for conn in self.connections:
            try:
                conn.channel.close()
            except:
                pass
        event.accept()
