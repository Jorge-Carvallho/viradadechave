from flask import Flask, request, jsonify
import psycopg2
from decouple import config

app = Flask(__name__)

# Configuração de conexão com o PostgreSQL
def get_db_connection():
    """ 
    Estabelece conexão com o banco de dados PostgreSQL utilizando variáveis de ambiente.
    """
    conn = psycopg2.connect(
        host=config('HOST_PGSQL'),         # Nome do host do banco de dados
        database=config('NAME_PGSQL'),      # Nome do banco de dados
        user=config('USER_PGSQL'),          # Usuário do banco
        password=config('PASS_PGSQL')       # Senha do banco
    )
    return conn

# Função para criar a tabela users se não existir
def create_table():
    """ 
    Cria a tabela 'users' no banco de dados caso ela ainda não exista.
    Utiliza UUID como chave primária.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')  # Habilita extensão UUID, se necessário
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),  -- Gera um ID único automaticamente
            user_name VARCHAR(255) NOT NULL,   -- Nome do usuário (campo obrigatório)
            email VARCHAR(255) NOT NULL,       -- Email principal (campo obrigatório)
            email_user_second VARCHAR(255),    -- Email secundário (opcional)
            passw VARCHAR(255) NOT NULL        -- Senha do usuário (campo obrigatório)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# =================== ROTA DE REGISTRO DE USUÁRIO ===================
@app.route('/api/register', methods=['POST'])
def register_user():
    """ 
    Rota para registrar um novo usuário no banco de dados.
    Método: POST
    Corpo da requisição (JSON):
    {
        "user_name": "Nome do usuário",
        "email": "email@exemplo.com",
        "email_user_second": "email2@exemplo.com" (opcional),
        "passw": "senha123"
    }
    Respostas:
    - 201: Usuário registrado com sucesso
    - 400: Dados inválidos ou erro no registro
    """
    data = request.get_json()
    user_name = data['user_name']
    email = data['email']
    email_user_second = data.get('email_user_second', '')  # Se não for fornecido, será uma string vazia
    passw = data['passw']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (user_name, email, email_user_second, passw) VALUES (%s, %s, %s, %s) RETURNING id, user_name, email, email_user_second',
            (user_name, email, email_user_second, passw)
        )
        user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Usuário registrado com sucesso!",
            "user": {
                "id": str(user[0]),  # Converte o UUID para string
                "user_name": user[1],
                "email": user[2],
                "email_user_second": user[3]
            }
        }), 201
    except Exception as e:
        return jsonify({"message": "Erro ao registrar usuário", "error": str(e)}), 400

# =================== ROTA DE LOGIN ===================
@app.route('/api/login', methods=['POST'])
def login_user():
    """ 
    Rota para autenticar um usuário e permitir login.
    Método: POST
    Corpo da requisição (JSON):
    {
        "email": "email@exemplo.com",
        "passw": "senha123"
    }
    Respostas:
    - 200: Login realizado com sucesso
    - 401: Credenciais inválidas
    """
    data = request.get_json()
    email = data['email']
    passw = data['passw']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, user_name, email, passw FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and user[3] == passw:
        return jsonify({
            "message": "Login realizado com sucesso!",
            "user": {
                "id": str(user[0]),
                "user_name": user[1],
                "email": user[2]
            }
        }), 200
    else:
        return jsonify({
            "message": "Credenciais inválidas. Login não realizado."
        }), 401

if __name__ == '__main__':
    create_table()  # Garante que a tabela seja criada antes de iniciar o servidor
    app.run(debug=True, host='0.0.0.0', port=5000)  # Executa o Flask
