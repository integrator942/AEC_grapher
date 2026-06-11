import numpy as np
from scipy.interpolate import LinearNDInterpolator
import matplotlib.pyplot as plt

# Исходные данные
data = {
    100: {
        'мАс': [2.0, 4.0, 6.3, 8.0, 12.5, 16.0, 25.0],
        'IQF': [2.86, 4.56, 5.99, 5.97, 7.05, 7.45, 7.48],
        'Яркость': [635.0, 1181.0, 1838.0, 2280.0, 3544.0, 4483.0, 6973.0],
        'Доза': [30.3, 60.7, 97.3, 120.0, 192.0, 237.0, 368.0]
    },
    110: {
        'мАс': [1.25, 2.5, 4.0, 5.0, 8.0, 10.0, 16.0],
        'IQF': [2.65, 4.36, 5.43, 5.66, 6.5, 6.67, 7.56],
        'Яркость': [574.0, 1051.0, 1626.0, 2020.0, 3180.0, 3967.0, 6305.0],
        'Доза': [22.7, 45.0, 72.0, 90.0, 143.0, 179.0, 281.0]
    },
    120: {
        'мАс': [1.0, 2.0, 3.2, 4.0, 6.3, 8.0, 12.5],
        'IQF': [2.06, 3.79, 4.89, 5.01, 6.37, 6.6, 7.08],
        'Яркость': [601.0, 1111.0, 1731.0, 2147.0, 3395.0, 4216.0, 6611.0],
        'Доза': [20.9, 41.7, 66.7, 83.3, 132.0, 166.0, 261.0]
    }
}

# Подготовка данных для интерполяции
X_mas = []
X_kv = []
Y_iqf = []
Y_bright = []
Y_dose = []

for kv, vals in data.items():
    for mas, iqf, bright, dose in zip(vals['мАс'], vals['IQF'], vals['Яркость'], vals['Доза']):
        X_mas.append(mas)
        X_kv.append(kv)
        Y_iqf.append(iqf)
        Y_bright.append(bright)
        Y_dose.append(dose)

X_mas = np.array(X_mas)
X_kv = np.array(X_kv)
Y_iqf = np.array(Y_iqf)
Y_bright = np.array(Y_bright)
Y_dose = np.array(Y_dose)

# Вычисляем IQF/доза для исходных точек
Y_iqf_dose = Y_iqf / Y_dose

# Интерполяторы
points_mas_kv = np.column_stack((X_mas, X_kv))
iqf_interpolator = LinearNDInterpolator(points_mas_kv, Y_iqf)

points_bright_kv = np.column_stack((Y_bright, X_kv))
iqf_from_bright_interpolator = LinearNDInterpolator(points_bright_kv, Y_iqf)

iqf_dose_interpolator = LinearNDInterpolator(points_mas_kv, Y_iqf_dose)

# Создание сеток
mas_grid = np.linspace(min([value for key in data for value in data[key]['мАс']]), max([value for key in data for value in data[key]['мАс']]), 100)
kv_grid = np.linspace(100, 120, 100)
MAS_grid, KV_grid = np.meshgrid(mas_grid, kv_grid)
bright_grid = np.linspace(min([value for key in data for value in data[key]['Яркость']])-50, max([value for key in data for value in data[key]['Яркость']])+50, 100)
BRIGHT_grid, KV_grid2 = np.meshgrid(bright_grid, kv_grid)

# Вычисление значений на сетках
points_grid_mas_kv = np.column_stack((MAS_grid.ravel(), KV_grid.ravel()))
IQF_grid = iqf_interpolator(points_grid_mas_kv).reshape(MAS_grid.shape)

points_grid_bright_kv = np.column_stack((BRIGHT_grid.ravel(), KV_grid2.ravel()))
IQF_bright_grid = iqf_from_bright_interpolator(points_grid_bright_kv).reshape(BRIGHT_grid.shape)

IQF_dose_grid = iqf_dose_interpolator(points_grid_mas_kv).reshape(MAS_grid.shape)

# Функция для добавления подписей значений на график
def add_value_labels(ax, x_data, y_data, values):
    for j, (x, y, val) in enumerate(zip(x_data, y_data, values), 1):
        if j % 2 == 0:
            va_pos = 'bottom'
        else:
            va_pos = 'top'
        ax.text(x, y, f'{val:.2f}'.replace('.', ','),
                ha='center', va=va_pos,
                fontsize=8,
                color='black',
                fontweight='bold',
                zorder=3)

# График 1: IQF = f(мАс, кВ)
fig1, ax1 = plt.subplots(figsize=(8, 6))
im1 = ax1.contourf(MAS_grid, KV_grid, IQF_grid, levels=20, cmap='viridis')
ax1.scatter(X_mas, X_kv, s=2, color='black')
add_value_labels(ax1, X_mas, X_kv, Y_iqf)
ax1.set_xlabel('мАс')
ax1.set_ylabel('кВ')
ax1.set_title('IQFinv = f(мАс, кВ)')
ax1.set_ylim(99, 121)
ax1.set_xlim(0.05, max([value for key in data for value in data[key]['мАс']]))
plt.colorbar(im1, ax=ax1, label='IQFinv')
plt.tight_layout()

# График 2: IQF = f(яркость, кВ)
fig2, ax2 = plt.subplots(figsize=(8, 6))
im2 = ax2.contourf(BRIGHT_grid, KV_grid2, IQF_bright_grid, levels=20, cmap='plasma')
ax2.scatter(Y_bright, X_kv, s=2, color='black')
add_value_labels(ax2, Y_bright, X_kv, Y_iqf)
ax2.set_xlabel('Яркость')
ax2.set_ylabel('кВ')
ax2.set_title('IQFinv = f(яркость, кВ)')
ax2.set_ylim(99, 121)
ax2.set_xlim(min([value for key in data for value in data[key]['Яркость']])-50, max([value for key in data for value in data[key]['Яркость']])+50)
plt.colorbar(im2, ax=ax2, label='IQFinv')
plt.tight_layout()

# График 3: IQF/доза = f(мАс, кВ)
fig3, ax3 = plt.subplots(figsize=(8, 6))
im3 = ax3.contourf(MAS_grid, KV_grid, IQF_dose_grid, levels=20, cmap='coolwarm')
ax3.scatter(X_mas, X_kv, s=2, color='black')
add_value_labels(ax3, X_mas, X_kv, Y_iqf_dose)
ax3.set_xlabel('мАс')
ax3.set_ylabel('кВ')
ax3.set_title('IQFinv/доза = f(мАс, кВ)')
ax3.set_ylim(99, 121)
ax3.set_xlim(0.05, max([value for key in data for value in data[key]['мАс']]))
plt.colorbar(im3, ax=ax3, label='IQFinv/доза')
plt.tight_layout()

plt.show()