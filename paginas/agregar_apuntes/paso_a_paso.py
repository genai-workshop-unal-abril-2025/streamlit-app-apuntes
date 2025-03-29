import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from watsonx_connection import call_watsonx_vision_model

#Se inicializan variables de la sesion que son necesarias para la aplicación
if "imagen_apuntes" not in st.session_state:
    st.session_state["imagen_apuntes"] = None

if "texto_extraido" not in st.session_state:
    st.session_state["texto_extraido"] = None

if "embedding_ejemplo" not in st.session_state:
    st.session_state["embedding_ejemplo"] = None

#Se define una funcion que ayuda a borrar las variables de sesion cuando se cambie de modo
def borrar_session_state_variables():
    if "imagen_apuntes" in st.session_state:
        del st.session_state["imagen_apuntes"]

    if "texto_extraido" in st.session_state:
        del st.session_state["texto_extraido"]

    if "embedding_ejemplo" in st.session_state:
        del st.session_state["embedding_ejemplo"]


#Mensaje al inicio de la pagina
st.markdown("# Paso a paso para agregar un apunte a la base de datos vectorial")

#Titulo del paso 1
st.markdown("## Paso 1: Toma una foto o sube una imagen de tus apuntes")

#Seleccionar si tomar una foto o subir una imagen
selector_modo_imagen = st.radio("Selecciona una de las siguientes opciones",["Subir una imagen","Tomar una foto"],on_change=borrar_session_state_variables)

if selector_modo_imagen == "Subir una imagen":
    uploaded_file = st.file_uploader("Elige un archivo", ["jpg","jpeg","png"])
    if uploaded_file is not None:
        #Asignar la variable de estado para mantener la imagen durante la sesion del usuario
        st.session_state["imagen_apuntes"] = uploaded_file

        #Leer los bytes del archivo subido
        image_bytes_data = st.session_state["imagen_apuntes"].getvalue()
        st.write(f"La imagen subida es:")
        st.image(image_bytes_data)

elif selector_modo_imagen == "Tomar una foto":
    #Segundo modo: Tomar la foto de los apuntes con la webcam del computador
    permitir_camara = st.checkbox("Permitir cámara")
    foto_apuntes = st.camera_input("Toma una foto de tus apuntes", disabled=(not permitir_camara))

    if foto_apuntes:
        #Asignar la variable de estado para mantener la imagen sin importar si se recarga la página
        st.session_state["imagen_apuntes"] = foto_apuntes

#Verificar que exista una imagen antes de continuar con el siguiente paso
if st.session_state["imagen_apuntes"]:
    #Titulo del paso 2
    st.markdown("## Paso 2: Extraer el texto de la imagen")

    st.write("Para extraer el texto de la imagen se va a utilizar un modelo multimodal, haz click en el boton para extraer el texto:")

    boton_extraer_texto = st.button("Extraer texto de la imagen")
    if boton_extraer_texto:
        #Llamar a watson para extraer el texto y mostrar el texto extraido
        st.session_state["texto_extraido"] = call_watsonx_vision_model(st.session_state["imagen_apuntes"])
    
    if st.session_state["texto_extraido"]:
        st.write("El texto extraido de la imagen es el siguiente:")
        st.write(st.session_state["texto_extraido"])

#Verificar que se haya extraido un texto antes de continuar con el siguiente paso
if st.session_state["texto_extraido"]:
    #Paso 2.5
    st.write("#### Paso 2.5 (Opcional): Visualizar un ejemplo del embedding del texto extraido")
    st.text("En este paso se va a generar un embedding del texto extraido para ver la representación vectorial del mismo. Este embedding se va a generar con el modelo ibm-granite/granite-embedding-278m-multilingual")

    boton_generar_embedding = st.button("Generar embedding a partir del texto")
    if boton_generar_embedding:
        modelo_embedding = SentenceTransformer("ibm-granite/granite-embedding-278m-multilingual")
        st.session_state["embedding_ejemplo"] = modelo_embedding.encode(st.session_state["texto_extraido"]).tolist()

    if st.session_state["embedding_ejemplo"] != None:
        st.write(f"Tamaño del embedding: {len(st.session_state["embedding_ejemplo"])}")
        st.write("Valores que componene el vector:")
        st.write(st.session_state["embedding_ejemplo"])

#Paso 3: Almacenar los apuntes y el embedding en una base de datos vectorial
#Verificar que se haya extraido un texto antes de continuar con el siguiente paso
#Iniciar cliente para conectarse a la base de datos vectorial persistente
chroma_client = chromadb.PersistentClient(path="./chroma")
if st.session_state["texto_extraido"]:
    st.write("## Paso 3: Almacenar los apuntes y el embedding en una base de datos vectorial")
    st.write("El texto extraido y su embedding se van a almacenar en una base de datos vectorial para que posteriormente puedan ser consultados con mayor facilidad y se puedan utilizar dentro del RAG.")

    st.write("Escribe un identificador con el cual quieres que se guarden estos apuntes en la base de datos vectorial:")
    identificador = st.text_input("Identificador para los apuntes",placeholder="MisApuntes")

    boton_almacenar_embedding = st.button("Almacenar texto en la base de datos vectorial")
    if boton_almacenar_embedding:
        #Definir la funcion de embedding que se va a utilizar en la coleccion de la base de datos vectorial
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="ibm-granite/granite-embedding-278m-multilingual"
        )

        #Crear o acceder a la coleccion de la base de datos vectorial donde se van a tener los apuntes
        #Se define la funcion de embedding que se va a usar en los documentos de la coleccion
        collection_apuntes = chroma_client.get_or_create_collection(
            name="apuntes", 
            embedding_function=embedding_function
        )

        #Se agrega el texto extraido a la base de datos vectorial:
        #La base de datos se encarga de almacenar el texto y el embedding calculado con la funcion dicha anteriormente
        collection_apuntes.add(
            ids=[identificador],
            documents=[st.session_state["texto_extraido"]]
        )

        #Si todo el proceso fue exitoso poner este texto informativo en la pantalla
        st.write("El texto fue almacenado correctamente, para visualizar los textos guarados puedes ir a la pestaña 'Visualizar documentos guardados'")
        