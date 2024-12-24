import pytest
import json
from datetime import datetime
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String,
    DateTime, ForeignKey
)
from sqlalchemy.sql import text
from src.introspect import introspect_database

POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_USER = "postgres"  # Username for test database
POSTGRES_PASSWORD = "postgres"  # Password for test database 
POSTGRES_NAME = "nestjs"  # Test database name

def create_test_db(connection_string: str):
    """Helper function to create a test database with known schema"""
    engine = create_engine(connection_string)
    
    # Create test schema
    with engine.begin() as conn:
        conn.execute(text('DROP SCHEMA IF EXISTS test_schema CASCADE'))
        conn.execute(text('CREATE SCHEMA test_schema'))
    
    metadata = MetaData(schema='test_schema')  # Set schema for all tables
    
    # Create a test table
    Table('test_table', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50), nullable=False)
    )
    
    # Create tables
    metadata.create_all(engine)
    
    return engine

def test_introspect_database():
    """Test database introspection with PostgreSQL database"""
    # PostgreSQL connection string
    connection_string = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"
    )
    
    # Create test database
    engine = create_test_db(connection_string)
    
    # Introspect the database
    schema_json = introspect_database(connection_string)
    schema = json.loads(schema_json)
    
    # Verify the schema structure - note the schema-qualified table name
    assert 'test_schema.test_table' in schema
    assert 'columns' in schema['test_schema.test_table']
    
    columns = schema['test_schema.test_table']['columns']
    assert 'id' in columns
    assert 'name' in columns
    
    # Verify column properties
    assert columns['id']['primary_key'] is True
    assert columns['name']['nullable'] is False
    assert 'VARCHAR(50)' in columns['name']['type'].upper()

def test_introspect_empty_schema():
    """Test introspection of an empty schema"""
    connection_string = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"
    )
    
    engine = create_engine(connection_string)
    
    # Create empty schema
    with engine.begin() as conn:
        conn.execute(text('DROP SCHEMA IF EXISTS empty_schema CASCADE'))
        conn.execute(text('CREATE SCHEMA empty_schema'))
    
    schema_json = introspect_database(connection_string, schema='empty_schema')
    schema = json.loads(schema_json)
    
    assert len(schema) == 0

def test_introspect_invalid_schema():
    """Test introspection with non-existent schema"""
    connection_string = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"
    )
    
    schema_json = introspect_database(connection_string, schema='nonexistent_schema')
    schema = json.loads(schema_json)
    
    assert 'error' in schema

def test_complex_schema():
    """Test introspection with various column types and relationships"""
    connection_string = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
        f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"
    )
    
    engine = create_engine(connection_string)
    
    # Create test schema with complex tables
    with engine.begin() as conn:
        conn.execute(text('DROP SCHEMA IF EXISTS complex_schema CASCADE'))
        conn.execute(text('CREATE SCHEMA complex_schema'))
    
    metadata = MetaData(schema='complex_schema')
    
    # Parent table
    users = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('email', String(100), unique=True, nullable=False),
        Column('points', Integer, default=0),
        Column('location', String(50))
    )
    
    # Child table with foreign key
    posts = Table('posts', metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer, ForeignKey('complex_schema.users.id')),
        Column('title', String(200), nullable=False),
        Column('created_at', DateTime, server_default=text('CURRENT_TIMESTAMP'))
    )
    
    metadata.create_all(engine)
    
    schema_json = introspect_database(connection_string, schema='complex_schema')
    schema = json.loads(schema_json)
    
    # Verify complex schema structure
    assert 'complex_schema.users' in schema
    assert 'complex_schema.posts' in schema
    
    # Check foreign key relationship
    posts_schema = schema['complex_schema.posts']
    assert len(posts_schema['columns']['user_id']['foreign_keys']) > 0
    
    # Check column types and constraints
    users_schema = schema['complex_schema.users']
    assert users_schema['columns']['email']['nullable'] is False
    assert 'TIMESTAMP' in posts_schema['columns']['created_at']['type'].upper()

def test_introspect_invalid_connection():
    """Test handling of invalid connection string"""
    schema_json = introspect_database("invalid://connection:string")
    schema = json.loads(schema_json)
    
    # Verify error handling
    assert 'error' in schema
