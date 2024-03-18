from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

# Список доступных картриджей
cartridges = ["Картридж 1", "Картридж 2", "Картридж 3"]

@app.route('/')
def index():
    return render_template('index.html',cartridge=cartridges)

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
