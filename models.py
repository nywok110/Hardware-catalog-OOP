from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from decimal import Decimal, InvalidOperation


class HardwareMapper(MutableMapping):
    """Маппинг с хранением пар в списке, без стандартного словаря."""

    def __init__(self):
        self._pairs = []

    def __getitem__(self, key):
        for stored_key, value in self._pairs:
            if stored_key == key:
                return value
        raise KeyError(key)

    def __setitem__(self, key, value):
        for index, pair in enumerate(self._pairs):
            if pair[0] == key:
                self._pairs[index] = (key, value)
                return
        self._pairs.append((key, value))

    def __delitem__(self, key):
        for index, pair in enumerate(self._pairs):
            if pair[0] == key:
                self._pairs.pop(index)
                return
        raise KeyError(key)

    def __iter__(self):
        for key, _ in self._pairs:
            yield key

    def __len__(self):
        return len(self._pairs)

    def put(self, key, value):
        self[key] = value

    def __repr__(self):
        return f"HardwareMapper({self._pairs!r})"


class Validation:
    @staticmethod
    def text(value, field):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field}: введите непустую строку.")
        return value.strip()

    @staticmethod
    def money(value):
        try:
            result = Decimal(str(value).strip().replace(",", "."))
        except (InvalidOperation, ValueError):
            raise ValueError("Цена должна быть числом.") from None

        if not result.is_finite() or result < 0:
            raise ValueError("Цена должна быть конечным неотрицательным числом.")

        if result > Decimal("999999999"):
            raise ValueError("Цена не должна превышать 999 999 999 ₽.")

        return result.quantize(Decimal("0.01"))

    @staticmethod
    def positive_integer(value, field):
        if isinstance(value, bool):
            raise ValueError(f"{field}: требуется положительное целое число.")

        if not isinstance(value, (str, int)):
            raise ValueError(f"{field}: требуется положительное целое число.")

        try:
            result = int(value)
        except (ValueError, TypeError):
            raise ValueError(
                f"{field}: требуется положительное целое число."
            ) from None

        if result <= 0:
            raise ValueError(f"{field}: значение должно быть больше нуля.")

        return result


class BaseHardwareEntity(ABC):
    def __init__(self, sku, name, price):
        self.sku = sku
        self.name = name
        self.price = price

    @property
    def sku(self):
        return self._sku

    @sku.setter
    def sku(self, value):
        self._sku = Validation.text(value, "Артикул")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = Validation.text(value, "Название")

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = Validation.money(value)

    @property
    @abstractmethod
    def category(self):
        pass

    @abstractmethod
    def get_info(self):
        pass

    @abstractmethod
    def specification_key(self):
        """Характеристики, участвующие в сравнении."""
        pass

    def comparison_key(self):
        return (
            self.price,
            self.category,
            self.sku,
            self.name,
            self.specification_key(),
        )

    def __eq__(self, other):
        if not isinstance(other, BaseHardwareEntity):
            return NotImplemented
        return self.comparison_key() == other.comparison_key()

    def __lt__(self, other):
        if not isinstance(other, BaseHardwareEntity):
            return NotImplemented
        return self.comparison_key() < other.comparison_key()

    def __gt__(self, other):
        if not isinstance(other, BaseHardwareEntity):
            return NotImplemented
        return self.comparison_key() > other.comparison_key()

    def __add__(self, other):
        if not isinstance(other, BaseHardwareEntity):
            return NotImplemented
        return self.price + other.price

    def __len__(self):
        return len(self.name)

    def __str__(self):
        return f"{self.name} — {self.price:,.2f} ₽"

    def __repr__(self):
        return (
            f"{type(self).__name__}("
            f"sku={self.sku!r}, name={self.name!r}, "
            f"price={str(self.price)!r}, "
            f"specification={self.specification_key()!r})"
        )


class Processor(BaseHardwareEntity):
    def __init__(self, sku, name, price, cores):
        super().__init__(sku, name, price)
        self.cores = cores

    @property
    def category(self):
        return "Процессоры"

    @property
    def cores(self):
        return self._cores

    @cores.setter
    def cores(self, value):
        self._cores = Validation.positive_integer(value, "Количество ядер")

    def get_info(self):
        return f"Ядер: {self.cores}"

    def specification_key(self):
        return (self.cores,)

    def __eq__(self, other):
        return super().__eq__(other)

    def __lt__(self, other):
        return super().__lt__(other)

    def __gt__(self, other):
        return super().__gt__(other)

    def __add__(self, other):
        return super().__add__(other)

    def __len__(self):
        return super().__len__()

    def __str__(self):
        return f"Процессор: {super().__str__()}"

    def __repr__(self):
        return super().__repr__()


class GraphicsCard(BaseHardwareEntity):
    def __init__(self, sku, name, price, memory_gb):
        super().__init__(sku, name, price)
        self.memory_gb = memory_gb

    @property
    def category(self):
        return "Видеокарты"

    @property
    def memory_gb(self):
        return self._memory_gb

    @memory_gb.setter
    def memory_gb(self, value):
        self._memory_gb = Validation.positive_integer(
            value, "Объём видеопамяти"
        )

    def get_info(self):
        return f"Видеопамять: {self.memory_gb} ГБ"

    def specification_key(self):
        return (self.memory_gb,)

    def __eq__(self, other):
        return super().__eq__(other)

    def __lt__(self, other):
        return super().__lt__(other)

    def __gt__(self, other):
        return super().__gt__(other)

    def __add__(self, other):
        return super().__add__(other)

    def __len__(self):
        return super().__len__()

    def __str__(self):
        return f"Видеокарта: {super().__str__()}"

    def __repr__(self):
        return super().__repr__()


class RAM(BaseHardwareEntity):
    def __init__(self, sku, name, price, capacity_gb):
        super().__init__(sku, name, price)
        self.capacity_gb = capacity_gb

    @property
    def category(self):
        return "Оперативная память"

    @property
    def capacity_gb(self):
        return self._capacity_gb

    @capacity_gb.setter
    def capacity_gb(self, value):
        self._capacity_gb = Validation.positive_integer(
            value, "Объём оперативной памяти"
        )

    def get_info(self):
        return f"Объём: {self.capacity_gb} ГБ"

    def specification_key(self):
        return (self.capacity_gb,)

    def __eq__(self, other):
        return super().__eq__(other)

    def __lt__(self, other):
        return super().__lt__(other)

    def __gt__(self, other):
        return super().__gt__(other)

    def __add__(self, other):
        return super().__add__(other)

    def __len__(self):
        return super().__len__()

    def __str__(self):
        return f"Оперативная память: {super().__str__()}"

    def __repr__(self):
        return super().__repr__()


class HardwareFactory:
    def __init__(self):
        self._types = HardwareMapper()
        self._types["Процессоры"] = Processor
        self._types["Видеокарты"] = GraphicsCard
        self._types["Оперативная память"] = RAM

    @property
    def categories(self):
        return list(self._types)

    def create(self, category, sku, name, price, specification):
        entity_class = self._types.get(category)

        if entity_class is None:
            raise ValueError("Выберите существующую категорию.")

        return entity_class(sku, name, price, specification)


class HardwareCatalog:
    ALL = "Все категории"
    SORT_ASC = "Цена ↑"
    SORT_DESC = "Цена ↓"
    SORT_NAME = "Название"

    def __init__(self, categories):
        self._groups = HardwareMapper()

        for category in categories:
            self._groups[category] = []

    @property
    def items(self):
        result = []

        for category in self._groups:
            result.extend(self._groups[category])

        return result

    def add(self, entity):
        if not isinstance(entity, BaseHardwareEntity):
            raise TypeError("В каталог можно добавлять только комплектующие.")

        if entity.category not in self._groups:
            raise ValueError("Неизвестная категория.")

        if any(
            item.sku.casefold() == entity.sku.casefold()
            for item in self.items
        ):
            raise ValueError("Товар с таким артикулом уже существует.")

        self._groups[entity.category].append(entity)

    def remove(self, sku):
        for category in self._groups:
            group = self._groups[category]

            for index, item in enumerate(group):
                if item.sku == sku:
                    return group.pop(index)

        raise ValueError("Товар не найден.")

    def search(self, query="", category=ALL, max_price=None, sort=SORT_ASC):
        source = (
            self.items
            if category == self.ALL
            else list(self._groups.get(category, []))
        )

        query = query.strip().casefold()
        result = []

        for item in source:
            searchable_text = (
                f"{item.sku} {item.name} {item.category} {item.get_info()}"
            ).casefold()

            if query and query not in searchable_text:
                continue

            if max_price is not None and item.price > max_price:
                continue

            result.append(item)

        if sort == self.SORT_NAME:
            result.sort(key=self.name_key)
        else:
            result.sort(reverse=sort == self.SORT_DESC)

        return result

    @staticmethod
    def name_key(item):
        return item.name.casefold()

    @staticmethod
    def total_price(items):
        return sum((item.price for item in items), Decimal("0.00"))

    def __len__(self):
        return len(self.items)


class DemoData:
    @staticmethod
    def create():
        return [
            Processor("CPU-001", "AMD Ryzen 5 5600", 11990, 6),
            Processor("CPU-002", "Intel Core i5-12400F", 13990, 6),
            Processor("CPU-003", "AMD Ryzen 7 5700X", 18990, 8),
            Processor("CPU-004", "Intel Core i7-12700", 27990, 12),

            GraphicsCard("GPU-001", "GeForce RTX 3060", 29990, 12),
            GraphicsCard("GPU-002", "GeForce RTX 4060", 35990, 8),
            GraphicsCard("GPU-003", "Radeon RX 6600", 22990, 8),
            GraphicsCard("GPU-004", "Radeon RX 7800 XT", 57990, 16),

            RAM("RAM-001", "Kingston Fury Beast DDR4", 3990, 16),
            RAM("RAM-002", "Corsair Vengeance DDR4", 6990, 32),
            RAM("RAM-003", "ADATA XPG Lancer DDR5", 8990, 32),
            RAM("RAM-004", "Crucial DDR5", 15990, 64),
        ]