from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4 as uuid
import spacy
import httpx

app = FastAPI()

# Configuración de las credenciales de Supabase
SUPABASE_URL = "https://vursptbyijkkpxkxwnvp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ1cnNwdGJ5aWpra3B4a3h3bnZwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTA2MjIxMzEsImV4cCI6MjAyNjE5ODEzMX0.kmf8365to2zG6AoXwYeMzQuKxo985UqER44TBdnqaKo"

# Modelo de datos para el post
class Post(BaseModel):
    id: str
    sentence1: str
    sentence2: str
    similarity: float

# Cargar el modelo de spaCy
nlp = spacy.load("es_core_news_md")

# Función de lematización
def lemmatize(text):
    doc = nlp(text)
    lemmas = [token.lemma_ for token in doc]
    return ' '.join(lemmas)

# Método POST para crear un nuevo post
@app.post('/posts') 
async def save_post(post: Post):
    # Generar un ID único
    post.id = str(uuid())

    # Lematizar las oraciones y calcular la similitud
    lemmatized_sentence1 = lemmatize(post.sentence1)
    lemmatized_sentence2 = lemmatize(post.sentence2)
    doc1 = nlp(lemmatized_sentence1)
    doc2 = nlp(lemmatized_sentence2)
    post.similarity = doc1.similarity(doc2)
    
    # Guardar el post en SUPABASE
    await save_post_to_supabase(post)

    return post

# Función para guardar el post en SUPABASE
async def save_post_to_supabase(post: Post):
    async with httpx.AsyncClient() as client:
        url = f"{SUPABASE_URL}/rest/v1/posts"
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json",
        }
        data = {
            "id": post.id,
            "sentence1": post.sentence1,
            "sentence2": post.sentence2,
            "similarity": post.similarity,
        }
        response = await client.post(url, headers=headers, json=data)
        response.raise_for_status()

# Método GET para obtener todos los posts
@app.get('/posts') 
async def get_posts():
    async with httpx.AsyncClient() as client:
        url = f"{SUPABASE_URL}/rest/v1/posts"
        headers = {
            "apikey": SUPABASE_KEY,
        }
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

# Método GET para obtener un post por su id
@app.get('/posts/{post_id}')
async def get_post_by_id(post_id:str):
    async with httpx.AsyncClient() as client:
        url = f"{SUPABASE_URL}/rest/v1/posts?id=eq.{post_id}"
        headers = {
            "apikey": SUPABASE_KEY,
        }
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
