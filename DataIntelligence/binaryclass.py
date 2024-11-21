import os
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
import re
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import nltk

nltk.download('punkt')
nltk.download('stopwords')

# Cambia esta ruta a donde tengas los archivos `train.tsv` y `test.tsv`

os.chdir(r'/Users/fernandoleonfranco/Documents/GitHub/Semestre_III/DataIntelligence/exist2021')

# Cargar los datos
df_train = pd.read_csv("train.tsv", sep='\t')
df_test = pd.read_csv("test.tsv", sep='\t')

print('Tamaño training:', df_train.shape)
print('Tamaño test:', df_test.shape)

# Filtrar por idioma inglés
df_train = df_train[df_train['language'] == 'en']
df_test = df_test[df_test['language'] == 'en']
print('Tamaño training (solo inglés):', df_train.shape)
print('Tamaño test (solo inglés):', df_test.shape)

# Preparar las columnas necesarias
df_train = df_train.drop(['test_case', 'id', 'source', 'task2'], axis=1)
df_test = df_test.drop(['test_case', 'id', 'source', 'task2'], axis=1)
df_train = df_train.rename(columns={'task1': 'label'})
df_test = df_test.rename(columns={'task1': 'label'})
print('Primeros registros del training:')
print(df_train.head())


stopwords_en = stopwords.words("english")

# Preprocesamiento de texto
def clean_text(text):
    text = str(text).lower()  # Minúsculas
    from nltk.tokenize.punkt import PunktSentenceTokenizer
    punkt_tokenizer = PunktSentenceTokenizer()  # Instanciar el tokenizador
    
    tokens = punkt_tokenizer.tokenize(text)  # Tokenizar
    tokens = [word for word in tokens if word not in stopwords_en]  # Eliminar stopwords
    tokens = [PorterStemmer().stem(word) for word in tokens]  # Stemming
    min_length = 3
    p = re.compile('^[a-zA-Z]+$')
    filtered_tokens = [token for token in tokens if len(token) >= min_length and p.match(token)]
    return filtered_tokens


# Codificación de etiquetas
y_train = df_train['label'].tolist()
y_test = df_test['label'].tolist()

le = LabelEncoder()
y_train = le.fit_transform(y_train)
y_test = le.transform(y_test)
LABELS = le.classes_
print('Etiquetas:', LABELS)

# Crear el pipeline
pipeline = Pipeline([
    ('bow', CountVectorizer(analyzer=clean_text)),
    ('tf', TfidfTransformer()),
    ('svm', SVC()),
])

# Entrenar el modelo
X_train = df_train['text'].tolist()
pipeline.fit(X_train, y_train)

# Evaluar el modelo
X_test = df_test['text'].tolist()
predictions = pipeline.predict(X_test)

# Métricas de evaluación
print(classification_report(y_test, predictions, target_names=LABELS))

# Matriz de confusión
conf_matrix = confusion_matrix(y_test, predictions)
print('Matriz de confusión:')
print(conf_matrix)

disp = ConfusionMatrixDisplay(conf_matrix, display_labels=LABELS)
disp.plot(cmap=plt.cm.Blues)
plt.show()
