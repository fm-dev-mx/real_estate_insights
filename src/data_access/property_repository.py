import pandas as pd
import psycopg2
from psycopg2 import extras
import logging

from src.data_access.database_connection import get_db_connection

logger = logging.getLogger(__name__)

class PropertyRepository:
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

    def _get_connection(self):
        return get_db_connection(self.db_name, self.db_user, self.db_password, self.db_host, self.db_port)

    def load_properties(self, df, db_columns):
        """
        Carga un DataFrame de pandas a la tabla 'properties' en PostgreSQL.
        Utiliza INSERT ... ON CONFLICT (id) DO UPDATE para manejar duplicados.
        """
        logger.info("[LOAD] Iniciando carga de datos a PostgreSQL.")
        conn = None
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            logger.info("[LOAD] Conexión a la base de datos PostgreSQL exitosa.")

            columns = db_columns

            data_to_insert = []
            for index, row in df[columns].iterrows():
                processed_row = []
                for col_name in columns:
                    value = row[col_name]
                    if pd.isna(value):
                        processed_row.append(None)
                    elif isinstance(value, pd.Int64Dtype.type):
                        processed_row.append(int(value))
                    elif isinstance(value, bool):
                        processed_row.append(bool(value))
                    else:
                        processed_row.append(value)
                data_to_insert.append(tuple(processed_row))

            update_columns = [col for col in columns if col not in ['id', 'fecha_alta']]
            update_set_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])
            update_set_clause += ", updated_at = CURRENT_TIMESTAMP"

            insert_sql = f'''
            INSERT INTO properties ({', '.join(columns)})
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                {update_set_clause}
            '''

            logger.info(f"[LOAD] Insertando/actualizando {len(data_to_insert)} registros en la tabla 'properties'.")
            extras.execute_values(cur, insert_sql, data_to_insert, page_size=1000)
            conn.commit()
            logger.info(f"[LOAD] Carga de datos a PostgreSQL completada exitosamente. {len(data_to_insert)} registros procesados.")

        except psycopg2.Error as e:
            logger.error(f"[LOAD] Error al cargar datos a PostgreSQL: {e}")
            if conn:
                conn.rollback()
        except Exception as e:
            logger.error(f"[LOAD] Un error inesperado ocurrió durante la carga de datos: {e}")
        finally:
            if conn:
                conn.close()
                logger.info("[LOAD] Conexión a la base de datos cerrada.")

    def get_properties_from_db(
        self, min_price=None, max_price=None, property_operation_type=None, property_type=None,
        min_bedrooms=None, min_bathrooms=None, max_age_years=None,
        min_construction_m2=None, min_land_m2=None, has_parking=None, keywords_description=None,
        property_status=None, min_commission=None, contract_types_to_include=None
    ):
        """
        Obtiene propiedades de la base de datos PostgreSQL aplicando varios filtros.
        """
        conn = None
        try:
            conn = self._get_connection()
            logger.info("[DB_RETRIEVE] Conexión a la base de datos exitosa.")

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
                query += " AND banos_totales >= %(min_bathrooms)s"
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
                query += " AND tipo_contrato IN %(contract_types_to_include)s"
                params['contract_types_to_include'] = tuple(contract_types_to_include)
            if min_commission is not None:
                query += " AND comision >= %(min_commission)s"
                params['min_commission'] = float(min_commission)

            logger.info(f"[DB_RETRIEVE] Ejecutando consulta SQL: {query}")
            logger.info(f"[DB_RETRIEVE] Con parámetros: {params}")

            df = pd.read_sql(query, conn, params=params)
            logger.info(f"[DB_RETRIEVE] Consulta SQL ejecutada. Se encontraron {len(df)} propiedades.")

            return df

        except psycopg2.Error as e:
            logger.error(f"[DB_RETRIEVE] Error de PostgreSQL al cargar propiedades: {e}")
        except ValueError as e:
            logger.error(f"[DB_RETRIEVE] Error de configuración de la base de datos: {e}")
        except Exception as e:
            logger.error(f"[DB_RETRIEVE] Un error inesperado ocurrió al cargar propiedades: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if conn:
                conn.close()
                logger.info("[DB_RETRIEVE] Conexión a la base de datos cerrada.")
        return pd.DataFrame()
