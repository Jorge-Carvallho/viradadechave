"""
Script de inicialização do banco de dados

Funcionalidades:
1. Cria a tabela 'users' se não existir
2. Cria a tabela 'password_resets' para recuperação de senha
3. Configuração via variáveis de ambiente (.env)

Requisitos:
- PostgreSQL rodando com as credenciais configuradas no .env
- Bibliotecas: psycopg2-binary, python-decouple
"""

import psycopg2
from psycopg2 import OperationalError
from decouple import config
import logging
from typing import Optional

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection(max_retries: int = 3) -> Optional[psycopg2.extensions.connection]:
    """
    Estabelece conexão com o PostgreSQL com tentativas de reconexão
    
    Args:
        max_retries: Número máximo de tentativas de conexão
        
    Returns:
        Objeto de conexão ou None em caso de falha
    """
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=config('HOST_PGSQL'),
                database=config('NAME_PGSQL'),
                user=config('USER_PGSQL'),
                password=config('PASS_PGSQL'),
                connect_timeout=5
            )
            logger.info("Conexão com o banco estabelecida com sucesso")
            return conn
        except OperationalError as e:
            logger.warning(f"Tentativa {attempt + 1} falhou: {str(e)}")
            if attempt == max_retries - 1:
                logger.error("Falha ao conectar ao banco após %s tentativas", max_retries)
                raise
            time.sleep(2)

def create_table():
    """
    Cria a tabela 'users' com estrutura básica:
    - id: Serial (auto-incremento)
    - user_name: Nome do usuário (obrigatório)
    - email: E-mail único (obrigatório)
    - email_user_second: E-mail secundário (opcional)
    - passw: Senha (hash recomendado)
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    email_user_second VARCHAR(255),
                    passw VARCHAR(255) NOT NULL
                )
            ''')
            logger.info("Tabela 'users' criada/verificada")
        conn.commit()
    except Exception as e:
        logger.error(f"Erro ao criar tabela 'users': {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def create_password_reset_table():
    """
    Cria a tabela 'password_resets' para gerenciamento de recuperação:
    - id: Serial (auto-incremento)
    - user_id: Chave estrangeira para users.id
    - recovery_code: Código único para recuperação
    - expiration: Timestamp de expiração do código
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_resets (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    recovery_code VARCHAR(255) NOT NULL UNIQUE,
                    expiration TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            logger.info("Tabela 'password_resets' criada/verificada")
        conn.commit()
    except Exception as e:
        logger.error(f"Erro ao criar tabela 'password_resets': {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def main():
    """Fluxo principal de execução"""
    try:
        logger.info("Iniciando inicialização do banco de dados...")
        create_table()
        create_password_reset_table()
        logger.info("Banco de dados inicializado com sucesso!")
    except Exception as e:
        logger.critical(f"Falha crítica na inicialização: {str(e)}")
        raise

if __name__ == "__main__":
    main()






















#     Objetivo:
# Esse script inicializa o banco de dados PostgreSQL criando as tabelas necessárias para o funcionamento de um sistema de usuários e recuperação de senhas.

# Funções:
# get_db_connection(max_retries: int = 3)
# Tenta se conectar ao banco de dados PostgreSQL, com um número máximo de tentativas (max_retries). Se a conexão falhar, o script tenta novamente após um pequeno intervalo. Retorna uma conexão válida ou gera um erro após falhas repetidas.

# create_table()
# Cria a tabela users, que armazena dados dos usuários (nome, e-mail, senha). Se a tabela já existir, nada acontece.

# create_password_reset_table()
# Cria a tabela password_resets para gerenciar a recuperação de senhas dos usuários. Ela guarda o código de recuperação e a data de expiração.

# main()
# Função principal que chama as funções create_table() e create_password_reset_table(), garantindo que as tabelas necessárias existam no banco de dados.

# Requisitos:
# Banco de dados PostgreSQL funcionando e configurado com credenciais no arquivo .env.

# Bibliotecas necessárias: psycopg2 (para conectar ao PostgreSQL) e decouple (para carregar variáveis de ambiente).

# Processo:
# Conecta ao banco de dados.

# Cria as tabelas users e password_resets se elas não existirem.

# Exibe mensagens no log informando o sucesso ou falha da operação.