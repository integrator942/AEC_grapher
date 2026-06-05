import numpy as np
from scipy.interpolate import LinearNDInterpolator
import matplotlib.pyplot as plt

# Исходные данные
data = {
    100: {
        'мАс': [0.1, 0.2, 0.32, 0.4, 0.63, 0.8, 1.25],
        'IQF': [3.33, 5.67, 6.39, 6.92, 7.44, 7.79, 8.17],
        'Яркость': [390, 706, 1091, 1361, 2112, 2667, 4160],
        'Доза': [1.64, 3.15, 5, 6.2, 10, 12.2, 19.5]
    },
    110: {
        'мАс': [0.1, 0.16, 0.25, 0.32, 0.5, 0.63, 1],
        'IQF': [3.9, 5.11, 6.55, 6.97, 7.64, 7.73, 8.25],
        'Яркость': [487, 736, 1106, 1412, 2161, 2726, 4315],
        'Доза': [2, 3.07, 4.69, 5.93, 9.51, 11.7, 18.4]
    },
    120: {
        'мАс': [0.1, 0.125, 0.2, 0.25, 0.4, 0.5, 0.8],
        'IQF': [4.87, 4.95, 6.15, 6.84, 7.36, 7.74, 8.23],
        'Яркость': [603, 736, 1120, 1376, 2172, 2724, 4315],
        'Доза': [2.4, 2.93, 4.47, 5.53, 8.65, 10.6, 27.7]
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
mas_grid = np.linspace(0.1, 1.25, 100)
kv_grid = np.linspace(100, 120, 100)
MAS_grid, KV_grid = np.meshgrid(mas_grid, kv_grid)

bright_grid = np.linspace(390, 4400, 100)
BRIGHT_grid, KV_grid2 = np.meshgrid(bright_grid, kv_grid)

# Вычисление значений на сетках
points_grid_mas_kv = np.column_stack((MAS_grid.ravel(), KV_grid.ravel()))
IQF_grid = iqf_interpolator(points_grid_mas_kv).reshape(MAS_grid.shape)

points_grid_bright_kv = np.column_stack((BRIGHT_grid.ravel(), KV_grid2.ravel()))
IQF_bright_grid = iqf_from_bright_interpolator(points_grid_bright_kv).reshape(BRIGHT_grid.shape)

IQF_dose_grid = iqf_dose_interpolator(points_grid_mas_kv).reshape(MAS_grid.shape)

# Построение графиков
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# График 1: IQF = f(мАс, кВ)
im1 = axes[0].contourf(MAS_grid, KV_grid, IQF_grid, levels=20, cmap='viridis')
j=0
for i, (x, y, iqf_val) in enumerate(zip(X_mas, X_kv, Y_iqf)):
    j = j + 1
    # Белый круг побольше как фон для текста
    axes[0].scatter(X_mas, X_kv, s=2, color='black')
    # Текст значения внутри круга
    if j % 2 == 0:
        va_pos='bottom'
    else:
        va_pos ='top'
    axes[0].text(x, y, f'{iqf_val:.2f}'.replace('.', ','),
                ha='center', va=va_pos,
                fontsize=8,
                color='black',
                fontweight='bold',
                zorder=3)
axes[0].set_xlabel('мАс')
axes[0].set_ylabel('кВ')
axes[0].set_title('IQFinv = f(мАс, кВ)')
axes[0].set_ylim(99, 121)
axes[0].set_xlim(0.05, 1.3)
plt.colorbar(im1, ax=axes[0], label='IQFinv')

# График 2: IQF = f(яркость, кВ)
im2 = axes[1].contourf(BRIGHT_grid, KV_grid2, IQF_bright_grid, levels=20, cmap='plasma')
j=0
for i, (x, y, iqf_val) in enumerate(zip(Y_bright, X_kv, Y_iqf)):
    j = j + 1
    # Белый круг побольше как фон для текста
    axes[1].scatter(Y_bright, X_kv, s=2, color='black')
    # Текст значения внутри круга
    if j % 2 == 0:
        va_pos='bottom'
    else:
        va_pos ='top'
    axes[1].text(x, y, f'{iqf_val:.2f}'.replace('.', ','),
                ha='center', va=va_pos,
                fontsize=8,
                color='black',
                fontweight='bold',
                zorder=3)
axes[1].set_xlabel('Яркость')
axes[1].set_ylabel('кВ')
axes[1].set_title('IQFinv = f(яркость, кВ)')
axes[1].set_ylim(99, 121)
axes[1].set_xlim(350, 4500)
plt.colorbar(im2, ax=axes[1], label='IQF')

# График 3: IQF/доза = f(мАс, кВ)
im3 = axes[2].contourf(MAS_grid, KV_grid, IQF_dose_grid, levels=20, cmap='coolwarm')
j=0
for i, (x, y, iqf_val) in enumerate(zip(X_mas, X_kv, Y_iqf_dose)):
    j=j+1
    # Белый круг побольше как фон для текста
    axes[2].scatter(X_mas, X_kv, s=2, color='black')
    # Текст значения внутри круга
    if j % 2 == 0:
        va_pos='bottom'
    else:
        va_pos ='top'
    axes[2].text(x, y, f'{iqf_val:.2f}'.replace('.', ','),
                ha='center', va=va_pos,
                fontsize=8,
                color='black',
                fontweight='bold',
                zorder=3)
axes[2].set_xlabel('мАс')
axes[2].set_ylabel('кВ')
axes[2].set_title('IQF/доза = f(мАс, кВ)')
axes[2].set_ylim(99, 121)
axes[2].set_xlim(0.05, 1.3)
plt.colorbar(im3, ax=axes[2], label='IQF/доза')

plt.tight_layout()
plt.show()