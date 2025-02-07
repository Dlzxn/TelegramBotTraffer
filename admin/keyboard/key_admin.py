from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton




# Клавиатура для администратора
but1 = InlineKeyboardButton(text="Офферы", callback_data="adm_offer")
but2 = InlineKeyboardButton(text="👉 Выдать права", callback_data="adm_prava")
but3 = InlineKeyboardButton(text="✏️ Изменить профиль", callback_data="refact_profile")
but4 = InlineKeyboardButton(text="💰 Запросы на вывод", callback_data="get_money")

but5 = InlineKeyboardButton(text="💼 Вернуться назад", callback_data="adm_cancel")

admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[[but1, but2], [but3, but4]])


but_search=InlineKeyboardButton(text="Поиск по офферу", callback_data="adm_offer_search")
but_create_offer=InlineKeyboardButton(text="Создать оффер", callback_data="create_offer")
but_create=InlineKeyboardButton(text="Изменить оффер", callback_data="refactoring_offers")
but_set=InlineKeyboardButton(text="Выдать оффер", callback_data="user_take_offer")
but_get=InlineKeyboardButton(text="Запросы на оффер", callback_data="give_me_url")
but_menu = InlineKeyboardButton(text="Выйти", callback_data="main_menu")


offer_keyboard = InlineKeyboardMarkup(inline_keyboard = [[but_create_offer], [but_search, but_create], [but_set, but_get], [but_menu]])