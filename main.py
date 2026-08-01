import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import threading
from finder import find_local_maxima
from file_utils import load_array, save_results


class App:
    def __init__(self, root):
        self.root = root
        root.title("Поиск локальных максимумов в n-мерных массивах")
        root.geometry("900x700")

        # Переменные
        self.files = []  # список выбранных файлов
        self.axis_var = tk.IntVar(value=0)
        self.diag_var = tk.BooleanVar(value=True)
        self.results = {}  # словарь {file_path: список (coord, val)}

        self.create_widgets()

    def create_widgets(self):
        # Верхняя панель выбора файлов
        frame_files = tk.LabelFrame(self.root, text="Файлы для обработки", padx=5, pady=5)
        frame_files.pack(fill='x', padx=10, pady=5)

        btn_add = tk.Button(frame_files, text="Добавить файлы", command=self.add_files)
        btn_add.pack(side='left', padx=5)

        btn_clear = tk.Button(frame_files, text="Очистить список", command=self.clear_files)
        btn_clear.pack(side='left', padx=5)

        self.file_listbox = tk.Listbox(frame_files, height=5)
        self.file_listbox.pack(fill='x', padx=5, pady=5)

        # Панель настроек
        frame_settings = tk.LabelFrame(self.root, text="Настройки", padx=5, pady=5)
        frame_settings.pack(fill='x', padx=10, pady=5)

        tk.Label(frame_settings, text="Ось (индекс):").pack(side='left', padx=5)
        self.axis_spin = tk.Spinbox(frame_settings, from_=0, to=10, width=5, textvariable=self.axis_var)
        self.axis_spin.pack(side='left', padx=5)

        self.diag_check = tk.Checkbutton(frame_settings, text="Учитывать диагональных соседей", variable=self.diag_var)
        self.diag_check.pack(side='left', padx=20)

        btn_run = tk.Button(frame_settings, text="Запустить обработку", command=self.run_processing, bg="lightgreen")
        btn_run.pack(side='right', padx=5)

        # Таблица результатов
        frame_table = tk.LabelFrame(self.root, text="Результаты для выбранного файла", padx=5, pady=5)
        frame_table.pack(fill='both', expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(frame_table, columns=("coords", "value"), show="headings")
        self.tree.heading("coords", text="Координаты")
        self.tree.heading("value", text="Значение")
        self.tree.pack(fill='both', expand=True)

        # Лог
        frame_log = tk.LabelFrame(self.root, text="Лог", padx=5, pady=5)
        frame_log.pack(fill='both', expand=False, padx=10, pady=5)
        self.log_text = scrolledtext.ScrolledText(frame_log, height=6, state='disabled')
        self.log_text.pack(fill='both', expand=True)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Выберите файлы с массивами",
            filetypes=[("Все поддерживаемые", "*.npy *.npz *.csv *.txt"),
                       ("NumPy", "*.npy *.npz"), ("CSV/TXT", "*.csv *.txt")]
        )
        if files:
            for f in files:
                if f not in self.files:
                    self.files.append(f)
                    self.file_listbox.insert(tk.END, f)
            self.log(f"Добавлено файлов: {len(files)}")

    def clear_files(self):
        self.files.clear()
        self.file_listbox.delete(0, tk.END)
        self.results.clear()
        self.clear_tree()

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def run_processing(self):
        if not self.files:
            messagebox.showwarning("Нет файлов", "Добавьте хотя бы один файл.")
            return
        # Запускаем в отдельном потоке, чтобы не блокировать GUI
        threading.Thread(target=self.process_files, daemon=True).start()

    def process_files(self):
        self.log("Начало обработки...")
        axis = self.axis_var.get()
        include_diag = self.diag_var.get()
        self.results.clear()

        for file_path in self.files:
            self.log(f"Обработка: {os.path.basename(file_path)}")
            try:
                arr = load_array(file_path)
                self.log(f"  Размерность: {arr.ndim}, форма: {arr.shape}")
                # Если ось выходит за пределы, скорректируем
                if axis >= arr.ndim:
                    self.log(f"  Ось {axis} недопустима для этого массива (макс. {arr.ndim - 1}). Пропускаем.")
                    continue
                results = find_local_maxima(arr, axis, include_diag)
                self.log(f"  Найдено локальных максимумов: {len(results)}")
                self.results[file_path] = results
                # Автосохранение
                base, ext = os.path.splitext(file_path)
                out_file = base + "_maxima.txt"
                save_results(results, out_file, original_file=file_path)
                self.log(f"  Результаты сохранены в: {out_file}")
                # Если это первый файл, покажем в таблице (можно сделать выбор по клику в списке)
                if len(self.results) == 1:
                    self.show_results(results)
            except Exception as e:
                self.log(f"  Ошибка при обработке {file_path}: {e}")
        self.log("Обработка завершена.")
        # Если есть результаты, показываем последний обработанный
        if self.results:
            last_file = self.files[-1]
            if last_file in self.results:
                self.show_results(self.results[last_file])

    def show_results(self, results):
        self.clear_tree()
        for coord, val in results:
            coord_str = ', '.join(map(str, coord))
            self.tree.insert("", tk.END, values=(coord_str, f"{val:.6g}"))
        # Обновим заголовок количества
        self.tree.heading("coords", text=f"Координаты ({len(results)} шт.)")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()