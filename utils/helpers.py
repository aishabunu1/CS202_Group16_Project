def calculate_discounted_price(original_price, discount_percentage):
    return round(original_price * (1 - discount_percentage / 100), 2)