# Импортируем необходимые модули
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import pandas as pd
from datetime import datetime
import os
import sys

# Класс приложения конвертера валют
class CurrencyConverterApp:
    def __init__(self, root):
        self.last_updated_time = None
        self.root = root
        self.root.iconbitmap("resources/app_icon.ico")  # Устанавливаем иконку приложения
        self.root.title("Конвертер валют")  # Заголовок окна
        self.root.geometry("600x400")  # Размер окна
        self.root.configure(bg='#2c3e50')  # Фон окна
        self.root.resizable(False, False)  # Отключаем возможность изменения размера окна
        self.center_window()  # Центрируем окно
        self.main_frame = ttk.Frame(root, padding="20")  # Создаем основной фрейм
        self.currency_data = pd.DataFrame()  # Инициализируем пустой DataFrame для данных валют
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")  # Размещаем фрейм по центру окна

        # Словарь с кодами валют и их названиями
        self.currencies = {
            'USD': 'Доллар США',
            'EUR': 'Евро',
            'GBP': 'Фунт стерлингов',
            'JPY': 'Японская иена',
            'AUD': 'Австралийский доллар',
            'CAD': 'Канадский доллар',
            'CHF': 'Швейцарский франк',
            'CNY': 'Китайский юань',
            'SEK': 'Шведская крона',
            'NZD': 'Новозеландский доллар',
            'RUB': 'Российский рубль',
            'INR': 'Индийская рупия',
            'BRL': 'Бразильский реал',
            'MXN': 'Мексиканский песо',
            'HKD': 'Гонконгский доллар',
            'NOK': 'Норвежская крона',
            'KRW': 'Южнокорейская вона',
            'TRY': 'Турецкая лира',
            'ILS': 'Израильский шекель',
            'PLN': 'Польский злотый',
            'IDR': 'Индонезийская рупия',
            'HUF': 'Венгерский форинт',
            'CZK': 'Чешская крона',
            'DKK': 'Датская крона',
            'MYR': 'Малайзийский ринггит',
            'PHP': 'Филиппинский песо',
            'PKR': 'Пакистанская рупия',
            'EGP': 'Египетский фунт',
            'KZT': 'Казахстанский тенге',
            'ARS': 'Аргентинский песо',
            'CLP': 'Чилийский песо',
            'UAH': 'Украинская гривна',
            'AED': 'Дирхам ОАЭ',
            'SAR': 'Саудовский риял',
            'QAR': 'Катарский риал',
        }

        self.flag_images = self.load_flag_images()  # Загружаем изображения флагов

        fetch_result = self.fetch_currency_data()  # Загружаем данные о валютных курсах
        if fetch_result == "quit":  # Если загрузка не удалась и нет локальных данных, выходим из программы
            sys.exit(0)

        self.create_widgets()  # Создаем виджеты интерфейса
        self.convert()  # Выполняем первую конвертацию для отображения
        self.display_last_updated_time()  # Отображаем время последнего обновления данных
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Обрабатываем закрытие окна

    def create_widgets(self):
        # Настраиваем стили для виджетов
        style = ttk.Style()
        style.configure('TFrame', background='#34495e')
        style.configure('TLabel', background='#34495e', foreground='white', font=('Helvetica', 10))
        style.configure('TButton', background='#16a085', foreground='#16a085', font=('Helvetica', 10, 'bold'))
        style.configure('TEntry', background='#ecf0f1', foreground='black', font=('Helvetica', 10))

        # Создаем и размещаем виджет выбора валюты "Из"
        self.from_label = ttk.Label(self.main_frame, text="Из:", font=('Helvetica', 12, 'bold'))
        self.from_label.grid(row=0, column=0, padx=10, pady=5, sticky='e')

        self.from_currency_var = tk.StringVar(self.root)
        self.from_currency_var.set('USD')
        self.from_currency_menu = self.create_currency_menu(self.main_frame, self.from_currency_var, self.convert)
        self.from_currency_menu.grid(row=0, column=1, padx=(0, 10), pady=5, sticky='w')

        # Создаем и размещаем виджет выбора валюты "В"
        self.to_label = ttk.Label(self.main_frame, text="В:", font=('Helvetica', 12, 'bold'))
        self.to_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')

        self.to_currency_var = tk.StringVar(self.root)
        self.to_currency_var.set('EUR')
        self.to_currency_menu = self.create_currency_menu(self.main_frame, self.to_currency_var, self.convert)
        self.to_currency_menu.grid(row=1, column=1, padx=(0, 10), pady=5, sticky='w')

        # Создаем и размещаем виджет ввода суммы
        self.amount_label = ttk.Label(self.main_frame, text="Сумма:", font=('Helvetica', 12, 'bold'))
        self.amount_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')

        self.amount_var = tk.StringVar()
        self.amount_var.trace_add('write', self.validate_amount)  # Добавляем обработчик ввода
        self.amount_entry = ttk.Entry(self.main_frame, textvariable=self.amount_var)
        self.amount_entry.grid(row=2, column=1, padx=(0, 10), pady=5, sticky='w')
        self.amount_entry.insert(0, '100')
        self.amount_entry.bind('<KeyRelease>', self.convert)

        # Создаем и размещаем фрейм для результата конвертации
        self.result_frame = ttk.Frame(self.main_frame, padding="10", relief="solid", borderwidth=1)
        self.result_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky='nsew')
        self.result_frame.grid_propagate(True)

        self.result_label = ttk.Label(self.result_frame, text="", anchor='center', font=('Helvetica', 12, 'bold'),
                                      wraplength=500, width=50)
        self.result_label.pack(fill='both', expand=True, padx=10, pady=10)

        # Создаем и размещаем фрейм для кнопки обновления курсов
        self.button_frame = ttk.Frame(self.main_frame, padding="10", relief="solid", borderwidth=1)
        self.button_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky='we')

        self.update_button = ttk.Button(self.button_frame, text="Обновить курсы", command=self.update_currency_data)
        self.update_button.pack(fill='x')

        # Создаем и размещаем метку для времени последнего обновления курсов
        self.last_updated_label = ttk.Label(self.main_frame, text="", anchor='w', font=('Helvetica', 8))
        self.last_updated_label.grid(row=5, column=0, columnspan=2, padx=10, pady=(0, 10), sticky='w')

    # Создаем выпадающий список валют
    def create_currency_menu(self, parent, variable, command):
        menu = tk.OptionMenu(parent, variable, *self.get_currency_options(), command=command)
        menu.config(width=20, bg='#34495e', fg='white', activebackground='#16a085', activeforeground='white',
                    highlightthickness=1, highlightbackground='#16a085')
        menu['menu'].delete(0, 'end')  # Очищаем элементы меню
        menu['menu'].config(bg='#34495e', fg='white', activebackground='#16a085', activeforeground='white')

        # Добавляем элементы меню с флагами
        for code, name in self.currencies.items():
            img = self.flag_images.get(code, None)
            menu['menu'].add_command(label=f"{code} ({name})", image=img, compound='left',
                                     command=lambda c=code: [variable.set(c), command()])

        return menu

    # Загружаем изображения флагов
    def load_flag_images(self):
        images = {}
        for code in self.currencies.keys():
            try:
                image = tk.PhotoImage(file=f"resources/flags/{code}.png").subsample(5, 5)
                images[code] = image
            except Exception as e:
                print(f"Could not load image for {code}: {e}")
        return images

    # Центрируем окно на экране
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    # Получаем список опций для выпадающего меню валют
    def get_currency_options(self):
        return [f"{code} ({name})" for code, name in self.currencies.items()]

    # Обновляем выбранную валюту "Из"
    def update_from_currency_display(self, selection):
        code = selection.split()[0]
        self.from_currency_var.set(code)
        self.convert()

    # Обновляем выбранную валюту "В"
    def update_to_currency_display(self, selection):
        code = selection.split()[0]
        self.to_currency_var.set(code)
        self.convert()

    # Загружаем данные о курсах валют
    def fetch_currency_data(self):
        try:
            url = 'https://api.exchangerate-api.com/v4/latest/USD'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            rates = data.get('rates', {})
            filtered_rates = {currency: rates[currency] for currency in self.currencies if currency in rates}
            self.currency_data = pd.DataFrame(filtered_rates, index=[0])
            self.last_updated_time = datetime.now()
            self.save_currency_data_to_csv()
            return "internet"
        except requests.ConnectionError:
            if self.load_currency_data_from_csv():
                messagebox.showerror("Ошибка", "Нет подключения к интернету. Используются сохраненные данные.")
                return "file"
            else:
                return "quit"
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить курсы валют: {str(e)}")
            self.root.quit()
            return "quit"

    # Загружаем данные о курсах валют из локального CSV файла
    def load_currency_data_from_csv(self):
        filename = "resources/currency_data.csv"
        if os.path.exists(filename):
            self.currency_data = pd.read_csv(filename)
            return True
        else:
            messagebox.showerror("Ошибка",
                                 "Файл с сохраненными данными о курсах валют не найден. Приложение будет закрыто.")
            self.root.quit()
            return False

    # Обновляем данные о курсах валют
    def update_currency_data(self):
        fetch_result = self.fetch_currency_data()
        if fetch_result == "internet":
            self.save_currency_data_to_csv()
            self.display_last_updated_time()
            messagebox.showinfo("Успех", "Курсы валют успешно обновлены!")
        elif fetch_result == "file":
            self.display_last_updated_time()

    # Проверяем и ограничиваем ввод суммы
    def validate_amount(self, *args):
        amount = self.amount_var.get()
        if len(amount) > 16:
            self.amount_var.set(amount[:16])

    # Конвертируем валюту
    def convert(self, event=None):
        try:
            from_currency = self.from_currency_var.get().split()[0]
            to_currency = self.to_currency_var.get().split()[0]
            amount_str = self.amount_entry.get()

            # Обработка пустой строки или нулевой суммы
            if not amount_str or float(amount_str) == 0:
                self.result_label.config(text=f"0 {from_currency} = 0 {to_currency}")
                return

            amount = float(amount_str)

            if from_currency == to_currency:
                converted_amount = amount
            else:
                conversion_rate = self.currency_data.loc[0, to_currency] / self.currency_data.loc[0, from_currency]
                converted_amount = amount * conversion_rate

            if converted_amount > 1e10 or converted_amount < 1e-10:
                result_text = f"{amount:.2f} {from_currency} = {converted_amount:.2e} {to_currency}"
            else:
                result_text = f"{amount:.2f} {from_currency} = {converted_amount:.2f} {to_currency}"

            self.result_label.config(text=result_text)
        except ValueError:
            self.result_label.config(text="Ошибка ввода")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при конвертации: {str(e)}")

    # Обрабатываем закрытие окна
    def on_closing(self):
        if messagebox.askokcancel("Выход", "Вы точно хотите выйти?"):
            self.root.quit()

    # Отображаем время последнего обновления данных
    def display_last_updated_time(self):
        if self.last_updated_time:
            formatted_time = self.last_updated_time.strftime("%d.%m.%Y %H:%M:%S")
            self.last_updated_label.config(text=f"Последнее обновление: {formatted_time}")

    # Сохраняем данные о курсах валют в локальный CSV файл
    def save_currency_data_to_csv(self):
        filename = "resources/currency_data.csv"
        self.currency_data.to_csv(filename, index=False)

# Запускаем приложение
if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = CurrencyConverterApp(root)
        root.mainloop()
    except tk.TclError:
        sys.exit(0)
