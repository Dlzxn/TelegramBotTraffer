from PIL import Image, ImageDraw, ImageFont


def create_profile_image(user_data: dict):

    base_image = Image.open("profile/profile.png").convert("RGBA")

    # 2. Создаем временный слой для рисования
    txt_layer = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    # 3. Настройки шрифта
    try:
        font = ImageFont.truetype("profile/font/first_font.ttf", 170)
        print("Наш шрифт")
    except Exception as e:
        print(e)
        font = ImageFont.load_default()  # Используем стандартный шрифт

    text_color = (0, 104, 222)
    positions = {
        'name': (700, 250),
    }

    # 5. Рисуем текст с тенью
    for key, pos in positions.items():
        # Основной текст
        draw.text(pos, f"{user_data[key]}", font=font, fill=text_color)

    font = ImageFont.truetype("profile/font/first_font.ttf", 170)
    text_color = (255, 255, 255)
    positions = {
        'money': (700, 950)
    }

    for key, pos in positions.items():
        # Основной текст
        draw.text(pos, f"{user_data[key]}", font=font, fill=text_color)



    text_color = (57, 136, 227)
    font = ImageFont.truetype("profile/font/first_font.ttf", 70)
    positions = {
        'rang': (740, 420),
    }

    # 5. Рисуем текст с тенью
    for key, pos in positions.items():
        # Основной текст
        draw.text(pos, f"{user_data[key]}", font=font, fill=text_color)




    text_color = (0, 0, 0)
    font = ImageFont.truetype("profile/font/2font.ttf", 45)
    positions = {
        'lids': (1550, 740),
    }

    # 5. Рисуем текст с тенью
    for key, pos in positions.items():
        # Основной текст
        draw.text(pos, f"{user_data[key]}", font=font, fill=text_color)

    # 6. Совмещаем слои
    result = Image.alpha_composite(base_image, txt_layer)

    # 7. Сохраняем результат
    result.convert("RGB").save(f"profile/image_users/{user_data["id"]}.png")
    print(f"Изображение сохранено как {user_data["id"]}")
    return f"profile/image_users/{user_data["id"]}.png"


# Пример использования
user_data = {
    "id": 1,
    'name': 'Dlzxn',
    'age': '25',
    'bio': 'Python',
    "money": 100000,
    "rang": "diamond",
    "lids": 254
}
