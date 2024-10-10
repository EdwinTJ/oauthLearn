from sqlalchemy import create_engine, inspect
from .database import DATABASE_URL

# Create engine
engine = create_engine(DATABASE_URL)

def show_tables():
    # Use SQLAlchemy's inspector to get table info
    inspector = inspect(engine)

    # Get all table names
    tables = inspector.get_table_names()
    
    print("Tables in the database:")
    for table_name in tables:
        print(f"\nTable: {table_name}")
        
        # Get the columns in the table
        columns = inspector.get_columns(table_name)
        
        print("Columns:")
        for column in columns:
            name = column['name']
            data_type = column['type']
            nullable = column['nullable']
            default = column['default']
            print(f" - {name}: {data_type}, Nullable: {nullable}, Default: {default}")

if __name__ == "__main__":
    show_tables()
