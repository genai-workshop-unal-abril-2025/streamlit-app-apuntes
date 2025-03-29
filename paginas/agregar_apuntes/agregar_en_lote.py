import chromadb
import streamlit as st
from chromadb.utils import embedding_functions

from watsonx_connection import call_watsonx_vision_model

#Iniciar cliente para conectarse a la base de datos vectorial persistente
chroma_client = chromadb.PersistentClient(path="./chroma")

#Se inicializan variables de la sesion que son necesarias para la aplicación
if "imagenes_lote_apuntes" not in st.session_state:
    st.session_state["imagenes_lote_apuntes"] = None

if "lista_textos_extraidos" not in st.session_state:
    st.session_state["lista_textos_extraidos"] = None

if "lista_identificadores" not in st.session_state:
    st.session_state["lista_identificadores"] = None

#Mensaje al inicio de la pagina
st.markdown("# Agregar apuntes en lote")

#Titulo del paso 1
st.markdown("## Paso 1: Elige las imagenes de los apuntes que quieres subir")
uploaded_files = st.file_uploader("Elige un archivo", ["jpg","jpeg","png"], accept_multiple_files=True)
if uploaded_files is not None:
    #Asignar la variable de estado para mantener la imagen durante la sesion del usuario
    st.session_state["imagenes_lote_apuntes"] = uploaded_files

    #Leer los bytes de cada archivo subido y mostrarla
    #TODO Mejorar visualizacion
    for imagen in st.session_state["imagenes_lote_apuntes"]:
        image_bytes_data = imagen.getvalue()
        st.write(f"La imagen subida es:")
        st.image(image_bytes_data)

#Paso 2: Extraer el texto de las imagenes subidas
#Antes de habilitar este paso primero se verifica que hayan imagenes subidas
if st.session_state["imagenes_lote_apuntes"]:
    #Titulo del paso 2
    st.markdown("## Paso 2: Extraer el texto de las imagenes subidas")
    #Boton para extraer el texto de todas las imagenes subidas
    boton_extraer_texto_imagenes = st.button("Extraer texto imagenes")
    if boton_extraer_texto_imagenes:
        lista_temporal_textos_extraidos = []
        for imagen in st.session_state["imagenes_lote_apuntes"]:
            #Llamar a watson para extraer el texto y mostrar el texto extraido
            texto_extraido = call_watsonx_vision_model(imagen)
            lista_temporal_textos_extraidos.append(texto_extraido)
        
        st.session_state["lista_textos_extraidos"] = lista_temporal_textos_extraidos
    
    if st.session_state["lista_textos_extraidos"]:
        for texto_extraido in st.session_state["lista_textos_extraidos"]:
            st.write("El texto extraido de la imagen es el siguiente:")
            st.write(texto_extraido)


#Paso 3: Ingresar el identificador con el que se quiere guardar cada texto extraido anteriormente
if st.session_state["lista_textos_extraidos"]:
    #Titulo del paso 3
    st.markdown("## Paso 3: Ingresar un indentificador para cada apunte que se va a almacenar")
    lista_temporal_identificadores = []
    for imagen in st.session_state["imagenes_lote_apuntes"]:
        st.write("Escribe un identificador para cada uno de los apuntes extraidos de las imagenes:")
        identificador = st.text_input(f"Identificador para los apuntes extraidos de la imagen {imagen.name}",placeholder="MisApuntes")
        lista_temporal_identificadores.append(identificador)

    st.session_state["lista_identificadores"] = lista_temporal_identificadores

#Paso 4: Almacenar todos los textos extraidos en la base de datos vectorial
if st.session_state["lista_textos_extraidos"]:
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

        #Se agregan los textos y los identificadores creados

        #Se agrega el texto extraido a la base de datos vectorial:
        #La base de datos se encarga de almacenar el texto y el embedding calculado con la funcion dicha anteriormente
        collection_apuntes.add(
            ids=st.session_state["lista_identificadores"],
            documents=st.session_state["lista_textos_extraidos"]
        )

        #Si todo el proceso fue exitoso poner este texto informativo en la pantalla
        st.write("El texto fue almacenado correctamente, para visualizar los textos guarados puedes ir a la pestaña 'Visualizar documentos guardados'")
