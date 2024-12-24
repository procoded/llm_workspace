# src/introspect.py

from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import text
import json
from typing import Optional
from geoalchemy2 import Geometry

def introspect_database(connection_string: str, schema: str = 'test_schema') -> str:
    """
    Connect to the database using the provided connection string,
    reflect the schema, and return a string representation (JSON) of it.
    
    Args:
        connection_string: SQLAlchemy connection string for the database
        schema: Database schema to introspect (defaults to 'test_schema')
        
    Returns:
        JSON string representing the database schema
    """
    try:
        # Create engine
        engine = create_engine(connection_string)
        
        # First check if schema exists
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema"
            ), {"schema": schema})
            if not result.fetchone():
                return json.dumps({"error": f"Schema '{schema}' does not exist"}, indent=2)
        
        # Create MetaData instance with schema
        metadata = MetaData(schema=schema)
        
        # Reflect only the specified schema
        metadata.reflect(bind=engine, schema=schema)
        
        # Build schema representation
        schema_dict = {}
        for table_name, table in metadata.tables.items():
            # Add schema prefix to table name
            qualified_table_name = f"{schema}.{table.name}"
            columns = {}
            for column in table.columns:
                # Handle geometry types specially
                if isinstance(column.type, Geometry):
                    col_type = f"GEOMETRY({column.type.geometry_type}, {column.type.srid})"
                else:
                    col_type = str(column.type)
                
                columns[column.name] = {
                    "type": col_type,
                    "nullable": column.nullable,
                    "primary_key": column.primary_key,
                    "foreign_keys": [str(fk) for fk in column.foreign_keys]
                }
            
            schema_dict[qualified_table_name] = {
                "columns": columns,
                "indexes": [{"name": idx.name, "columns": [c.name for c in idx.columns]} 
                          for idx in table.indexes]
            }
        
        # Convert to JSON string
        return json.dumps(schema_dict, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
