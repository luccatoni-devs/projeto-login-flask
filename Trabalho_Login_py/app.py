import os
import random
import sqlite3
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import SECRET_KEY, EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS, DATABASE
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = SECRET_KEY

CARACTERES_ESPECIAIS = "!@#$%^&*(),.?\":{}|<>"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def criar_tabelas():
    """Cria a tabela de usuários no banco de dados, caso não exista."""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                verificado INTEGER DEFAULT 0,
                codigo_verificacao TEXT,
                token_recuperacao TEXT
            )
        ''')
        conn.commit()

import secrets

def gerar_token_recuperacao():
    """Gera um token de recuperação de senha seguro e aleatório."""
    return secrets.token_hex(16)  # Gera um token de 32 caracteres em hexadecimal

def enviar_email_verificacao(destinatario, codigo):
    """Envia um e-mail de verificação com o código gerado."""
    msg = MIMEText(f"Seu código de verificação é: {codigo}")
    msg["Subject"] = "Código de Verificação"
    msg["From"] = EMAIL_USER
    msg["To"] = destinatario
    
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, destinatario, msg.as_string())
        return True
    except Exception as e:
        print("Erro ao enviar email:", e)
        return False

def enviar_email_recuperacao(destinatario, token):
    """Envia um e-mail de recuperação de senha com o token gerado."""
    url_recuperacao = url_for('recuperar_senha', token=token, _external=True)  # Gera o link completo
    corpo_email = f"""
    <html>
    <body>
        <h2>Recuperação de Senha</h2>
        <p>Olá,</p>
        <p>Recebemos uma solicitação para redefinir sua senha. Para continuar, clique no link abaixo:</p>
        <p><a href="{url_recuperacao}">Clique aqui para redefinir sua senha</a></p>
        <p>Se você não solicitou a recuperação de senha, ignore este e-mail.</p>
        <br>
        <p>Atenciosamente,</p>
        <p>Equipe do Sistema</p>
    </body>
    </html>
    """
    msg = MIMEText(corpo_email, 'html')
    msg["Subject"] = "Recuperação de Senha"
    msg["From"] = EMAIL_USER
    msg["To"] = destinatario
    
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, destinatario, msg.as_string())
        return True
    except Exception as e:
        print("Erro ao enviar email:", e)
        return False

@app.route("/recuperar_senha", methods=["GET", "POST"])
def recuperar_senha():
    """Página para solicitar recuperação de senha e enviar o link com token."""
    if request.method == "POST":
        email = request.form["email"]
        
        # Gerando o token de recuperação
        token = gerar_token_recuperacao()

        # Armazenando o token no banco de dados associado ao e-mail
        with get_db_connection() as conn:
            # Atualiza o banco com o token gerado para o e-mail fornecido
            conn.execute("UPDATE usuarios SET token_recuperacao = ? WHERE email = ?", (token, email))
            conn.commit()

        # Enviando o e-mail com o link de recuperação
        if enviar_email_recuperacao(email, token):
            flash("Um e-mail foi enviado com as instruções para recuperar sua senha.", "success")
        else:
            flash("Erro ao enviar o e-mail. Tente novamente.", "danger")
        
    return render_template("recuperar_senha.html")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        print(f"[LOGIN] Tentativa de login para: {email}")

        with get_db_connection() as conn:
            usuario = conn.execute("SELECT id, verificado, senha FROM usuarios WHERE email = ?", (email,)).fetchone()

        if usuario and check_password_hash(usuario["senha"], senha):
            if usuario["verificado"] == 0:
                flash("Conta não verificada. Verifique seu e-mail.", "danger")
                return redirect(url_for("verificar", email=email))
            session["usuario_id"] = usuario["id"]
            flash("Login bem-sucedido!", "success")
            return redirect(url_for("dashboard"))

        flash("E-mail ou senha incorretos.", "danger")
    return render_template("index.html")

@app.route("/registro", methods=["GET", "POST"])
def registro():
    """Página de registro do usuário."""
    if request.method == "POST":
        nome = request.form["nome"]  # Novo campo Nome
        email = request.form["email"]
        senha = request.form["senha"]
        confirmar_senha = request.form["confirmar_senha"]
        
        if senha != confirmar_senha:
            flash("As senhas não coincidem.", "danger")
            return redirect(url_for("registro"))

        # Verificação da força da senha
        if len(senha) < 8 or not any(c.isupper() for c in senha) or not any(c.isdigit() for c in senha) or not any(c in "!@#$%^&*(),.?\":{}|<>" for c in senha):
            flash("A senha deve ter pelo menos 8 caracteres, incluindo uma letra maiúscula, um número e um caractere especial.", "danger")
            return redirect(url_for("registro"))
        
        # Gerando o hash da senha
        senha_hash = generate_password_hash(senha)

        codigo_verificacao = str(random.randint(100000, 999999))
        
        with get_db_connection() as conn:
            try:
                # Salvando o nome no banco
                conn.execute("INSERT INTO usuarios (nome, email, senha, codigo_verificacao) VALUES (?, ?, ?, ?)", (nome, email, senha_hash, codigo_verificacao))
                conn.commit()
                enviar_email_verificacao(email, codigo_verificacao)
                flash("Registro bem-sucedido! Verifique seu e-mail.", "success")
                return redirect(url_for("verificar", email=email))
            except sqlite3.IntegrityError:
                flash("E-mail já cadastrado!", "danger")
    return render_template("registro.html")

@app.route("/verificar/<email>", methods=["GET", "POST"])
def verificar(email):
    with get_db_connection() as conn:
        usuario = conn.execute("SELECT id FROM usuarios WHERE email = ?", (email,)).fetchone()
        if not usuario:
            flash("E-mail inválido.", "danger")
            return redirect(url_for("login"))

        if request.method == "POST":
            codigo_digitado = request.form["codigo"]
            usuario = conn.execute("SELECT id FROM usuarios WHERE email = ? AND codigo_verificacao = ?", (email, codigo_digitado)).fetchone()
            if usuario:
                conn.execute("UPDATE usuarios SET verificado = 1 WHERE email = ?", (email,))
                conn.commit()
                session["usuario_id"] = usuario["id"]
                flash("Conta verificada com sucesso!", "success")
                return redirect(url_for("dashboard"))

            flash("Código incorreto!", "danger")
    return render_template("verificar.html", email=email)

@app.route("/dashboard")
def dashboard():
    if "usuario_id" not in session:
        flash("Você precisa estar logado!", "danger")
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    flash("Você saiu da sessão.", "info")
    return redirect(url_for("login"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('erro.html', mensagem="Página não encontrada."), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('erro.html', mensagem="Erro interno no servidor."), 500

@app.route("/resetar_senha/<token>", methods=["GET", "POST"])
def resetar_senha(token):
    """Página para redefinir a senha, validando o token de recuperação."""

    # Verificando se o token existe no banco de dados
    with get_db_connection() as conn:
        usuario = conn.execute("SELECT id FROM usuarios WHERE token_recuperacao = ?", (token,)).fetchone()

    if not usuario:
        flash("Token inválido ou expirado.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        nova_senha = request.form["nova_senha"]
        confirmar_senha = request.form["confirmar_senha"]

        if nova_senha != confirmar_senha:
            flash("As senhas não coincidem.", "danger")
            return redirect(url_for("resetar_senha", token=token))

        # Verificação da força da senha
        if len(nova_senha) < 8 or not any(c.isupper() for c in nova_senha) or not any(c.isdigit() for c in nova_senha) or not any(c in "!@#$%^&*(),.?\":{}|<>" for c in nova_senha):
            flash("A senha deve ter pelo menos 8 caracteres, incluindo uma letra maiúscula, um número e um caractere especial.", "danger")
            return redirect(url_for("resetar_senha", token=token))

        # Gerando o hash da nova senha
        senha_hash = generate_password_hash(nova_senha)

        # Atualizando a senha no banco de dados
        with get_db_connection() as conn:
            conn.execute("UPDATE usuarios SET senha = ?, token_recuperacao = NULL WHERE token_recuperacao = ?", (senha_hash, token))
            conn.commit()

        flash("Senha atualizada com sucesso!", "success")
        return redirect(url_for("login"))

    return render_template("resetar_senha.html", token=token)

if __name__ == "__main__":
    criar_tabelas()
    app.run(debug=True)