# 🔐 Sistema de Autenticação em Flask

Este projeto é um sistema completo de autenticação desenvolvido com **Flask**, incluindo funcionalidades modernas como:

- Registro de usuários com senha segura
- Verificação de e-mail com código de ativação
- Login protegido por sessão
- Recuperação de senha por e-mail com token único
- Redefinição de senha segura

---

## 📌 Funcionalidades

- ✅ Registro com validação de senha forte (mínimo 8 caracteres, número, letra maiúscula e caractere especial)
- ✅ Verificação por e-mail com código de 6 dígitos
- ✅ Login com proteção contra acesso sem verificação
- ✅ Recuperação de senha por link/token enviado por e-mail
- ✅ Redefinição de senha com validações
- ✅ Sessão ativa e logout
- ✅ Mensagens de feedback com `flash()`

---

## 🧰 Tecnologias utilizadas

- [Python 3.11+](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/)
- SQLite (banco de dados embutido)
- SMTP (protocolo de envio de e-mail)
- Jinja2 (template engine)

---

## ⚙️ Como rodar o projeto

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/flask-auth-system.git
   cd Trabalho_Login_py
   
