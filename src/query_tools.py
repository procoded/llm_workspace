from typing import Dict, List, Optional, Tuple
from sqlalchemy import create_engine, text
import pandas as pd
import re
import json

class QueryTools:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.allowed_tables = set()  # Will be populated from schema
        self.allowed_columns = {}    # Will be populated from schema

    def validate_query(self, query: str) -> Tuple[bool, str]:
        """Validate SQL query for safety and allowed operations"""
        # Remove markdown code block formatting if present
        query = re.sub(r'^```sql\s*|\s*```$', '', query, flags=re.MULTILINE)
        
        # Remove any SQL comments and normalize whitespace
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        query = ' '.join(query.lower().split())
        
        # Add debug logging
        print(f"Normalized query: {query}")  # Debug logging
        
        # Extract the first word to check if it's SELECT
        first_word = query.split()[0] if query.split() else ''
        print(f"First word: '{first_word}'")  # Debug logging
        
        if first_word != 'select':
            return False, "Only SELECT queries are allowed"

        # Prevent multiple statements
        if ";" in query[:-1]:  # Allow semicolon at end
            return False, "Multiple statements are not allowed"

        # Check for dangerous keywords in a way that won't flag subqueries
        dangerous_patterns = [
            r'\b(drop|delete|truncate|update|insert|alter|create)\b\s+\w+',  # Must be followed by a word
            r';\s*(drop|delete|truncate|update|insert|alter|create)\b'  # After semicolon
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False, f"Dangerous operations not allowed"

        # Skip table validation for now as schema might not be loaded yet
        if self.allowed_tables:
            tables_in_query = self._extract_tables(query)
            invalid_tables = [t for t in tables_in_query if t not in self.allowed_tables]
            if invalid_tables:
                return False, f"Invalid tables referenced: {', '.join(invalid_tables)}"

        return True, "Query validated successfully"

    def execute_query(self, query: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """Execute a validated SQL query and return results"""
        # Remove markdown code block formatting if present
        query = re.sub(r'^```sql\s*|\s*```$', '', query, flags=re.MULTILINE)
        
        # Add debug logging
        print(f"Executing query: {query}")
        
        is_valid, message = self.validate_query(query)
        if not is_valid:
            print(f"Validation failed: {message}")  # Debug logging
            return False, message, None

        try:
            # Use pandas read_sql_query with the SQLAlchemy text object
            df = pd.read_sql_query(sql=text(query), con=self.engine)
            return True, "Query executed successfully", df
        except Exception as e:
            print(f"Execution error: {str(e)}")  # Debug logging
            return False, f"Error executing query: {str(e)}", None

    def _extract_tables(self, query: str) -> List[str]:
        """Extract table names from SQL query"""
        # More comprehensive regex for table names
        table_pattern = r'''
            \b(FROM|JOIN)\s+    # FROM or JOIN keyword
            (?!.*SELECT)        # Not followed by SELECT (to avoid subqueries)
            ([a-zA-Z_][a-zA-Z0-9_]*) # Table name
        '''
        
        matches = re.finditer(table_pattern, query, re.IGNORECASE | re.VERBOSE)
        tables = [match.group(2) for match in matches]
        return list(set(tables))

    def update_schema_info(self, schema_json: str):
        """Update allowed tables and columns from schema"""
        try:
            schema = json.loads(schema_json)
            self.allowed_tables = set()
            self.allowed_columns = {}
            
            for table_name, table_info in schema.items():
                # Strip schema prefix if present
                clean_table_name = table_name.split('.')[-1]
                self.allowed_tables.add(clean_table_name)
                self.allowed_columns[clean_table_name] = list(table_info['columns'].keys())
                
            print(f"Loaded tables: {self.allowed_tables}")  # Debug logging
        except Exception as e:
            print(f"Error updating schema info: {str(e)}")  # Debug logging
