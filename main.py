import atexit
from functools import partial
from pathlib import Path

import flet as ft

from models import (
    DemoData,
    HardwareCatalog,
    HardwareFactory,
    Validation,
)
from session import SessionLogger


CREDENTIALS = {"login": "admin_admin", "password": "admin_admin"}


class AppTitle(ft.Text):
    def __init__(self):
        super().__init__(
            value="Каталог компьютерного оборудования",
            size=26,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_800,
        )


class SearchField(ft.TextField):
    def __init__(self, on_change):
        super().__init__(
            label="Поиск по названию, артикулу и характеристикам",
            prefix_icon=ft.Icons.SEARCH,
            on_change=on_change,
            expand=True,
            border_radius=10,
        )


class CategoryDropdown(ft.Dropdown):
    def __init__(self, categories, on_change=None, include_all=False):
        values = list(categories)

        if include_all:
            values.insert(0, HardwareCatalog.ALL)

        super().__init__(
            label="Категория",
            value=values[0],
            options=[ft.dropdown.Option(value) for value in values],
            on_change=on_change,
            width=240,
            border_radius=10,
        )


class SortDropdown(ft.Dropdown):
    def __init__(self, on_change):
        super().__init__(
            label="Сортировка",
            value=HardwareCatalog.SORT_ASC,
            options=[
                ft.dropdown.Option(HardwareCatalog.SORT_ASC),
                ft.dropdown.Option(HardwareCatalog.SORT_DESC),
                ft.dropdown.Option(HardwareCatalog.SORT_NAME),
            ],
            on_change=on_change,
            width=170,
            border_radius=10,
        )


class PriceField(ft.TextField):
    def __init__(self, label, on_change=None):
        super().__init__(
            label=label,
            suffix_text="₽",
            width=190,
            on_change=on_change,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_radius=10,
        )


class ActionButton(ft.ElevatedButton):
    def __init__(self, text, icon, on_click):
        super().__init__(
            text=text,
            icon=icon,
            on_click=on_click,
            height=42,
        )


class StatusText(ft.Text):
    def __init__(self):
        super().__init__(
            value="Каталог готов к работе.",
            size=13,
            color=ft.Colors.GREEN_800,
            selectable=True,
        )

    def show_message(self, message, error=False):
        self.value = message
        self.color = ft.Colors.RED_700 if error else ft.Colors.GREEN_800


class SummaryText(ft.Text):
    def __init__(self):
        super().__init__(
            value="",
            size=15,
            weight=ft.FontWeight.BOLD,
        )

    def set_summary(self, visible_count, total_count, total_price):
        self.value = (
            f"Показано: {visible_count} из {total_count}   •   "
            f"Стоимость показанных товаров: {total_price:,.2f} ₽"
        )


class FormField(ft.TextField):
    def __init__(self, label, width=220):
        super().__init__(
            label=label,
            width=width,
            border_radius=10,
        )


class LoginView(ft.Container):
    def __init__(self, on_login):
        self._on_login = on_login

        self._login_field = FormField("Логин", width=280)
        self._password_field = ft.TextField(
            label="Пароль",
            password=True,
            can_reveal_password=True,
            width=280,
            border_radius=10,
            on_submit=self._submit,
        )
        self._error = ft.Text(value="", color=ft.Colors.RED_700, size=13)

        super().__init__(
            expand=True,
            alignment=ft.alignment.center,
            content=ft.Container(
                width=360,
                padding=24,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
                border_radius=12,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            ft.Icons.LOCK_OUTLINE,
                            size=40,
                            color=ft.Colors.BLUE_800,
                        ),
                        ft.Text(
                            "Вход в систему",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        self._login_field,
                        self._password_field,
                        self._error,
                        ActionButton(
                            "Войти",
                            ft.Icons.LOGIN,
                            self._submit,
                        ),
                    ],
                    spacing=14,
                ),
            ),
        )

    async def _submit(self, event):
        if (
            self._login_field.value == CREDENTIALS["login"]
            and self._password_field.value == CREDENTIALS["password"]
        ):
            self._on_login(self._login_field.value)
            return

        self._error.value = "Неверный логин или пароль."
        self._password_field.value = ""
        self.page.update()


class HardwareCard(ft.Container):
    def __init__(self, item, on_delete):
        super().__init__(
            padding=16,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
            border_radius=12,
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.MEMORY,
                        size=34,
                        color=ft.Colors.BLUE_700,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                item.name,
                                size=17,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text(
                                f"{item.category} • {item.sku}",
                                color=ft.Colors.BLUE_GREY_600,
                            ),
                            ft.Text(item.get_info()),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.Text(
                        f"{item.price:,.2f} ₽",
                        size=17,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_600,
                        tooltip="Удалить товар",
                        on_click=on_delete,
                    ),
                ],
                spacing=16,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )


class CatalogList(ft.ListView):
    def __init__(self):
        super().__init__(
            expand=True,
            spacing=10,
            padding=4,
        )

    def set_items(self, items, on_delete):
        self.controls.clear()

        if not items:
            self.controls.append(
                ft.Container(
                    content=ft.Text(
                        "По заданным условиям ничего не найдено.",
                        size=17,
                    ),
                    padding=30,
                    alignment=ft.alignment.center,
                )
            )
            return

        for item in items:
            self.controls.append(
                HardwareCard(
                    item,
                    partial(on_delete, item.sku),
                )
            )


class FiltersPanel(ft.Container):
    def __init__(self, search, category, sort, price, reset):
        super().__init__(
            padding=16,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[search],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Row(
                        controls=[category, sort, price, reset],
                        spacing=12,
                        run_spacing=12,
                        wrap=True,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=12,
            ),
        )


class EditorPanel(ft.Container):
    def __init__(
        self,
        category,
        sku,
        name,
        price,
        specification,
        add_button,
    ):
        super().__init__(
            padding=16,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Добавить комплектующее",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        controls=[category, sku, name],
                        spacing=12,
                        run_spacing=12,
                        wrap=True,
                    ),
                    ft.Row(
                        controls=[price, specification, add_button],
                        spacing=12,
                        run_spacing=12,
                        wrap=True,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=12,
            ),
        )


class HardwareApplication:
    def __init__(self, page, login):
        self._page = page
        self._factory = HardwareFactory()
        self._catalog = HardwareCatalog(self._factory.categories)
        self._closing = False

        report_path = Path(__file__).resolve().parent / "sessions.txt"
        self._session = SessionLogger(login, report_path)

        for item in DemoData.create():
            self._catalog.add(item)

        self._configure_window()
        self._create_controls()
        self._build_layout()
        self._refresh()

        atexit.register(self._save_on_interpreter_exit)

    @property
    def page(self):
        return self._page

    def _configure_window(self):
        self.page.title = "Hardware Catalog"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.bgcolor = ft.Colors.BLUE_GREY_50
        self.page.padding = 20

        self.page.window.width = 1180
        self.page.window.height = 900
        self.page.window.min_width = 950
        self.page.window.min_height = 820

        self.page.window.prevent_close = True
        self.page.window.on_event = self._on_window_event

    def _create_controls(self):
        self._title = AppTitle()
        self._status = StatusText()
        self._summary = SummaryText()
        self._list = CatalogList()

        self._search = SearchField(self._on_filters_changed)
        self._category = CategoryDropdown(
            self._factory.categories,
            on_change=self._on_filters_changed,
            include_all=True,
        )
        self._sort = SortDropdown(self._on_filters_changed)
        self._max_price = PriceField(
            "Максимальная цена",
            on_change=self._on_filters_changed,
        )
        self._reset_button = ActionButton(
            "Сбросить",
            ft.Icons.RESTART_ALT,
            self._reset_filters,
        )

        self._new_category = CategoryDropdown(
            self._factory.categories,
            on_change=self._on_editor_category_changed,
        )
        self._new_sku = FormField("Артикул", width=180)
        self._new_name = FormField("Название модели", width=350)
        self._new_price = PriceField("Цена")
        self._new_specification = FormField("Количество ядер", width=240)

        self._add_button = ActionButton(
            "Добавить",
            ft.Icons.ADD,
            self._add_item,
        )
        self._exit_button = ActionButton(
            "Сохранить отчёт и выйти",
            ft.Icons.EXIT_TO_APP,
            self._close,
        )

    def _build_layout(self):
        filters = FiltersPanel(
            self._search,
            self._category,
            self._sort,
            self._max_price,
            self._reset_button,
        )

        editor = EditorPanel(
            self._new_category,
            self._new_sku,
            self._new_name,
            self._new_price,
            self._new_specification,
            self._add_button,
        )

        self.page.add(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self._title,
                            ft.Text(
                                f"Пользователь: {self._session.login}",
                                color=ft.Colors.BLUE_GREY_700,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    filters,
                    editor,
                    self._summary,
                    self._list,
                    ft.Divider(height=1),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=self._status,
                                expand=True,
                            ),
                            self._exit_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=14,
                expand=True,
            )
        )

    def _refresh(self):
        self._max_price.error_text = None
        raw_max_price = (self._max_price.value or "").strip()

        try:
            max_price = (
                Validation.money(raw_max_price)
                if raw_max_price
                else None
            )
        except ValueError as error:
            self._max_price.error_text = str(error)
            self._status.show_message(
                "Исправьте максимальную цену. Список пока не обновлён.",
                error=True,
            )
            self.page.update()
            return

        items = self._catalog.search(
            query=self._search.value or "",
            category=self._category.value,
            max_price=max_price,
            sort=self._sort.value,
        )

        self._list.set_items(items, self._delete_item)
        self._summary.set_summary(
            len(items),
            len(self._catalog),
            self._catalog.total_price(items),
        )
        self.page.update()

    async def _on_filters_changed(self, event):
        self._status.show_message("Фильтры применены.")
        self._refresh()

    def _clear_filters(self):
        self._search.value = ""
        self._category.value = HardwareCatalog.ALL
        self._sort.value = HardwareCatalog.SORT_ASC
        self._max_price.value = ""
        self._max_price.error_text = None

    async def _reset_filters(self, event):
        self._clear_filters()
        self._status.show_message("Фильтры сброшены.")
        self._refresh()

    async def _on_editor_category_changed(self, event):
        category = self._new_category.value

        if category == "Процессоры":
            self._new_specification.label = "Количество ядер"
        elif category == "Видеокарты":
            self._new_specification.label = "Видеопамять, ГБ"
        else:
            self._new_specification.label = "Объём ОЗУ, ГБ"

        self._new_specification.value = ""
        self.page.update()

    async def _add_item(self, event):
        try:
            item = self._factory.create(
                category=self._new_category.value,
                sku=self._new_sku.value or "",
                name=self._new_name.value or "",
                price=self._new_price.value or "",
                specification=self._new_specification.value or "",
            )
            self._catalog.add(item)
        except (ValueError, TypeError) as error:
            self._status.show_message(str(error), error=True)
            self.page.update()
            return

        self._new_sku.value = ""
        self._new_name.value = ""
        self._new_price.value = ""
        self._new_specification.value = ""

        self._clear_filters()
        self._status.show_message(f"Добавлен товар: {item.name}.")
        self._refresh()

    async def _delete_item(self, sku, event):
        try:
            removed = self._catalog.remove(sku)
        except ValueError as error:
            self._status.show_message(str(error), error=True)
            self.page.update()
            return

        if self._max_price.error_text:
            self._max_price.value = ""
            self._max_price.error_text = None

        self._status.show_message(f"Удалён товар: {removed.name}.")
        self._refresh()

    async def _on_window_event(self, event):
        if event.data == "close":
            await self._close(event)

    async def _close(self, event=None):
        if self._closing:
            return

        self._closing = True

        try:
            self._session.finish()
        except OSError as error:
            self._closing = False
            self._status.show_message(
                f"Не удалось записать отчёт: {error}. "
                "Проверьте права доступа и повторите закрытие.",
                error=True,
            )
            self.page.update()
            return

        try:
            await self.page.window.destroy()
        except Exception:
            self._closing = False
            raise

    def _save_on_interpreter_exit(self):
        try:
            self._session.finish()
        except OSError as error:
            print(f"Ошибка резервной записи отчёта: {error}")


async def main(page: ft.Page):
    page.title = "Hardware Catalog — вход"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.padding = 20

    page.window.width = 1180
    page.window.height = 900
    page.window.min_width = 950
    page.window.min_height = 820

    def start_app(login):
        page.controls.clear()
        HardwareApplication(page, login)

    page.add(LoginView(start_app))


if __name__ == "__main__":
    ft.app(target=main)