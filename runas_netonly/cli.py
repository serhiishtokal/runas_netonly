r"""
Launch processes as a different Windows user with /netonly auth.
Password is stored in Windows Credential Manager — enter it once, then never again.

Usage:
    runas_netonly --domain DOMAIN --user USER --exe "C:\path\app.exe"
    runas_netonly --domain DOMAIN --user USER --init     # store password (GUI prompt)
    runas_netonly --domain DOMAIN --user USER --check    # show stored credential
    runas_netonly --domain DOMAIN --user USER --reset    # update stored password (GUI)
    runas_netonly --domain DOMAIN --user USER --delete   # remove stored credential

Requires: Python 3.7+ on Windows. No external packages.
"""

import argparse
import os
import sys

# pythonw.exe has no console — guard against None stdout/stderr
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

from .winauth import (
    STARTUPINFOW, PROCESS_INFORMATION,
    LOGON_NETCREDENTIALS_ONLY,
    CREATE_NEW_CONSOLE, CREATE_UNICODE_ENVIRONMENT,
    CreateProcessWithLogonW, CloseHandle,
    ensure_credentials, handle_cred_commands,
    ctypes,
)

GUI_TITLE = "runas_netonly — Windows Authentication"


def launch(username: str, domain: str, password: str,
           command_line: str) -> int:
    """Launch a process as domain\\user with /netonly auth. Returns PID."""
    si = STARTUPINFOW()
    si.cb = ctypes.sizeof(STARTUPINFOW)
    pi = PROCESS_INFORMATION()

    creation_flags = CREATE_NEW_CONSOLE | CREATE_UNICODE_ENVIRONMENT
    cmd_buf        = ctypes.create_unicode_buffer(command_line)

    ok = CreateProcessWithLogonW(
        username, domain, password, LOGON_NETCREDENTIALS_ONLY,
        None, cmd_buf, creation_flags, None, None,
        ctypes.byref(si), ctypes.byref(pi),
    )
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())

    print(f"[OK] Launched as {domain}\\{username} (netonly), PID={pi.dwProcessId}")
    CloseHandle(pi.hProcess)
    CloseHandle(pi.hThread)
    return pi.dwProcessId


def main():
    parser = argparse.ArgumentParser(
        description="Launch a process with /netonly auth (password saved in Credential Manager)"
    )
    parser.add_argument("--exe",    help="executable / command line to launch")
    parser.add_argument("--domain", required=True, help="Windows domain")
    parser.add_argument("--user",   required=True, help="Windows username")
    parser.add_argument("--pause",  action="store_true", help="keep the window open after command finishes")
    parser.add_argument("--init",   action="store_true", help="store credential (GUI prompt) and exit")
    parser.add_argument("--check",  action="store_true", help="show stored credential (masked)")
    parser.add_argument("--reveal", action="store_true", help="use with --check to show full password")
    parser.add_argument("--reset",  action="store_true", help="update stored credential (GUI prompt)")
    parser.add_argument("--delete", action="store_true", help="remove stored credential")
    args = parser.parse_args()

    # ── credential management ──
    if args.check:
        handle_cred_commands("check", args.domain, args.user, reveal=args.reveal)
        return
    if args.init or args.reset:
        handle_cred_commands("reset", args.domain, args.user, gui_title=GUI_TITLE)
        return
    if args.delete:
        handle_cred_commands("delete", args.domain, args.user)
        return

    # ── require --exe for launch ──
    if not args.exe:
        parser.error("--exe is required to launch a process")

    # ── resolve credentials (auto-prompt if missing) ──
    domain, user, password = ensure_credentials(args.domain, args.user, gui_title=GUI_TITLE)

    # ── launch ──
    exe = args.exe
    if args.pause:
        exe = f'cmd /c "{exe} & pause"'

    launch(user, domain, password, exe)


if __name__ == "__main__":
    main()
