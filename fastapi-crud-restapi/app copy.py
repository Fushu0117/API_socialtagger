# Importación de FastAPI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Text
from datetime import datetime
from uuid import uuid4 as uuid
import spacy

app = FastAPI()

posts = []

# Post Model
class Post(BaseModel):
    id: Optional[str]
    sentence1: str
    sentence2: str
    similarity: float  # Nuevo campo para almacenar la similitud
   # created_at: datetime = datetime.now()

# Cargar el modelo de spaCy con vectores de palabras
nlp = spacy.load("es_core_news_md")

# Definir la función de lematización
def lemmatize(text):
    # Procesar el texto con spaCy
    doc = nlp(text)
    # Obtener las formas base de las palabras (lemas)
    lemmas = [token.lemma_ for token in doc]
    # Unir las lemas en una sola cadena
    lemmatized_text = ' '.join(lemmas)
    return lemmatized_text

# Definición del método http POST para crear un nuevo post
@app.post('/posts') 
def save_post(post: Post):
    post.id = str(uuid())
    # Lematizar las oraciones
    lemmatized_sentence1 = lemmatize(post.sentence1)
    lemmatized_sentence2 = lemmatize(post.sentence2)
    # Procesar las oraciones lematizadas con spaCy
    doc1 = nlp(lemmatized_sentence1)
    doc2 = nlp(lemmatized_sentence2)
    # Calcular la similitud entre las dos oraciones
    similarity = doc1.similarity(doc2)
    post.similarity = similarity  # Asignar la similitud al campo similarity
    posts.append(post.dict())
    return posts[-1]

# Definición del método http GET para obtener todos los posts
@app.get('/posts') 
def get_posts():
    return posts

# Definición del método http GET para obtener un post por su id
@app.get('/posts/{post_id}')
def get_post(post_id:str):
    for post in posts:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")