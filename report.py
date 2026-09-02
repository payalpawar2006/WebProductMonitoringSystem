import sqlite3


DATABASE = "data/products.db"


def generate_report():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    # Get all products
    cursor.execute("""
        SELECT product_url, product_name, price,
               availability, scraped_at
        FROM products
        ORDER BY product_url, scraped_at
    """)

    rows = cursor.fetchall()

    price_increase = 0
    price_decrease = 0
    newly_available = 0
    became_unavailable = 0
    new_products = 0
    no_change = 0

    previous_data = {}

    for row in rows:

        url = row[0]
        name = row[1]
        price = row[2]
        availability = row[3]

        current_available = (
            "in stock" in availability.lower()
        )

        # First snapshot
        if url not in previous_data:

            new_products += 1

            previous_data[url] = (
                price,
                current_available
            )

            continue

        old_price, old_available = previous_data[url]

        changed = False

        # Price increase
        if price > old_price:

            price_increase += 1
            changed = True

        # Price decrease
        elif price < old_price:

            price_decrease += 1
            changed = True

        # Became unavailable
        if old_available and not current_available:

            became_unavailable += 1
            changed = True

        # Newly available
        elif not old_available and current_available:

            newly_available += 1
            changed = True

        if not changed:

            no_change += 1

        # Update previous snapshot
        previous_data[url] = (
            price,
            current_available
        )


    connection.close()


    # ==========================================
    # REPORT
    # ==========================================

    print("\n")
    print("==========================================")
    print("          PRODUCT MONITORING REPORT")
    print("==========================================")

    print(
        f"\nNew Products          : {new_products}"
    )

    print(
        f"Price Increases       : {price_increase}"
    )

    print(
        f"Price Decreases       : {price_decrease}"
    )

    print(
        f"Newly Available       : {newly_available}"
    )

    print(
        f"Became Unavailable    : {became_unavailable}"
    )

    print(
        f"No Change             : {no_change}"
    )

    print("\n==========================================")


if __name__ == "__main__":

    generate_report()
    