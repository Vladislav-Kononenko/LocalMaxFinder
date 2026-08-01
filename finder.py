import numpy as np
from scipy.ndimage import maximum_filter


def find_local_maxima(arr, axis, include_diagonal=True):
    """
    Находит локальные максимумы в каждом срезе по заданной оси.
    Возвращает список кортежей (координаты, значение).
    """
    ndim = arr.ndim
    # Проверка оси
    if axis < 0 or axis >= ndim:
        raise ValueError(f"Ось должна быть от 0 до {ndim - 1}")

    # Формируем структурный элемент (окрестность) для фильтра
    footprint = np.ones([3] * ndim, dtype=bool)
    center = tuple([1] * ndim)
    footprint[center] = False  # убираем центр
    # Обнуляем смещения по заданной оси
    for idx in np.ndindex(*([3] * ndim)):
        if idx[axis] != 0:
            footprint[idx] = False
    # Если не нужны диагональные, убираем смещения с более чем одной ненулевой координатой
    if not include_diagonal:
        for idx in np.ndindex(*([3] * ndim)):
            if idx[axis] == 0:
                # считаем количество ненулевых смещений по другим осям
                non_zero = sum(1 for d in range(ndim) if d != axis and idx[d] != 0)
                if non_zero > 1:
                    footprint[idx] = False

    # Фильтр максимумов соседей
    max_neighbors = maximum_filter(arr, footprint=footprint, mode='constant', cval=-np.inf)
    # Маска локальных максимумов (строго больше)
    is_max = arr > max_neighbors
    coords = np.argwhere(is_max)
    # Добавляем значения
    results = [(tuple(coord), arr[tuple(coord)]) for coord in coords]
    return results