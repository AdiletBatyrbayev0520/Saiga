# Руководство по визуализации изображений с боксами

## Обзор

Этот модуль предоставляет функции для создания визуализации изображений с нарисованными боксами, используя отфильтрованные боксы и оригинальные изображения.

## Основные функции

### 1. `draw_bounding_boxes_on_image()`
Рисует боксы на одном изображении и сохраняет результат.

**Параметры:**
- `image_path`: Путь к исходному изображению
- `boxes`: Список боксов в формате [x1, y1, x2, y2]
- `output_path`: Путь для сохранения результата
- `box_color`: Цвет боксов (по умолчанию "red")
- `box_width`: Толщина линий боксов (по умолчанию 3)
- `label`: Подпись для боксов (по умолчанию "saiga")
- `font_size`: Размер шрифта (по умолчанию 20)

### 2. `create_visualization_from_filtered_boxes()`
Создает визуализацию для всех изображений в папке с отфильтрованными боксами.

**Параметры:**
- `original_images_folder`: Папка с оригинальными изображениями
- `filtered_boxes_list`: Список отфильтрованных боксов
- `output_folder`: Папка для сохранения результатов
- `box_color`: Цвет боксов
- `box_width`: Толщина линий боксов
- `label`: Подпись для боксов

### 3. `create_single_image_visualization()`
Создает визуализацию для одного конкретного изображения.

### 4. `create_comparison_visualization()`
Создает сравнительную визуализацию оригинальных и отфильтрованных боксов.

## Примеры использования

### Пример 1: Визуализация всех изображений
```python
from src.main.python.utils.visualization import create_visualization_from_filtered_boxes

create_visualization_from_filtered_boxes(
    original_images_folder="dataset/0.0.1/АФС для обработки ИИ/",
    filtered_boxes_list=filtered_boxes_list,
    output_folder="visualized_images_with_boxes",
    box_color="red",
    box_width=3,
    label="saiga"
)
```

### Пример 2: Визуализация одного изображения
```python
from src.main.python.utils.visualization import create_single_image_visualization

create_single_image_visualization(
    image_path="dataset/0.0.1/АФС для обработки ИИ/image.jpg",
    filtered_boxes_list=filtered_boxes_list,
    output_path="single_visualization.jpg",
    box_color="green",
    box_width=4
)
```

### Пример 3: Прямое рисование боксов
```python
from src.main.python.utils.visualization import draw_bounding_boxes_on_image

boxes = [[100, 100, 200, 200], [300, 150, 400, 250]]
draw_bounding_boxes_on_image(
    image_path="image.jpg",
    boxes=boxes,
    output_path="result.jpg",
    box_color="yellow",
    box_width=5
)
```

## Формат данных

### Отфильтрованные боксы (filtered_boxes_list)
Список словарей, где каждый словарь содержит:
```python
{
    'source_image_path': 'путь/к/изображению.png',
    'coordinates': [[x1, y1, x2, y2], [x1, y1, x2, y2], ...]
}
```

### Координаты боксов
Каждый бокс представлен как список из 4 чисел: [x1, y1, x2, y2], где:
- (x1, y1) - левый верхний угол
- (x2, y2) - правый нижний угол

## Поддерживаемые форматы изображений
- JPG/JPEG
- PNG
- Другие форматы, поддерживаемые PIL

## Настройка внешнего вида

### Цвета боксов
Можно использовать:
- Названия цветов: "red", "blue", "green", "yellow", "purple", "orange"
- HEX коды: "#FF0000", "#00FF00"
- RGB значения: (255, 0, 0)

### Размеры
- `box_width`: Толщина линий боксов (1-10)
- `font_size`: Размер шрифта для подписей (10-50)

## Интеграция с существующим кодом

Функции легко интегрируются с вашим существующим pipeline:

```python
# После получения filtered_boxes_list из вашего кода
create_visualization_from_filtered_boxes(
    original_images_folder="dataset/0.0.1/АФС для обработки ИИ/",
    filtered_boxes_list=filtered_boxes_list,
    output_folder="results_visualization"
)
```

Это создаст визуализированные изображения для всех ваших данных с нарисованными боксами.
