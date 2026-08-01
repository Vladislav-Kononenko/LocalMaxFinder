import numpy as np
import pandas as pd
import os

def load_array(file_path):
    """Загружает массив из файла, определяя формат по расширению."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.npy':
        return np.load(file_path)
    elif ext == '.npz':
        # Если .npz, берём первый массив
        data = np.load(file_path)
        # Берём первый ключ (обычно 'arr_0')
        key = list(data.keys())[0]
        return data[key]
    elif ext in ['.csv', '.txt']:
        # Пытаемся прочитать как таблицу чисел
        try:
            df = pd.read_csv(file_path, header=None)
            arr = df.values
            # Если только одна строка или столбец, может быть 1D
            if arr.ndim == 2 and (arr.shape[0] == 1 or arr.shape[1] == 1):
                arr = arr.flatten()
            return arr
        except:
            # Если не таблица, читаем как простой текстовый файл с числами
            data = np.loadtxt(file_path)
            return data
    else:
        raise ValueError(f"Неподдерживаемый формат: {ext}")

def save_results(results, output_path, original_file=None):
    """Сохраняет координаты и значения в текстовый файл."""
    with open(output_path, 'w') as f:
        if original_file:
            f.write(f"# Результаты для файла: {original_file}\n")
        f.write("# Координаты (по всем осям) и значение\n")
        for coord, val in results:
            coord_str = ' '.join(map(str, coord))
            f.write(f"{coord_str}  {val}\n")