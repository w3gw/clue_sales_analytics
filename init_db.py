from utils.database import init_db

def main():
    print("Initializing database...")
    engine = init_db()
    print("Database initialized successfully!")
    print("Tables created:")
    print("- sales (with indexes on date, product_id, region, and date+product_id)")

if __name__ == "__main__":
    main()