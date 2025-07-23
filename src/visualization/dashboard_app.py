import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from utils.constants import (
    STATUS_EN_PROMOCION, STATUS_CON_INTENCION, STATUS_VENDIDAS,
    CONTRACT_TYPE_EXCLUSIVA, CONTRACT_TYPE_OPCION
)
from data_access.property_repository import PropertyRepository
from visualization.dashboard_logic import apply_dashboard_transformations
from data_processing.data_validator import get_incomplete_properties

load_dotenv() # Cargar variables de entorno desde .env

# --- DB CONFIGURATION (from environment variables) ---
DB_NAME = os.environ.get('REI_DB_NAME', 'real_estate_db')
DB_USER = os.environ.get('REI_DB_USER', 'fm_asesor')
DB_PASSWORD = os.environ.get('REI_DB_PASSWORD')
DB_HOST = os.environ.get('REI_DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('REI_DB_PORT', '5432')

property_repo = PropertyRepository(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)

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
properties_df = property_repo.get_properties_from_db(
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

    properties_df = apply_dashboard_transformations(properties_df)

    st.write(f"Total de propiedades encontradas: {len(properties_df)}")
    st.dataframe(properties_df, column_config={
        "precio": st.column_config.NumberColumn("Precio", format="$,.0f"),
        "comision": st.column_config.NumberColumn("Comisión", format="%.2f%%") # Assuming commission is a percentage
    })

    # Tabla adicional para propiedades con campos faltantes
    st.subheader('Propiedades con Campos Faltantes')

    incomplete_properties_df = get_incomplete_properties(properties_df)

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
