"""Exercise real Tk entry bindings without accessing the system clipboard."""

import ctypes
import sys
import unittest
from unittest.mock import patch

if sys.platform == "win32":
    import tkinter as tk
    from runas_netonly.winauth import ask_credentials_gui


@unittest.skipUnless(sys.platform == "win32", "Windows credential dialog")
class CredentialDialogTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.addCleanup(self.root.destroy)
        with patch.object(tk, "Tk", return_value=self.root), patch.object(self.root, "mainloop"):
            ask_credentials_gui("TEST", "test-user")
        self.root.attributes("-topmost", False)
        self.root.geometry("380x220+-2000+-2000")
        self.root.update()
        self.entries = [w for w in self.root.winfo_children()[0].winfo_children()
                        if isinstance(w, tk.Entry)]
        # Keep test data and clipboard operations inside this Tcl interpreter.
        self.root.tk.eval('''
            set test_clipboard ""
            proc ::tk::GetSelection {w selection} {return $::test_clipboard}
            rename clipboard real_clipboard
            proc clipboard {command args} {
                if {$command eq "clear"} {set ::test_clipboard ""}
                if {$command eq "append"} {append ::test_clipboard [lindex $args end]}
            }
        ''')
        self.user32 = ctypes.WinDLL("user32")
        self.user32.GetKeyboardLayout.argtypes = [ctypes.c_ulong]
        self.user32.GetKeyboardLayout.restype = ctypes.c_void_p
        self.user32.ActivateKeyboardLayout.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        self.user32.ActivateKeyboardLayout.restype = ctypes.c_void_p
        self.user32.GetKeyboardLayoutList.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)]
        original_layout = self.user32.GetKeyboardLayout(0)
        self.addCleanup(self.user32.ActivateKeyboardLayout, original_layout, 0)

    def key(self, entry, keycode, state=4):
        entry.focus_force()
        self.root.update()
        entry.event_generate("<KeyPress>", keycode=keycode, state=state)
        self.root.update()

    def test_paste_and_select_all_in_every_loaded_layout(self):
        count = self.user32.GetKeyboardLayoutList(0, None)
        layouts = (ctypes.c_void_p * count)()
        self.user32.GetKeyboardLayoutList(count, layouts)
        for layout in layouts:
            self.assertTrue(self.user32.ActivateKeyboardLayout(layout, 0))
            for entry in self.entries:
                for modifiers in (4, 6):  # Ctrl, Ctrl+CapsLock
                    with self.subTest(layout=hex(layout), entry=str(entry), modifiers=modifiers):
                        entry.delete(0, "end")
                        entry.insert(0, "replace this")
                        self.key(entry, 0x41, modifiers)
                        self.assertTrue(entry.selection_present())
                        self.root.tk.setvar("test_clipboard", "  Test-zażółć-Пароль-123!  ")
                        self.key(entry, 0x56, modifiers)
                        self.assertEqual(entry.get(), "  Test-zażółć-Пароль-123!  ")

    def test_shift_insert_pastes(self):
        for entry in self.entries:
            entry.delete(0, "end")
            self.root.tk.setvar("test_clipboard", "test paste")
            self.key(entry, 0x2D, 1)  # Shift+Insert
            self.assertEqual(entry.get(), "test paste")

    def test_copy_and_cut_keep_password_masked(self):
        for entry in self.entries:
            entry.delete(0, "end")
            entry.insert(0, "test-value")
            entry.selection_range(0, "end")
            self.key(entry, 0x43)
            expected = "*" * 10 if entry.cget("show") else "test-value"
            self.assertEqual(self.root.tk.getvar("test_clipboard"), expected)
            self.key(entry, 0x58)
            self.assertEqual(entry.get(), "")
            self.assertEqual(self.root.tk.getvar("test_clipboard"), expected)

    def test_altgr_does_not_trigger_paste(self):
        entry = self.entries[0]
        entry.delete(0, "end")
        self.root.tk.setvar("test_clipboard", "should not be pasted")
        self.key(entry, 0x56, 4 | 0x20000)  # Ctrl+Alt
        self.assertNotIn("should not be pasted", entry.get())

    def test_context_menu_pastes_into_each_entry(self):
        for entry in self.entries:
            menus = [w for w in entry.winfo_children() if isinstance(w, tk.Menu)]
            self.assertEqual(len(menus), 1)
            menu = menus[0]
            with patch.object(menu, "tk_popup") as popup:
                entry.event_generate("<Button-3>", x=5, y=5)
                self.root.update()
                popup.assert_called_once()
            entry.delete(0, "end")
            entry.insert(0, "old value")
            menu.invoke("Select all")
            self.root.tk.setvar("test_clipboard", "menu paste")
            menu.invoke("Paste")
            self.assertEqual(entry.get(), "menu paste")


if __name__ == "__main__":
    unittest.main()
