from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime
import glob

app = Flask(__name__)

@app.route('/')
def index():
    try:
        # Чтение данных из файла Excel
        df = pd.read_excel("список_картриджей.xlsx")
        # Преобразование названий столбцов к ожидаемому формату
        df.columns = ['Организация', 'Картридж', 'Количество']
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
        
        # Создание нового DataFrame только с выбранными строками
        selected_rows = []
        for index, row in df.iterrows():
            quantity_taken_str = request.form.get(f"quantity_taken_{index}", '')  # Получаем строку из формы
            quantity_taken = int(quantity_taken_str) if quantity_taken_str else 0  # Пытаемся преобразовать в число
            if quantity_taken > 0:
                selected_rows.append({'Организация': row['Организация'], 'Картридж': row['Картридж'], 'Сколько взяли': quantity_taken, 'Время взятия': datetime.now()})
                # Обновляем количество оставшихся картриджей
                df.at[index, 'Количество'] = max(row['Количество'] - quantity_taken, 0)

        # Создаем DataFrame из выбранных данных
        new_df = pd.DataFrame(selected_rows)
        
        # Сохранение нового DataFrame в файл
        new_df.to_excel(f"выбранные_картриджи_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx", index=False)
        
        # Сохранение обновленного DataFrame в основной файл
        try:
            # Сохранение обновленного DataFrame в основной файл
            df.to_excel("список_картриджей.xlsx", index=False)
            print("Данные успешно обновлены и записаны в основной файл.")
        except Exception as e:
            print(f"Произошла ошибка при обновлении основного файла Excel: {e}")
        
        # Редирект на главную страницу
        return redirect(url_for('index'))
    

    except Exception as e:
        return f"Произошла ошибка при обновлении файла Excel: {e}"

@app.route('/create_report', methods=['POST'])
def create_report():
    try:
        # Получение начальной и конечной даты/времени из формы
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        # Преобразование строковых значений в объекты datetime
        start_date = datetime.fromisoformat(start_date)
        end_date = datetime.fromisoformat(end_date)

        # Поиск файлов, соответствующих заданному интервалу дат
        file_pattern = f"выбранные_картриджи_{start_date.strftime('%Y-%m-%d')}*.xlsx"
        files = glob.glob(file_pattern)
        
        # Отладочный вывод найденных файлов
        print("Найденные файлы:", files)
        
        # Проверка наличия файлов
        if not files:
            return "Нет данных за выбранный период для создания отчета."
        
        # Считывание данных из найденных файлов
        dataframes = [pd.read_excel(file) for file in files]
        
        # Объединение данных из всех файлов в один DataFrame
        df_combined = pd.concat(dataframes, ignore_index=True)
        
        # Фильтрация данных по выбранному промежутку времени
        df_filtered = df_combined[(df_combined['Время взятия'] >= start_date) & (df_combined['Время взятия'] <= end_date)]
        
        # Создание отчета на основе отфильтрованных данных
        report_filename = f"отчет_{start_date.strftime('%Y-%m-%d_%H-%M-%S')}_{end_date.strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        df_filtered.to_excel(report_filename, index=False)
        
        return f"Отчет успешно создан. <a href='{report_filename}'>Скачать отчет</a>"

    except Exception as e:
        return f"Произошла ошибка при создании отчета: {e}"

if __name__ == '__main__':
    app.run(debug=True)
