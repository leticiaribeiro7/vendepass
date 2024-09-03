FROM python
WORKDIR /app

# Copiar o arquivo requirements.txt (se houver) para o container
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação para o diretório de trabalho
COPY . .

EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "-u", "server.py"]


#
# docker build -t servidor -f Dockerfile .  
# docker run -it --name servidor -p 5000:5000 servidor
