# Pycamt

[![Release](https://img.shields.io/github/v/release/ODAncona/pycamt)](https://img.shields.io/github/v/release/ODAncona/pycamt)
[![Build status](https://img.shields.io/github/actions/workflow/status/ODAncona/pycamt/main.yml?branch=main)](https://github.com/ODAncona/pycamt/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/ODAncona/pycamt/branch/main/graph/badge.svg)](https://codecov.io/gh/ODAncona/pycamt)
[![Commit activity](https://img.shields.io/github/commit-activity/m/ODAncona/pycamt)](https://img.shields.io/github/commit-activity/m/ODAncona/pycamt)
[![License](https://img.shields.io/github/license/ODAncona/pycamt)](https://img.shields.io/github/license/ODAncona/pycamt)

- **Github repository**: <https://github.com/ODAncona/pycamt/>
- **Documentation** <https://ODAncona.github.io/pycamt/>

## Overview

Pycamt is a flexible and extensible Python class designed to parse CAMT.053 XML files, which are used for bank-to-customer account report messages in the financial industry. The parser supports multiple versions of the CAMT.053 standard, making it a versatile tool for extracting financial transaction data.

[https://docs.findock.com/processing-camt-053-files#:~:text=The%20camt.,structured%20MT%20940%20bank%20file.](Documentation)

## Installation

To use Camt053Parser, simply copy the Camt053Parser.py file into your project directory, or include it as part of your Python package.

```bash
pip install pycamt
```

## Usage

### Creating an Instance

You can create an instance of the Camt053Parser by providing the XML data as a string:

```python
from pycamt.parser import Camt053Parser

xml_data = "<Document>...</Document>"  # Your CAMT.053 XML data as a string
parser = Camt053Parser(xml_data)
```

Alternatively, you can initialize the parser with a file path:

```python
parser = Camt053Parser.from_file('path/to/your/file.xml')
```

### Extracting Group Header Information

To extract group header information such as message ID and creation date/time:

```python
group_header = parser.get_group_header()
print(group_header)
```

### Extracting Transactions

To retrieve all transaction entries from the file:

```python
transactions = parser.get_transactions()
for transaction in transactions:
    print(transaction)
```

### Extracting Statement Information

To get basic statement information like IBAN and opening/closing balance:

```python
statement_info = parser.get_statement_info()
print(statement_info)
```

## Contributing

Contributions to Camt053Parser are welcome! If you have suggestions for improvements or encounter any issues, please feel free to open an issue or submit a pull request.

## Guidelines

For submitting enhancements or new features, please ensure your code is well-documented and includes relevant docstrings.
Ensure your contributions are tested to maintain reliability and stability of the parser.
Adhere to the existing code style for consistency.
License
Specify your chosen license here, providing users with information on how they can use, modify, and share your code.
