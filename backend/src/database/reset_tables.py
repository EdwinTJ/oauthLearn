from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .models import User, Video, Comment, AISummary  # Import your models
from .database import Base, engine  # Import Base and engine from your database setup
from .database import DATABASE_URL  # Ensure your database URL is available


# Create a new engine instance
engine = create_engine(DATABASE_URL)

# Step 1: Drop all existing tables
def drop_all_tables():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("All tables have been dropped.")

# Step 2: Recreate tables from the models
def recreate_tables():
    print("Recreating all tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables have been recreated.")

# Optional: Inspect the database to see the current tables and columns
def show_tables():
    inspector = inspect(engine)

    # Get all table names
    tables = inspector.get_table_names()
    print("Tables in the database:")
    for table_name in tables:
        print(f"\nTable: {table_name}")
        # Get the columns in each table
        columns = inspector.get_columns(table_name)
        print("Columns:")
        for column in columns:
            name = column['name']
            data_type = column['type']
            nullable = column['nullable']
            default = column['default']
            print(f" - {name}: {data_type}, Nullable: {nullable}, Default: {default}")

if __name__ == "__main__":
    # Step 3: Drop, recreate tables, and display schema
    drop_all_tables()
    recreate_tables()
    show_tables()  # Optional: Check the current schema