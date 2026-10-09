import json
import os
import tkinter as tk
from helpers import clean_screen
from canvas import app
from PIL import Image, ImageTk

base_folder = os.path.dirname(__file__)

def update_current_user(username, product_id):
    with open("db/users.txt", "r+") as f:
        users = [json.loads(u.strip()) for u in f]
        for user in users:
            if user["username"] == username:
                user["products"].append(product_id)
                f.seek(0)
                f.truncate()
                f.writelines(json.dumps(u) + "\n" for u in users)
                return

def purchase_product(product_id):
    with open("db/products.txt", "r+") as f:
        products = [json.loads(p.strip()) for p in f]
        for product in products:
            if product["id"] == product_id:
                product["count"] -= 1
                f.seek(0)
                f.truncate()
                f.writelines(json.dumps(p) + "\n" for p in products)
                return

def buy_product(product_id):
    with open("db/current_user.txt") as file:
        username = file.read().strip()

    if username:
        update_current_user(username, product_id)
        purchase_product(product_id)

    render_products_screen()

def add_product(name, image, count):
    with open("db/products.txt", "r+") as f:
        if name == "" or image == "" or count == "":
            render_add_product_screen(error="All fields are required!")
            return
        if not count.isdigit():
            render_add_product_screen(error="Count must be a valid number")
            return
        f.write(json.dumps({
            "id": len(f.readlines()) + 1,
            "name": name,
            "img_path": image,
            "count": int(count)
        }) + "\n")

    render_products_screen()


def render_add_product_screen(error=None):
    clean_screen()

    tk.Label(app, text="Name: ").grid(row=0, column=0)
    name = tk.Entry(app)
    name.grid(row=0, column=1)

    tk.Label(app, text="Image: ").grid(row=1, column=0)
    img = tk.Entry(app)
    img.grid(row=1, column=1)

    tk.Label(app, text="Count: ").grid(row=2, column=0)
    count = tk.Entry(app)
    count.grid(row=2, column=1)

    tk.Button(app,
              text="Add",
              command=lambda: add_product(name.get(), img.get(), count.get())
              ).grid(row=3, column=0)

    if error:
        tk.Label(app, text=error).grid(row=4, column=0)

def render_products_screen():
    clean_screen()

    with open("db/current_user.txt") as f:
        username = f.read()
    with open("db/users.txt") as f:
        users = [json.loads(u.strip()) for u in f]
        for user in users:
            if user["username"] == username:
                if user.get("is_admin"):
                    tk.Button(app,
                              text="Add product",
                              command=render_add_product_screen
                              ).grid(row=0, column=0)
                break

    with open("db/products.txt") as file:
        products = [json.loads(p.strip()) for p in file]
        products = [p for p in products if p["count"] > 0]
        products_per_row = 6
        rows_for_product = len(products[0])
        for i, product in enumerate(products):
            row = i // products_per_row * rows_for_product + 1
            column = i % products_per_row

            tk.Label(app, text=product["name"]).grid(row=row, column=column)

            img = Image.open(os.path.join(base_folder, "db/images", product["img_path"])).resize((100, 100))
            photo_image = ImageTk.PhotoImage(img)
            image_label = tk.Label(image=photo_image)
            image_label.image = photo_image
            image_label.grid(row=row+1, column=column)

            tk.Label(app, text=product["count"]).grid(row=row+2, column=column)
            tk.Button(app,
                      text=f"Buy {product['id']}",
                      command=lambda p=product["id"]: buy_product(p)
                      ).grid(row=row+3, column=column)




