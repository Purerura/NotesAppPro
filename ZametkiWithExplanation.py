import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import json
from datetime import datetime

#имя файла, в котором хранятся все заметки
DATA_FILE = "notes_data.json"
#цвета интерфейса - все в одном месте
COLORS = {
    "bg_main": "#1e1e2f", "bg_side": "#25253a", "bg_card": "#2f3146",
    "bg_entry": "#353754", "fg_white": "#ffffff", "fg_gray": "#9ca3af",
    "fg_dark": "#1e1e2f", "btn_blue": "#4f7cff", "btn_light": "#f0f0f0"
}


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes App Pro")
        self.root.geometry("1150x680")
        self.root.minsize(980, 560)
        self.root.configure(bg=COLORS["bg_main"])

        #состояние данных, здесь хранится всё что нужно программе во время работы
        self.notes = []
        #номера заметок, которые сейчас видны в списке, при поиске их меньше чем всего заметок
        self.visible_indices = []
        #номер открытой заметки, None, если заметка новая и ещё не сохранялась
        self.current_note_index = None
        self.categories = ["Без категории"]

        #переменные интерфейса - специальные переменные tkinter, которые автоматически обновляют связанные поля на экране при изменении значения
        self.title_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Без категории")
        self.sort_var = tk.StringVar(value="По дате")

        #строим окно, настраиваем горячие клавиши и загружаем сохранённые заметки
        self._init_ui()
        self._bind_events()
        self.load_notes()

    def _init_ui(self):
        #боковая панель - список заметок, поиск и сортировка
        sidebar = tk.Frame(self.root, bg=COLORS["bg_side"], width=320)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Заметки", bg=COLORS["bg_side"], fg=COLORS["fg_white"],
                 font=("Arial", 20, "bold")).pack(pady=15)

        self.make_button(sidebar, "+ Новая заметка", self.new_note, COLORS["btn_light"], COLORS["fg_dark"]).pack(
            fill=tk.X, padx=15, pady=5)

        self.search_entry = tk.Entry(sidebar, textvariable=self.search_var, bg=COLORS["bg_entry"],
                                     fg=COLORS["fg_gray"], insertbackground="white", relief="flat", font=("Arial", 11))
        self.search_entry.pack(fill=tk.X, padx=15, pady=10, ipady=6)
        #подсказка в поле поиска, исчезает когда пользователь нажимает на поле
        self.search_entry.insert(0, "Search")

        tk.Label(sidebar, text="Сортировка", bg=COLORS["bg_side"], fg=COLORS["fg_white"],
                 font=("Arial", 10, "bold")).pack(anchor="w", padx=15)
        self.sort_menu = tk.OptionMenu(sidebar, self.sort_var, "По дате", "По названию", "По категории",
                                       command=lambda _: self.sort_notes())
        self._style_widget(self.sort_menu)
        self.sort_menu.pack(fill=tk.X, padx=15, pady=8)

        self.notes_listbox = tk.Listbox(sidebar, bg=COLORS["bg_card"], fg=COLORS["fg_white"],
                                        selectbackground=COLORS["btn_blue"], relief="flat", bd=0, font=("Arial", 10))
        self.notes_listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        #редактор - поле заголовка, выбор категории и текстовое поле
        main = tk.Frame(self.root, bg=COLORS["bg_main"])
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.title_entry = tk.Entry(main, textvariable=self.title_var, bg=COLORS["bg_entry"],
                                    fg=COLORS["fg_white"], insertbackground="white", relief="flat", font=("Arial", 18))
        self.title_entry.pack(fill=tk.X, padx=20, pady=(15, 8), ipady=8)

        cat_frame = tk.Frame(main, bg=COLORS["bg_main"])
        cat_frame.pack(fill=tk.X, padx=20, pady=5)

        self.cat_option_menu = tk.OptionMenu(cat_frame, self.category_var, *self.categories)
        self._style_widget(self.cat_option_menu)
        self.cat_option_menu.config(width=15)
        self.cat_option_menu.pack(side=tk.LEFT, padx=(0, 10))

        for text, cmd in [("Новая", self.add_category), ("Изменить", self.rename_category),
                          ("Удалить", self.delete_category)]:
            self.make_button(cat_frame, text, cmd, COLORS["btn_light"], COLORS["fg_dark"], width=10).pack(side=tk.LEFT,
                                                                                                          padx=5)

        self.text_area = tk.Text(main, wrap=tk.WORD, bg=COLORS["bg_card"], fg=COLORS["fg_white"],
                                 insertbackground="white", relief="flat", font=("Arial", 13), undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        btn_row = tk.Frame(main, bg=COLORS["bg_main"])
        btn_row.pack(fill=tk.X, padx=20, pady=10)
        for text, cmd in [("Сохранить", self.save_note), ("Удалить", self.delete_note), ("Импорт", self.import_note),
                          ("Экспорт", self.export_note)]:
            self.make_button(btn_row, text, cmd, COLORS["btn_light"], COLORS["fg_dark"]).pack(side=tk.LEFT, padx=5)

    #метод для создания кнопок, чтобы не повторять одинаковые настройки каждый раз
    def make_button(self, parent, text, command, color, fg, width=None):
        btn = tk.Button(parent, text=text, command=command, bg=color, fg=fg, relief="flat",
                        cursor="hand2", font=("Arial", 10, "bold"), padx=12, pady=8, activebackground=color)
        if width: btn.config(width=width)
        return btn

    #применяет тёмное оформление к выпадающим меню
    def _style_widget(self, widget):
        widget.config(bg=COLORS["bg_entry"], fg="white", relief="flat", bd=0, font=("Arial", 10))
        widget["menu"].config(bg=COLORS["bg_entry"], fg="white", activebackground=COLORS["btn_blue"])

    #привязывает события к обработчикам - что делать программе при разных действиях пользователя
    def _bind_events(self):
        #ctrl+клавиша на уровне всего окна
        self.root.bind("<Control-KeyPress>", self._handle_hotkeys)
        #убираем подсказку Search когда пользователь нажимает на поле поиска
        self.search_entry.bind("<FocusIn>", lambda _: self._toggle_search_placeholder(True))
        self.search_entry.bind("<FocusOut>", lambda _: self._toggle_search_placeholder(False))
        #запускаем поиск автоматически при каждом изменении текста - не нужно нажимать кнопку
        self.search_var.trace_add("write", lambda *_: self.on_search())
        self.notes_listbox.bind("<<ListboxSelect>>", self.on_note_select)

    #обрабатывает нажатия ctrl+C/V/X/A
    def _handle_hotkeys(self, event):
        #проверяем клавишу двумя способами: по символу и по числовому коду, чтобы работало и при русской раскладке
        key, code = event.keysym.lower(), event.keycode
        if code == 67 or key in ['c', 'с']: self._clip_op("copy"); return "break"
        if code == 86 or key in ['v', 'м']: self._clip_op("paste"); return "break"
        if code == 88 or key in ['x', 'ч']: self._clip_op("cut"); return "break"
        if code == 65 or key in ['a', 'ф']: self._clip_op("select_all"); return "break"

    #выполняет операции с буфером обмена: копирование, вставка, вырезание, выделить всё
    def _clip_op(self, op):
        w = self.root.focus_get()
        #работает только если курсор стоит в текстовом поле или поле ввода
        if not isinstance(w, (tk.Text, tk.Entry)): return
        try:
            if op == "copy":
                val = w.get("sel.first", "sel.last") if isinstance(w, tk.Text) else w.selection_get()
                self.root.clipboard_clear();
                self.root.clipboard_append(val)
            elif op == "paste":
                val = self.root.clipboard_get()
                if isinstance(w, tk.Text):
                    #если есть выделенный текст - удаляем его перед вставкой
                    try:
                        w.delete("sel.first", "sel.last")
                    except:
                        pass
                    w.insert(tk.INSERT, val)
                else:
                    w.insert(tk.INSERT, val)
            elif op == "cut":
                self._clip_op("copy")
                w.delete("sel.first", "sel.last")
            elif op == "select_all":
                if isinstance(w, tk.Text):
                    w.tag_add("sel", "1.0", "end")
                else:
                    w.select_range(0, tk.END); w.icursor(tk.END)
        except:
            pass

    #создание новой категории - открывает окно с полем ввода
    def add_category(self):
        name = simpledialog.askstring("Категория", "Имя новой категории:")
        if name and name.strip() and name not in self.categories:
            self.categories.append(name.strip());
            self._update_cat_menu()

    #переименование категории - меняет название и в списке, и во всех заметках
    def rename_category(self):
        old = self.category_var.get()
        if old == "Без категории": return
        new = simpledialog.askstring("Изменить", f"Новое имя для '{old}':")
        if new and new.strip() and new not in self.categories:
            self.categories[self.categories.index(old)] = new.strip()
            #обновляет категорию во всех заметках, чтобы они не потерялись после переименования
            for n in self.notes:
                if n['category'] == old: n['category'] = new.strip()
            self.category_var.set(new.strip());
            self._update_cat_menu();
            self._finalize_change()

    #удаление категории - все заметки из неё переходят в категорию по умолчанию
    def delete_category(self):
        cat = self.category_var.get()
        if cat == "Без категории": return
        if messagebox.askyesno("Удалить", f"Удалить категорию '{cat}'?"):
            self.categories.remove(cat)
            #переносит все заметки удалённой категории в Без категории
            for n in self.notes:
                if n['category'] == cat: n['category'] = "Без категории"
            self.category_var.set("Без категории");
            self._update_cat_menu();
            self._finalize_change()

    #перестраивает выпадающее меню категорий заново, вызывается после каждого изменения списка
    def _update_cat_menu(self):
        menu = self.cat_option_menu["menu"];
        menu.delete(0, "end")
        for c in self.categories: menu.add_command(label=c, command=lambda v=c: self.category_var.set(v))

    #управляет подсказкой Search: убирает при нажатии на поле, возвращает если поле оставили пустым
    def _toggle_search_placeholder(self, is_focus):
        if is_focus and self.search_entry.get() == "Search":
            self.search_entry.delete(0, tk.END);
            self.search_entry.config(fg=COLORS["fg_white"])
        elif not is_focus and not self.search_entry.get():
            self.search_entry.insert(0, "Search");
            self.search_entry.config(fg=COLORS["fg_gray"])

    #фильтрует список заметок по тексту в поле поиска, ищет одновременно в заголовке и в содержимом
    def on_search(self):
        q = self.search_var.get().lower()
        #слово Search - подсказка, не поисковый запрос
        if q == "search": q = ""
        self.visible_indices = [i for i, n in enumerate(self.notes) if
                                q in n['title'].lower() or q in n['content'].lower()] if q else list(
            range(len(self.notes)))
        self.refresh_listbox()

    #переходит в режим создания новой заметки, очищает все поля
    def new_note(self):
        self.current_note_index = None
        self.title_var.set("");
        self.category_var.set("Без категории");
        self.text_area.delete("1.0", tk.END)

    #сохраняет заметку: если новая - добавляет в список, если существующая - заменяет
    def save_note(self):
        title = self.title_var.get().strip()
        if not title: return messagebox.showwarning("!", "Нужен заголовок")
        data = {"title": title, "content": self.text_area.get("1.0", tk.END).strip(),
                "category": self.category_var.get(), "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
        #None означает новую заметку - добавляет, если иначе - заменяет существующую
        if self.current_note_index is None:
            self.notes.append(data)
        else:
            self.notes[self.current_note_index] = data
        self._finalize_change()

    #удаляет текущую заметку после подтверждения
    def delete_note(self):
        if self.current_note_index is not None and messagebox.askyesno("?", "Удалить заметку?"):
            del self.notes[self.current_note_index];
            self.new_note();
            self._finalize_change()

    #срабатывает когда пользователь нажимает на заметку в списке
    def on_note_select(self, _):
        selection = self.notes_listbox.curselection()
        if not selection: return
        self.current_note_index = self.visible_indices[selection[0]]
        n = self.notes[self.current_note_index]
        self.title_var.set(n['title']);
        self.category_var.set(n['category'])
        self.text_area.delete("1.0", tk.END);
        self.text_area.insert("1.0", n['content'])

    #сортирует список заметок по выбранному варианту: по дате, названию или категории
    def sort_notes(self):
        mode = self.sort_var.get()
        if mode == "По названию":
            self.notes.sort(key=lambda x: x['title'].lower())
        elif mode == "По категории":
            self.notes.sort(key=lambda x: x['category'].lower())
        else:
            self.notes.sort(key=lambda x: x['date'], reverse=True)
        self.refresh_list()

    #сбрасывает фильтр поиска и показывает все заметки
    def refresh_list(self):
        self.visible_indices = list(range(len(self.notes)));
        self.refresh_listbox()

    #перерисовывает список на экране, показывает только заметки из visible_indices
    def refresh_listbox(self):
        self.notes_listbox.delete(0, tk.END)
        for i in self.visible_indices:
            n = self.notes[i]
            self.notes_listbox.insert(tk.END, f"{n['title']} [{n['category']}] ({n.get('date', '---')})")

    #сохраняет в файл и обновляет список, вызывается после любого изменения
    def _finalize_change(self):
        self.save_to_file();
        self.refresh_list()

    #записывает все заметки в JSON-файл, перезаписывает его целиком
    def save_to_file(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(self.notes, f, indent=4, ensure_ascii=False)

    #загружает заметки из файла при запуске программы
    def load_notes(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.notes = json.load(f)
                #восстанавливает список категорий из сохранённых заметок
                for n in self.notes:
                    if n['category'] not in self.categories: self.categories.append(n['category'])
        #если файл не найден при первом запуске или повреждён - значит начинает с пустым списком
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        self._update_cat_menu();
        self.refresh_list()

    #сохраняет заметки в отдельный файл, одну текущую или все сразу
    def export_note(self):
        if not self.notes: return
        win = tk.Toplevel(self.root);
        win.title("Экспорт");
        win.geometry("320x120")
        win.configure(bg=COLORS["bg_main"]);
        win.transient(self.root);
        win.grab_set()
        tk.Label(win, text="Экспорт:", bg=COLORS["bg_main"], fg=COLORS["fg_white"], font=("Arial", 11, "bold")).pack(
            pady=10)
        btns = tk.Frame(win, bg=COLORS["bg_main"]);
        btns.pack()

        #is_all=True - экспортируем все заметки, еслиFalse - только текущую
        def run_export(is_all):
            if not is_all and self.current_note_index is None: return messagebox.showwarning("!", "Выберите заметку")
            win.destroy()
            fname = "all_notes.json" if is_all else f"{self.notes[self.current_note_index]['title']}.json"
            path = filedialog.asksaveasfilename(defaultextension=".json", initialfile=fname,
                                                filetypes=[("JSON", "*.json")])
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self.notes if is_all else self.notes[self.current_note_index], f, indent=4,
                              ensure_ascii=False)
                messagebox.showinfo("Готово", "Успешно сохранено")

        self.make_button(btns, "Текущую", lambda: run_export(False), COLORS["btn_light"], COLORS["fg_dark"]).pack(
            side=tk.LEFT, padx=10)
        self.make_button(btns, "Все заметки", lambda: run_export(True), COLORS["btn_light"], COLORS["fg_dark"]).pack(
            side=tk.LEFT, padx=10)

    #загружает заметки из внешнего файла и добавляет их к существующим
    def import_note(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                #файл может содержать одну заметку или список - добавляем в список
                items = data if isinstance(data, list) else [data]
                for it in items:
                    if isinstance(it, dict) and 'title' in it:
                        if it.get('category') not in self.categories: self.categories.append(it['category'])
                        self.notes.append(it)
            self._update_cat_menu();
            self._finalize_change()
            messagebox.showinfo("Импорт", "Готово")
        except:
            messagebox.showerror("Ошибка", "Файл поврежден")


#запускаем программу только при прямом запуске файла, а не при подключении к другому коду
if __name__ == "__main__":
    app = NotesApp(tk.Tk())
    app.root.mainloop()