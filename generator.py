from PIL import Image
from random import choice
import json
from pathlib import Path

canvas = input("<< Enter canvas size >> ")
directory = input ("<< Enter path to traits >>")
quantity_ = int(input ("Enter quantity to generate >> "))
canvas = int(canvas.split("x")[0]), int(canvas.split("x")[1])

generated_images = {}

def generate_image(trait_config, size, quantity):
    global generated_images

    # count completed image generations
    generated = 0
    traits = json.load(trait_config)
    while generated != quantity:
        # blank canvas of same size as project
        image_construct = Image.new("RGBA", size)
        selected_traits = []
        for trait in traits:
            if directory:
                path = f"./{directory}/{trait}"
            else:
                path = f"./{trait}"

            path_obj = Path(path)
            items = [i.name for i in path_obj.iterdir() if i.is_file()]
            selected = choice(items)
            im = Image.open(f"{path}/{selected}")
            selected_traits.append(selected)
            image_construct.alpha_composite(im)
        signature = tuple(selected_traits)

        # Prevent Image collision
        if signature not in generated_images:
            generated_images[signature] = True

        image_construct.save(f"{generated}.png")
        print(f"Saved Image {generated}.png")
        generated += 1


with open("traits_config.json", "r") as file:
    generate_image(file, canvas, quantity_)
