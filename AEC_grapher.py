import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import LinearNDInterpolator

# Исходные данные
data = {
    100: {
        'мАс': [0.1, 0.2, 0.32, 0.4, 0.63, 0.8, 1.25],
        'IQF': [3.33, 5.67, 6.39, 6.92, 7.44, 7.79, 8.17],
        'Яркость': [390, 706, 1091, 1361, 2112, 2667, 4160],
        'мАс_для_3мкГр': 0.4  # при 100 кВ доза 3 мкГр при 0.4 мАс
    },
    110: {
        'мАс': [0.1, 0.16, 0.25, 0.32, 0.5, 0.63, 1],
        'IQF': [3.9, 5.11, 6.55, 6.97, 7.64, 7.73, 8.25],
        'Яркость': [487, 736, 1106, 1412, 2161, 2726, 4315],
        'мАс_для_3мкГр': 0.32  # при 110 кВ доза 3 мкГр при 0.32 мАс
    },
    120: {
        'мАс': [0.1, 0.125, 0.2, 0.25, 0.4, 0.5, 0.8],
        'IQF': [4.87, 4.95, 6.15, 6.84, 7.36, 7.74, 8.23],
        'Яркость': [603, 736, 1120, 1376, 2172, 2724, 4315],
        'мАс_для_3мкГр': 0.25  # при 120 кВ доза 3 мкГр при 0.25 мАс
    }
}

# Подготовка данных
X_mas, X_kv, Y_iqf, Y_dose, Y_iqf_per_dose = [], [], [], [], []

for kv, vals in data.items():
    mas_ref_3 = vals['мАс_для_3мкГр']
    for mas, iqf in zip(vals['мАс'], vals['IQF']):
        dose = 3.0 * (mas / mas_ref_3)  # доза в мкГр
        iqf_per_dose = iqf / dose

        X_mas.append(mas)
        X_kv.append(kv)
        Y_iqf.append(iqf)
        Y_dose.append(dose)
        Y_iqf_per_dose.append(iqf_per_dose)

X_mas = np.array(X_mas)
X_kv = np.array(X_kv)
Y_iqf = np.array(Y_iqf)
Y_iqf_per_dose = np.array(Y_iqf_per_dose)

# Интерполяторы
points_mas_kv = np.column_stack((X_mas, X_kv))
iqf_interpolator = LinearNDInterpolator(points_mas_kv, Y_iqf)
iqf_per_dose_interpolator = LinearNDInterpolator(points_mas_kv, Y_iqf_per_dose)

# Сетка для графиков
mas_grid = np.linspace(0.1, 1.25, 50)
kv_grid = np.linspace(100, 120, 50)
MAS_grid, KV_grid = np.meshgrid(mas_grid, kv_grid)
points_grid = np.column_stack((MAS_grid.ravel(), KV_grid.ravel()))

IQF_grid = iqf_interpolator(points_grid).reshape(MAS_grid.shape)
IQF_per_dose_grid = iqf_per_dose_interpolator(points_grid).reshape(MAS_grid.shape)

# Построение 3D графиков
fig = plt.figure(figsize=(18, 5))

# График 1: IQF = f(мАс, кВ)
ax1 = fig.add_subplot(1, 3, 1, projection='3d')
surf1 = ax1.plot_surface(MAS_grid, KV_grid, IQF_grid, cmap='viridis', edgecolor='none')
ax1.set_xlabel('мАс')
ax1.set_ylabel('кВ')
ax1.set_zlabel('IQF')
ax1.set_title('IQF = f(мАс, кВ)')
fig.colorbar(surf1, ax=ax1, shrink=0.5, aspect=10)

# График 2: IQF = f(яркость, кВ) — оставляем как было
data_for_bright = {100: data[100], 110: data[110], 120: data[120]}
X_bright, X_kv2, Y_iqf2 = [], [], []
for kv, vals in data_for_bright.items():
    for bright, iqf in zip(vals['Яркость'], vals['IQF']):
        X_bright.append(bright)
        X_kv2.append(kv)
        Y_iqf2.append(iqf)

points_bright_kv = np.column_stack((X_bright, X_kv2))
iqf_from_bright_interp = LinearNDInterpolator(points_bright_kv, Y_iqf2)

bright_grid = np.linspace(390, 4400, 50)
KV_grid2, BRIGHT_grid = np.meshgrid(kv_grid, bright_grid)
points_bright_grid = np.column_stack((BRIGHT_grid.ravel(), KV_grid2.ravel()))
IQF_from_bright_grid = iqf_from_bright_interp(points_bright_grid).reshape(BRIGHT_grid.shape)

ax2 = fig.add_subplot(1, 3, 2, projection='3d')
surf2 = ax2.plot_surface(BRIGHT_grid, KV_grid2, IQF_from_bright_grid, cmap='plasma', edgecolor='none')
ax2.set_xlabel('Яркость')
ax2.set_ylabel('кВ')
ax2.set_zlabel('IQF')
ax2.set_title('IQF = f(яркость, кВ)')
fig.colorbar(surf2, ax=ax2, shrink=0.5, aspect=10)

# График 3: IQF / Dose = f(мАс, кВ)
ax3 = fig.add_subplot(1, 3, 3, projection='3d')
surf3 = ax3.plot_surface(MAS_grid, KV_grid, IQF_per_dose_grid, cmap='coolwarm', edgecolor='none')
ax3.set_xlabel('мАс')
ax3.set_ylabel('кВ')
ax3.set_zlabel('IQF / Dose (мкГр⁻¹)')
ax3.set_title('IQF / Dose = f(мАс, кВ)')
fig.colorbar(surf3, ax=ax3, shrink=0.5, aspect=10)

plt.tight_layout()
plt.show()

# Пример расчёта
print("\nПримеры интерполяции:")
print(f"IQF при мАс=0.5, кВ=105: {iqf_interpolator(0.5, 105):.3f}")
print(f"IQF/Dose при мАс=0.5, кВ=105: {iqf_per_dose_interpolator(0.5, 105):.3f} мкГр⁻¹")

# Исходные значения IQF/Dose для контроля
print("\nИсходные IQF/Dose (по точкам):")
for kv, vals in data.items():
    mas_ref = vals['мАс_для_3мкГр']
    for mas, iqf in zip(vals['мАс'], vals['IQF']):
        dose = 3 * mas / mas_ref
        print(f"  {kv} кВ, мАс={mas}: IQF/Dose = {iqf / dose:.3f}")