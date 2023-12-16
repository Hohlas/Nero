# %% считывание из файла csv
import csv

def read_data(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # Пропускаем строку с заголовком
        data = []
        empty_cells = []  # Список для хранения информации о пустых ячейках
        for i, row in enumerate(reader, start=2):  # Начинаем с 2, так как пропустили строку с заголовком
            fractals = row[1:]
            # Проверяем каждую ячейку на пустоту
            for j, fractal in enumerate(fractals, start=1):  # Начинаем с 1, так как пропустили ячейку со временем
                if not fractal:
                    empty_cells.append((i, j))  # Добавляем информацию о пустой ячейке
            fractals = [fractal for fractal in fractals if fractal]
            sorted_fractals = sorted(fractals, key=lambda x: int(x.split(':')[0]) if x.split(':')[0] else 0)
            data.append([row[0]] + sorted_fractals)
        print("из файла ",filename,f" считано {len(data)} строк.")  # Выводим сообщение внутри функции
        # Выводим информацию о пустых ячейках
        if empty_cells:
            print("Найдены пустые ячейки в следующих местах (строка / столбец):")
            for cell in empty_cells:
                print(cell)
        else:
            print("Пустых ячеек не найдено.")
    return data

from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
# %% преобразование из текста в списки и нормализация
def normalize_data(data):
    for i in range(len(data)):
        for j in range(1, len(data[i])): # пропускаем первый столбец со временем
            data[i][j] = np.array(data[i][j].split(':')).astype(float) # преобразование из текста в списки
    
    for row in data: # в каждой строке в данных 
        row.insert(1, [0, 0]) # вставляем новый список [0, 0] после 'даты'
     
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            for k in range(2, len(data[j])):
                a=data[i][2][13]; b=data[j][k][13]; strong=data[j][k][5]
                if data[i][2][13] == data[j][k][13] and data[j][k][5] > 0:
                    data[i][1][0] = 1
                    data[i][1][1] = data[j][k][13]
                    break
    

     
    for row in data:
        for index in [0, 1, 6, 7, 8, 9, 10, 11, 12]:  # индексы для нормализации
            values = [float(item[index]) for item in row[2:]]  # извлекаем значения для нормализации
            min_val, max_val = min(values), max(values) # минимальное и максимальное значения
            # выполняем нормализацию
            for item in row[2:]:
                item[index] = (float(item[index]) - min_val) / (max_val - min_val) if max_val > min_val else 0.5
            if index == 1: # минимальное и максимальное значения для индекса 1 (цена)
                min_max_values = [min_val, max_val - min_val]
        # Нормализация данных с индексами 3 и 4 вместе
        values_3 = [float(item[3]) for item in row[2:]]
        values_4 = [float(item[4]) for item in row[2:]]
        min_val = min(min(values_3), min(values_4))
        max_val = max(max(values_3), max(values_4))
        for item in row[2:]:
            item[3] = (float(item[3]) - min_val) / (max_val - min_val) if max_val > min_val else 0.5
            item[4] = (float(item[4]) - min_val) / (max_val - min_val) if max_val > min_val else 0.5
        row.insert(1, min_max_values) # Добавляем минимальное и максимальное значения в data после столбца с временем
    print('данные нормализованы')
    
    return data   
 
csv_data = read_data('Nero_XAUUSD60.csv') # Nero_XAUUSD60.csv    Nero_5.csv
normalized_data=normalize_data(csv_data)
          
# %% save to csv
df = pd.DataFrame(normalized_data) # Создаем объект DataFrame из массива данных
df.to_csv('normalized.csv', index=False) # Сохраняем DataFrame в файл normalized.csv  

# %% нормализация
