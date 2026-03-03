def calculate_total(price, tax):
    return price + (price * float(tax.strip('%')) / 100)

if __name__ == "__main__":
    print(calculate_total(100, "10%"))