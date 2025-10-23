# Адаптация скриптов для Linux

## Выполненные изменения

### 1. `src/main/python/utils/utils.py`
- Заменил `filename.split('/')[-1]` на `os.path.basename(filename)` для кроссплатформенной работы

### 2. `src/main/python/image_slicer/image_slicer.py`
- Заменил конкатенацию строк на `os.path.join()` для создания путей
- Обновил импорт для использования `IMAGES_FOLDER` из конфигурации
- Исправил создание путей к изображениям

### 3. `src/main/python/image_slicer/visualize_slicing.py`
- Файл уже был совместим с Linux (использовал `os.path.basename`)

### 4. `src/main/python/model/yolo.py`
- Заменил все Windows-специфичные разделители путей на `os.path.join()`
- Исправил `prediction.path.split('\\')[-1]` на `os.path.basename(prediction.path)`
- Убрал `.replace('\\', '/')` и заменил на `os.path.splitext()`
- Обновил все пути для кроссплатформенной работы

### 5. `src/main/python/iou_filter/iou_filter.py`
- Заменил `boxes['source_image_path'].split('/')[-1]` на `os.path.basename()`
- Добавил импорт `os` в функцию

### 6. `src/main/python/outlier_filter/outlier_filter.py`
- Полностью переписал функцию `filter_outliers()` для исправления синтаксических ошибок
- Добавил правильные импорты и документацию
- Сделал функцию более надежной с проверками на пустые списки

### 7. `src/main/resources/config.py`
- Добавил импорт `os`
- Добавил Linux-совместимые пути:
  - `DATASET_FOLDER = "dataset"`
  - `IMAGES_FOLDER = os.path.join(DATASET_FOLDER, "0.0.1", "АФС для обработки ИИ")`

## Основные принципы адаптации

1. **Использование `os.path.join()`** вместо конкатенации строк с разделителями
2. **Использование `os.path.basename()`** вместо `split('/')[-1]`
3. **Использование `os.path.splitext()`** для работы с расширениями файлов
4. **Удаление Windows-специфичных замен** типа `.replace('\\', '/')`
5. **Добавление кроссплатформенных путей** в конфигурацию

## Результат

Все скрипты теперь полностью совместимы с Linux и будут корректно работать на обеих платформах (Windows и Linux) без дополнительных изменений.
