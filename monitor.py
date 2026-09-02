from database import Database


def check_product_change(database, name, price, availability, url):

    # Previous snapshot database मधून घ्या
    previous = database.get_previous_product(url)

    # Product पहिल्यांदाच मिळाला
    if previous is None:
        return "NEW PRODUCT"

    old_name, old_price, old_availability, old_rating, old_url, old_time = previous

    changes = []

    # ==========================================
    # PRICE CHANGE
    # ==========================================

    if price > old_price:
        changes.append(
            f"PRICE INCREASE: £{old_price} -> £{price}"
        )

    elif price < old_price:
        changes.append(
            f"PRICE DECREASE: £{old_price} -> £{price}"
        )

    # ==========================================
    # AVAILABILITY CHANGE
    # ==========================================

    old_available = "in stock" in old_availability.lower()
    current_available = "in stock" in availability.lower()

    # Product unavailable झाला
    if old_available and not current_available:

        changes.append(
            "PRODUCT BECAME UNAVAILABLE"
        )

    # Product पुन्हा available झाला
    elif not old_available and current_available:

        changes.append(
            "PRODUCT IS NOW AVAILABLE"
        )

    # ==========================================
    # NO CHANGE
    # ==========================================

    if not changes:
        return "NO CHANGE"

    return " | ".join(changes)