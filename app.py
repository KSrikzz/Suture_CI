def calculate_total(price, tax):
    return price + (price * tax)

if __name__ == "__main__":
    print(calculate_total(100, "10%"))