from PIL import Image, ImageDraw, ImageFont
import os

def draw_centered_text(draw, position, text, font, fill):
    """Рисует текст, выравнивая его по центру относительно заданной позиции."""
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    x = position[0] - text_width // 2
    y = position[1] - text_height // 2
    draw.text((x, y), text, font=font, fill=fill)

def create_profile_image(user_data: dict):
    # 1. Загружаем базовое изображение
    base_image = Image.open("profile/profile.png").convert("RGBA")

    # 2. Создаем временный слой для рисования
    txt_layer = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    # 3. Настройки шрифта (обязательно поддержка кириллицы)
    try:
        font_path = "profile/font/SF-Pro-Display-Black.otf"

        if not os.path.exists(font_path):
            print(f"Файл шрифта не найден по пути: {font_path}")
        font = ImageFont.truetype(font_path, 170)
        print("Шрифт успешно загружен.")
    except Exception as e:
        print(f"Ошибка загрузки шрифта: {e}")
        font = ImageFont.load_default()

    # Цвета текста
    name_color = (0, 104, 222)
    money_color = (255, 255, 255)
    rang_color = (57, 136, 227)
    lids_color = (0, 0, 0)

    # 4. Рисуем текст
    draw_centered_text(draw, (950, 300), user_data['name'], font, name_color)  # Имя
    draw_centered_text(draw, (950, 1000), str(user_data['money']) + "RUB", font, money_color)  # Деньги

    # Ранг
    font_rang = ImageFont.truetype(font_path, 70)
    draw_centered_text(draw, (950, 500), str(user_data['rang']), font_rang, rang_color)

    # Лиды
    font_lids = ImageFont.truetype(font_path, 60)
    draw_centered_text(draw, (1620, 720), str(user_data['lids']), font_lids, lids_color)

    # 5. Совмещаем слои
    result = Image.alpha_composite(base_image, txt_layer)

    # 6. Сохраняем результат
    image_path = f"profile/image_users/{user_data['id']}.png"
    result.convert("RGB").save(image_path)
    print(f"Изображение сохранено как {image_path}")
    return image_path


