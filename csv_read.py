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

sorted_data = sort_data('Nero_XAUUSD60.csv')

