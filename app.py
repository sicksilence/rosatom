from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# Папка для хранения выбранных файлов
chosen_folder = "выбранные"
if not os.path.exists(chosen_folder):
    os.makedirs(chosen_folder)

# Папка для хранения отчетов
reports_folder = "отчеты"
if not os.path.exists(reports_folder):
    os.makedirs(reports_folder)

@app.route('/')
def index():
    try:
        df = pd.read_excel("список_картриджей.xlsx")
        data = df.to_dict(orient='records')
        print(data)
    except Exception as e:
        print("Ошибка чтения файла Excel:", e)
        data = None
    return render_template('index.html', data=data)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        df = pd.read_excel("список_картриджей.xlsx")
        
        selected_rows = []
        for index, row in df.iterrows():
            quantity_taken_str = request.form.get(f"quantity_taken_{index}", '')
            quantity_taken = int(quantity_taken_str) if quantity_taken_str else 0
            if quantity_taken > 0:
                selected_rows.append({'Картридж': row['Картридж'], 'Организация': row['Организация'], 'Было': row['Было'], 'Сколько взяли': quantity_taken, 'Время взятия': datetime.now()})
                df.at[index, 'Количество'] = max(row['Количество'] - quantity_taken, 0)

        new_df = pd.DataFrame(selected_rows)
        
        current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_path = os.path.join(chosen_folder, f"выбранные_картриджи_{current_date}.xlsx")
        new_df.to_excel(file_path, index=False)
        
        try:
            df.to_excel("список_картриджей.xlsx", index=False)
            print("Данные успешно обновлены и записаны в основной файл.")
        except Exception as e:
            print(f"Произошла ошибка при обновлении основного файла Excel: {e}")
        
        return redirect(url_for('index'))
    except Exception as e:
        return f"Произошла ошибка при обновлении файла Excel: {e}"

@app.route('/create_report', methods=['POST'])
def create_report():
    try:
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        files = []
        for file_name in os.listdir(chosen_folder):
            if file_name.startswith("выбранные_картриджи_") and file_name.endswith(".xlsx"):
                file_date = datetime.strptime(file_name.split('_')[2].split('.')[0], '%Y-%m-%d')
                if start_date <= file_date <= end_date:
                    files.append(os.path.join(chosen_folder, file_name))
        
        print("Найденные файлы:", files)
        
        if not files:
            return "Нет данных за выбранный период для создания отчета."
        
        dataframes = [pd.read_excel(file) for file in files]
        df_combined = pd.concat(dataframes, ignore_index=True)
        
        report_filename = f"отчет_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        report_file_path = os.path.join("отчеты", report_filename)
        df_combined.to_excel(report_file_path, index=False)
        
        return send_file(report_file_path, as_attachment=True)

    except Exception as e:
        return f"Произошла ошибка при создании отчета: {e}"

if __name__ == '__main__':
    app.run(debug=True)
