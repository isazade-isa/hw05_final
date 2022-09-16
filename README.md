# Социальная сеть YaTube

## Описание:  
Предоставляет пользователям возможность создать учетную запись, публиковать записи, подписываться на любимых авторов и комментировать понравившиеся записи.

Stacks:
* Python 3.7
* Django framework
* HTML+CSS (Bootstrap)
* jwt token authorize
* Pillow
* sorl-thumbnail
* unittest (Unit test framework)

### Покрытие тестами
Покрытие тестами выполнено при помощи unittest(Unit test framework)
Тесты находятся в папке `./yatube/posts/test/`. Модуль теста начинается со слова `test_`. Тесты покрывают следующие области:

- тесты кэширования страниц 
- тесты комментариев
- тесты следования и подписок на авторов
- тесты форм
- тесты загрузки изображений
- тесты моделей базы данных
- тесты URL проекта
- тесты view функций

Каждому тесту соответствует отдельный файл.

## Запуск проекта:

Клонируйте репозиторий и перейти в него в командной строке: 

    git clone https://github.com/isazade-isa/hw05_final.git

Установите и активируйте виртуальное окружение: 

    python -m venv venv 
    source venv/Scripts/activate

Установите зависимости из файла requirements.txt:   
    
    pip install -r requirements.txt

Выполните миграции: 

    python manage.py migrate

В папке с файлом manage.py выполните команду:  

    python manage.py runserver
