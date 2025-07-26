import streamlit as st
import pandas as pd
import os
import subprocess
import logging

from src.utils.logging_config import setup_logging

setup_logging(log_file_prefix="dashboard_app_log")
logger = logging.getLogger(__name__)
logger.info("Dashboard app started.")

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from src.utils.constants import (
    STATUS_EN_PROMOCION, STATUS_CON_INTENCION, STATUS_VENDIDAS,
    CONTRACT_TYPE_EXCLUSIVA, CONTRACT_TYPE_OPCION,
    DEFAULT_MIN_PRICE, DEFAULT_MAX_PRICE, DEFAULT_PROPERTY_OPERATION_TYPE,
    DEFAULT_MIN_BEDROOMS, DEFAULT_MIN_BATHROOMS, DEFAULT_MAX_AGE_YEARS,
    DEFAULT_MIN_CONSTRUCTION_M2, DEFAULT_MIN_LAND_M2, DEFAULT_HAS_PARKING,
    DEFAULT_KEYWORDS_DESCRIPTION, DEFAULT_IS_EXCLUSIVE_FILTER, DEFAULT_HAS_OPTION_FILTER,
    PDF_DOWNLOAD_BASE_DIR
)
from src.data_access.property_repository import PropertyRepository
from src.visualization.dashboard_logic import apply_dashboard_transformations
from src.data_processing.data_validator import get_incomplete_properties, COLUMN_PRIORITY
from src.data_collection.download_pdf import download_property_pdf
from src.scripts.pdf_autofill import autofill_from_pdf
from src.scripts.apply_manual_fixes import apply_manual_fixes

# Initialize PropertyRepository with environment variables
property_repo = PropertyRepository(
    db=os.getenv('REI_DB_NAME'),
    user=os.getenv('REI_DB_USER'),
    pwd=os.getenv('REI_DB_PASSWORD'),
    host=os.getenv('REI_DB_HOST'),
    port=os.getenv('REI_DB_PORT')
)

# --- Streamlit App ---
st.set_page_config(layout="wide")
st.title('Análisis de Propiedades Inmobiliarias')

# --- Columnas de la tabla según la vista seleccionada ---
FIXED_INITIAL_COLUMNS = ["id", "colonia", "precio"]

SUMMARY_VIEW_COLUMNS = FIXED_INITIAL_COLUMNS + [
    "m2_construccion", "m2_terreno", "recamaras", "banos_totales", "edad"
]

DETAILED_VIEW_COLUMNS = FIXED_INITIAL_COLUMNS + [
    "tipo_operacion", "tipo_contrato", "status", "nombre_agente", "comision", "descripcion"
]

INVESTMENT_VIEW_COLUMNS = FIXED_INITIAL_COLUMNS + [
    "dias_en_mercado", "comision", "comision_compartir_externas", "edad", "estacionamientos", "pdf_available"
]

VIEW_OPTIONS = {
    "Resumen": SUMMARY_VIEW_COLUMNS,
    "Detallada": DETAILED_VIEW_COLUMNS,
    "Inversión": INVESTMENT_VIEW_COLUMNS,
}

selected_view_name = st.radio(
    "Selecciona la vista de la tabla:",
    list(VIEW_OPTIONS.keys()),
    horizontal=True,
    key="view_selector"
)

columns_to_display = VIEW_OPTIONS[selected_view_name]

# Sidebar para filtros interactivos
st.sidebar.header('Filtros de Propiedades')

# Rango de Precios
st.sidebar.subheader('Rango de Precios')
min_default_price = DEFAULT_MIN_PRICE
max_default_price = DEFAULT_MAX_PRICE

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
selected_operation_type = st.sidebar.multiselect('Tipo de Operación', options=operation_types, default=DEFAULT_PROPERTY_OPERATION_TYPE)

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
is_exclusive_filter = st.sidebar.checkbox('Mostrar solo exclusivas', value=DEFAULT_IS_EXCLUSIVE_FILTER)
has_option_filter = st.sidebar.checkbox('Incluir propiedades con estatus "opción"', value=DEFAULT_HAS_OPTION_FILTER)

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
selected_property_type = st.sidebar.multiselect('Tipo de Propiedad', options=property_types, default=DEFAULT_PROPERTY_OPERATION_TYPE)

# Recámaras
min_bedrooms_input = st.sidebar.number_input('Recámaras Mínimas', min_value=0, value=int(DEFAULT_MIN_BEDROOMS))

# Baños
min_bathrooms_input = st.sidebar.number_input('Baños Mínimos', min_value=0.0, value=float(DEFAULT_MIN_BATHROOMS))

# Edad de la Propiedad
max_age_years_input = st.sidebar.number_input('Edad Máxima (años)', min_value=0, value=int(DEFAULT_MAX_AGE_YEARS))

# M2 Construcción
min_construction_m2_input = st.sidebar.number_input('M2 Construcción Mínimos', min_value=0.0, value=float(DEFAULT_MIN_CONSTRUCTION_M2))

# M2 Terreno
min_land_m2_input = st.sidebar.number_input('M2 Terreno Mínimos', min_value=0.0, value=float(DEFAULT_MIN_LAND_M2))

# Define parking options
has_parking_options = {
    "Sí": True,
    "No": False,
    "No importa": None
}

# Estacionamiento
selected_has_parking = st.sidebar.radio('¿Tiene Estacionamiento?', 
    options=list(has_parking_options.keys()), 
    format_func=lambda x: x, 
    index=list(has_parking_options.keys()).index("No importa"))

# Palabras Clave en Descripción
keywords_description_input = st.sidebar.text_input('Palabras Clave en Descripción (separadas por coma)', value=DEFAULT_KEYWORDS_DESCRIPTION)

# Filtro para propiedades con datos faltantes críticos
filter_missing_critical = st.sidebar.checkbox('Mostrar solo propiedades con datos críticos faltantes', value=False)

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
    contract_types_to_include=contract_types_to_include,
    filter_missing_critical=filter_missing_critical
)

if not properties_df.empty:
    st.subheader('Propiedades Seleccionadas')

    properties_df = apply_dashboard_transformations(properties_df)

    st.write(f"Total de propiedades encontradas: {len(properties_df)}")

    # Custom display for properties with PDF download/view buttons
    # Ajustar el ancho de las columnas dinámicamente
    num_cols = len(columns_to_display) + 1 # +1 para el botón de PDF o indicador
    if filter_missing_critical: # Si estamos filtrando por gaps, añadimos la columna de acciones
        num_cols += 1
    col_widths = [0.5] * num_cols # Ancho base para todas las columnas
    # Ajustes específicos de ancho para algunas columnas
    if "precio" in columns_to_display: col_widths[columns_to_display.index("precio")] = 1
    if "descripcion" in columns_to_display: col_widths[columns_to_display.index("descripcion")] = 2
    if "colonia" in columns_to_display: col_widths[columns_to_display.index("colonia")] = 1.5

    cols_header = st.columns(col_widths)
    headers = [col.replace("_", " ").title() for col in columns_to_display]

    # Añadir el encabezado para la columna de PDF/Acción
    if selected_view_name == "Inversión":
        headers.append("PDF Disponible")
    else:
        headers.append("PDF")
    
    if filter_missing_critical:
        headers.append("Acciones")

    for col_idx, header in enumerate(headers):
        cols_header[col_idx].write(f"**{header}**")

    for index, row in properties_df.iterrows():
        cols_data = st.columns(col_widths)
        property_id = row['id']
        pdf_local_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')), PDF_DOWNLOAD_BASE_DIR, f"{property_id}.pdf")

        for col_idx, col_name in enumerate(columns_to_display):
            if col_name == "precio":
                cols_data[col_idx].write(f"${row[col_name]:,}")
            elif col_name == "banos_totales":
                cols_data[col_idx].write(f"{row[col_name]:.1f}" if pd.notna(row[col_name]) else "N/A")
            elif col_name == "dias_en_mercado":
                cols_data[col_idx].write(f"{row[col_name]:.0f}")
            elif col_name == "descripcion":
                # Truncar descripción para la vista detallada
                description_text = row[col_name]
                if pd.notna(description_text) and len(description_text) > 100:
                    cols_data[col_idx].write(f"{description_text[:97]}...")
                else:
                    cols_data[col_idx].write(description_text)
            elif col_name == "pdf_available":
                # Mostrar un checkmark o X para la vista de inversión
                if row[col_name]:
                    cols_data[col_idx].write("✅")
                else:
                    cols_data[col_idx].write("❌")
            else:
                cols_data[col_idx].write(row[col_name])

        # Lógica para el botón de PDF (o indicador)
        if selected_view_name != "Inversión": # Si no es la vista de inversión, mostrar el botón
            if os.path.exists(pdf_local_path):
                button_label = "Ver PDF"
                button_type = "primary"
            else:
                button_label = "Descargar PDF"
                button_type = "secondary"

            if cols_data[num_cols - 2].button(button_label, key=f"pdf_action_{property_id}", type=button_type):
                if button_label == "Ver PDF":
                    try:
                        subprocess.Popen([pdf_local_path], shell=True)
                        st.success(f"Abriendo PDF de {property_id}...")
                    except Exception as e:
                        st.error(f"Error al abrir PDF de {property_id}: {e}")
                else: # Descargar PDF
                    with st.spinner(f"Descargando PDF de {property_id}..."):
                        progress_text = "Operación en progreso. Por favor, espere."
                        my_bar = st.progress(0, text=progress_text)
                        downloaded_path = download_property_pdf(property_id)
                        if downloaded_path:
                            my_bar.progress(100, text="Descarga completa!")
                            st.success(f"PDF de {property_id} descargado en {downloaded_path}")
                            st.rerun() # Rerun to update button state
                        else:
                            my_bar.progress(0, text="Fallo en la descarga.")
                            st.error(f"Fallo al descargar PDF de {property_id}.")

        # Lógica para el botón Corregir Gaps
        if filter_missing_critical and row['has_critical_gaps']:
            if cols_data[num_cols - 1].button("Corregir Gaps", key=f"fix_gaps_{property_id}"):
                st.session_state[f'show_fix_gaps_{property_id}'] = not st.session_state.get(f'show_fix_gaps_{property_id}', False)
                st.rerun()

        if st.session_state.get(f'show_fix_gaps_{property_id}', False):
            with st.expander(f"Corregir Gaps para Propiedad {property_id}", expanded=True):
                property_details = property_repo.get_property_details(property_id)
                if property_details is None:
                    st.warning(f"No se pudieron cargar los detalles para la propiedad {property_id}.")
                else:
                    st.write("**Campos Críticos Faltantes:**")
                    missing_critical_cols = []
                    for col in COLUMN_PRIORITY["critical"]:
                        if col not in property_details or pd.isna(property_details[col]) or (isinstance(property_details[col], str) and property_details[col].strip() == ''):
                            missing_critical_cols.append(col)
                            st.write(f"- {col.replace("_", " ").title()}")

                    if not missing_critical_cols:
                        st.success(f"¡La propiedad {property_id} ya no tiene gaps críticos!")
                        st.session_state[f'show_fix_gaps_{property_id}'] = False # Cerrar expander
                        st.rerun()
                    else:
                        st.write("--- Ingrese los valores o use Auto-llenar ---")
                        
                        # Diccionario para almacenar los nuevos valores
                        new_values = {}
                        for col in missing_critical_cols:
                            current_value = property_details.get(col)
                            # Usar un key único para cada input
                            new_values[col] = st.text_input(
                                f"Nuevo valor para {col.replace("_", " ").title()}:",
                                value=str(current_value) if pd.notna(current_value) else "",
                                key=f"input_{property_id}_{col}"
                            )

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Auto-llenar con PDF para {property_id}", key=f"autofill_btn_{property_id}"):
                                with st.spinner("Intentando auto-llenar desde PDF..."):
                                    autofilled_data = autofill_from_pdf(property_id, missing_critical_cols)
                                    if autofilled_data:
                                        for k, v in autofilled_data.items():
                                            st.session_state[f"input_{property_id}_{k}"] = str(v) # Actualizar el input
                                        st.success("Auto-llenado completado. Revise los campos.")
                                        st.rerun() # Rerun para actualizar los inputs
                                    else:
                                        st.warning("No se pudieron auto-llenar datos desde el PDF.")
                        with col2:
                            if st.button(f"Guardar Correcciones Manuales para {property_id}", key=f"save_manual_btn_{property_id}"):
                                with st.spinner("Guardando correcciones..."):
                                    corrections_applied = 0
                                    for col in missing_critical_cols:
                                        old_val = property_details.get(col)
                                        new_val = new_values[col]
                                        
                                        # Convertir a tipo adecuado si es posible (ej. numérico)
                                        if col in ['precio', 'm2_construccion', 'm2_terreno', 'recamaras', 'banos_totales', 'latitud', 'longitud']:
                                            try:
                                                new_val = float(new_val) if '.' in str(new_val) else int(new_val)
                                            except ValueError:
                                                st.error(f"Valor inválido para {col}: {new_val}. Debe ser numérico.")
                                                continue

                                        if str(old_val) != str(new_val) and new_val not in ["", None]: # Solo guardar si hay cambio y no está vacío
                                            success = apply_manual_fixes(
                                                property_id=property_id,
                                                field_name=col,
                                                old_value=old_val,
                                                new_value=new_val,
                                                changed_by="Dashboard User", # TODO: Implement user authentication
                                                change_reason="Manual correction via dashboard"
                                            )
                                            if success:
                                                corrections_applied += 1
                                            else:
                                                st.error(f"Fallo al guardar corrección para {col}.")
                                    
                                    if corrections_applied > 0:
                                        st.success(f"Se aplicaron {corrections_applied} correcciones. Actualizando tabla...")
                                        st.session_state[f'show_fix_gaps_{property_id}'] = False # Cerrar expander
                                        st.rerun() # Rerun para actualizar la tabla
                                    else:
                                        st.warning("No se detectaron cambios o valores válidos para guardar.")

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
