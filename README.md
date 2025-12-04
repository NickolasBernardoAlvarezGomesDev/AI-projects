# AI-projects-rag
MongoDB local rodando (mongodb://localhost:27017)

OpenSearch local (http://localhost:9200)

Redis local (redis://localhost:6379)

passos:

# criar projeto e instalar deps
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows

pip install -r requirements.txt

export OPENAI_API_KEY="sua_chave"
# (opcional) export MONGODB_URI, OPENSEARCH_HOST, etc.

# migrations básicas do Django
python manage.py migrate

# subir o celery worker
celery -A core worker --loglevel=info

# em outro terminal, subir o servidor django
python manage.py runserver 8000

####Testes rápidos (com curl ou Postman)#####

1-cadastrar texto

curl -X POST http://localhost:8000/api/docs/ \
  -H "Content-Type: application/json" \
  -d '{"text": "A água é um composto formado por hidrogênio e oxigênio. Seu ponto de ebulição é 100°C a 1 atm."}'

2-fazer pergunta

curl -X POST http://localhost:8000/api/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual é o ponto de ebulição da água a 1 atm?"}'


3-usar agente

curl -X POST http://localhost:8000/api/agent/ \
  -H "Content-Type: application/json" \
  -d '{"goal": "Crie um resumo em até 3 parágrafos sobre o que os documentos falam."}'
