import sqlite3
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import date

# Устанавливаем соединение с базой данных
conn = sqlite3.connect('tgbotwithtrigger.db', check_same_thread=False)
cursor = conn.cursor()
current_date = date.today()
# Создаем таблицы
cursor.execute('''CREATE TABLE IF NOT EXISTS Товары
                    (ID_товара INT PRIMARY KEY,
                    Название_товара nchar(50) NOT NULL,
                    Категория_товара NCHAR(30) NOT NULL,
                    Стоимость_товара MONEY NOT NULL,
                    Количество_товара INT NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Покупатель
                  (ID_покупателя INT PRIMARY KEY,
                  ФИО_покупателя nchar(50) NOT NULL,
                  [E-mail] NCHAR(50) NOT NULL,
                  Телефон_покупателя NCHAR(15) NOT NULL,
                  Адрес_покупателя NCHAR(100) NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Заказы
                  (ID_заказа INT PRIMARY KEY,
                  ID_покупателя INT NOT NULL,
                  ID_товара INT NOT NULL,
                  Дата_заказа DATE NOT NULL,
                  Количество_товара INT  NOT NULL,
                  FOREIGN KEY (ID_покупателя) REFERENCES Покупатель (ID_покупателя),
                  FOREIGN KEY (ID_товара) REFERENCES Товары (ID_товара))''')
# Добавляем тестовые данные
cursor.execute("""INSERT INTO Товары (ID_товара, Название_товара, Категория_товара, Стоимость_товара, Количество_товара)
    VALUES
    (38, 'Холодильник BOCSH', 'Холодильники', 40000, 1000),
    (40, 'Микроволновая печь SHARP', 'Микроволновые печи', 3500, 1500),
    (42, 'Телевизор Samsung', 'Телевизоры', 39500, 1000);""")
cursor.execute("""INSERT INTO Покупатель (ID_покупателя, ФИО_покупателя, "E-mail", Телефон_покупателя, Адрес_покупателя)
    VALUES
    (1, 'Черных Е. М', 'chernich@mail.ru', '+79278885423', 'г. Москва, ул. Пушкина, д.45, кв.34'),
    (2, 'Браго А. Л', 'bargoh@mail.ru', '+79278883212', 'г. Москва, ул. Есенина, д.40, кв.32'),
    (3, 'Сорокина Е. Л.', 'siirifjssh@mail.ru', '+79278351623', 'г. Москва, ул. Летчиков, д.332, кв.1234'),
    (4, 'Еленова М. Г', 'ueuwidh@mail.ru', '+79278885421', 'г. Москва, ул. Тургенева, д.1, кв.342'),
    (5, 'Подольский М. Н', 'mnhdw@mail.ru', '+79372616353', 'г. Подольск, ул. Главная, д.64, кв.1'),
    (6, 'АОООАО Г. Л.', 'cfjjdjwh@mail.ru', '+79278883209', 'г. Москва, ул. Щипок, д.56, кв.134'),
    (7, 'Смирнов Г. Л.', 'Smirnovh@mail.ru', '+79278885213', 'г. Москва, ул. Кулера, д.392, кв.343');""")
cursor.execute("""INSERT INTO Заказы (ID_заказа, ID_покупателя, ID_товара, Дата_заказа, Количество_товара)
    VALUES
    (1, 2, 38, '2022-01-01', 1),
    (2, 1, 40, '2022-01-02', 10),
    (3, 3, 40, '2022-01-03', 2),
    (4, 3, 42, '2022-01-03', 1),
    (5, 1, 42, '2022-01-04', 1),
    (6, 3, 40, '2022-01-05', 2),
    (7, 1, 38, '2022-01-06', 5),
    (8, 1, 40, '2022-01-07', 2),
    (9, 2, 38, '2022-03-12', 2),
    (10, 3, 42, '2022-03-12', 10);""")

conn.commit()
current_date = date.today()
# Функция для обработки команды /start
def start(update, context):
    update.message.reply_text('Добро пожаловать в магазин бытовой техники! Доступные комадны: /products - доступные товары; /order - заказ товара (/order ID Количество)')
# Функция для обработки команды /products
def products(update, context):
    # Получаем список товаров из базы данных
    cursor.execute("SELECT * FROM Товары")
    products = cursor.fetchall()
    # Отправляем список товаров пользователю
    message = ''
    for product in products:
        message += f"{product[0]} {product[1]} ({product[2]}) - {product[3]} руб.\n"
    update.message.reply_text(message)

# Функция для обработки команды /order
def order(update, context):
    # Получаем id покупателя
    customer_id = update.message.from_user.id
    # Получаем id товара
    product_id = int(context.args[0])
    # Получаем количество товара
    quantity = int(context.args[1])
    # Получаем информацию о товаре из базы данных
    cursor.execute(f"SELECT * FROM Товары WHERE ID_товара={product_id}")
    product = cursor.fetchone()
    # Проверяем, что товар есть в наличии
    if product[4] >= quantity:
        # Уменьшаем количество товара на складе
        cursor.execute(f"UPDATE Товары SET Количество_товара=Количество_товара-{quantity} WHERE ID_товара={product_id}")
        conn.commit()
        # Добавляем информацию о заказе в базу данных
        cursor.execute(f"INSERT INTO Заказы (ID_покупателя, ID_товара, Дата_заказа, Количество_товара) VALUES ({customer_id}, {product_id}, {current_date}, {quantity})")
        conn.commit()
        update.message.reply_text(f"Заказ на {quantity} шт.")
    else:
        update.message.reply_text('К сожалению, данного товара нет в наличии.')

def echo(update, context):
    update.message.reply_text('Извините, я не понимаю ваш запрос. Попробуйте другую команду.')

updater = Updater('6019667267:AAGAMnlM1nJxO3ZRLqOnOseYcutMdiXQ-cg', use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('products', products))
updater.dispatcher.add_handler(CommandHandler('order', order, pass_args=True))
updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
updater.start_polling()
updater.idle()
conn.close()