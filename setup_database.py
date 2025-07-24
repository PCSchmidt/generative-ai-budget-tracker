"""
Database initialization script for AI Budget Tracker
Run this to set up the database schema on Railway PostgreSQL
"""

import os
import psycopg2
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in .env file")
        return
    
    print(f"🔗 Connecting to database...")
    print(f"Host: {database_url.split('@')[1].split(':')[0]}")
    
    try:
        # Connect to Railway PostgreSQL
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        print("✅ Connected to Railway PostgreSQL!")
        
        # Read and execute the schema
        with open('database/init.sql', 'r') as f:
            schema_sql = f.read()
        
        print("📊 Deploying database schema...")
        cur.execute(schema_sql)
        conn.commit()
        
        print("✅ Database schema deployed successfully!")
        
        # Verify tables were created
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        print(f"📋 Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check sample data
        cur.execute("SELECT COUNT(*) FROM users;")
        user_count = cur.fetchone()[0]
        print(f"👤 Sample users: {user_count}")
        
        cur.execute("SELECT COUNT(*) FROM expenses;")
        expense_count = cur.fetchone()[0]
        print(f"💰 Sample expenses: {expense_count}")
        
        conn.close()
        print("🎉 Database setup complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check your DATABASE_URL in .env file")
        print("2. Ensure Railway PostgreSQL is running")
        print("3. Verify network connectivity")

if __name__ == "__main__":
    main()
