from flask import Flask, request, jsonify
import psycopg2
from decouple import config

app = Flask(__name__)

# Configuração de conexão com o PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        host=config('HOST_PGSQL'),         # Nome do serviço no Docker Compose (app-data)
        database=config('NAME_PGSQL'),     # Nome do banco de dados
        user=config('USER_PGSQL'),         # Usuário do PostgreSQL
        password=config('PASS_PGSQL')      # Senha do PostgreSQL
    )
    return conn

# Função para criar a tabela users se não existir
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            email_user_second VARCHAR(255),
            passw VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# Rota para registrar um novo usuário
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    user_name = data['user_name']
    email = data['email']
    email_user_second = data.get('email_user_second', '')
    passw = data['passw']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (user_name, email, email_user_second, passw) VALUES (%s, %s, %s, %s) RETURNING id, user_name, email, email_user_second',
                   (user_name, email, email_user_second, passw))
    user = cursor.fetchone()
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "id": user[0],
        "user_name": user[1],
        "email": user[2],
        "email_user_second": user[3]
    }), 201

if __name__ == '__main__':
    create_table()  # Cria a tabela quando o app é iniciado
    app.run(debug=True, host='0.0.0.0', port=5000)  # Roda o Flask no host 0.0.0.0
