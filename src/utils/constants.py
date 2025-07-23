# src/utils/constants.py

# --- Estatus de Propiedad ---
STATUS_EN_PROMOCION = 'enPromocion'
STATUS_CON_INTENCION = 'conIntencion'
STATUS_VENDIDAS = 'vendidas'

# --- Tipos de Contrato ---
CONTRACT_TYPE_EXCLUSIVA = 'exclusiva'
CONTRACT_TYPE_OPCION = 'opcion'

# --- Columnas de Base de Datos ---
DB_COLUMNS = [
    'id', 'fecha_alta', 'status', 'tipo_operacion', 'tipo_contrato', 'en_internet',
    'clave', 'clave_oficina', 'subtipo_propiedad', 'calle', 'numero',
    'colonia', 'municipio', 'latitud', 'longitud', 'codigo_postal',
    'precio', 'comision', 'comision_compartir_externas', 'm2_construccion',
    'm2_terreno', 'recamaras', 'banios', 'medios_banios', 'cocina',
    'niveles_construidos', 'edad', 'estacionamientos', 'descripcion',
    'nombre_agente', 'apellido_paterno_agente', 'apellido_materno_agente'
]