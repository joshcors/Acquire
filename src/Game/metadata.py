import json
import os 

dir_path = os.path.dirname(os.path.realpath(__file__))

def save_stock_metadata():
    stock_price_path = os.path.join(dir_path, "STOCK_PRICE.json")
    bonus_path = os.path.join(dir_path, "BONUS.json")

    stock_price = {}
    bonus = {}

    hotels = ["Tower", "Luxor", "American", "Worldwide", "Festival", "Imperial", "Continental"]

    starting = {}

    for hotel in hotels:
        if hotel in ["Tower", "Luxor"]:
            starting[hotel] = 200
        elif hotel in ["American", "Worldwide", "Festival"]:
            starting[hotel] = 300
        else:
            starting[hotel] = 400

    slices = [slice(0,3), slice(3, 4), slice(4, 5), slice(5, 6), slice(6, 11), slice(11, 21), slice(21, 31), slice(31, 41), slice(41, 42)]

    for hotel in hotels:
        stock_price[hotel] = {}
        bonus[hotel] = {}

        value = starting[hotel]
        values = [0 for i in range(42)]

        for _slice in slices:
            values[_slice] = [value, ] * (_slice.stop - _slice.start)
            value += 100

        for n in range(2, 42):
            stock_price[hotel][n] = values[n]
            bonus[hotel][n] = values[n] * 10

    with open(stock_price_path, "w") as f:
        json.dump(stock_price, f, indent=2)

    with open(bonus_path, "w") as f:
        json.dump(bonus, f, indent=2)

def save_stock_names():
    names = ["Tower", "Luxor", "American", "Worldwide", "Festival", "Imperial", "Continental"]

    name_write_string = '\n'.join(names)

    with open(os.path.join(dir_path, "stock_names.txt"), 'w') as f:
        f.write(name_write_string)

if __name__=="__main__":
    save_stock_metadata()
    save_stock_names()