from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import csv
# %% считывание из файла csv в строковый формат с разделителями ':'
""" данные в файле csv имеют следующий вид (разделитель внутри ячеек ':')
25.09.2023 7:00     3:1924.2:1:1.6:1.5:0:0:0:29.0:7:360:2.0:1.6:2111	2:1922.6:-1:6.5:1.6:0:0:1:26.6:7:300:2.0:2.1:2222	...
25.09.2023 10:00	4:1924.2:1:1.6:1.5:0:3:0:29.0:7:360:2.0:1.6:3111	5:1922.6:-1:6.5:1.6:0:4:1:26.6:7:300:2.0:2.1:3222	...
25.09.2023 11:00	5:1924.2:1:1.6:1.5:0:4:0:29.0:7:360:2.0:1.6:4111	6:1922.6:-1:6.5:1.6:0:5:1:26.6:7:300:2.0:2.1:4222	...
"""
def read_data(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=';')# Создаем объект reader для чтения CSV-файла
        next(reader)  # Пропускаем строку с заголовком
        data = []
        empty_cells = []  # Список для хранения пустых ячеех
        for i, row in enumerate(reader, start=2):  # Читаем каждую строку CSV-файла, начиная со второй
            fractals = row[1:] # Получаем из строки данные о фракталах пропуская 'time' с индексом [0]
            # Проверяем каждую ячейку на пустоту
            for j, fractal in enumerate(fractals, start=1):  # Перебираем все фракталы в строке
                if not fractal: # Если фрактал пустой
                    empty_cells.append((i, j))  # Добавляем информацию о пустой ячейке
            fractals = [fractal for fractal in fractals if fractal] # Удаляем пустые фракталы из списка
            fractals = [list(map(float, fractal.split(':'))) for fractal in fractals] # Преобразуем текст с разделителями ':' в числа
            sorted_fractals = sorted(fractals, key=lambda x: x[0] if x else 0) # Сортируем фракталы по первому значению в строке
            data.append([row[0]] + sorted_fractals) # Добавляем отсортированные фракталы в список данных
        print("from ",filename,f" read {len(data)} lines.")  # Выводим сообщение внутри функции
        # Выводим информацию о пустых ячейках
        if empty_cells: # Если попались пустые ячейки
            print("Find empty cells in (row / column):")
            for cell in empty_cells:
                print(cell)
        else:
            print("OK: no empty cells in file ",filename)
    
    for row in data: # в каждой строке в данных после 'даты' 
        row.insert(1, [0, 0]) # вставляем новый столбец predictor[0,0] чтобы записывать туда статус "ключевого" уровня
        row.insert(1, [0, 0])  # Добавляем новый столбец restore[0,0] для min_max_values
# после преобразований получили список списков
# time[0] predictor[0] restore[0] fractal[0][0] fractal[0][1] ... fractal[0][n]
# time[1] predictor[1] restore[1] fractal[1][0] fractal[1][1] ... fractal[1][n]  
# ...
# time[m] predictor[m] restore[m] fractal[m][0] fractal[m][1] ... fractal[m][n]  
 
# проверка каждого фрактала "не станет ли он в будущем ключевым уровнем" и поиск "ближайшего ключевого уровня". 
# predictor['статус фрактала в будущем', 'значение ближайшего ключевогоуровня']               
    first_levels_counter=np.zeros(len(data),dtype=int)
    for i in range(len(data)): # каждую строку
        for j in range(i + 1, len(data)): # сверяем со следующей и ниже
            for k in range(3, len(data[j])): # начиная со второго индекса (fractal[j][0])
                # поиск ближайшего "ключевого" уровня в будущем
                if data[j][k][5] > 0 and data[i][2][1] ==0: # в будущей истории найден ключевой уровень, и ни один уровень еще не сохранен
                    data[i][2][1] =  data[j][k][1] # сохраняем значение ближайшего в будущем "ключевого" уровня
                # проверка, будет ли текущий фрактал в будущем "ключевым уровнем"
                if data[i][3][13] == data[j][k][13] and data[j][k][5] > 0: # время терущего фрактала совпало со временем фрактала из будущего, и тот со статусом "ключевой"
                    data[i][2][0] = 1 # говорит о том, что в будущем этот фрактал будет "ключевым уровнем"
                    first_levels_counter[i]=1 # счеткик количества найденных ключевых уровней
                    break
    print('find ',sum(first_levels_counter)," first levels")                 
    
# нормализация всех данных к диапазону 0..1 и сохранение параметров нормализации цены в массив
# restore[min_val, max_val - min_val] для последующего восстановления значения цены 
    for row in data:
        for index in [0, 1, 6, 7, 8, 9, 10, 11, 12]:  # индексы для нормализации
            values = [float(item[index]) for item in row[3:]]  # извлекаем значения для нормализации
            min_val, max_val = min(values), max(values) # минимальное и максимальное значения
            # выполняем нормализацию
            for item in row[3:]:
                item[index] = (float(item[index]) - min_val) / (max_val - min_val) if max_val > min_val else 0.5
            if index == 1: # минимальное и максимальное значения для индекса 1 (цена)
                row[1] = [min_val, max_val - min_val]  # Добавляем минимальное и максимальное значения в data после столбца с временем
        # Нормализация данных с индексами 3 и 4 вместе
        values_3 = [float(item[3]) for item in row[3:]]
        values_4 = [float(item[4]) for item in row[3:]]
        min_val = min(min(values_3), min(values_4))
        max_val = max(max(values_3), max(values_4))
        for item in row[3:]:
            item[3] = (float(item[3]) - min_val) / (max_val - min_val) if max_val > min_val else 0.5
            item[4] = (float(item[4]) - min_val) / (max_val - min_val) if max_val > min_val else 0.5
    print('OK: data normalized')
    return data   
 
check = read_data('Nero_XAUUSD60.csv') # Nero_XAUUSD60.csv    Nero_5.csv
 # получили список списков
# time[0] predictor[0] restore[0] fractal[0][0] fractal[0][1] ... fractal[0][n]
# time[1] predictor[1] restore[1] fractal[1][0] fractal[1][1] ... fractal[1][n]  
# ...
# time[m] predictor[m] restore[m] fractal[m][0] fractal[m][1] ... fractal[m][n]           
# %% save to csv
#df = pd.DataFrame(check) # Создаем объект DataFrame из массива данных
#df.to_csv('normalized.csv', index=False) # Сохраняем DataFrame в файл normalized.csv  

with open('normalized.csv', 'w', newline='') as f:  # Открываем файл для записи
    writer = csv.writer(f, delimiter=';')  # Создаем объект writer для записи в CSV-файл
    for row in check:  # Перебираем каждую строку в данных
        new_row = [row[0]]  # Время сохраняется без изменений
        new_row += [':'.join(map(str, item)) for item in row[1:]]  # Преобразуем списки в строки, разделенные ':'
        writer.writerow(new_row)  # Записываем строку в файл

print(f"Data saved to {'normalized.csv'}")

# %% нормализация
