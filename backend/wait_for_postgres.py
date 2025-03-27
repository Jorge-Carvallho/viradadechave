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












#     Documentação - Conexão com PostgreSQL (Função wait_for_postgres)
# Objetivo
# A função wait_for_postgres tem como objetivo verificar se o banco de dados PostgreSQL está acessível antes de permitir que a aplicação prossiga. A função tenta se conectar ao banco de dados utilizando credenciais de ambiente, com um número máximo de tentativas e intervalos entre elas para garantir que o banco esteja pronto para conexões.

# Funcionalidade
# Verificação de Conexão: A função tenta estabelecer uma conexão com o banco de dados PostgreSQL, usando os parâmetros fornecidos pelas variáveis de ambiente, como nome de usuário, senha e nome do banco de dados.

# Tentativas e Atrasos: Caso a primeira tentativa de conexão falhe, a função continuará tentando estabelecer a conexão até um número máximo de tentativas (10 tentativas no total). Entre cada tentativa, será aguardado um tempo específico (5 segundos).

# Resposta de Sucesso ou Falha:

# Se a conexão for bem-sucedida, a função imprime uma mensagem de sucesso e a aplicação poderá prosseguir.

# Caso o número máximo de tentativas seja atingido sem sucesso, a função imprime uma mensagem de erro e levanta uma exceção para interromper a execução.

# Parâmetros
# max_retries: O número máximo de tentativas de conexão (configurado para 10 tentativas).

# retry_delay: O intervalo entre as tentativas de conexão em segundos (configurado para 5 segundos).

# Variáveis de ambiente: São utilizadas para passar as credenciais necessárias para a conexão com o banco de dados (usuário, senha, nome do banco de dados).

# Comportamento
# Sucesso: A função considera a conexão bem-sucedida quando consegue se conectar ao banco de dados sem erros. Nesse caso, ela imprime "PostgreSQL pronto para conexões!" e a execução continua.

# Falha: Se todas as tentativas de conexão falharem, a função imprime "Falha crítica - PostgreSQL não está acessível" e levanta uma exceção, interrompendo a execução da aplicação.

# Cenários de Uso
# Esta função é ideal para ser utilizada em aplicações que dependem de um banco de dados PostgreSQL, especialmente em ambientes de contêineres (como Docker), onde o banco de dados pode não estar imediatamente disponível para conexões assim que o serviço é iniciado.

# Exceções Tratadas
# A função lida com exceções do tipo OperationalError do psycopg2, que são levantadas quando a tentativa de conexão com o banco de dados falha. Se a função atingir o limite máximo de tentativas sem sucesso, uma exceção é levantada para interromper a execução.