import os

# Chave secreta para sessões e proteção de dados em Flask
SECRET_KEY = os.getenv("SECRET_KEY", "chave_secreta_super_segura")

# Configurações do servidor de e-mail para envio de mensagens
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))  # A porta 587 é geralmente usada para SMTP com TLS
EMAIL_USER = os.getenv("EMAIL_USER", "figmaaluno@gmail.com")  # Substitua com seu e-mail para envio
EMAIL_PASS = os.getenv("EMAIL_PASS", "aluno98406612")  # Substitua com a senha de app gerada no Gmail

# Caminho para o banco de dados SQLite
DATABASE = "database.db"  # Define o nome e o caminho do banco de dados (pode ser ajustado conforme necessário)
