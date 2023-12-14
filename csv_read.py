# %% считывание из файла csv
import csv

def sort_data(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # Пропускаем строку с заголовком
        sorted_data = []
        empty_cells = []  # Список для хранения информации о пустых ячейках
        for i, row in enumerate(reader, start=2):  # Начинаем с 2, так как пропустили строку с заголовком
            fractals = row[1:]
            # Проверяем каждую ячейку на пустоту
            for j, fractal in enumerate(fractals, start=1):  # Начинаем с 1, так как пропустили ячейку со временем
                if not fractal:
                    empty_cells.append((i, j))  # Добавляем информацию о пустой ячейке
            fractals = [fractal for fractal in fractals if fractal]
            sorted_fractals = sorted(fractals, key=lambda x: int(x.split(':')[0]) if x.split(':')[0] else 0)
            sorted_data.append([row[0]] + sorted_fractals)
        print(f"Обработано {len(sorted_data)} строк.")  # Выводим сообщение внутри функции
        # Выводим информацию о пустых ячейках
        if empty_cells:
            print("Найдены пустые ячейки в следующих местах (строка / столбец):")
            for cell in empty_cells:
                print(cell)
        else:
            print("Отлично, пустых ячеек не найдено.")
    return sorted_data

sorted_data = sort_data('Nero_5.csv') # Nero_XAUUSD60.csv

# %% нормализация
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
# Инициализируем splited_data как копию sorted_data
splited_data = sorted_data.copy()

for i in range(len(sorted_data)):
    for j in range(len(sorted_data[i])):
        # Проверяем, является ли элемент строкой, прежде чем разделять его
        splited_data[i][j] = np.array(splited_data[i][j].split(':'))
        
# Дополнительный код для нормализации
for row in splited_data:
    for index in [1, 3, 4, 8, 9, 10]:  # индексы для нормализации
        values = [float(item[index]) for item in row[1:]]  # извлекаем значения для нормализации
        min_val, max_val = min(values), max(values)  # находим минимальное и максимальное значения
        # выполняем нормализацию
        for item in row[1:]:
            item[index] = (float(item[index]) - min_val) / (max_val - min_val) if max_val > min_val else 0.5
df = pd.DataFrame(splited_data) # Создаем объект DataFrame из массива данных
df.to_csv('normalized.csv', index=False) # Сохраняем DataFrame в файл normalized.csv            
# %%
for i in range(len(sorted_data)):
    for j in range(len(sorted_data[i])):
        # Проверяем, является ли элемент строкой, прежде чем разделять его
        if isinstance(sorted_data[i][j], str):
            fractal = np.array(sorted_data[i][j].split(':'))  
            # Выберите столбцы для нормализации
            cols_to_normalize = [1, 2, 4, 5, 9, 10]
            # Нормализуем данные
            fractal[cols_to_normalize] = MinMaxScaler().fit_transform(fractal[cols_to_normalize].reshape(-1, 1))
            splited_data[i][j] = fractal.tolist()  # Преобразуем массив NumPy обратно в список

data = [np.array(row) for row in splited_data]  # Преобразуем каждую строку списка в массив NumPy