data = """Доза, мкГр*м^2	20,9	41,7	66,7	83,3	132	166	261
мАс	1	2	3,2	4	6,3	8	12,5
IQFinv_18см	2,06	3,79	4,89	5,01	6,37	6,6	7,08
Яркость	601	1111	1731	2147	3395	4216	6611"""


def parse_data(data_string):
    result = {}
    lines = data_string.strip().split('\n')

    for line in lines:
        parts = line.split('\t')

        # Обработка названия параметра
        param_name = parts[0].split(',')[0].strip()
        if 'IQFinv' in param_name:
            param_name = 'IQF'

        # Парсинг значений
        values = []
        for val in parts[1:]:
            val = val.replace(',', '.')
            try:
                values.append(float(val))
            except ValueError:
                values.append(val)

        result[param_name] = values

    return result


# Конвертация данных
parsed_data = parse_data(data)

# Задаем порядок вывода
output_order = ['мАс', 'IQF', 'Яркость', 'Доза']

# Вывод результата в нужном формате и порядке
print("Сконвертированные данные:")
print("{")
for i, key in enumerate(output_order):
    values = parsed_data[key]
    if i == len(output_order) - 1:
        print(f"    '{key}': {values}")
    else:
        print(f"    '{key}': {values},")
print("}")