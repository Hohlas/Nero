import csv

def sort_data(filename):
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # Пропускаем строку с заголовком
        sorted_data = []
        for row in reader: # Проходим по каждой строке в файле
            fractals = row[1:] # берем все данные из текущей строки, пропуская элемент [0], содержащий время
            # Сортируем фракталы по значению 'shift' и добавляем результат в sorted_data
            sorted_fractals = sorted(fractals, key=lambda x: int(x.split(':')[0]) if x.split(':')[0] else 0)
            sorted_data.append([row[0]] + sorted_fractals)
        print(f"Обработано {len(sorted_data)} строк.")
    return sorted_data

sorted_data = sort_data('Nero_XAUUSD60.csv')
