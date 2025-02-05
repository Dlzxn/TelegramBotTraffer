from profile.create_img import create_profile_image
# Пример использования
user_data = {
    "id": 2,
    'name': 'Алексей',  # Русские символы
    'age': '25',
    'bio': 'Python',
    "money": 100,
    "rang": "Security Master",
    "lids": 254
}


create_profile_image(user_data)