# %% считывание из файла csv
import csv

def sort_data(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # Пропускаем строку с заголовком
        input_data = []
        empty_cells = []  # Список для хранения информации о пустых ячейках
        for i, row in enumerate(reader, start=2):  # Начинаем с 2, так как пропустили строку с заголовком
            fractals = row[1:]
            # Проверяем каждую ячейку на пустоту
            for j, fractal in enumerate(fractals, start=1):  # Начинаем с 1, так как пропустили ячейку со временем
                if not fractal:
                    empty_cells.append((i, j))  # Добавляем информацию о пустой ячейке
            fractals = [fractal for fractal in fractals if fractal]
            sorted_fractals = sorted(fractals, key=lambda x: int(x.split(':')[0]) if x.split(':')[0] else 0)
            input_data.append([row[0]] + sorted_fractals)
        print(f"Обработано {len(input_data)} строк.")  # Выводим сообщение внутри функции
        # Выводим информацию о пустых ячейках
        if empty_cells:
            print("Найдены пустые ячейки в следующих местах (строка / столбец):")
            for cell in empty_cells:
                print(cell)
        else:
            print("Отлично, пустых ячеек не найдено.")
    return input_data

input_data = sort_data('Nero_5.csv') # Nero_XAUUSD60.csv    Nero_5.csv

# %% преобразование из текста в списки
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd

for i in range(len(input_data)):
    for j in range(1, len(input_data[i])): # пропускаем первый столбец со временем
        input_data[i][j] = np.array(input_data[i][j].split(':'))
# %% нормализация
for row in input_data:
    for index in [0, 1, 6, 7, 8, 9, 10]:  # индексы для нормализации
        values = [float(item[index]) for item in row[1:]]  # извлекаем значения для нормализации
        min_val, max_val = min(values), max(values)  # находим минимальное и максимальное значения
        # выполняем нормализацию
        for item in row[1:]:
            item[index] = (float(item[index]) - min_val) / (max_val - min_val) if max_val > min_val else 0.5
        if index == 1: # сохраняем минимальное и максимальное значения для индекса 1
            min_max_values = [min_val, max_val - min_val]
    # Нормализация данных с индексами 3 и 4 вместе
    values_3 = [float(item[3]) for item in row[1:]]
    values_4 = [float(item[4]) for item in row[1:]]
    min_val = min(min(values_3), min(values_4))
    max_val = max(max(values_3), max(values_4))
    for item in row[1:]:
        item[3] = (float(item[3]) - min_val) / (max_val - min_val) if max_val > min_val else 0.5
        item[4] = (float(item[4]) - min_val) / (max_val - min_val) if max_val > min_val else 0.5
    row.insert(1, min_max_values) # Добавляем минимальное и максимальное значения в input_data после столбца с временем
df = pd.DataFrame(input_data) # Создаем объект DataFrame из массива данных
df.to_csv('normalized.csv', index=False) # Сохраняем DataFrame в файл normalized.csv            
# %% old code
# %% нормализация
