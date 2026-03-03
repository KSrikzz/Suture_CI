def calculate_total(price, tax):
    tax_rate = float(tax.strip('%')) / 100
    return price + (price * tax_rate)

if __name__ == "__main__":
    print(calculate_total(100, "10%"))