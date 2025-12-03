import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime

DATA_FILE = "notes.json"

COLORS = {
    "bg_main": "#2b2b2b",
    "bg_side": "#3c3f41",
    "bg_entry": "#4a4a4a",
    "fg_white": "#ffffff",
    "fg_gray": "#aaaaaa",
    "btn": "#5c6370",
    "btn_fg": "#ffffff",
    "select": "#214283"
}


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Заметки")
        self.root.geometry("900x550")
        self.root.configure(bg=COLORS["bg_main"])

        self.notes = []
        self.visible_indices = []
        self.current_note_index = None

        self._init_ui()
        self.load_notes()

    def _init_ui(self):
        sidebar = tk.Frame(self.root, bg=COLORS["bg_side"], width=270)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Заметки", bg=COLORS["bg_side"], fg=COLORS["fg_white"],
                 font=("Arial", 16, "bold")).pack(pady=12)

        tk.Button(sidebar, text="+ Новая заметка", command=self.new_note,
                  bg=COLORS["btn"], fg=COLORS["btn_fg"], relief="flat",
                  font=("Arial", 10, "bold"), cursor="hand2").pack(fill=tk.X, padx=12, pady=4)

        search_frame = tk.Frame(sidebar, bg=COLORS["bg_side"])
        search_frame.pack(fill=tk.X, padx=12, pady=5)

        self.search_entry = tk.Entry(search_frame, bg=COLORS["bg_entry"], fg=COLORS["fg_white"],
                                     insertbackground="white", relief="flat", font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

        tk.Button(search_frame, text="=", command=self.on_search,
                  bg=COLORS["btn"], fg=COLORS["btn_fg"], relief="flat",
                  font=("Arial", 10), cursor="hand2").pack(side=tk.LEFT, padx=(4, 0))

        self.notes_listbox = tk.Listbox(sidebar, bg=COLORS["bg_entry"], fg=COLORS["fg_white"],
                                        selectbackground=COLORS["select"],
                                        relief="flat", bd=0, font=("Arial", 10))
        self.notes_listbox.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        self.notes_listbox.bind("<<ListboxSelect>>", self.on_note_select)

        main = tk.Frame(self.root, bg=COLORS["bg_main"])
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.title_entry = tk.Entry(main, bg=COLORS["bg_entry"], fg=COLORS["fg_white"],
                                    insertbackground="white", relief="flat", font=("Arial", 16))
        self.title_entry.pack(fill=tk.X, padx=18, pady=(15, 6), ipady=7)

        self.text_area = tk.Text(main, wrap=tk.WORD, bg=COLORS["bg_entry"], fg=COLORS["fg_white"],
                                 insertbackground="white", relief="flat", font=("Arial", 12))
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=18, pady=6)

        btn_row = tk.Frame(main, bg=COLORS["bg_main"])
        btn_row.pack(fill=tk.X, padx=18, pady=10)

        for text, cmd in [("Сохранить", self.save_note), ("Удалить", self.delete_note)]:
            tk.Button(btn_row, text=text, command=cmd, bg=COLORS["btn"], fg=COLORS["btn_fg"],
                      relief="flat", cursor="hand2", font=("Arial", 10, "bold"),
                      padx=10, pady=6).pack(side=tk.LEFT, padx=4)

    def new_note(self):
        self.current_note_index = None
        self.title_entry.delete(0, tk.END)
        self.text_area.delete("1.0", tk.END)

    def save_note(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("!", "Нужен заголовок")
            return
        data = {
            "title": title,
            "content": self.text_area.get("1.0", tk.END).strip(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        if self.current_note_index is None:
            self.notes.append(data)
        else:
            self.notes[self.current_note_index] = data
        self.save_to_file()
        self.refresh_list()

    def delete_note(self):
        if self.current_note_index is not None:
            if messagebox.askyesno("?", "Удалить заметку?"):
                del self.notes[self.current_note_index]
                self.new_note()
                self.save_to_file()
                self.refresh_list()

    def on_search(self):
        q = self.search_entry.get().strip().lower()
        if not q:
            self.visible_indices = list(range(len(self.notes)))
        else:
            self.visible_indices = [i for i, n in enumerate(self.notes)
                                    if q in n['title'].lower() or q in n['content'].lower()]
        self.refresh_listbox()

    def on_note_select(self, _):
        selection = self.notes_listbox.curselection()
        if not selection:
            return
        self.current_note_index = self.visible_indices[selection[0]]
        n = self.notes[self.current_note_index]
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, n["title"])
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", n["content"])

    def refresh_list(self):
        self.visible_indices = list(range(len(self.notes)))
        self.refresh_listbox()

    def refresh_listbox(self):
        self.notes_listbox.delete(0, tk.END)
        for i in self.visible_indices:
            n = self.notes[i]
            self.notes_listbox.insert(tk.END, f"{n['title']}  ({n.get('date', '---')})")

    def save_to_file(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.notes, f, indent=4, ensure_ascii=False)

    def load_notes(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.notes = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        self.refresh_list()


if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()