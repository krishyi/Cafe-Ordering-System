CATALOG = {
    "espresso": {"price": 3.50, "category": "beverage"},
    "latte": {"price": 5.00, "category": "beverage"},
    "cappuccino": {"price": 4.50, "category": "beverage"},
    "americano": {"price": 3.00, "category": "beverage"},
    "croissant": {"price": 3.00, "category": "food"},
    "muffin": {"price": 2.50, "category": "food"},
    "sandwich": {"price": 7.00, "category": "food"},
}

COMBOS = {
    "breakfast_deal": {
        "items": ["latte", "croissant"],
        "discount": 1.50,
        "label": "Breakfast Deal"
    },
    "coffee_and_snack": {
        "items": ["espresso", "muffin"],
        "discount": 1.00,
        "label": "Coffee & Snack"
    }
}

MODIFIERS = {
    "oat_milk": {"price": 0.50, "applies_to": ["beverage"]},
    "extra_shot": {"price": 0.75, "applies_to": ["beverage"]},
    "large": {"price": 1.00, "applies_to": ["beverage", "food"]}
}