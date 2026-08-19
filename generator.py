from PIL import Image
from random import choices
import json
from pathlib import Path
from colorama import Fore, Style

"""
* Construct trait config, users can edit weights for unique trait in the config file
* weight goes from 0 - 100
"""

class BadLayerConfig(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


# Generate the trait config file from given directory. If directory is not provided, default directory "/traits"
#  is used instead.
def build_trait_config(dir_):
    if Path("./trait_config.json").exists():
        decision = input("Do you want to use existing trait config file? (y/n)")
        if decision == "y":
            return
        else:
            print("A new trait config file will be created")

    name = input("Set project name \n")
    description = input("Set project description \n")

    data = {}
    traits = {}


    # Identify traits
    dir_ = Path(f"./{dir_}/")
    traits_category = [i.name for i in dir_.iterdir() if i.is_dir()]
    traits_order = {traits_category.index(i): i for i in traits_category}
    print(f"Found {len(traits_category)} folders, Edit layer order")

    # List out layer order in terminal
    count = 1
    for i in traits_category:
        print(Fore.CYAN,f"{count}. {i}")
        count += 1
    print(Style.RESET_ALL,"Enter the order in which the image should be layered using their numbers. e.g, 1, 3, 4, 2")

    order = input(">> ")
    order = order.strip()
    order = order.split(",")

    # Re-order layer to match user preference
    traits_category = [traits_order[int(i) - 1] for i in order]
    # reset counter for reuse
    count = 1

    for i in traits_category:
        print(Style.RESET_ALL, "New layer order")
        print(Fore.CYAN, f"{count}. {i}")
        count += 1

    for trait in list(traits_category):
        traits[trait] = {}
        path = Path(f"./{dir_}/{trait}")
        items = [i.name for i in path.iterdir() if i.is_file()]
        for item in items:
            traits[trait][item] = 0

    # Construct config skeleton
    data["project"] = {"name": name, "description": description}
    data["traits"] = traits
    # Write config data
    with open("trait_config.json", "w") as file:
        json.dump(data, file, indent=4)
    print(Fore.CYAN,"Trait config built, Edit trait_config.json to set rarity details")


def generate_image(trait_config, size, quantity, dir_):
    # Ensure all image are of equal size and mode
    global generated_images
    # count completed image generations
    generated = 0
    traits = json.load(trait_config)
    images = Path("./out/images")
    metadata = Path("./out/metadata")
    images.mkdir(parents=True, exist_ok=True)
    metadata.mkdir(parents=True, exist_ok=True)

    # Continuous image generation until given amount is reached
    while generated != quantity:
        image_meta = open(metadata/f"{generated}.json", "w")
        data = {}

        skeleton = {"name": f"{traits["project"]["name"]} #{generated}",
            "description": f"{traits['project']['description']}",
            "image": f"{generated}.png",
            "edition": 1,
            "attributes": []
        }

        data.update(skeleton)
        # blank canvas of same size as project
        image_construct = Image.new("RGBA", size)
        selected_traits = []
        for trait in traits["traits"]:
            if dir_:
                path = f"./{dir_}/{trait}"
            else:
                path = f"./{trait}"

            path_obj = Path(path)

            # Fetch all images item from directory
            items = [i.name for i in path_obj.iterdir() if i.is_file()]

            # Assign weights as given in config file
            weights = [traits["traits"][trait][i] for i in items]
            selected = choices(items, k=1, weights=weights)

            # Add traits to metadata
            data["attributes"].append({
                "trait_type": trait,
                "value": selected[0]
            })

            im = Image.open(f"{path}/{selected[0]}")
            selected_traits.append(selected)
            image_construct.alpha_composite(im)
        signature = tuple(selected_traits)

        # Prevent Image collision
        if signature in generated_images:
            continue
        else:
            generated_images.append(signature)

        # Write image and metadata
        image_construct.save(f"./out/images/{generated}.png")
        json.dump(data, image_meta, indent=4)

        print(Fore.GREEN, f"Saved Image {generated}.png")
        generated += 1
    print(Fore.LIGHTYELLOW_EX,f"Generated {generated} images, saved to ./generated")


# def get_canvas_size(img):
#     return img.size

traits_dir = input("Enter traits directory \n") or "traits"
quantity_ = int(input ("Enter quantity to generate\n") or 10)
canvas = input("Enter canvas to generate e.g 512x512 \n")
canvas = int(canvas.split("x")[0]), int(canvas.split("x")[1])

generated_images = []

build_trait_config(traits_dir)

with open("trait_config.json", "r") as config_file:
    generate_image(config_file, canvas, quantity_, traits_dir)

