from src.schema_agent import BaseModel, Field
from typing import Dict, List, Optional
import json
from src.introspect import introspect_database

class ColumnInfo(BaseModel):
    """Represents information about a database column"""
    type: str
    nullable: bool
    primary_key: bool
    foreign_keys: List[str]

class IndexInfo(BaseModel):
    """Represents information about a database index"""
    name: str
    columns: List[str]

class TableInfo(BaseModel):
    """Represents information about a database table"""
    columns: Dict[str, ColumnInfo]
    indexes: List[IndexInfo]

class DatabaseSchema(BaseModel):
    """Represents the entire database schema"""
    tables: Dict[str, TableInfo]

class IntrospectionTool:
    """Tool for database schema introspection"""
    
    @staticmethod
    def introspect(connection_string: str, schema: str = 'public') -> DatabaseSchema:
        """
        Introspect a database schema and return structured information
        
        Args:
            connection_string: Database connection string
            schema: Name of the schema to introspect (default: 'public')
            
        Returns:
            DatabaseSchema object containing the introspected information
            
        Raises:
            ValueError: If introspection fails or returns an error
        """
        # Get JSON string from introspection
        result = introspect_database(connection_string, schema)
        
        # Parse the JSON result
        data = json.loads(result)
        
        # Check for errors
        if 'error' in data:
            raise ValueError(f"Introspection failed: {data['error']}")
            
        # Convert the raw dictionary to our Pydantic model
        return DatabaseSchema(tables=data)

    @staticmethod
    def get_table_info(schema: DatabaseSchema, table_name: str) -> Optional[TableInfo]:
        """
        Get information about a specific table from the schema
        
        Args:
            schema: DatabaseSchema object
            table_name: Name of the table to look up
            
        Returns:
            TableInfo object if table exists, None otherwise
        """
        return schema.tables.get(table_name)
