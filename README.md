
# Нейронная сеть на основе tensorflow для торгового робота
* [Считывание из файла и упорядочивание](#считывание-из-файла-и-упорядочивание)
* [Нормализация](#нормализация)
* [Тренировка нейронной сети](#тренировка-нейронной-сети) 

## Считывание из файла и упорядочивание
Требуется создать нейронную сеть для автоматической торговли на валютной паре XAUUSD60 путем формирования сигналов открытия позиций. Входные данные для сети содержатся в файле.
Файл представляет собой трехмерный массив таймсерию. Но содержит информацию не о барах, а о фракталах. Поэтому временной интервал между строками данных в файле будет разный. Фракталом будем называть ценовую формацию из трех бар, в которой цена меняет свое направление. Другими словами фрактал – это либо пик (когда средний бар выше предыдущего и последующего), либо впадина (когда средний бар ниже предыдущего и последующего). 
Итак, файл формируется следующим образом. При формировании на графике цены очередного фрактала в файл записывается строка. В первой ячейке строки записывается время формирования этого фрактала ‘time’. Далее записывается массив списков. Каждый элемент массива – это список, содержащий информацию об определенном фрактале. Назовем данный список ‘fractal’. Таким образом, каждая строка файла содержит ячейку со временем ‘time’ и [n] ячеек ‘fractal’ с информацией о последних [n] фракталах.
```bash
time[0] ; fractal[0,0] ; fractal[0,1]; … ; fractal[0,n]
time[1] ; fractal[1,0] ; fractal[1,1]; … ; fractal[1,n]
time[k] ; fractal[k,0] ; fractal[k,1]; … ; fractal[k,n]
```
Каждая ячейка ‘fractal[i,j]’ содержит список параметров фрактала, с разделителем ‘:’.  Структура данного списка следующая.
shift : price : direction : front : back : strong : break : reverse : power : count : impulse 
Значения данных параметров следующие.
```bash
shift(int) – сдвиг в барах относительно текущего (последнего) фрактала;
price(float) – значение цены фрактала;
direction(char) – направление разворота фрактала (1=пик, или -1=впадина);
front(float) – величина переднего фронта – движение, предшествующее фракталу; 
back(float) – величина заднего фронта – движение, последующее после фрактала;
strong(bool) – признак уникальности, т.е. данный фрактал может являться сигналом для открытия сделки с большим отношением profit/loss;
break(char) – количество раз, которое фрактал был пробит последующими ценовыми движениями;
reverse(char) – признак того, что фрактал пробил хотя бы один из предшествующих ему фракталов;
power(float) – сила (значимость, относительный рейтинг) фрактала;
count(char) – количество совпадений по значению цены с остальными фракталами (влияет на силу);
minutes(ushort) – кол-во минут с начала суток для текущего фрактала;
atr(float) – быстрый ATR в момент формирования фрактала;
impulse(float) – импульс цены (скорость разворота), который задал данный фрактал.
```
Все эти значения пересчитываются и обновляются с каждым новым фракталом, поэтому данные из файла нельзя подавать на вход нейронной сети в виде скользящего временного окна. Каждый цикл на вход нейронной сети нужно подавать всю строку (массив списков) целиком. На каждом следующем цикле полностью обновлять входные данные нейронной сети значениями новой строки.
Напиши программу на Python чтобы отсортировать каждую строку файла (массив fractal[1] ; fractal[2] ; … ; fractal[n]) по возрастанию значения ‘shift’. 
  
## Нормализация
Мы имеем переменную ‘input_data’ следующего вида:

```bash
17.04.2023	6:1981.1:-1:67.5:14.8:0:0:1:34.1:1:2.3	11:2010.6:1:5.7:29.5:0:0:0:34.1:2:2.3	12:1995.9:1:14.8:1.7:0:0:1:34.1:5:2.3
17.04.2023	13:2010.6:1:5.7:29.5:0:0:0:6.5:2:1.2	15:1987.2:-1:4.9:8.7:0:0:0:6.5:1:1.2	18:1981.1:-1:67.5:14.8:0:0:1:6.5:1:1.2
```

Преобразуем текст в список:

```python
for i in range(len(input_data)):
    for j in range(1, len(input_data[i])): # пропускаем первый столбец со временем
        input_data[i][j] = np.array(input_data[i][j].split(':'))
```  
получаем список списков
```bash
17.04.2023	6,1981.1,-1,67.5,14.8,0,0,1,34.1,1,2.3	11,2010.6,1,5.7,29.5,0,0,0,34.1,2,2.3	12,1995.9,1,14.8,1.7,0,0,1,34.1,5,2.3
17.04.2023	13,2010.6,1,5.7,29.5,0,0,0,6.5,2,1.2	15,1987.2,-1,4.9,8.7,0,0,0,6.5,1,1.2	18,1981.1,-1,67.5,14.8,0,0,1,6.5,1,1.2
```           
Переменная ‘input_data’ представляет собой список списков, и имеет следующий вид:

```python
time[0] fractal[0,0] fractal[0,1] … fractal[0,n]
time[1] fractal[1,0] fractal[1,1] … fractal[1,n]
……
time[k] fractal[k,0] fractal[k,1] … fractal[k,n]
```

В первом столбце содержится время ‘time’. Следующие столбцы представляют собой списки ‘fractal’ из 13 значений:

```python
fractal=[
shift(int)
price(float)
direction(char)
front(float)
back(float)
strong(bool)
break(char)
reverse(char)
power(float)
count(char)
minute(ushort)
atr(float)
impulse(float)
]
```

В списке ‘input_data’ в пределах каждой строки среди списков fractal[0]...fractal[n] нужно нормализовать значения переменной shift к диапазону [0..1], значение price нормализовать к диапазону [0..1]. 
Аналогично нормализовать break, reverse, power, count, minute, atr, impulse.
Переменные front и back имеют общую единицу измерения и общие пределы (max_val, min_val), поэтому их необходимо нормализовать вместе к общему диапазону [0..1].   
При дальнейшей работе со списком ‘input_data’ потребуется восстановить нормализованное значение ‘price’ к исходному значению. Поэтому в список ‘input_data’ сразу после столбца ‘time’ нужно добавить столбец ‘recover’, содержащий данные [min_val, multiplier] для восстановления ‘price’.
Напиши код на Python, реализующий данную задачу. 

## Тренировка нейронной сети
Требуется создать нейронную сеть для автоматической торговли на валютной паре XAUUSD60. Сеть должна формировать цены входа в позицию путем обработки массива ценовых данных. Входные данные для тренировки сети представляют собой список ‘input_data’, объединяющий в себе списки ‘fractals_list’. 
Фракталом будем называть ценовую формацию из трех бар, в которой цена меняет свое направление. Другими словами, фрактал - это либо пик (когда средний бар выше предыдущего и последующего), либо впадина (когда средний бар ниже предыдущего и последующего). 
При формировании на ценовом графике очередного фрактала в список ‘input_data’ добавляется список ‘fractals_list’. Список ‘fractals_list’ содержит время формирования этого фрактала ‘time’, массив ‘recover’ и массив списков [fractal[0] , fractal[1] ,…, fractal[n]].  
Таким образом, список ‘input_data’ имеет следующую структуру: 
```bash
time[0] recover[0] fractal[0,0] fractal[0,1] … fractal[0,n]
time[1] recover[1] fractal[1,0] fractal[1,1] … fractal[1,n]
…..
time[k] recover[k] fractal[k,0] fractal[k,1] … fractal[k,n]
```
Где n=99 – количество фракталов, одновременно подаваемых на вход нейронной сети;  
k=10000…100000 – общее количество фракталов в истории. Самый старый фрактал имеет индекс [0], самый новый – индекс [k].  
time – время формирования фрактала формата ‘DD.MM.YYYY  hh:mm:ss’  
recover – массив [min_val, multiplier] для восстановления нормализованного значения цены ‘price’.  
Каждый список ‘fractal[i,j]’ содержит набор параметров  определенного фрактала:
```bash
fractal=[shift, price, direction, front, back, strong, break, reverse, power, count, impulse]
```
Эти параметры имеют следующие значения.
```bash
[0] shift(int) – сдвиг в барах относительно текущего (последнего) фрактала;
[1] price(float) – значение цены фрактала;
[2] direction(char) – направление разворота фрактала (1=пик, или -1=впадина);
[3] front(float) – величина переднего фронта – движение, предшествующее фракталу; 
[4] back(float) – величина заднего фронта – движение, последующее после фрактала;
[5] strong(bool) – признак уникальности, т.е. данный фрактал может являться сигналом для открытия сделки с большим отношением profit/loss;
[6] break(char) – количество раз, которое фрактал был пробит последующими ценовыми движениями;
[7] reverse(char) – признак того, что фрактал пробил хотя бы один из предшествующих ему фракталов;
[8] power(float) – сила (значимость, относительный рейтинг) фрактала;
[9] count(char) – количество совпадений по значению цены с остальными фракталами (влияет на силу);
[10] minutes(ushort) – кол-во минут с начала суток для текущего фрактала;
[11] atr(float) – быстрый ATR в момент формирования фрактала;
[12] impulse(float) – импульс цены (скорость разворота), который задал данный фрактал.
[13] time(dtime) – время формирования фрактала;
```
Все эти значения пересчитываются и обновляются с каждым новым фракталом, поэтому данные из файла нельзя подавать на вход модели в виде скользящего временного окна. Каждый цикл на вход нейронной сети в качестве признаков нужно подавать весь список ‘fractals_list’ за исключением значений ‘time’ и ‘recover’.  
Меткой (выходом) будут значения ‘price’  ‘direction’ и ‘strong’.

