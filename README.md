# Каталог компьютерного оборудования

Приложение по ООП — 2 курс, Python + Flet.

## Файлы проекта

- **main.py** — запуск приложения, экран входа и свои UI-компоненты.
- **models.py** — классы `BaseHardwareEntity`, `Processor`, `GraphicsCard`, `RAM`, `HardwareMapper`, `Validation`, `HardwareFactory`, `HardwareCatalog`, `DemoData`.
- **session.py** — класс `SessionLogger`, записывает отчёт о сессии.
- **requirements.txt** — зависимости.

## Как запустить

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Версия Flet закреплена — 0.28.3. При первом запуске Flet скачивает клиент окна, поэтому нужен интернет.

## Что умеет

- вход по логину и паролю — `admin_admin` / `admin_admin`
- 12 стартовых товаров в трёх категориях: процессоры, видеокарты, оперативная память
- поиск по названию, артикулу и характеристикам
- фильтр по категории и максимальной цене
- сортировка по цене и по названию
- добавление и удаление товаров
- сводка «показано / всего» и общая стоимость показанных товаров
- при выходе в `sessions.txt` дописывается отчёт — логин, время входа и выхода

## Про ООП

- абстрактный класс `BaseHardwareEntity`, от которого наследуются `Processor`, `GraphicsCard` и `RAM`
- собственный класс `HardwareMapper` вместо обычного словаря — реализует `MutableMapping`
- переопределённые магические методы: `__eq__`, `__lt__`, `__gt__`, `__add__`, `__len__`, `__str__`, `__repr__`
- геттеры и сеттеры с валидацией через класс `Validation`
- фабрика `HardwareFactory`, создающая объекты по категории
- свои UI-компоненты в `main.py`: `AppTitle`, `SearchField`, `CategoryDropdown`, `SortDropdown`, `PriceField`, `ActionButton`, `StatusText`, `SummaryText`, `FormField`, `LoginView`, `HardwareCard`, `CatalogList`, `FiltersPanel`, `EditorPanel`
