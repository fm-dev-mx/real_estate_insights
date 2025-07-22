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

# --- CONSTANTES ---
STATUS_EN_PROMOCION = 'enPromocion'
STATUS_CON_INTENCION = 'conIntencion'
STATUS_VENDIDAS = 'vendidas'

CONTRACT_TYPE_EXCLUSIVA = 'exclusiva'
CONTRACT_TYPE_OPCION = 'opcion'

# --- FUNCIONES DE AYUDA ---

@st.cache_data
def get_properties_from_db(
    min_price=None, max_price=None, property_operation_type=None, property_type=None,
    min_bedrooms=None, min_bathrooms=None, max_age_years=None,
    min_construction_m2=None, min_land_m2=None, has_parking=None, keywords_description=None,
    property_status=None, min_commission=None, contract_types_to_include=None
):
    """
    Obtiene propiedades de la base de datos PostgreSQL aplicando varios filtros.

    Args:
        min_price (float, optional): Precio mínimo de la propiedad.
        max_price (float, optional): Precio máximo de la propiedad.
        property_operation_type (str, optional): Tipo de operación (ej. 'venta', 'renta').
        property_type (str, optional): Tipo de propiedad (ej. 'casa', 'departamento').
        min_bedrooms (int, optional): Número mínimo de recámaras.
        min_bathrooms (int, optional): Número mínimo de baños.
        max_age_years (int, optional): Edad máxima de la propiedad en años.
        min_construction_m2 (float, optional): Metros cuadrados de construcción mínimos.
        min_land_m2 (float, optional): Metros cuadrados de terreno mínimos.
        has_parking (bool, optional): Si la propiedad tiene estacionamiento.
        keywords_description (str, optional): Palabras clave a buscar en la descripción.
        property_status (str, optional): Estatus de la propiedad (ej. 'enPromocion').
        min_commission (float, optional): Comisión mínima de la propiedad.
        contract_types_to_include (list, optional): Tipos de contrato a incluir (ej. ['Exclusiva', 'Opcion']).

    Returns:
        pd.DataFrame: DataFrame de pandas con las propiedades filtradas.
    """
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
        if property_status:
            status_types = [s.strip() for s in property_status.split(',')]
            query += " AND status IN %(status_types)s"
            params['status_types'] = tuple(status_types)
        if contract_types_to_include:
            # Ensure the values in contract_types_to_include match the case in the DB
            # Assuming 'Exclusiva' and 'Opcion' are the exact values in the DB
            query += " AND tipo_contrato IN %(contract_types_to_include)s"
            params['contract_types_to_include'] = tuple(contract_types_to_include)
        if min_commission is not None:
            query += " AND comision >= %(min_commission)s"
            params['min_commission'] = float(min_commission)

        df = pd.read_sql(query, conn, params=params)
        return df

    except psycopg2.Error as e:
        st.error(f"Error de PostgreSQL al cargar propiedades: {e}")
    except Exception as e:
        st.error(f"Un error inesperado ocurrió al cargar propiedades: {e}")
        st.exception(e) # Display the full traceback in Streamlit
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
st.sidebar.subheader('Rango de Precios')
min_default_price = int(float(os.environ.get('MIN_PRICE', 1500000)))
max_default_price = int(float(os.environ.get('MAX_PRICE', 3500000)))

price_range = st.sidebar.slider(
    'Selecciona el rango de precios',
    min_value=500000,
    max_value=20000000, # Límite superior de $20,000,000
    value=(min_default_price, max_default_price),
    step=50000,
    format='$%d'
)
min_price_input = price_range[0]
max_price_input = price_range[1]

# Tipo de Operación (mantener si es relevante, aunque el foco es el estatus)
operation_types = ['venta', 'renta', 'traspaso', 'opcion']
selected_operation_type = st.sidebar.multiselect('Tipo de Operación', options=operation_types, default=os.environ.get('PROPERTY_OPERATION_TYPE', '').split(',') if os.environ.get('PROPERTY_OPERATION_TYPE') else [])

# Estatus de Propiedad
st.sidebar.subheader('Estatus de Propiedad')
selected_status = [STATUS_EN_PROMOCION] # Por defecto

if st.sidebar.checkbox(f'Incluir "{STATUS_CON_INTENCION}"', value=False):
    selected_status.append(STATUS_CON_INTENCION)
if st.sidebar.checkbox(f'Incluir "{STATUS_VENDIDAS}"', value=False):
    selected_status.append(STATUS_VENDIDAS) # Asumiendo 'vendidas' es el estatus para propiedades vendidas

property_status_filter = ','.join(selected_status)

# Exclusivas y Opción
st.sidebar.subheader('Exclusividad y Opción')
is_exclusive_filter = st.sidebar.checkbox('Mostrar solo exclusivas', value=True) # Por defecto True
has_option_filter = st.sidebar.checkbox('Incluir propiedades con estatus "opción"', value=False) # Por defecto False

contract_types_to_include = []
if is_exclusive_filter:
    contract_types_to_include.append(CONTRACT_TYPE_EXCLUSIVA)
if has_option_filter:
    contract_types_to_include.append(CONTRACT_TYPE_OPCION)

# Comisión Mínima
st.sidebar.subheader('Comisión Mínima')
min_commission_input = st.sidebar.number_input('Comisión Mínima (%)', min_value=0.0, max_value=100.0, value=3.0, step=0.5)

# Tipo de Propiedad
property_types = ['casa', 'departamento', 'terreno', 'oficina', 'local', 'bodega', 'consultorio'] # Puedes expandir esta lista
selected_property_type = st.sidebar.multiselect('Tipo de Propiedad', options=property_types, default=os.environ.get('PROPERTY_TYPE', '').split(',') if os.environ.get('PROPERTY_TYPE') else [])

# Recámaras
min_bedrooms_input = st.sidebar.number_input('Recámaras Mínimas', min_value=0, value=int(os.environ.get('MIN_BEDROOMS', 0)))

# Baños
min_bathrooms_input = st.sidebar.number_input('Baños Mínimos', min_value=0, value=int(float(os.environ.get('MIN_BATHROOMS', 0.0))))

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
    keywords_description=keywords_description_input,
    property_status=property_status_filter,
    min_commission=min_commission_input,
    contract_types_to_include=contract_types_to_include
)

if not properties_df.empty:
    st.subheader('Propiedades Seleccionadas')

    # Calcular 'días en mercado'
    if 'fecha_alta' in properties_df.columns:
        properties_df['fecha_alta'] = pd.to_datetime(properties_df['fecha_alta'])
        properties_df['dias_en_mercado'] = (pd.to_datetime('today') - properties_df['fecha_alta']).dt.days

    # Redondear metros de construcción y terreno
    if 'm2_construccion' in properties_df.columns:
        properties_df['m2_construccion'] = properties_df['m2_construccion'].round()
    if 'm2_terreno' in properties_df.columns:
        properties_df['m2_terreno'] = properties_df['m2_terreno'].round()

    # Unificar baños totales (sumando medios baños)
    if 'banos' in properties_df.columns and 'medios_banos' in properties_df.columns:
        properties_df['banos_totales'] = properties_df['banos'] + (properties_df['medios_banos'] * 0.5)
    elif 'banos' in properties_df.columns:
        properties_df['banos_totales'] = properties_df['banos']
    elif 'medios_banos' in properties_df.columns:
        properties_df['banos_totales'] = properties_df['medios_banos'] * 0.5

    # Eliminar columnas de fechas y cocina
    columns_to_drop = [
        'fecha_alta', 'fecha_creacion', 'fecha_modificacion', 'cocina', 'banos', 'medios_banos',
        'apellido_paterno_agente', 'apellido_materno_agente', 'created_at', 'updated_at',
        'latitud', 'longitud', 'codigo_postal', 'comision_compartir_externas'
    ]
    properties_df = properties_df.drop(columns=[col for col in columns_to_drop if col in properties_df.columns], errors='ignore')

    st.write(f"Total de propiedades encontradas: {len(properties_df)}")
    st.dataframe(properties_df, column_config={
        "precio": st.column_config.NumberColumn("Precio", format="$%,d"),
        "comision": st.column_config.NumberColumn("Comisión", format="%.2f%%") # Assuming commission is a percentage
    })

    # Tabla adicional para propiedades con campos faltantes
    st.subheader('Propiedades con Campos Faltantes')

    # Definir columnas clave que no deberían estar vacías
    # Usamos las columnas originales para la detección de faltantes antes de cualquier transformación
    # y luego mostramos las columnas transformadas si existen
    missing_check_columns = ['banos', 'medios_banos', 'm2_construccion', 'm2_terreno', 'descripcion']

    # Filtrar propiedades donde al menos una de las columnas clave es nula o vacía
    # Asegurarse de que las columnas existan antes de intentar acceder a ellas
    incomplete_properties_mask = pd.Series([False] * len(properties_df)) # Máscara inicial de falsos
    for col in missing_check_columns:
        if col in properties_df.columns:
            if properties_df[col].dtype == 'object': # Para columnas de texto, verificar si son nulas o cadenas vacías
                incomplete_properties_mask = incomplete_properties_mask | properties_df[col].isnull() | (properties_df[col] == '')
            else: # Para columnas numéricas, verificar solo nulos
                incomplete_properties_mask = incomplete_properties_mask | properties_df[col].isnull()

    incomplete_properties_df = properties_df[incomplete_properties_mask]

    if not incomplete_properties_df.empty:
        st.write(f"Total de propiedades con campos faltantes: {len(incomplete_properties_df)}")
        st.dataframe(incomplete_properties_df)
    else:
        st.info("No se encontraron propiedades con campos faltantes en las columnas clave.")

    # Puedes añadir más visualizaciones aquí, por ejemplo:
    # st.subheader('Distribución de Precios')
    # st.hist(properties_df['precio'])

    # st.subheader('Propiedades en Mapa (si tienes latitud y longitud)')
    # if 'latitud' in properties_df.columns and 'longitud' in properties_df.columns:
    #     st.map(properties_df)

else:
    st.info("No se encontraron propiedades o hubo un error al cargar los datos.")
