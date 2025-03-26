# =================== ESTÁGIO DE CONSTRUÇÃO ===================
FROM python:3.9-slim as builder

WORKDIR /app

# 1. Instala dependências de compilação
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Cria e ativa ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 3. Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =================== ESTÁGIO FINAL ===================
FROM python:3.9-slim

WORKDIR /app

# 4. Copia apenas o necessário do estágio builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 5. Instala apenas bibliotecas de sistema necessárias
RUN apt-get update && apt-get install -y \
    libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 6. Copia aplicação e scripts
COPY --chown=flaskuser:flaskuser . .
COPY --chown=flaskuser:flaskuser wait_for_postgres.py /wait_for_postgres.py
RUN chmod +x /wait_for_postgres.py

# 7. Configura usuário não-root
RUN useradd -m flaskuser && \
    chown -R flaskuser:flaskuser /app
USER flaskuser

# 8. Porta da aplicação
EXPOSE 5000

# 9. Comando de inicialização com health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/api/health || exit 1

CMD ["sh", "-c", "python /wait_for_postgres.py && python app.py"]