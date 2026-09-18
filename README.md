# runas_netonly

Windows utility to launch processes with domain credentials using `/netonly` authentication.
Passwords are securely stored in Windows Credential Manager (DPAPI-encrypted) -- enter your password once, then never again.

## Features

- Launch any process with alternate domain credentials (netonly mode)
- Credentials stored securely in Windows Credential Manager
- GUI prompt for password entry (tkinter)
- Pure Python, no external dependencies

## Requirements

- Windows 10/11
- Python 3.10+ (for pip install method)
- No external packages required

## Installation

### Option 1: Standalone .exe (no Python required)

Download `runas-netonly.exe` from the [Releases](https://github.com/sshtokal/runas_netonly/releases) page.

### Option 2: pip install from GitHub

```
pip install git+https://github.com/sshtokal/runas_netonly.git
```

### Option 3: pip install from wheel

```
pip install runas_netonly-1.0.0-py3-none-any.whl
```

### Option 4: Development install

```
git clone https://github.com/sshtokal/runas_netonly.git
cd runas_netonly
pip install -e .
```

## Usage

After installation, the `runas-netonly` command is available.

### Launch a process

```
runas-netonly --domain CORP --user jsmith --exe "C:\Windows\System32\mmc.exe"
```

### Store credentials (GUI prompt)

```
runas-netonly --domain CORP --user jsmith --init
```

### Check stored credential

```
runas-netonly --domain CORP --user jsmith --check
runas-netonly --domain CORP --user jsmith --check --reveal
```

### Update stored password

```
runas-netonly --domain CORP --user jsmith --reset
```

All credential fields support Ctrl+V (paste), Ctrl+A (select all), Ctrl+C,
and Ctrl+X, including with Ukrainian and other non-Latin Windows keyboard
layouts. You can also use Shift+Insert or right-click a field and choose
**Paste**. Passwords remain masked.

### Delete stored credential

```
runas-netonly --domain CORP --user jsmith --delete
```

### Keep window open after launch

```
runas-netonly --domain CORP --user jsmith --exe "ipconfig /all" --pause
```

### Run as a Python module

```
python -m runas_netonly --domain CORP --user jsmith --exe "notepad.exe"
```

## AI Agent Skill

The `skill/` folder contains a portable agent skill file (`SKILL.md`) that teaches AI coding agents how to install and use this tool. Copy it into your project's skill/instructions directory to give your agent access to `runas-netonly`.

## Building the standalone .exe

```
pip install pyinstaller
python build_exe.py
```

Output: `dist/runas-netonly.exe`

For a portable desktop shortcut without a console window:

```
python -m PyInstaller --onefile --windowed --name runas_netonly --hidden-import tkinter --collect-submodules runas_netonly runas_netonly/__main__.py
```

Output: `dist/runas_netonly.exe`

## Tests

Run on Windows with Python and Tkinter installed:

```
python -m unittest discover -s tests -v
```

The dialog tests exercise the installed keyboard layouts, including non-Latin
layouts when available. They use test data without accessing the system clipboard
or storing credentials.

## License

MIT
