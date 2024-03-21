from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

# Список доступных картриджей
cartridges = ["Картридж 1", "Картридж 2", "Картридж 3"]

@app.route('/')
def index():
    # Прочитать данные из файла Excel
    try:
        df = pd.read_excel("список_картриджей.xlsx")
        # Преобразовать названия столбцов к нижнему регистру для согласованности с шаблоном
        df.columns = df.columns.str.lower()
        # Преобразовать данные в формат, который можно передать в HTML-шаблон
        data = df.to_dict(orient='records')
        print(data)  # Вывод данных для отладки
    except Exception as e:
        print("Ошибка чтения файла Excel:", e)
        data = None
    return render_template('index.html', data=data)

@app.route('/submit', methods=['POST'])
def submit():
    data = []
    total_cost = 0
    
    for cartridge in cartridges:
        quantity = int(request.form.get(cartridge, 0))
        if quantity > 0:
            cost = quantity * 10  # Здесь можно заменить на реальные данные
            total_cost += cost
            data.append({'Картридж': cartridge, 'Количество': quantity, 'Стоимость': cost})
        else :
            return "Введите значение"
    df = pd.DataFrame(data)
    df.to_excel("список_картриджей.xlsx", index=False)
    
    return f'Список картриджей сохранен в файл "список_картриджей.xlsx". Общая стоимость: {total_cost}'

if __name__ == '__main__':
    app.run(debug=True)