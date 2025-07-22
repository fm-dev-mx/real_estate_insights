import streamlit as st
import pandas as pd
import os
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# --- CONFIGURACIÓN DE LA BASE DE DATOS (desde variables de entorno) ---
DB_NAME = os.environ.get('REI_DB_NAME')
DB_USER = os.environ.get('REI_DB_USER')
DB_PASSWORD = os.environ.get('REI_DB_PASSWORD')
DB_HOST = os.environ.get('REI_DB_HOST')
DB_PORT = os.environ.get('REI_DB_PORT')

@st.cache_data
def get_properties_from_db(
    min_price=None, max_price=None, property_operation_type=None, property_type=None,
    min_bedrooms=None, min_bathrooms=None, max_age_years=None,
    min_construction_m2=None, min_land_m2=None, has_parking=None, keywords_description=None
):
    conn = None
    try:
        if not all([DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT]):
            st.error("Error: Faltan variables de entorno de la base de datos. Asegúrese de que REI_DB_NAME, REI_DB_USER, REI_DB_PASSWORD, REI_DB_HOST, REI_DB_PORT estén configuradas en el archivo .env")
            return pd.DataFrame()

        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        query = "SELECT * FROM properties WHERE 1=1"
        params = {}

        if min_price is not None:
            query += " AND precio >= %(min_price)s"
            params['min_price'] = float(min_price)
        if max_price is not None:
            query += " AND precio <= %(max_price)s"
            params['max_price'] = float(max_price)
        if property_operation_type:
            op_types = [op.strip() for op in property_operation_type.split(',')]
            query += " AND tipo_operacion IN %(op_types)s"
            params['op_types'] = tuple(op_types)
        if property_type:
            prop_types = [pt.strip() for pt in property_type.split(',')]
            query += " AND subtipo_propiedad IN %(prop_types)s"
            params['prop_types'] = tuple(prop_types)
        if min_bedrooms is not None:
            query += " AND recamaras >= %(min_bedrooms)s"
            params['min_bedrooms'] = int(min_bedrooms)
        if min_bathrooms is not None:
            query += " AND banios >= %(min_bathrooms)s"
            params['min_bathrooms'] = float(min_bathrooms)
        if max_age_years is not None:
            query += " AND edad <= %(max_age_years)s"
            params['max_age_years'] = int(max_age_years)
        if min_construction_m2 is not None:
            query += " AND m2_construccion >= %(min_construction_m2)s"
            params['min_construction_m2'] = float(min_construction_m2)
        if min_land_m2 is not None:
            query += " AND m2_terreno >= %(min_land_m2)s"
            params['min_land_m2'] = float(min_land_m2)
        if has_parking is not None:
            if has_parking:
                query += " AND estacionamientos > 0"
            else:
                query += " AND (estacionamientos IS NULL OR estacionamientos = 0)"
        if keywords_description:
            keywords = [k.strip() for k in keywords_description.split(',')]
            keyword_conditions = [f"descripcion ILIKE '%%{k}%%'" for k in keywords]
            query += f" AND ({' OR '.join(keyword_conditions)})"

        df = pd.read_sql(query, conn, params=params)
        return df

    except psycopg2.Error as e:
        st.error(f"Error de PostgreSQL al cargar propiedades: {e}")
    except Exception as e:
        st.error(f"Un error inesperado ocurrió al cargar propiedades: {e}")
    finally:
        if conn:
            conn.close()
    return pd.DataFrame()

# --- Streamlit App ---
st.set_page_config(layout="wide")
st.title('Análisis de Propiedades Inmobiliarias')

# Sidebar para filtros interactivos
st.sidebar.header('Filtros de Propiedades')

# Rango de Precios
min_price_input = st.sidebar.number_input('Precio Mínimo', min_value=0.0, value=float(os.environ.get('MIN_PRICE', 0.0)))
max_price_input = st.sidebar.number_input('Precio Máximo', min_value=0.0, value=float(os.environ.get('MAX_PRICE', 100000000.0)))

# Tipo de Operación
operation_types = ['venta', 'renta', 'traspaso', 'opcion']
selected_operation_type = st.sidebar.multiselect('Tipo de Operación', options=operation_types, default=os.environ.get('PROPERTY_OPERATION_TYPE', '').split(',') if os.environ.get('PROPERTY_OPERATION_TYPE') else [])

# Tipo de Propiedad
property_types = ['casa', 'departamento', 'terreno', 'oficina', 'local', 'bodega', 'consultorio'] # Puedes expandir esta lista
selected_property_type = st.sidebar.multiselect('Tipo de Propiedad', options=property_types, default=os.environ.get('PROPERTY_TYPE', '').split(',') if os.environ.get('PROPERTY_TYPE') else [])

# Recámaras
min_bedrooms_input = st.sidebar.number_input('Recámaras Mínimas', min_value=0, value=int(os.environ.get('MIN_BEDROOMS', 0)))

# Baños
min_bathrooms_input = st.sidebar.number_input('Baños Mínimos', min_value=0.0, value=float(os.environ.get('MIN_BATHROOMS', 0.0)))

# Edad de la Propiedad
max_age_years_input = st.sidebar.number_input('Edad Máxima (años)', min_value=0, value=int(os.environ.get('MAX_AGE_YEARS', 999)))

# M2 Construcción
min_construction_m2_input = st.sidebar.number_input('M2 Construcción Mínimos', min_value=0.0, value=float(os.environ.get('MIN_CONSTRUCTION_M2', 0.0)))

# M2 Terreno
min_land_m2_input = st.sidebar.number_input('M2 Terreno Mínimos', min_value=0.0, value=float(os.environ.get('MIN_LAND_M2', 0.0)))

# Estacionamiento
has_parking_options = {'No importa': None, 'Sí': True, 'No': False}
default_has_parking = os.environ.get('HAS_PARKING')
if default_has_parking is not None:
    default_has_parking = True if default_has_parking.lower() == 'true' else (False if default_has_parking.lower() == 'false' else None)
selected_has_parking = st.sidebar.radio('¿Tiene Estacionamiento?', options=list(has_parking_options.keys()), format_func=lambda x: x, index=list(has_parking_options.values()).index(default_has_parking))

# Palabras Clave en Descripción
keywords_description_input = st.sidebar.text_input('Palabras Clave en Descripción (separadas por coma)', value=os.environ.get('KEYWORDS_DESCRIPTION', ''))

# Obtener propiedades con los filtros seleccionados
properties_df = get_properties_from_db(
    min_price=min_price_input,
    max_price=max_price_input,
    property_operation_type=','.join(selected_operation_type) if selected_operation_type else None,
    property_type=','.join(selected_property_type) if selected_property_type else None,
    min_bedrooms=min_bedrooms_input,
    min_bathrooms=min_bathrooms_input,
    max_age_years=max_age_years_input,
    min_construction_m2=min_construction_m2_input,
    min_land_m2=min_land_m2_input,
    has_parking=has_parking_options[selected_has_parking],
    keywords_description=keywords_description_input
)

if not properties_df.empty:
    st.subheader('Propiedades Seleccionadas')
    st.write(f"Total de propiedades encontradas: {len(properties_df)}")
    st.dataframe(properties_df)

    # Puedes añadir más visualizaciones aquí, por ejemplo:
    # st.subheader('Distribución de Precios')
    # st.hist(properties_df['precio'])

    # st.subheader('Propiedades en Mapa (si tienes latitud y longitud)')
    # if 'latitud' in properties_df.columns and 'longitud' in properties_df.columns:
    #     st.map(properties_df)

else:
    st.info("No se encontraron propiedades o hubo un error al cargar los datos.")