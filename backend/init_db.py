import psycopg2
from decouple import config

def get_db_connection():
    conn = psycopg2.connect(
        host=config('HOST_PGSQL'),
        database=config('NAME_PGSQL'),
        user=config('USER_PGSQL'),
        password=config('PASS_PGSQL')
    )
    return conn

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
    print("Tabela users criada com sucesso!")

#Adicionando a tabela password_resets
def create_password_reset_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            recovery_code VARCHAR(255) NOT NULL,
            expiration TIMESTAMP NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()
    print("Tabela password_resets criada com sucesso!")



if __name__ == "__main__":
    create_table()
