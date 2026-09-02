import sqlite3
import csv
import os


DATABASE = "data/products.db"
OUTPUT_FILE = "data/products_report.csv"


def export_to_csv():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            product_name,
            price,
            availability,
            rating,
            product_url,
            scraped_at
        FROM products
        ORDER BY id
    """)

    rows = cursor.fetchall()

    # Create CSV file
    os.makedirs("data", exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        # Header
        writer.writerow([
            "ID",
            "Product Name",
            "Price",
            "Availability",
            "Rating",
            "Product URL",
            "Scraped At"
        ])

        # Data
        writer.writerows(rows)

    connection.close()

    print("\n==========================================")
    print("          CSV EXPORT COMPLETED")
    print("==========================================")

    print(f"Total records exported: {len(rows)}")
    print(f"CSV file: {OUTPUT_FILE}")

    print("==========================================")


if __name__ == "__main__":

    export_to_csv()