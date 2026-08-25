# FoodBankInventory
# Food Bank Management System

A simple desktop application for managing food bank clients, inventory, donations, distributions, and activity.

## Features

* 👥 Client management
* 📦 Inventory management
* 🏷️ Item and category management
* 🤝 Donor management
* 📥 Donation tracking
* 📤 Food distribution tracking
* 👤 User accounts
* 📋 Activity logging
* 💾 Local SQLite database
* 🖥️ Windows desktop application

## Installation

Download the latest release and run the installer.

The application stores its database and user data separately from the installed program so updates and reinstalls don't overwrite your data.

## Development

This project is written in Python and uses a virtual environment for development.

Install the required dependencies with:

```bash
pip install -r requirements.txt
```

Run the application with:

```bash
python main.py
```

## Building

The application can be packaged into a Windows executable using PyInstaller.

```bash
pyinstaller --clean --noconfirm yourspecfile.spec
```

## Database

The application uses SQLite.

The database is automatically created on first launch and stored in the user's local application data directory.

## Usage

If something isn't obvious:

**RTFM.**

## License

This project is currently provided as-is.

and yes chatgpt did write that for me because its 3 in the morning and i'm a lazy bum.
