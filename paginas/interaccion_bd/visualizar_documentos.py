import chromadb
from chromadb.utils import embedding_functions
import streamlit as st

st.write("## Visualizar los documentos almacenados en la base de datos vectorial")

#Iniciar cliente para conectarse a la base de datos vectorial persistente
chroma_client = chromadb.PersistentClient(path="./chroma") 

#Se verifica que exista la collecion apuntes en la base de datos
if "apuntes" in chroma_client.list_collections():
    st.write("Pulsando en el siguiente boton se pueden visualizar algunos de los documentos guardados en la base de datos")

    boton_ver_coleccion = st.button("Ver documentos en la coleccion")
    if boton_ver_coleccion:
        #Definir la funcion de embedding que se va a utilizar en la coleccion de la base de datos vectorial
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="ibm-granite/granite-embedding-278m-multilingual"
        )
        #Acceder a la coleccion
        collection_apuntes = chroma_client.get_collection(
            name="apuntes", 
            embedding_function=embedding_function
        )
        documentos = collection_apuntes.get()
        
        #Se realiza un bucle para recorrer los documentos y mostrarlos
        for index in range(len(documentos['ids'])):
            st.write(f"{documentos['ids'][index]}: {documentos['documents'][index]}")

else:
    st.write("No has agregado apuntes a la base de datos, por favor agregalos para poder visualizarlos en esta pestaña")