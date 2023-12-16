from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import csv
# %% считывание из файла csv в строковый формат с разделителями ':'
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
        print("from ",filename,f" read {len(data)} lines.")  # Выводим сообщение внутри функции
        # Выводим информацию о пустых ячейках
        if empty_cells:
            print("Find empty cells in (row / column):")
            for cell in empty_cells:
                print(cell)
        else:
            print("OK: no empty cells in file ",filename)
    return data
# %% преобразование из текста с разделителямми ':' в списки 
def txt_2_list(data):
    for i in range(len(data)):
        for j in range(1, len(data[i])): # пропускаем первый столбец со временем
            data[i][j] = np.array(data[i][j].split(':')).astype(float) # преобразование из текста в списки
    #keys = ["date"] + ["fr" + str(i) for i in range(1, len(data[0]))]
    #dict_data = [dict(zip(keys, sublist)) for sublist in data]
    return data
#check = read_data('Nero_XAUUSD60.csv') # Nero_XAUUSD60.csv    Nero_5.csv
#check = txt_2_list(check)
# %% проверка каждого фрактала "не станет ли он в будущем первым уровнем" и запись статуса в доп. столбец. 
def find_strong_levels(data):
    for row in data: # в каждой строке в данных 
        row.insert(1, [0, 0]) # вставляем после 'даты' новый список status[0, 0] чтобы записывать туда статус первого уровня
    # time[0] status[0] fractal[0][0] fractal[0][1] ... fractal[0][n]
    # time[1] status[1] fractal[1][0] fractal[1][1] ... fractal[1][n]     
    first_levels=np.zeros(len(data),dtype=int)
    for i in range(len(data)): # каждую строку
        for j in range(i + 1, len(data)): # сверяем со следующей и ниже
            for k in range(2, len(data[j])): # начиная со второго индекса (fractal[j][0])
                if data[i][2][13] == data[j][k][13] and data[j][k][5] > 0: # время терущего фрактала совпало со временем фрактала из будущего, и тот со статусом "первый"
                    data[i][1][0] = 1 # записываем статус новому фракталу
                    data[i][1][1] = data[j][k][13] #
                    first_levels[i]=1
                    break
    print('find ',sum(first_levels)," first levels")                
    return data
# %% нормализация всех данных к диапазону 0..1
def normalize(data):     
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
    print('OK: data normalized')
    return data   
 
check = read_data('Nero_XAUUSD60.csv') # Nero_XAUUSD60.csv    Nero_5.csv
check = txt_2_list(check)
check = find_strong_levels(check)
check = normalize(check)
          
# %% save to csv
df = pd.DataFrame(check) # Создаем объект DataFrame из массива данных
df.to_csv('normalized.csv', index=False) # Сохраняем DataFrame в файл normalized.csv  

# %% нормализация
