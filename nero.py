# %% Импорт необходимых библиотек
import numpy as np
import pandas as pd # pip install pandas
import tensorflow as tf # pip install tensorflow
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler # pip install scikit-learn
from sklearn.model_selection import train_test_split
import requests
from io import BytesIO
import tensorflow.python.platform.build_info as build_info

print("Tensorflow ver-",tf.__version__," CUDA ver-",build_info.build_info['cuda_version'])
# %% Подключение GPU
devices = tf.config.list_physical_devices('GPU')
if len(devices) > 0:
    tf.config.experimental.set_memory_growth(devices[0], True)
    print('connect GPU ',len(devices))
else:
    print("GPU not available")
# %%
tf.config.experimental_connect_to_cluster(tpu)
tf.tpu.experimental.initialize_tpu_system(tpu)
tpu_strategy = tf.distribute.TPUStrategy(tpu)

# Загрузка данных
history_data = 'EURUSD60.csv' # 'https://drive.google.com/uc?id=1_eYsMYv8L_rrFrNnVN39ugbSVvC12Mm5'
data = pd.read_csv(history_data, header=None, sep=',', names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'])
data = data[['high', 'low']]

# Проверка на пустые строки
data.dropna(inplace=True)

# %% Создание набора данных для обучения и валидации
X = []
y = []
scaler_high = MinMaxScaler(feature_range=(0, 1))
scaler_low = MinMaxScaler(feature_range=(0, 1))
for i in range(100, len(data)):
    window_high = scaler_high.fit_transform(data['high'][i-100:i].values.reshape(-1, 1))
    window_low = scaler_low.fit_transform(data['low'][i-100:i].values.reshape(-1, 1))
    window = np.hstack((window_high, window_low))
    X.append(window)
    y.append(1 if data.iloc[i, 0] > data.iloc[i-1, 0] else 0)
X, y = np.array(X), np.array(y)
X = np.reshape(X, (X.shape[0], X.shape[1], 2))

# Разделение данных на обучающую и валидационную выборки
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# %% Создание модели LSTM
with tpu_strategy.scope():
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 2)))
    model.add(LSTM(units=50))
    model.add(Dense(1, activation='sigmoid'))

    # Компиляция и обучение модели
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=10, batch_size=32)

# %% Прогнозирование следующего бара
last_100_data_high = scaler_high.transform(data['high'][-100:].values.reshape(-1, 1))
last_100_data_low = scaler_low.transform(data['low'][-100:].values.reshape(-1, 1))
last_100_data = np.hstack((last_100_data_high, last_100_data_low))
predicted_price = model.predict(np.reshape(last_100_data, (1, last_100_data.shape[0], 2)))
predicted_direction = 'up' if predicted_price > 0.5 else 'down'
print(f'Предсказанное направление для следующего бара - {predicted_direction}.')

# %%
