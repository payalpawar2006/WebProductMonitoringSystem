import sqlite3
import os


class Database:

    def __init__(self, db_name="data/products.db"):

        # Create data folder automatically
        os.makedirs("data", exist_ok=True)

        self.connection = sqlite3.connect(db_name)

        self.create_table()


    def create_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            price REAL,
            availability TEXT,
            rating TEXT,
            product_url TEXT,
            scraped_at TEXT
        )
        """

        self.connection.execute(query)
        self.connection.commit()


    def insert_product(
        self,
        name,
        price,
        availability,
        rating,
        url,
        scraped_at
    ):

        query = """
        INSERT INTO products
        (
            product_name,
            price,
            availability,
            rating,
            product_url,
            scraped_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """

        self.connection.execute(
            query,
            (
                name,
                price,
                availability,
                rating,
                url,
                scraped_at
            )
        )

        self.connection.commit()


    def get_previous_product(self, url):

        query = """
        SELECT
            product_name,
            price,
            availability,
            rating,
            product_url,
            scraped_at
        FROM products
        WHERE product_url = ?
        ORDER BY scraped_at DESC
        LIMIT 1
        """

        cursor = self.connection.execute(
            query,
            (url,)
        )

        return cursor.fetchone()


    def close(self):

        self.connection.close()