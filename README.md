# NFT Generator

A lightweight, configurable Python tool for generating unique layered artwork from trait folders.

Built with **Python + Pillow**, this generator automates the process of combining image layers into NFT collections while giving creators control over trait rarity, layer order, collection size, metadata, and output.


> **Status:** Early-stage / actively improving

## ✨ Features

- 🖼️ Layered image generation
- 🎲 Weighted trait selection
- ♻️ Duplicate prevention
- 📊 Rarity reporting
- 📝 CSV metadata generation(Opensea format)
- ⚙️ Automatic trait configuration
- 📁 Automatic output directories
- 🧩 Configurable layer order

## 📦 Requirements

- Python 3.x
- Pillow
- Colorama

Install dependencies:

```bash
pip install pillow colorama
```

## 📂 Project Structure

Organize each collection using trait categories as folders (check the Bots folder for example):

```text
my-collection/
├── Background/
│   ├── Blue.png
│   ├── Red.png
│   └── Green.png
├── Body/
│   ├── Human.png
│   └── Robot.png
├── Eyes/
│   ├── Normal.png
│   ├── Laser.png
│   └── Angry.png
└── Head/
    ├── Cap.png
    ├── Crown.png
    └── None.png
```

Each folder represents a trait category, and each image represents a possible trait.

## 🚀 Getting Started

Clone the repository and install dependencies:

```bash
git clone https://github.com/0xStacker/Nft-Generator
cd Nft-generator
pip install pillow colorama
```

Run the generator:

```bash
python generator.py
```

The generator will display available project directories and ask you to select one.

You will then specify the collection size and canvas dimensions.

Example:

```text
Enter quantity to generate
333

Enter canvas to generate e.g 512x512
1024x1024
```

## ⚙️ Trait Configuration

On the first run, the generator discovers the trait folders and creates a `trait_config.json` file.

You can also choose the order in which layers are composited.

Example:

```text
Found 4 folders, Edit layer order

1. Background
2. Body
3. Eyes
4. Head

Enter the order in which the image should be layered using their numbers.
e.g, 1, 3, 4, 2
```

A generated configuration looks like:

```json
{
    "project": {
        "name": "My Collection",
        "description": "A collection of generated characters."
    },
    "traits": {
        "Background": {
            "Blue.png": 1,
            "Red.png": 1
        },
        "Body": {
            "Robot.png": 1,
            "Human.png": 1
        },
        "Eyes": {
            "Normal.png": 1,
            "Laser.png": 1
        }
    }
}
```

## 🎲 Trait Rarity

Trait weights can be edited directly in `trait_config.json`.

```json
"Eyes": {
    "Normal.png": 70,
    "Laser.png": 20,
    "Angry.png": 10
}
```

Higher weights make traits more likely to be selected.

## ♻️ Duplicate Prevention

Each generated NFT receives a signature based on its selected trait combination.

For example:

```text
Background: Blue.png
Body: Robot.png
Eyes: Laser.png
Head: Cap.png
```

Previously generated combinations are stored and checked before an image is saved. This prevents duplicate trait combinations from entering the collection.

## 🔢 Combination Limit

Before generation begins, the generator calculates the theoretical number of possible combinations.

For example:

```text
Background = 5
Body       = 4
Eyes       = 6
Head       = 3
```

Total:

```text
5 × 4 × 6 × 3 = 360
```

If the requested collection size exceeds the total number of possible combinations, generation stops before attempting to create the collection.

## 🖼️ Image Generation

For every NFT, the generator:

1. Creates a blank RGBA canvas.
2. Selects a trait from every category.
3. Applies the configured weights.
4. Composites the selected layers.
5. Creates a unique trait signature.
6. Checks for duplicates.
7. Saves the image.
8. Records metadata.
9. Updates the rarity distribution.

Generated images are saved to:

```text
<project>/out/images/
```

## 📝 Metadata

The generator creates an opensea-ready CSV metadata file containing:

- Token ID
- Name
- Description
- Filename
- Selected trait for each category

Example:

```csv
tokenID,name,description,filename,attributes[Background],attributes[Body],attributes[Eyes]
1,My Collection #1,A collection of generated characters.,1.png,Blue,Robot,Laser
```

## 📊 Rarity Report

After generation, the generator creates:

```text
rarity_report.txt
```

The report records how many times each trait was selected.

Example:

```text
Background:
============
Blue.png: 72
Red.png: 28

Eyes:
============
Normal.png: 81
Laser.png: 12
Angry.png: 7
```

## 🛠️ How It Works

```text
Trait folders
      │
      ▼
Discover traits
      │
      ▼
Build configuration
      │
      ▼
Configure weights
      │
      ▼
Calculate combinations
      │
      ▼
Select weighted traits
      │
      ▼
Composite layers
      │
      ▼
Check duplicates
      │
      ├── Duplicate → Generate again
      │
      └── Unique
            │
            ▼
        Save image
            │
            ▼
       Save metadata
            │
            ▼
       Update rarity
```

## 📁 Output

After generation:

```text
my-collection/
├── Background/
├── Body/
├── Eyes/
├── Head/
├── trait_config.json
├── rarity_report.txt
└── out/
    ├── images/
    │   ├── 1.png
    │   ├── 2.png
    │   └── ...
    └── metadata/
        └── metadata.csv
```

## ⚠️ Current Limitations

This project is still under development.

- Input validation is limited.
- The interface is currently terminal-based.
- Metadata is currently generated as CSV.
- Existing output handling is basic.
- Trait compatibility rules are not currently supported.
- More advanced collection configuration is still being developed.

## 🗺️ Roadmap

- [ ] Better CLI interface
- [ ] Stronger input validation
- [ ] Cleaner project configuration
- [ ] JSON metadata support
- [ ] Trait compatibility / exclusion rules
- [ ] Better output management
- [ ] Seeded generation
- [ ] Automated rarity analysis
- [ ] Unit tests
- [ ] Installable Python package
- [ ] Command-line arguments
- [ ] Improved error handling
- [ ] Documentation and examples

## 🤝 Contributing

Contributions, ideas, and improvements are welcome.

If you find a bug or have an idea for improving the generator, feel free to open an issue or submit a pull request.

## 📜 License

```text
MIT License
```

## 💡 Why I Built This

Cause all the tools i found online were paid and expensive. 

## ⭐ If You Find This Useful

Give the repository a star ⭐ and feel free to experiment with it, improve it, or build on top of it.
