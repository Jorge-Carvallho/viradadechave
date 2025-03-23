# Use a imagem oficial do Python 3.12 (slim) como base para o container.
# A versão slim é uma versão mais enxuta da imagem do Python.
FROM python:3.12-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo requirements.txt para o diretório de trabalho dentro do container
COPY requirements.txt requirements.txt

# Atualiza o pip e instala todas as dependências do requirements.txt
# Isso garante que as bibliotecas necessárias (como Flask, psycopg2, etc.) sejam instaladas.
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia todo o conteúdo do diretório atual (onde o Dockerfile está localizado) para o diretório /app no container
COPY . .

# Expõe a porta 5000 para que a aplicação Flask seja acessível fora do container.
EXPOSE 5000

# Antes de rodar o Flask, o comando cria as tabelas no banco de dados usando o script init_db.py.
# Após isso, o script app.py será iniciado, que é o servidor Flask.
# O comando sh -c permite rodar múltiplos comandos, então o init_db.py é executado primeiro e depois o Flask.
CMD ["sh", "-c", "python init_db.py && python app.py"]
