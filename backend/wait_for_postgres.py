import os
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_postgres():
    max_retries = 10
    retry_delay = 5
    
    print("🔍 Verificando conexão com PostgreSQL...")
    
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host="app-data",  # Nome do serviço no docker-compose
                database=os.getenv("NAME_PGSQL"),
                user=os.getenv("USER_PGSQL"),
                password=os.getenv("PASS_PGSQL"),
                connect_timeout=5
            )
            conn.close()
            print("✅ PostgreSQL pronto para conexões!")
            return True
        except OperationalError as e:
            print(f"⚠️ Tentativa {i+1}/{max_retries} - PostgreSQL não responde...")
            if i == max_retries - 1:
                print("❌ Falha crítica - PostgreSQL não está acessível")
                raise
            time.sleep(retry_delay)

if __name__ == '__main__':
    wait_for_postgres()