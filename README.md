# Vanity.py: Solana Vanity Address Generator

Vanity.py is a Python script to generate Solana vanity wallet addresses. It allows you to search for wallet addresses that start or end with a specific text pattern. The script is optimized for speed, utilizing multi-core processing to generate addresses as quickly as possible.

---

## Features

- **Multi-Core Support**: Utilizes all available CPU cores for faster generation.
- **Customizable Search**: Search for addresses that start or end with a specific text.
- **Case-Insensitive Matching**: Option to ignore case during text matching.
- **Real-Time Progress**: Displays real-time progress, including speed and total attempts.
- **Save Results**: Automatically saves results to a JSON file.

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/therealjosephdev/vanity.py.git
cd vanity.py
```

### 2. Install Dependencies
Ensure you have Python 3.7+ installed. Then, install the required dependencies:
```bash
pip install -r requirements.txt
```

---

## Usage
Run the script with the desired options:

```bash
python vanity.py --vanity-text <text> [--max-matches <number>] [--match-end] [--ignore-case]
```

### Options
- `--vanity-text`, `-v`: The text to search for in the wallet address (required).
- `--max-matches`, `-m`: The number of matches to find before exiting (default: 1).
- `--match-end`, `-e`: Match the vanity text at the end of the address instead of the beginning.
- `--ignore-case`, `-i`: Ignore case in text matching.

---

## Examples

### Generate an Address Ending with "pump":
```bash
python vanity.py --vanity-text pump --match-end
```

### Generate 5 Addresses Starting with "sol" (Case-Insensitive):
```bash
python vanity.py --vanity-text sol --max-matches 5 --ignore-case
```

### Generate an Address Starting with "Moon":
```bash
python vanity.py --vanity-text Moon
```

---

## Output
The script saves the results in a JSON file named `{vanity_text}-vanity-address.json`.

Example: If `--vanity-text pump` is used, the file will be named `pump-vanity-address.json`.

Each result includes the `public_key` and `secret_key` of the generated address.

### Example Output (`pump-vanity-address.json`):
```json
[
    {
        "public_key": "9Jb6rUz2er7ZVWiAoZgWm3nVft7oVM9yQUTMJXUbpump",
        "secret_key": "your_private_key_here"
    }
]
```

---

## Performance
- The script is optimized for speed and can generate **100,000+ addresses per second** on modern multi-core CPUs.
- Real-time progress is displayed, including the number of wallets searched and the speed (wallets/second).

---

## Contributing
Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

---

## Support
If you have any questions or need help, feel free to open an issue or contact the maintainers.

Enjoy generating your Solana vanity addresses! 🚀
