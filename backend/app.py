from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql
from decouple import config
import bcrypt
import re

app = Flask(__name__)

# =================== CONFIGURAÇÃO DA CONEXÃO COM O BANCO DE DADOS ===================
def get_db_connection():
    """
    Estabelece uma conexão com o banco de dados PostgreSQL utilizando variáveis de ambiente.
    Retorna um objeto de conexão.
    """
    return psycopg2.connect(
        host=config('HOST_PGSQL'),
        database=config('NAME_PGSQL'),
        user=config('USER_PGSQL'),
        password=config('PASS_PGSQL')
    )

# =================== CRIAÇÃO DA TABELA SE NÃO EXISTIR ===================
def create_table():
    """
    Cria a tabela 'users' no banco de dados caso ainda não exista.
    Utiliza UUID como chave primária e armazena a senha de forma segura.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Habilita a extensão UUID, caso necessário
    cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    
    # Criação da tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            email_user_second VARCHAR(255),
            passw TEXT NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# =================== FUNÇÃO PARA VALIDAR FORMATO DE E-MAIL ===================
def validar_email(email):
    """
    Valida se o e-mail fornecido segue um formato válido utilizando regex.
    Retorna True se for válido e False caso contrário.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))

# =================== ROTA DE REGISTRO DE USUÁRIO ===================
@app.route('/api/register', methods=['POST'])
def register_user():
    """
    Rota para registrar um novo usuário no banco de dados.
    Utiliza bcrypt para armazenar a senha de forma segura.
    """
    data = request.get_json()
    
    # Verifica se os campos obrigatórios estão presentes
    if not data.get('user_name') or not data.get('email') or not data.get('passw'):
        return jsonify({"message": "Campos obrigatórios ausentes. Forneça 'user_name', 'email' e 'passw'."}), 400
    
    user_name = data['user_name']
    email = data['email']
    email_user_second = data.get('email_user_second', '')  # Opcional
    passw = data['passw']
    
    # Valida o formato do e-mail
    if not validar_email(email):
        return jsonify({"message": "Formato de e-mail inválido."}), 422
    
    # Hash da senha usando bcrypt
    hashed_password = bcrypt.hashpw(passw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se o e-mail já está cadastrado
        cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            return jsonify({"message": "Este e-mail já está registrado."}), 409
        
        # Insere o novo usuário no banco
        cursor.execute(
            'INSERT INTO users (user_name, email, email_user_second, passw) VALUES (%s, %s, %s, %s) RETURNING id, user_name, email, email_user_second',
            (user_name, email, email_user_second, hashed_password)
        )
        user = cursor.fetchone()
        conn.commit()
        
        return jsonify({
            "message": "Usuário registrado com sucesso!",
            "user": {
                "id": str(user[0]),
                "user_name": user[1],
                "email": user[2],
                "email_user_second": user[3]
            }
        }), 201
    except Exception as e:
        return jsonify({"message": "Erro ao registrar usuário", "error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# =================== ROTA DE LOGIN ===================
@app.route('/api/login', methods=['POST'])
def login_user():
    """
    Rota para autenticar um usuário verificando o e-mail e a senha.
    """
    data = request.get_json()
    email = data.get('email')
    passw = data.get('passw')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, user_name, email, passw FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    # Verifica se o usuário existe e se a senha está correta
    if user and bcrypt.checkpw(passw.encode('utf-8'), user[3].encode('utf-8')):
        return jsonify({
            "message": "Login realizado com sucesso!",
            "user": {
                "id": str(user[0]),
                "user_name": user[1],
                "email": user[2]
            }
        }), 200
    else:
        return jsonify({"message": "Credenciais inválidas. Login não realizado."}), 401

# =================== ROTA PARA LISTAR USUÁRIOS ===================
@app.route('/api/users', methods=['GET'])
def get_users():
    """
    Rota para obter todos os usuários cadastrados.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, user_name, email, email_user_second FROM users')
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if users:
            return jsonify([
                {"id": str(u[0]), "user_name": u[1], "email": u[2], "email_user_second": u[3]} for u in users
            ]), 200
        else:
            return jsonify({"message": "Nenhum usuário encontrado."}), 404
    except Exception as e:
        return jsonify({"message": "Erro ao buscar usuários", "error": str(e)}), 500

# =================== EXECUÇÃO DA APLICAÇÃO ===================
if __name__ == '__main__':
    create_table()
    app.run(debug=True, host='0.0.0.0', port=5000)


























# Objetivo:
# Este script define uma aplicação Flask que oferece rotas para registrar, autenticar e listar usuários utilizando um banco de dados PostgreSQL. As senhas dos usuários são armazenadas de forma segura utilizando bcrypt.

# Funções e Componentes:
# get_db_connection()

# Descrição: Estabelece uma conexão com o banco de dados PostgreSQL utilizando variáveis de ambiente (como HOST_PGSQL, NAME_PGSQL, USER_PGSQL, PASS_PGSQL).

# Retorno: Retorna um objeto de conexão do PostgreSQL.

# create_table()

# Descrição: Cria a tabela users no banco de dados, caso ela não exista. A tabela possui campos como user_name, email, email_user_second (opcional) e passw (senha).

# Nota: Utiliza o tipo UUID para o campo id como chave primária.

# validar_email(email)

# Descrição: Valida se o formato do e-mail fornecido está correto utilizando expressões regulares (regex).

# Retorno: Retorna True se o e-mail for válido e False caso contrário.

# Rotas da API:
# 1. POST /api/register - Registro de Usuário
# Descrição: Permite o cadastro de um novo usuário, realizando validações no e-mail e armazenando a senha de forma segura (com hash usando bcrypt).

# Requisição (Body JSON):

# json

# {
#   "user_name": "Nome do Usuário",
#   "email": "email@dominio.com",
#   "passw": "senha123",
#   "email_user_second": "emailsecundario@dominio.com" (opcional)
# }
# Resposta de Sucesso (Status 201):

# json

# {
#   "message": "Usuário registrado com sucesso!",
#   "user": {
#     "id": "UUID_do_usuario",
#     "user_name": "Nome do Usuário",
#     "email": "email@dominio.com",
#     "email_user_second": "emailsecundario@dominio.com"
#   }
# }
# Resposta de Erro: Caso campos obrigatórios estejam ausentes ou o formato de e-mail seja inválido, o script retorna uma mensagem de erro.

# 2. POST /api/login - Login de Usuário
# Descrição: Permite que o usuário faça login utilizando o e-mail e a senha. A senha é verificada com bcrypt.

# Requisição (Body JSON):

# json

# {
#   "email": "email@dominio.com",
#   "passw": "senha123"
# }
# Resposta de Sucesso (Status 200):

# json

# {
#   "message": "Login realizado com sucesso!",
#   "user": {
#     "id": "UUID_do_usuario",
#     "user_name": "Nome do Usuário",
#     "email": "email@dominio.com"
#   }
# }
# Resposta de Erro (Status 401): Caso as credenciais sejam inválidas, retorna uma mensagem de erro.

# 3. GET /api/users - Listar Usuários
# Descrição: Retorna uma lista de todos os usuários cadastrados no banco de dados.

# Resposta de Sucesso (Status 200):

# json

# [
#   {
#     "id": "UUID_do_usuario",
#     "user_name": "Nome do Usuário",
#     "email": "email@dominio.com",
#     "email_user_second": "emailsecundario@dominio.com"
#   }
# ]
# Resposta de Erro (Status 404): Caso não haja usuários registrados, retorna uma mensagem indicando que nenhum usuário foi encontrado.

# Execução:
# create_table(): Antes de iniciar o servidor Flask, a função create_table() é chamada para garantir que a tabela users exista no banco de dados.

# Servidor Flask: A aplicação é executada em modo de depuração (debug=True) e escuta na porta 5000.

# Considerações:
# Segurança de Senhas: As senhas são sempre armazenadas de forma segura utilizando bcrypt para hashing.

# Validação de E-mail: O formato do e-mail é validado utilizando uma expressão regular para garantir que o e-mail esteja correto antes de ser registrado.

# Requisitos:
# Banco de Dados PostgreSQL configurado com as credenciais armazenadas em variáveis de ambiente.

# Bibliotecas Necessárias:

# Flask: Para criar a aplicação web.

# psycopg2: Para conectar e interagir com o banco de dados PostgreSQL.

# bcrypt: Para fazer o hash das senhas.

# re: Para validação do formato de e-mail com expressões regulares.

# decouple: Para carregar as variáveis de ambiente de forma segura.

