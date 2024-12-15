from flask import Flask, render_template, request, redirect
from models import db, Array
from sorting_lib.shell_sort import shell_sort
from sorting_lib.data_loader import random_arr

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация базы данных
db.init_app(app)

@app.before_request
def init_db():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sort', methods=['POST'])
def sort():
    if request.method == 'POST':
        array = request.form['array']
        reverse = request.form.get('reverse', 'false') == 'true'
        array = list(map(int, array.split()))  # Преобразуем строку в список чисел
        
        original_array = array.copy()  # Делаем копию оригинального массива
        sorted_array = shell_sort(array, reverse=reverse)  # Сортируем массив

        # Сохраняем в базу данных
        new_record = Array(
            original_array=" ".join(map(str, original_array)),  # Сохраняем оригинал
            sorted_array=" ".join(map(str, sorted_array))       # Сохраняем результат
        )
        db.session.add(new_record)
        db.session.commit()

        return render_template('result.html', original=original_array, sorted=sorted_array)


@app.route('/random', methods=['POST'])
def generate_random():
    try:
        size = int(request.form.get('size', 10))  # Размер массива из формы
        random_array = random_arr(size)          # Генерация массива
        return render_template('index.html', array=" ".join(map(str, random_array)))
    except ValueError:
        return render_template('index.html', error="Введите корректное число для размера массива.")

@app.route('/clear_history', methods=['POST'])
def clear_history():
    Array.query.delete()  # Удаляет все записи из таблицы Array
    db.session.commit()   # Применяет изменения в базе данных
    return redirect('/history')  # Перенаправляет обратно на страницу истории


import time

@app.route('/test_results', methods=['POST'])
def test_results():
    if request.method == 'POST':
        # Получаем размер массива из формы
        test_size = int(request.form['test_size'])

        # Генерируем случайный массив
        test_array = random_arr(test_size)
        reverse = False  # Сортируем по возрастанию

        # Точное измерение времени с помощью timeit
        import timeit
        execution_time = timeit.timeit(
            stmt=lambda: shell_sort(test_array.copy(), reverse=reverse),
            number=1  # Количество запусков сортировки
        )

        # Округляем до 6 знаков после запятой (или больше, если нужно)
        execution_time = round(execution_time, 10)

        # Сортируем массив
        sorted_array = shell_sort(test_array.copy(), reverse=reverse)

        # Передаём данные на страницу с результатами
        return render_template(
            'test_results.html',
            test_size=test_size,
            execution_time=execution_time,
            original=test_array,
            sorted=sorted_array
        )



@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/history')
def history():
    # Загружаем историю сортировок из базы данных
    records = Array.query.all()
    return render_template('history.html', records=records)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
