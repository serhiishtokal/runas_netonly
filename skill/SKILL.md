# runas-netonly — Windows Credential & Process Launcher

You are an AI agent assisting with `runas-netonly`, a Windows CLI tool that launches processes with domain credentials using `/netonly` authentication. Passwords are stored securely in Windows Credential Manager (DPAPI-encrypted).

## Setup

Before using the tool, ensure it is installed.

### Check if installed

```bash
runas-netonly --help
```

### Install if missing

**Via pip (requires Python 3.10+):**

```bash
pip install runas-netonly
```

**Via standalone .exe (no Python required):**

Download `runas-netonly.exe` from https://github.com/serhiishtokal/runas_netonly/releases/latest and place it in a directory on your PATH.

## Commands

### Store credentials (first-time setup)

Opens a GUI prompt to enter domain, username, and password. Credentials are stored encrypted in Windows Credential Manager.

```bash
runas-netonly --domain DOMAIN --user USERNAME --init
```

### Launch a process

Launches the specified executable using stored credentials with `/netonly` authentication.

```bash
runas-netonly --domain DOMAIN --user USERNAME --exe "COMMAND"
```

Examples:

```bash
runas-netonly --domain CORP --user jsmith --exe "C:\Windows\System32\mmc.exe"
runas-netonly --domain CORP --user jsmith --exe "sqlcmd -S server -d mydb -Q \"SELECT 1\""
runas-netonly --domain CORP --user jsmith --exe "ipconfig /all" --pause
```

The `--pause` flag keeps the console window open after the command finishes.

### Check stored credential

```bash
runas-netonly --domain DOMAIN --user USERNAME --check
runas-netonly --domain DOMAIN --user USERNAME --check --reveal
```

Without `--reveal`, the password is masked (first 2 and last 1 character shown).

### Update stored password

```bash
runas-netonly --domain DOMAIN --user USERNAME --reset
```

### Delete stored credential

```bash
runas-netonly --domain DOMAIN --user USERNAME --delete
```

## Behavior notes

- If no credential is stored and `--exe` is used, a GUI prompt appears automatically to collect and store the credentials before launching.
- Credentials are stored per domain\user pair in Windows Credential Manager under the key `runas_netonly/{domain}\{user}`.
- The tool uses `CreateProcessWithLogonW` with `LOGON_NETCREDENTIALS_ONLY` — the launched process runs under the current user's local profile but authenticates to network resources with the specified domain credentials.
- Only works on Windows.

## Typical workflow

1. Store credentials once: `runas-netonly --domain CORP --user jsmith --init`
2. Launch processes as needed: `runas-netonly --domain CORP --user jsmith --exe "mmc.exe"`
3. Update password when it changes: `runas-netonly --domain CORP --user jsmith --reset`
