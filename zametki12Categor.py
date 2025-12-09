import tkinter as tk
from tkinter import messagebox, simpledialog
import json
from datetime import datetime

DATA_FILE = "notes_data.json"

COLORS = {
    "bg_main": "#1f2335",
    "bg_side": "#24283b",
    "bg_card": "#2a2f45",
    "bg_entry": "#313551",
    "fg_white": "#c0caf5",
    "fg_gray": "#9aa5ce",
    "fg_dark": "#1f2335",
    "btn_blue": "#7aa2f7",
    "btn_light": "#c0caf5"
}


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Заметки")
        self.root.geometry("1000x600")
        self.root.configure(bg=COLORS["bg_main"])

        self.notes = []
        self.visible_indices = []
        self.current_note_index = None
        self.categories = ["Без категории"]

        self.title_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Без категории")

        self._init_ui()
        self._bind_events()
        self.load_notes()

    def _init_ui(self):
        sidebar = tk.Frame(self.root, bg=COLORS["bg_side"], width=290)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Заметки", bg=COLORS["bg_side"], fg=COLORS["fg_white"],
                 font=("Arial", 18, "bold")).pack(pady=13)

        self.make_button(sidebar, "+ Новая заметка", self.new_note,
                         COLORS["btn_light"], COLORS["fg_dark"]).pack(fill=tk.X, padx=13, pady=4)

        self.search_entry = tk.Entry(sidebar, textvariable=self.search_var, bg=COLORS["bg_entry"],
                                     fg=COLORS["fg_gray"], insertbackground="white",
                                     relief="flat", font=("Arial", 10))
        self.search_entry.pack(fill=tk.X, padx=13, pady=8, ipady=5)
        self.search_entry.insert(0, "Поиск...")

        self.notes_listbox = tk.Listbox(sidebar, bg=COLORS["bg_card"], fg=COLORS["fg_white"],
                                        selectbackground=COLORS["btn_blue"], relief="flat",
                                        bd=0, font=("Arial", 10))
        self.notes_listbox.pack(fill=tk.BOTH, expand=True, padx=13, pady=8)

        main = tk.Frame(self.root, bg=COLORS["bg_main"])
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.title_entry = tk.Entry(main, textvariable=self.title_var, bg=COLORS["bg_entry"],
                                    fg=COLORS["fg_white"], insertbackground="white",
                                    relief="flat", font=("Arial", 16))
        self.title_entry.pack(fill=tk.X, padx=18, pady=(15, 6), ipady=7)

        cat_frame = tk.Frame(main, bg=COLORS["bg_main"])
        cat_frame.pack(fill=tk.X, padx=18, pady=4)

        self.cat_option_menu = tk.OptionMenu(cat_frame, self.category_var, *self.categories)
        self._style_widget(self.cat_option_menu)
        self.cat_option_menu.config(width=14)
        self.cat_option_menu.pack(side=tk.LEFT, padx=(0, 8))

        self.make_button(cat_frame, "Новая", self.add_category,
                         COLORS["btn_light"], COLORS["fg_dark"], width=9).pack(side=tk.LEFT, padx=3)

        self.text_area = tk.Text(main, wrap=tk.WORD, bg=COLORS["bg_card"], fg=COLORS["fg_white"],
                                 insertbackground="white", relief="flat", font=("Arial", 12), undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=18, pady=8)

        btn_row = tk.Frame(main, bg=COLORS["bg_main"])
        btn_row.pack(fill=tk.X, padx=18, pady=8)

        for text, cmd in [("Сохранить", self.save_note), ("Удалить", self.delete_note)]:
            self.make_button(btn_row, text, cmd, COLORS["btn_light"], COLORS["fg_dark"]).pack(side=tk.LEFT, padx=4)

    def make_button(self, parent, text, command, color, fg, width=None):
        btn = tk.Button(parent, text=text, command=command, bg=color, fg=fg, relief="flat",
                        cursor="hand2", font=("Arial", 10, "bold"), padx=10, pady=7,
                        activebackground=color)
        if width:
            btn.config(width=width)
        return btn

    def _style_widget(self, widget):
        widget.config(bg=COLORS["bg_entry"], fg=COLORS["fg_white"], relief="flat", bd=0, font=("Arial", 10))
        widget["menu"].config(bg=COLORS["bg_entry"], fg=COLORS["fg_white"],
                              activebackground=COLORS["btn_blue"])

    def _bind_events(self):
        self.search_entry.bind("<FocusIn>", lambda _: self._toggle_search_placeholder(True))
        self.search_entry.bind("<FocusOut>", lambda _: self._toggle_search_placeholder(False))
        self.search_var.trace_add("write", lambda *_: self.on_search())
        self.notes_listbox.bind("<<ListboxSelect>>", self.on_note_select)

    def _toggle_search_placeholder(self, is_focus):
        if is_focus and self.search_entry.get() == "Поиск...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=COLORS["fg_white"])
        elif not is_focus and not self.search_entry.get():
            self.search_entry.insert(0, "Поиск...")
            self.search_entry.config(fg=COLORS["fg_gray"])

    def add_category(self):
        name = simpledialog.askstring("Категория", "Имя новой категории:")
        if name and name.strip() and name not in self.categories:
            self.categories.append(name.strip())
            self._update_cat_menu()

    def _update_cat_menu(self):
        menu = self.cat_option_menu["menu"]
        menu.delete(0, "end")
        for c in self.categories:
            menu.add_command(label=c, command=lambda v=c: self.category_var.set(v))

    def on_search(self):
        q = self.search_var.get().lower()
        if q in ("", "поиск..."):
            q = ""
        self.visible_indices = [i for i, n in enumerate(self.notes)
                                 if q in n['title'].lower() or q in n['content'].lower()] if q else list(
            range(len(self.notes)))
        self.refresh_listbox()

    def new_note(self):
        self.current_note_index = None
        self.title_var.set("")
        self.category_var.set("Без категории")
        self.text_area.delete("1.0", tk.END)

    def save_note(self):
        title = self.title_var.get().strip()
        if not title:
            return messagebox.showwarning("!", "Нужен заголовок")
        data = {"title": title, "content": self.text_area.get("1.0", tk.END).strip(),
                "category": self.category_var.get(), "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
        if self.current_note_index is None:
            self.notes.append(data)
        else:
            self.notes[self.current_note_index] = data
        self._finalize_change()

    def delete_note(self):
        if self.current_note_index is not None and messagebox.askyesno("?", "Удалить заметку?"):
            del self.notes[self.current_note_index]
            self.new_note()
            self._finalize_change()

    def on_note_select(self, _):
        selection = self.notes_listbox.curselection()
        if not selection:
            return
        self.current_note_index = self.visible_indices[selection[0]]
        n = self.notes[self.current_note_index]
        self.title_var.set(n['title'])
        self.category_var.set(n['category'])
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", n['content'])

    def refresh_list(self):
        self.visible_indices = list(range(len(self.notes)))
        self.refresh_listbox()

    def refresh_listbox(self):
        self.notes_listbox.delete(0, tk.END)
        for i in self.visible_indices:
            n = self.notes[i]
            self.notes_listbox.insert(tk.END, f"{n['title']} [{n['category']}] ({n.get('date', '---')})")

    def _finalize_change(self):
        self.save_to_file()
        self.refresh_list()

    def save_to_file(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.notes, f, indent=4, ensure_ascii=False)

    def load_notes(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.notes = json.load(f)
                for n in self.notes:
                    if n.get('category') and n['category'] not in self.categories:
                        self.categories.append(n['category'])
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        self._update_cat_menu()
        self.refresh_list()


if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()