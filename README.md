
A lightweight, configurable Python tool for generating unique layered NFT artwork from trait folders.

Built with **Python + Pillow**. Configure trait weights, layer order, subtraits, and compatibility rules from `trait_config.json`.

> **Status:** Early-stage / actively improving

## ✨ Features

- 🖼️ Layered image generation
- 🎲 Weighted trait selection
- 🧩 Subtrait support
- 🚫 Trait compatibility / exclusion rules
- ♻️ Duplicate prevention
- 📊 Rarity reporting
- 📝 OpenSea-style CSV metadata
- ⚙️ Automatic configuration and output directories

## 📦 Requirements

- Python 3.x
- Pillow
- Colorama

```bash
pip install pillow colorama
```

## 📂 Project Structure

Each top-level folder is a **trait category**. Images inside it are the available traits.

```text
my-collection/
├── Background/
│   ├── Blue.png
│   └── Red.png
├── Body/
│   ├── Human.png
│   └── Robot.png
├── Head/
│   ├── Cap.png
│   └── Crown.png
└── Clothes/
    ├── Hoodie/
    │   ├── Hood_Up.png
    │   └── Hood_Down.png
    └── Shirt.png
```

Subfolders are **subtraits**. They let related traits share a parent category while still being selected individually.

## 🚀 Usage

```bash
git clone https://github.com/0xStacker/Nft-Generator
cd Nft-generator
pip install pillow colorama
python generator.py
```

The generator will:
1. Let you select a project.
2. Ask for collection size and canvas dimensions.
3. Create `trait_config.json` if one doesn't exist.
4. Let you configure layer order.
5. Generate the collection.

## ⚙️ Configuration

`trait_config.json` controls project information, trait weights, and rules.

### Trait weights

Higher weights make a trait more likely to be selected:

```json
"Eyes": {
    "Normal.png": 70,
    "Laser.png": 20,
    "Angry.png": 10
}
```

### Trait rules

Rules are defined at the **trait-category level**.

```json
"rules": {
    "Hoodie": ["Helmet", "Suit"],
    "Helmet": ["Hoodie"]
}
```

This means `Hoodie` cannot be generated with `Helmet` or `Suit`.

A subtrait still belongs to its parent category. For example:

```text
Clothes/
└── Hoodie/
    ├── Hood_Up.png
    └── Hood_Down.png
```

Both `Hood_Up` and `Hood_Down` are treated as the `Clothes/Hoodie` category for rule checking. This lets you write rules once for the category instead of creating exclusions for every individual subtrait.

## 🧠 How Generation Works

For each NFT, the generator:

1. Selects one trait from every category using the configured weights.
2. Checks the selected combination against the configured rules.
3. Rejects conflicting combinations and tries again.
4. Composites the valid layers in the configured order.
5. Checks the trait combination for duplicates.
6. Saves the image and metadata.
7. Updates the rarity report.

In short:

```text
Select → Validate Rules → Composite → Check Duplicate → Save
             │
             └── Conflict → Select again
```

## 🔢 Combination Limit

Before generation, the generator calculates the theoretical number of combinations. If the requested supply exceeds that number, generation stops.

For example:

```text
5 Backgrounds × 4 Bodies × 6 Eyes × 3 Heads = 360 combinations
```

## 📁 Output

```text
my-collection/
├── trait_config.json
├── rarity_report.txt
└── out/
    ├── images/
    │   ├── 1.png
    │   └── ...
    └── metadata/
        └── metadata.csv
```

`metadata.csv` contains token ID, name, description, filename, and selected traits.

`rarity_report.txt` records how often each trait was selected.

## ⚠️ Current Limitations

- Terminal-based interface
- Limited input validation
- CSV metadata only
- Output handling is basic
- Generation currently relies on random retry for invalid combinations

## 🗺️ Roadmap

- [ ] Better CLI and input validation
- [ ] JSON metadata
- [ ] Seeded generation
- [ ] Automated rarity analysis
- [ ] Unit tests
- [ ] Installable package
- [ ] Better output management

## 🤝 Contributing

Ideas, bug reports, and pull requests are welcome.

## 📜 License

MIT License

## 💡 Why I Built This

Most NFT generators I found were paid or unnecessarily expensive. This one is built to be simple, configurable, and free to experiment with.

⭐ If you find it useful, consider starring the repository.
