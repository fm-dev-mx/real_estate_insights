# src/utils/constants.py

# --- Estatus de Propiedad ---
STATUS_EN_PROMOCION = 'enPromocion'
STATUS_CON_INTENCION = 'conIntencion'
STATUS_VENDIDAS = 'vendidas'

# --- Tipos de Contrato ---
CONTRACT_TYPE_EXCLUSIVA = 'exclusiva'
CONTRACT_TYPE_OPCION = 'opcion'

# --- URLs ---
LOGIN_URL = 'https://plus.21onlinemx.com/login2'
PROPERTIES_PAGE_URL = 'https://plus.21onlinemx.com/propiedades'
PDF_BASE_URL = "https://plus.21onlinemx.com/ft/"
PDF_SUFFIX = "/DTF/273/40120"

# --- Default Filter Values for Dashboard ---
DEFAULT_MIN_PRICE = 1500000
DEFAULT_MAX_PRICE = 3500000
DEFAULT_PROPERTY_OPERATION_TYPE = [] # e.g., ['venta']
DEFAULT_MIN_BEDROOMS = 0
DEFAULT_MIN_BATHROOMS = 0.0
DEFAULT_MAX_AGE_YEARS = 999
DEFAULT_MIN_CONSTRUCTION_M2 = 0.0
DEFAULT_MIN_LAND_M2 = 0.0
DEFAULT_HAS_PARKING = None # None for 'No importa', True for 'Sí', False for 'No'
DEFAULT_KEYWORDS_DESCRIPTION = ''
DEFAULT_IS_EXCLUSIVE_FILTER = True
DEFAULT_HAS_OPTION_FILTER = False

# --- Columnas de Base de Datos ---
DB_COLUMNS = [
    'id', 'fecha_alta', 'status', 'tipo_operacion', 'tipo_contrato', 'en_internet',
    'clave', 'clave_oficina', 'subtipo_propiedad', 'calle', 'numero',
    'colonia', 'municipio', 'latitud', 'longitud', 'codigo_postal',
    'precio', 'comision', 'comision_compartir_externas', 'm2_construccion',
    'm2_terreno', 'recamaras', 'banos_totales', 'cocina',
    'niveles_construidos', 'edad', 'estacionamientos', 'descripcion',
    'nombre_agente', 'apellido_paterno_agente', 'apellido_materno_agente'
]

# --- PDF Download Directory ---
PDF_DOWNLOAD_BASE_DIR = "data/pdfs"  # Directory for downloaded PDFs