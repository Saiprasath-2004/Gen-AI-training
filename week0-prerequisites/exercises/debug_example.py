def calculate_total(price,quantity, discount):
    subtotal = price * quantity
    tax = subtotal * 0.18
    total = subtotal + tax - discount
    return total


result = calculate_total(1000, 2, 50)

print(result)