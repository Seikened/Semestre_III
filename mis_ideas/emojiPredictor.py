import spacy
import emoji
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from spacy.lang.en.stop_words import STOP_WORDS

print("Iniciando programa...")

# Cargar el modelo de spaCy (en este caso, el inglés)
try:
    nlp = spacy.load('en_core_web_md')
    print("Modelo de spaCy cargado correctamente.")
except Exception as e:
    print(f"Error al cargar el modelo spaCy: {e}")

# Obtener la lista de emojis con sus descripciones usando la nueva API de emoji
try:
    emoji_dict = emoji.EMOJI_DATA  # Obtiene un diccionario con información de los emojis
    emoji_list = [(key, value['en']) for key, value in emoji_dict.items() if 'en' in value]
    print(f"Se han cargado {len(emoji_list)} emojis.")
except Exception as e:
    print(f"Error al cargar los emojis: {e}")

# Función para limpiar y filtrar palabras clave de la descripción
def clean_description(description):
    doc = nlp(description.lower())
    # Filtrar palabras clave eliminando stop words y tokens irrelevantes
    keywords = [token.lemma_ for token in doc if token.text not in STOP_WORDS and token.is_alpha]
    return " ".join(keywords)

# Función para obtener el vector de una palabra usando spaCy
def get_word_vector(word):
    return nlp(word).vector

# Función para obtener el vector de un emoji basado en su descripción
def get_emoji_vector(emoji_description):
    cleaned_description = clean_description(emoji_description)
    return nlp(cleaned_description).vector

# Ingresar una palabra para comparar
word = "love"
try:
    word_vector = get_word_vector(word)
    print(f"Vector de la palabra '{word}' obtenido correctamente.")
except Exception as e:
    print(f"Error al obtener el vector de la palabra: {e}")

# Calcula la similitud entre la palabra y cada emoji
emoji_scores = []
for emoji_char, emoji_description in emoji_list:
    if emoji_description:  # Asegurarse de que la descripción no esté vacía
        try:
            emoji_vector = get_emoji_vector(emoji_description)
            # Usar la similitud coseno entre el vector de la palabra y el vector del emoji
            similarity = cosine_similarity([word_vector], [emoji_vector])[0][0]
            emoji_scores.append((emoji_char, similarity))
        except Exception as e:
            print(f"Error al procesar el emoji {emoji_char}: {e}")

# Ordenar los emojis por similitud
emoji_scores.sort(key=lambda x: x[1], reverse=True)

# Mostrar los 5 emojis más similares
try:
    for em, score in emoji_scores[:5]:
        print(f"Emoji: {em} - Similarity: {score}")
except Exception as e:
    print(f"Error al mostrar los resultados: {e}")

print("Programa finalizado.")