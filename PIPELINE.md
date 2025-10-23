# 🔄 Пайплайн обработки проекта Saiga

Полное описание процесса обработки изображений от исходных данных до финальных результатов.

## 📋 Общая схема пайплайна

```
Исходные изображения → Разбиение на фрагменты → YOLO детекция → IoU фильтрация → Фильтрация выбросов → Финальные результаты
```

### 🔄 Визуальная схема пайплайна:

```
📁 dataset/0.0.1/АФС для обработки ИИ/
    ↓ (211 JPG файлов)
🔧 image_slicer.py
    ↓ (разбиение на фрагменты 640×640, перекрытие 20%)
📁 slices/
    ↓ (10,000+ PNG фрагментов)
🧠 yolo.py (best_4.pt)
    ↓ (YOLO детекция, confidence=0.5)
📁 predicted_images_with_annotations-best_4-0.5/
    ↓ (PNG + TXT аннотации)
🔄 iou_filter.py
    ↓ (удаление дубликатов, IoU=0.5)
📁 iou_filtered-best_4-0.5/
    ↓ (очищенные от дубликатов)
🎯 outlier_filter.py
    ↓ (удаление выбросов, K=3)
📁 outlier_filtered-best_4-0.5/
    ↓ (финальные результаты)
📊 results_*.jpg
    ↓ (визуализация с детекциями)
```

## 🎯 Детальный пайплайн по этапам

### **ЭТАП 1: Подготовка данных** 📁

#### Входные данные:
- **Папка**: `dataset/0.0.1/АФС для обработки ИИ/`
- **Формат**: `.JPG` файлы (211 изображений)
- **Размер**: Высокое разрешение аэрофотоснимков

#### Процесс:
```python
# Запуск разбиения изображений
python src/main/python/image_slicer/image_slicer.py
```

#### Выходные данные:
- **Папка**: `slices/` или `slices-2/`
- **Структура**: `slices/{имя_изображения}/`
- **Файлы**: 
  - `{имя}_slice_{row:03d}_{col:03d}_{left}_{top}.png` - фрагменты изображений
- **Параметры**: 
  - Размер фрагмента: 640×640 пикселей
  - Перекрытие: 20%
  - Формат: PNG

**Пример структуры:**
```
slices/
├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090/
│   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.png
│   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_001_512_0.png
│   └── ...
└── 2025_08_05_PhotoRieboR4_g201b201078_f003_091/
    ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_091_slice_000_000_0_0.png
    └── ...
```

---

### **ЭТАП 2: YOLO детекция** 🧠

#### Входные данные:
- **Папка**: `slices/` (фрагменты изображений)
- **Модель**: `best_4.pt` (обученная модель YOLO11)
- **Конфигурация**: `CONFIDENCE_THRESHOLD = 0.5`

#### Процесс:
```python
# Запуск детекции
from src.main.python.model.yolo import process_folders
process_folders(slices_folder, models, devices, output_folder)
```

#### Выходные данные:
- **Папка**: `predicted_images_with_annotations-{model_name}-{confidence}/`
- **Структура**: `predicted_images_with_annotations-best_4-0.5/`
- **Файлы**:
  - `{имя}_slice_{row:03d}_{col:03d}_{left}_{top}.png` - изображения с детекциями
  - `{имя}_slice_{row:03d}_{col:03d}_{left}_{top}.txt` - аннотации YOLO формата
  - `classes.txt` - файл классов

**Пример структуры:**
```
predicted_images_with_annotations-best_4-0.5/
├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090/
│   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.png
│   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.txt
│   └── ...
└── classes.txt
```

**Формат аннотаций (.txt):**
```
0 0.5 0.3 0.1 0.2  # class_id x_center y_center width height (нормализованные координаты)
```

---

### **ЭТАП 3: IoU фильтрация дубликатов** 🔄

#### Входные данные:
- **Папка**: `predicted_images_with_annotations-best_4-0.5/`
- **Параметр**: `IOU_THRESHOLD = 0.5`

#### Процесс:
```python
# Запуск IoU фильтрации
python src/main/python/iou_filter/iou_filter.py \
    --input_folder "predicted_images_with_annotations-best_4-0.5" \
    --output_folder "iou_filtered-best_4-0.5" \
    --iou_threshold 0.5
```

#### Выходные данные:
- **Папка**: `iou_filtered-{model_name}-{iou_threshold}/`
- **Структура**: `iou_filtered-best_4-0.5/`
- **Файлы**: Те же PNG и TXT файлы, но с удаленными дубликатами

**Пример структуры:**
```
iou_filtered-best_4-0.5/
├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090/
│   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.png
│   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.txt
│   └── ...
└── classes.txt
```

---

### **ЭТАП 4: Фильтрация выбросов** 🎯

#### Входные данные:
- **Папка**: `iou_filtered-best_4-0.5/`
- **Параметр**: `OUTLIER_THRESHOLD_K = 3`

#### Процесс:
```python
# Запуск фильтрации выбросов
python src/main/python/outlier_filter/outlier_filter.py \
    --input_folder "iou_filtered-best_4-0.5" \
    --output_folder "outlier_filtered-best_4-0.5" \
    --k_threshold 3
```

#### Выходные данные:
- **Папка**: `outlier_filtered-{model_name}-{k_threshold}/`
- **Структура**: `outlier_filtered-best_4-0.5/`
- **Файлы**: Очищенные от аномальных детекций

**Пример структуры:**
```
outlier_filtered-best_4-0.5/
├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090/
│   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.png
│   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.txt
│   └── ...
└── classes.txt
```

---

### **ЭТАП 5: Объединение результатов** 📊

#### Входные данные:
- **Папка**: `outlier_filtered-best_4-0.5/`
- **Процесс**: Объединение координат фрагментов в глобальные координаты

#### Выходные данные:
- **Файл**: `results_{имя_изображения}.jpg` - финальное изображение с детекциями
- **Статистика**: Количество обнаруженных сайгаков

---

## 🔧 Конфигурационные параметры

### Основные настройки (config.py):
```python
MODEL_NAME = "best_4"                    # Имя модели
SLICE_SIZE = 640                         # Размер фрагмента
OVERLAPPING_PERCENTAGE = 20             # Процент перекрытия
CONFIDENCE_THRESHOLD = 0.5              # Порог уверенности
IOU_THRESHOLD = 0.5                      # Порог IoU
OUTLIER_THRESHOLD_K = 3                  # Порог выбросов
```

### Папки результатов:
- `slices/` - Фрагменты изображений
- `predicted_images_with_annotations-{model}-{conf}/` - Результаты детекции
- `iou_filtered-{model}-{iou}/` - После IoU фильтрации
- `outlier_filtered-{model}-{k}/` - После фильтрации выбросов

---

## 📈 Статистика обработки

### Входные данные:
- **211 изображений** в формате JPG
- **Высокое разрешение** аэрофотоснимков
- **Общее количество сайгаков**: 1,317

### Промежуточные результаты:
- **Фрагменты**: ~10,000+ PNG файлов (640×640)
- **Детекции**: Аннотации в YOLO формате
- **После IoU**: Удаление ~30-50% дубликатов
- **После фильтрации выбросов**: Удаление аномальных детекций

### Финальные результаты:
- **Точность**: 87.6%
- **Recall**: 84.9%
- **mAP50**: 0.88
- **mAP50-95**: 0.53

---

## 🚀 Команды для запуска

### 1. Разбиение изображений:
```bash
python src/main/python/image_slicer/image_slicer.py
```

### 2. YOLO детекция:
```python
from src.main.python.model.yolo import process_folders
process_folders(slices_folder, models, devices, output_folder)
```

### 3. IoU фильтрация:
```bash
python src/main/python/iou_filter/iou_filter.py
```

### 4. Фильтрация выбросов:
```bash
python src/main/python/outlier_filter/outlier_filter.py
```

### 5. Полный пайплайн:
```bash
jupyter notebook pipeline.ipynb
```

## 🔍 Проверка результатов

### Проверка этапа 1 (фрагменты):
```bash
# Подсчет фрагментов
find slices/ -name "*.png" | wc -l

# Проверка структуры
ls slices/2025_08_05_PhotoRieboR4_g201b201078_f003_090/
```

### Проверка этапа 2 (детекции):
```bash
# Подсчет аннотаций
find predicted_images_with_annotations-best_4-0.5/ -name "*.txt" | wc -l

# Проверка содержимого аннотации
cat predicted_images_with_annotations-best_4-0.5/2025_08_05_PhotoRieboR4_g201b201078_f003_090/2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.txt
```

### Проверка этапа 3 (IoU фильтрация):
```bash
# Сравнение количества до и после
echo "До IoU фильтрации:"
find predicted_images_with_annotations-best_4-0.5/ -name "*.txt" | wc -l

echo "После IoU фильтрации:"
find iou_filtered-best_4-0.5/ -name "*.txt" | wc -l
```

### Проверка этапа 4 (фильтрация выбросов):
```bash
# Сравнение количества до и после
echo "До фильтрации выбросов:"
find iou_filtered-best_4-0.5/ -name "*.txt" | wc -l

echo "После фильтрации выбросов:"
find outlier_filtered-best_4-0.5/ -name "*.txt" | wc -l
```

### Проверка финальных результатов:
```bash
# Просмотр результатов
ls results_*.jpg

# Проверка размера файлов
du -h results_*.jpg
```

---

## 📁 Структура выходных папок

```
Saiga/
├── slices/                                    # ЭТАП 1: Фрагменты
│   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090/
│   │   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.png
│   │   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_001_512_0.png
│   │   └── ...
│   └── 2025_08_05_PhotoRieboR4_g201b201078_f003_091/
│       └── ...
├── predicted_images_with_annotations-best_4-0.5/  # ЭТАП 2: Детекции
│   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090/
│   │   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.png
│   │   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.txt
│   │   └── ...
│   └── classes.txt
├── iou_filtered-best_4-0.5/                  # ЭТАП 3: После IoU
│   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090/
│   │   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.png
│   │   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.txt
│   │   └── ...
│   └── classes.txt
├── outlier_filtered-best_4-0.5/              # ЭТАП 4: Финальные результаты
│   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090/
│   │   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.png
│   │   ├── 2025_08_05_PhotoRieboR4_g201b201078_f003_090_slice_000_000_0_0.txt
│   │   └── ...
│   └── classes.txt
└── results_*.jpg                              # ЭТАП 5: Визуализация
    ├── results_2025_08_05_PhotoRieboR4_g201b201078_f003_090.jpg
    └── results_2025_08_05_PhotoRieboR4_g201b201078_f003_091.jpg
```

## 📄 Форматы файлов

### PNG файлы (изображения):
- **Размер**: 640×640 пикселей
- **Формат**: PNG с альфа-каналом
- **Содержание**: Фрагменты исходных изображений

### TXT файлы (аннотации):
- **Формат**: YOLO формат
- **Структура**: `class_id x_center y_center width height`
- **Координаты**: Нормализованные (0-1)
- **Пример**: `0 0.5 0.3 0.1 0.2`

### JPG файлы (результаты):
- **Размер**: Исходное разрешение
- **Содержание**: Визуализация с ограничивающими рамками
- **Формат**: RGB изображения

---

## ⚡ Производительность

### Время обработки (RTX 5090):
- **Разбиение**: ~2-3 минуты на изображение
- **YOLO детекция**: ~5-10 секунд на фрагмент
- **IoU фильтрация**: ~1-2 минуты
- **Фильтрация выбросов**: ~30 секунд

### Использование ресурсов:
- **GPU память**: 3-4 GB
- **RAM**: 8-16 GB
- **Дисковое пространство**: ~50 GB для полного пайплайна

---

**Примечание**: Все этапы можно запускать как отдельно, так и в составе полного пайплайна через Jupyter Notebooks.
