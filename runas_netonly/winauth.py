"""
Shared Windows authentication library.

Provides:
- Win32 ctypes structures and API bindings
- Windows Credential Manager helpers (store, read, delete)
- Tkinter GUI credential prompt
- CLI credential management helper

Used by runas_auto.py and sqlrun.py. No external dependencies.
"""

import ctypes
import ctypes.wintypes
import sys

# ── Win32 Constants ───────────────────────────────────────────────────────────
CRED_TYPE_GENERIC          = 1
CRED_PERSIST_LOCAL_MACHINE = 2
LOGON_WITH_PROFILE         = 0x00000001
LOGON_NETCREDENTIALS_ONLY  = 0x00000002
CREATE_NEW_CONSOLE         = 0x00000010
CREATE_UNICODE_ENVIRONMENT = 0x00000400
STARTF_USESTDHANDLES       = 0x00000100
HANDLE_FLAG_INHERIT        = 0x00000001
INFINITE                   = 0xFFFFFFFF
GENERIC_READ               = 0x80000000
OPEN_EXISTING              = 3

# ── Win32 Structures ──────────────────────────────────────────────────────────

class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("nLength",              ctypes.wintypes.DWORD),
        ("lpSecurityDescriptor", ctypes.c_void_p),
        ("bInheritHandle",       ctypes.wintypes.BOOL),
    ]

class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ("Flags",              ctypes.wintypes.DWORD),
        ("Type",               ctypes.wintypes.DWORD),
        ("TargetName",         ctypes.wintypes.LPWSTR),
        ("Comment",            ctypes.wintypes.LPWSTR),
        ("LastWritten",        ctypes.wintypes.FILETIME),
        ("CredentialBlobSize", ctypes.wintypes.DWORD),
        ("CredentialBlob",     ctypes.POINTER(ctypes.c_char)),
        ("Persist",            ctypes.wintypes.DWORD),
        ("AttributeCount",     ctypes.wintypes.DWORD),
        ("Attributes",         ctypes.c_void_p),
        ("TargetAlias",        ctypes.wintypes.LPWSTR),
        ("UserName",           ctypes.wintypes.LPWSTR),
    ]

class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb",              ctypes.wintypes.DWORD),
        ("lpReserved",      ctypes.wintypes.LPWSTR),
        ("lpDesktop",       ctypes.wintypes.LPWSTR),
        ("lpTitle",         ctypes.wintypes.LPWSTR),
        ("dwX",             ctypes.wintypes.DWORD),
        ("dwY",             ctypes.wintypes.DWORD),
        ("dwXSize",         ctypes.wintypes.DWORD),
        ("dwYSize",         ctypes.wintypes.DWORD),
        ("dwXCountChars",   ctypes.wintypes.DWORD),
        ("dwYCountChars",   ctypes.wintypes.DWORD),
        ("dwFillAttribute", ctypes.wintypes.DWORD),
        ("dwFlags",         ctypes.wintypes.DWORD),
        ("wShowWindow",     ctypes.wintypes.WORD),
        ("cbReserved2",     ctypes.wintypes.WORD),
        ("lpReserved2",     ctypes.c_void_p),
        ("hStdInput",       ctypes.wintypes.HANDLE),
        ("hStdOutput",      ctypes.wintypes.HANDLE),
        ("hStdError",       ctypes.wintypes.HANDLE),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess",    ctypes.wintypes.HANDLE),
        ("hThread",     ctypes.wintypes.HANDLE),
        ("dwProcessId", ctypes.wintypes.DWORD),
        ("dwThreadId",  ctypes.wintypes.DWORD),
    ]

# ── Win32 API Bindings ────────────────────────────────────────────────────────
advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

CredWriteW = advapi32.CredWriteW
CredWriteW.argtypes = [ctypes.POINTER(CREDENTIAL), ctypes.wintypes.DWORD]
CredWriteW.restype  = ctypes.wintypes.BOOL

CredReadW = advapi32.CredReadW
CredReadW.argtypes  = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.DWORD,
                       ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
CredReadW.restype   = ctypes.wintypes.BOOL

CredDeleteW = advapi32.CredDeleteW
CredDeleteW.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD]
CredDeleteW.restype  = ctypes.wintypes.BOOL

CredFree = advapi32.CredFree
CredFree.argtypes = [ctypes.c_void_p]
CredFree.restype  = None

CreateProcessWithLogonW = advapi32.CreateProcessWithLogonW
CreateProcessWithLogonW.argtypes = [
    ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPCWSTR,
    ctypes.wintypes.DWORD, ctypes.wintypes.LPCWSTR, ctypes.wintypes.LPWSTR,
    ctypes.wintypes.DWORD, ctypes.c_void_p, ctypes.wintypes.LPCWSTR,
    ctypes.POINTER(STARTUPINFOW), ctypes.POINTER(PROCESS_INFORMATION),
]
CreateProcessWithLogonW.restype = ctypes.wintypes.BOOL

CloseHandle = kernel32.CloseHandle

CreatePipe = kernel32.CreatePipe
CreatePipe.argtypes = [ctypes.POINTER(ctypes.wintypes.HANDLE),
                       ctypes.POINTER(ctypes.wintypes.HANDLE),
                       ctypes.POINTER(SECURITY_ATTRIBUTES), ctypes.wintypes.DWORD]
CreatePipe.restype  = ctypes.wintypes.BOOL

SetHandleInformation = kernel32.SetHandleInformation
SetHandleInformation.argtypes = [ctypes.wintypes.HANDLE,
                                 ctypes.wintypes.DWORD, ctypes.wintypes.DWORD]
SetHandleInformation.restype  = ctypes.wintypes.BOOL

ReadFile = kernel32.ReadFile
ReadFile.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_void_p, ctypes.wintypes.DWORD,
                     ctypes.POINTER(ctypes.wintypes.DWORD), ctypes.c_void_p]
ReadFile.restype  = ctypes.wintypes.BOOL

WaitForSingleObject = kernel32.WaitForSingleObject
WaitForSingleObject.argtypes = [ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD]
WaitForSingleObject.restype  = ctypes.wintypes.DWORD

GetExitCodeProcess = kernel32.GetExitCodeProcess
GetExitCodeProcess.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(ctypes.wintypes.DWORD)]
GetExitCodeProcess.restype  = ctypes.wintypes.BOOL

CreateFileW = kernel32.CreateFileW
CreateFileW.argtypes = [ctypes.wintypes.LPCWSTR, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD,
                        ctypes.POINTER(SECURITY_ATTRIBUTES), ctypes.wintypes.DWORD,
                        ctypes.wintypes.DWORD, ctypes.wintypes.HANDLE]
CreateFileW.restype  = ctypes.wintypes.HANDLE

# ── Credential Manager ────────────────────────────────────────────────────────

def cred_target(domain: str, user: str) -> str:
    """Build the Credential Manager key: 'runas_netonly/{domain}\\{user}'."""
    return f"runas_netonly/{domain}\\{user}"


def cred_store(domain: str, user: str, password: str) -> None:
    """Store credentials in Windows Credential Manager (DPAPI-encrypted)."""
    target         = cred_target(domain, user)
    password_bytes = password.encode("utf-16-le")
    cred = CREDENTIAL()
    cred.Flags             = 0
    cred.Type              = CRED_TYPE_GENERIC
    cred.TargetName        = target
    cred.CredentialBlobSize = len(password_bytes)
    cred.CredentialBlob    = ctypes.cast(
        ctypes.create_string_buffer(password_bytes, len(password_bytes)),
        ctypes.POINTER(ctypes.c_char),
    )
    cred.Persist  = CRED_PERSIST_LOCAL_MACHINE
    cred.UserName = f"{domain}\\{user}"
    if not CredWriteW(ctypes.byref(cred), 0):
        raise ctypes.WinError(ctypes.get_last_error())


def cred_read(domain: str, user: str) -> str | None:
    """Read password from Credential Manager. Returns None if not found."""
    pcred = ctypes.POINTER(CREDENTIAL)()
    if not CredReadW(cred_target(domain, user), CRED_TYPE_GENERIC, 0, ctypes.byref(pcred)):
        return None
    try:
        blob = ctypes.string_at(pcred.contents.CredentialBlob, pcred.contents.CredentialBlobSize)
        return blob.decode("utf-16-le")
    finally:
        CredFree(pcred)


def cred_delete(domain: str, user: str) -> bool:
    """Delete credential. Returns True if deleted, False if not found."""
    return bool(CredDeleteW(cred_target(domain, user), CRED_TYPE_GENERIC, 0))


# ── GUI Credential Prompt ─────────────────────────────────────────────────────

def _bind_entry_editing(entry) -> None:
    """Keep Windows editing shortcuts working with non-Latin keyboard layouts."""
    import tkinter as tk

    shortcuts = {0x41: "<<SelectAll>>", 0x43: "<<Copy>>",
                 0x56: "<<Paste>>", 0x58: "<<Cut>>"}

    def on_control_key(event):
        # AltGr includes Ctrl; leave Ctrl+Alt combinations to Tk.
        if event.state & (0x0008 | 0x20000):
            return None
        # Tk 8.6 may report an unknown keysym for Cyrillic Ctrl+letter.
        # Windows virtual-key codes still identify A/C/V/X correctly.
        action = shortcuts.get(event.keycode)
        if action:
            entry.event_generate(action)
            return "break"  # Do not also execute the default class binding.
        return None

    entry.bind("<Control-KeyPress>", on_control_key)
    menu = tk.Menu(entry, tearoff=False)
    menu.add_command(label="Paste", command=lambda: entry.event_generate("<<Paste>>"))
    menu.add_command(label="Select all", command=lambda: entry.event_generate("<<SelectAll>>"))

    def show_menu(event):
        entry.focus_set()
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
        return "break"

    entry.bind("<Button-3>", show_menu)


def ask_credentials_gui(
    default_domain: str,
    default_user: str,
    title: str = "Windows Authentication",
    heading: str = "Windows domain authentication",
) -> tuple[str, str, str] | None:
    """Pop up a tkinter dialog for domain/user/password.
    Returns (domain, user, password) or None if cancelled."""
    import tkinter as tk

    result = [None]

    root = tk.Tk()
    root.title(title)
    root.resizable(False, False)
    root.attributes("-topmost", True)

    w, h = 380, 220
    x = (root.winfo_screenwidth()  - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    frame = tk.Frame(root, padx=20, pady=15)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text=heading,
             font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 12))

    tk.Label(frame, text="Domain:", anchor="e").grid(row=1, column=0, sticky="e", pady=3)
    domain_var = tk.StringVar(value=default_domain)
    domain_entry = tk.Entry(frame, textvariable=domain_var, width=30)
    domain_entry.grid(row=1, column=1, pady=3)

    tk.Label(frame, text="Username:", anchor="e").grid(row=2, column=0, sticky="e", pady=3)
    user_var = tk.StringVar(value=default_user)
    user_entry = tk.Entry(frame, textvariable=user_var, width=30)
    user_entry.grid(row=2, column=1, pady=3)

    tk.Label(frame, text="Password:", anchor="e").grid(row=3, column=0, sticky="e", pady=3)
    pass_entry = tk.Entry(frame, show="*", width=30)
    pass_entry.grid(row=3, column=1, pady=3)
    pass_entry.focus_set()

    for entry in (domain_entry, user_entry, pass_entry):
        _bind_entry_editing(entry)

    def on_ok(event=None):
        d = domain_var.get().strip()
        u = user_var.get().strip()
        p = pass_entry.get()
        if d and u and p:
            result[0] = (d, u, p)
            root.destroy()

    def on_cancel(event=None):
        root.destroy()

    btn_frame = tk.Frame(frame)
    btn_frame.grid(row=4, column=0, columnspan=2, pady=(12, 0))
    tk.Button(btn_frame, text="OK", width=10, command=on_ok).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Cancel", width=10, command=on_cancel).pack(side="left", padx=5)

    root.bind("<Return>", on_ok)
    root.bind("<Escape>", on_cancel)
    root.mainloop()
    return result[0]


# ── CLI Credential Management Helper ─────────────────────────────────────────

def handle_cred_commands(
    action: str,
    domain: str,
    user: str,
    reveal: bool = False,
    gui_title: str = "Windows Authentication",
) -> None:
    """Handle check / reset / delete credential commands.

    action: "check", "reset", or "delete"
    Prints output and calls sys.exit(1) on error. Returns on success.
    """
    if action == "check":
        pw = cred_read(domain, user)
        if pw is None:
            print(f"[--] No credential stored for {domain}\\{user}")
            sys.exit(1)
        masked = pw if reveal else (pw[:2] + "*" * (len(pw) - 3) + pw[-1] if len(pw) > 3 else "***")
        print(f"  User:     {domain}\\{user}")
        print(f"  Password: {masked}")

    elif action == "reset":
        creds = ask_credentials_gui(domain, user, title=gui_title)
        if creds is None:
            print("[--] Cancelled")
            sys.exit(1)
        domain, user, password = creds
        cred_store(domain, user, password)
        print(f"[OK] Credential stored for {domain}\\{user}")

    elif action == "delete":
        if cred_delete(domain, user):
            print(f"[OK] Credential removed for {domain}\\{user}")
        else:
            print(f"[--] No credential found for {domain}\\{user}")


def ensure_credentials(
    domain: str,
    user: str,
    gui_title: str = "Windows Authentication",
) -> tuple[str, str, str]:
    """Return (domain, user, password). Auto-prompts GUI if not stored.
    Calls sys.exit(1) if user cancels."""
    pw = cred_read(domain, user)
    if pw is not None:
        return domain, user, pw

    creds = ask_credentials_gui(domain, user, title=gui_title)
    if creds is None:
        print("[--] No credentials provided — aborting")
        sys.exit(1)
    domain, user, password = creds
    cred_store(domain, user, password)
    print(f"[OK] Credential stored for {domain}\\{user}")
    return domain, user, password
