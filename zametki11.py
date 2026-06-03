import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime

DATA_FILE = "notes.json"

COLORS = {
    "bg": "#ffffff",
    "fg": "#000000",
    "btn": "#e0e0e0",
    "select": "#0078d7"
}


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Заметки")
        self.root.geometry("800x500")
        self.root.configure(bg=COLORS["bg"])

        self.notes = []
        self.current_note_index = None

        self._init_ui()
        self.load_notes()

    def _init_ui(self):
        left = tk.Frame(self.root, bg=COLORS["bg"], width=250)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)

        tk.Label(left, text="Заметки", bg=COLORS["bg"], fg=COLORS["fg"],
                 font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(left, text="Новая заметка", command=self.new_note,
                  bg=COLORS["btn"], fg=COLORS["fg"], relief="raised",
                  font=("Arial", 10)).pack(fill=tk.X, padx=10, pady=3)

        self.notes_listbox = tk.Listbox(left, bg="white", fg=COLORS["fg"],
                                        selectbackground=COLORS["select"],
                                        relief="sunken", font=("Arial", 10))
        self.notes_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.notes_listbox.bind("<<ListboxSelect>>", self.on_note_select)

        right = tk.Frame(self.root, bg=COLORS["bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.title_entry = tk.Entry(right, bg="white", fg=COLORS["fg"],
                                    relief="sunken", font=("Arial", 14))
        self.title_entry.pack(fill=tk.X, padx=15, pady=(15, 5), ipady=5)

        self.text_area = tk.Text(right, wrap=tk.WORD, bg="white", fg=COLORS["fg"],
                                 relief="sunken", font=("Arial", 11))
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        btn_row = tk.Frame(right, bg=COLORS["bg"])
        btn_row.pack(fill=tk.X, padx=15, pady=8)

        tk.Button(btn_row, text="Сохранить", command=self.save_note,
                  bg=COLORS["btn"], fg=COLORS["fg"], font=("Arial", 10)).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_row, text="Удалить", command=self.delete_note,
                  bg=COLORS["btn"], fg=COLORS["fg"], font=("Arial", 10)).pack(side=tk.LEFT, padx=3)

    def new_note(self):
        self.current_note_index = None
        self.title_entry.delete(0, tk.END)
        self.text_area.delete("1.0", tk.END)

    def save_note(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Ошибка", "Введите заголовок")
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
            if messagebox.askyesno("Удалить", "Удалить заметку?"):
                del self.notes[self.current_note_index]
                self.new_note()
                self.save_to_file()
                self.refresh_list()

    def on_note_select(self, _):
        selection = self.notes_listbox.curselection()
        if not selection:
            return
        self.current_note_index = selection[0]
        n = self.notes[self.current_note_index]
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, n["title"])
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", n["content"])

    def refresh_list(self):
        self.notes_listbox.delete(0, tk.END)
        for n in self.notes:
            self.notes_listbox.insert(tk.END, n["title"])

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