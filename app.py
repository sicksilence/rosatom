from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    try:
        # Чтение данных из файла Excel
        df = pd.read_excel("список_картриджей.xlsx")
        # Преобразование названий столбцов к нижнему регистру для согласованности с шаблоном
        df.columns = df.columns.str.lower()
        # Преобразование данных в формат, который можно передать в HTML-шаблон
        data = df.to_dict(orient='records')
        print(data)  # Вывод данных для отладки
    except Exception as e:
        print("Ошибка чтения файла Excel:", e)
        data = None
    return render_template('index.html', data=data)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Чтение существующего файла Excel
        df = pd.read_excel("список_картриджей.xlsx")
        
        # Обновление данных в столбце quantity
        for index, row in df.iterrows():
            cartridge = row['cartridge']
            quantity_taken_str = request.form.get(f"quantity_taken_{index}", '')  # Получаем строку из формы
            quantity_taken = int(quantity_taken_str) if quantity_taken_str else 0  # Пытаемся преобразовать в число
            print(f"Картридж: {cartridge}, Количество взято: {quantity_taken}")  # Отладочный вывод
            df.at[index, 'quantity'] = max(row['quantity'] - quantity_taken, 0)

        # Сохранение обновленного DataFrame в файл
        df.to_excel("список_картриджей.xlsx", index=False)
        
        # Редирект на главную страницу
        return redirect(url_for('index'))

    except Exception as e:
        return f"Произошла ошибка при обновлении файла Excel: {e}"

if __name__ == '__main__':
    app.run(debug=True)
