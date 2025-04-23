import smtplib
from email.mime.text import MIMEText
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS

def enviar_email(destinatario, assunto, mensagem):
    """Função para enviar e-mail usando SMTP."""
    msg = MIMEText(mensagem)
    msg["Subject"] = assunto
    msg["From"] = EMAIL_USER
    msg["To"] = destinatario

    try:
        # Conectando ao servidor SMTP e utilizando o contexto de 'with' para garantir o fechamento correto
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as servidor:
            servidor.starttls()  # Inicia a conexão segura
            servidor.login(EMAIL_USER, EMAIL_PASS)  # Realiza login
            servidor.sendmail(EMAIL_USER, destinatario, msg.as_string())  # Envia o e-mail
            print(f"E-mail enviado com sucesso para {destinatario}")  # Confirmação de envio
    except Exception as e:
        # Captura e exibe erros, caso ocorram
        print(f"Erro ao enviar e-mail: {e}")
