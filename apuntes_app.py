import streamlit as st

#Definir las páginas que va a tener la aplicacion
inicio_page = st.Page(page='paginas/inicio/inicio.py', title='Inicio', icon='🏠')
paso_a_paso_page = st.Page(page='paginas/agregar_apuntes/paso_a_paso.py', title='Paso a paso para agregar un apunte')
agregar_apuntes_en_lote_page = st.Page(page='paginas/agregar_apuntes/agregar_en_lote.py', title='Agregar apuntes en lote')
visualizar_documentos_page = st.Page(page='paginas/interaccion_bd/visualizar_documentos.py', title='Visualizar documentos guardados')
realizar_consulta_bd_page = st.Page(page='paginas/interaccion_bd/realizar_consulta_bd.py', title='Realizar consulta a la bd')
rag_apuntes_page = st.Page(page='paginas/rag_apuntes/rag_apuntes.py', title='Consulta RAG Apuntes')

#Indicar cuales paginas existen en la aplicacion para que sean incluidas en la barra de navegacion
pg = st.navigation(
    {
        "Inicio": [inicio_page],
        "Agregar Apuntes": [paso_a_paso_page, agregar_apuntes_en_lote_page],
        "Interaccion con la base de datos vectorial": [visualizar_documentos_page,realizar_consulta_bd_page],
        "RAG": [rag_apuntes_page]
    }
)

pg.run()