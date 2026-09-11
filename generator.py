from PIL import Image
from random import choices
import json
from pathlib import Path
from colorama import Fore, Style
import csv


"""
* Construct trait config, users can edit weights for unique trait in the config file
* weight goes from 0 - 100
"""

class AmountExceedsLimit(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
        
class BadLayerConfig(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidRuleSetError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class File:
    def __init__(self, dir_, name, weight, parent_tree):
        self.file = dir_
        self.name = name
        self.weight = weight
        self.parent_trait = parent_tree[-1]
        self.origin_trait = parent_tree[0]


class Trait:
    def __init__(self, name, dir_, config):
        if not dir_.exists():
            raise BadLayerConfig(
                f"Trait {name} is declared in config but no such trait exists within project"
            )
        self.name = name
        self.path = Path(dir_)
        self.sub_traits = []
        # file => weight
        # files held in the trait's root folder
        self.items = [File(self.path / i, i, config["traits"][self.name][i], [self.name])
                      for i in config["traits"][self.name] if i != "subTraits"]
        # category => file => weight
        if "subTraits" in config["traits"][self.name]:
            sub_categories = config["traits"][self.name]["subTraits"]
            self.sub_items = []
            for sub in sub_categories:
                self.sub_traits.append(sub)
                for file in sub_categories[sub]:
                    self.sub_items.append(
                        File(self.path / sub / file, file, sub_categories[sub][file], [self.name, sub]
                             ))
            # Add subitems to total items
            self.items.extend(self.sub_items)

        if self.name in config["rules"]:
            self.rules = config["rules"][self.name]

    # Select randomly from current trait exclude an array of subtraits if required
    def choose(self, from_=None):
        pool = [i for i in self.items if i.parent_trait in from_] if from_ else self.items
        weights = [i.weight for i in self.items if i.parent_trait in from_] if from_ else [i.weight for i in self.items]
        result = choices(pool, k=1, weights=weights)
        result = result[0]
        return result



# Generate the trait config file from given directory. If directory is not provided, default directory "/traits"
#  is used instead.
def build_config(project):
    if (root / project / "trait_config.json").exists():
        decision = input("Do you want to use existing trait config file? (y/n)")
        if decision == "y":
            return
    
    print("A new trait config file will be created for project {project} \n\n")
    name = input("Set project name \n")
    description = input("Set project description \n")
    
    data = {}
    traits = {}
    # Identify individual traits folders and subtrait folders (only immediate subfolders considered)
    dir_ = root / project
    traits_category = [i.name for i in dir_.iterdir() if i.is_dir() and i.name != "out"]
    subtraits = {}

    for i in traits_category:
        sub = []
        for j in (dir_/i).iterdir():
            if j.is_dir():
                sub.append(j.name)
        subtraits[i] = sub

    traits_order = {traits_category.index(i): i for i in traits_category}
    print(f"Found {len(traits_category)} folders and {len(subtraits)} sub folders, Edit layer order")

    # List out layer order in terminal
    count = 1
    for i in traits_category:
        print(Fore.CYAN,f"{count}. {i}")
        if subtraits[i]:
            print(f" {subtraits[i]}")
        count += 1
    print(Style.RESET_ALL,"Enter the order in which the image should be layered using their numbers. e.g, 1, 3, 4, 2")

    order = input(">> ")


    if order:
        order = order.strip()
        order = order.split(",")
        # Re-order layer to match user preference
        traits_category = [traits_order[int(i) - 1] for i in order]
    # reset counter for reuse
    count = 1
    
    print(Style.RESET_ALL, "New layer order")
    for i in traits_category:
        print(Fore.CYAN, f"{count}. {i}")
        if subtraits[i]:
            print(subtraits[i])
        count += 1

    rules_ = {i: {"allowNone": False, "excludes": []} for i in traits_category}

    # Set default rarity config
    for trait in traits_category:
        path = root / dir_ / trait
        items = [i.name for i in path.iterdir() if i.is_file()]
        traits[trait] = {}
        for item in items:
            traits[trait][item] = 1

        # set default rarity for sub traits as well if exist
        if subtraits[trait]:
            traits[trait]["subTraits"] = {}
            for s in subtraits[trait]:
                rules_[s] = {"allowNone": False, "excludes": []}
                sub_items = [j.name for j in (path / s).iterdir() if j.is_file()]
                traits[trait]["subTraits"][s] = {i: 1 for i in sub_items}

    # Construct config skeleton
    data["project"] = {"name": name, "description": description}
    data["traits"] = traits
    data["rules"] = rules_
    # Write config data
    with open(f"./{dir_}/trait_config.json", "w") as file:
        json.dump(data, file, indent=4)
    print(Fore.CYAN,"Trait config built, Edit trait_config.json to set rarity details and trait rules")
    input(f"Click enter to begin image generation")


# Prepare output directories
def create_out(dir_):
    images = Path(f"./{dir_}/out/images")
    metadata = Path(f"./{dir_}/out/metadata")
    # create output directories
    images.mkdir(parents=True, exist_ok=True)
    metadata.mkdir(parents=True, exist_ok=True)
    return images, metadata

# Checks whether quantity amount of items is within range of possible generations of n traits
def can_generate(traits, quantity):
    possible_generations = 1
    for i in traits["traits"]:
        possible_generations *= len(traits["traits"][i])
    print("Possible generations:", possible_generations)
    if possible_generations < quantity:
        return False
    else:
        return True

# If you are excluding something that is not allowed to be none then your rule is faulty
def validate_rules():
    invalid_set = []
    for i in rules:
        for j in rules[i]["excludes"]:
            if not rules[j]["allowNone"]:
                invalid_set.append(j)
    return invalid_set


def select_layers(layers, size, meta):
    global rules

    invalids = validate_rules()
    print(invalids)
    if invalids:
        raise InvalidRuleSetError(f"Traits {invalids} are not allowed to be None")

    # this helps us keep track of subtraits for subtrait level violation inspection and also skip pruned traits in selection loop
    normalization = {i: i.sub_traits for i in layers}
    pruned = {i: False for i in normalization}
    meta = meta
    image = Image.new("RGBA", size)

    selected = []
    for i in normalization:
        if pruned[i]:
            continue
        # randomly choose trait
        choice = i.choose(normalization[i])
        print(choice.parent_trait)
        # apply rules and prune violating traits from pool if trait is defined in config rules
        if choice.parent_trait in rules:
            copy = normalization.copy()
            del copy[i]
            for j in copy:
                # prune main trait if need be
                if j.name in rules[choice.parent_trait]["excludes"]:
                    print("Pruned: ", j.name)
                    pruned[j] = True
                # prune violating subtraits
                else:
                    for k in normalization[j]:
                        if k in rules[choice.parent_trait]["excludes"]:
                            print("Pruned", k)
                    normalization[j] = [k for k in normalization[j] if k not in rules[choice.parent_trait]["excludes"]]
        selected.append(choice)

    for i in selected:
        meta[f"attributes[{i.origin_trait}]"] = i.name[: -4]
        # layer selected trait on top
        im = Image.open(i.file)
        image.alpha_composite(im)
    return selected, image, meta


rules = {}
def generate_image(trait_config, size, quantity, dir_):
    global rules
    # track unique images generated by keeping the layer order as id
    generated_images = set()
    # trait_category -> trait_type -> amount
    distribution = {}
    traits = json.load(trait_config)
    rules = traits["rules"]
    token_id = 1
    
    # Can we generate {quantity} unique images from n traits
    if not can_generate(traits, quantity):
        raise AmountExceedsLimit("Amount of generation required  has exceeded the total amount of possible combinations")
    
    # set up output folders   
    images, metadata = create_out(dir_)
    
    # Opensea format csv metadata headers
    attributes = [f"attributes[{i}]" for i in list(traits["traits"].keys())]
    fields = ["tokenID", "name", "description", "filename"]
    fields.extend(attributes)

    # load traits and validate existence
    layers = []
    for t in traits["traits"]:
        trait_obj = Trait(t, root/dir_/t, traits)
        #path = Path(f"./{dir_}/{t}")
        if t not in distribution:
            distribution[t] = {}
        layers.append(trait_obj)

    # Generate image, record metadata
    with open(metadata/"metadata.csv", "w", newline="") as image_meta:
        # blank canvas of same size as project
        writer = csv.DictWriter(image_meta, fieldnames=fields)
        writer.writeheader()
        while len(generated_images) < quantity:
            data = {"tokenID": token_id, "name": f"{traits["project"]["name"]} #{token_id}",
                "description": f"{traits['project']['description']}",
                "filename": f"{token_id}.png"}

            # construct image and check layer validity
            selected_layers, image, meta = select_layers(layers, size, data)
            # Prevent Image collision
            signature = (i.name for i in selected_layers)
            if signature in generated_images:
                continue
            generated_images.add(signature)
            # update trait distributions
            for i in selected_layers:
                if i.parent_trait not in distribution:
                    distribution[i.parent_trait] = {}
                    distribution[i.parent_trait][i.name] = 1
                elif i.name not in distribution[i.parent_trait]:
                    distribution[i.parent_trait][i.name] = 1
                else:
                    distribution[i.parent_trait][i.name] += 1

                       
            # Write image and metadata
            image.save(f"./{images}/{token_id}.png")
            writer.writerow(meta)
            print(Fore.GREEN, f"Saved Image {token_id}.png", end="\r")
            token_id += 1
            
    # document rarity distribution     
    with open(f"{dir_}/rarity_report.txt", "w") as rarity:
        for k, v in distribution.items():
            rarity.write(f"{k}\n============\n")
            for ik, iv in v.items():
                rarity.write(f"{ik}: {iv}\n")

    print(Fore.LIGHTYELLOW_EX,f"Generated {len(generated_images)} images, saved to ./out")

root = Path("./")

folders = [i.name for i in root.iterdir() if i.is_dir()]
folders = [i for i in folders if i !=".idea" and i !=".git"]
    
for sn, f in enumerate(folders):
    print(Fore.CYAN, f"{sn + 1} {f}")
print(Style.RESET_ALL, "")    

traits_dir = int(input("Choose project directory \n"))
traits_dir = folders[traits_dir - 1]
quantity_ = int(input ("Enter quantity to generate\n") or 10)
canvas = input("Enter canvas to generate e.g 512x512 \n") or "1024x1024"
canvas = int(canvas.split("x")[0]), int(canvas.split("x")[1])

build_config(traits_dir)

with open(f"./{traits_dir}/trait_config.json", "r") as config_file:
    generate_image(config_file, canvas, quantity_, traits_dir)

