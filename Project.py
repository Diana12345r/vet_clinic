import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QDialog, QLineEdit,\
    QTextBrowser, QFormLayout, QDialogButtonBox, QTimeEdit, QDateEdit, QMessageBox
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets
import datetime
import datetime as dt
import sqlite3

con = sqlite3.connect('Vet_clinic.sqlite')

cur = con.cursor()


class RecordDialog(QDialog):
    """Диалоговое окно для записи на прием"""
    def __init__(self):
        """Создание окна"""
        super().__init__()

        self.setWindowTitle('Запись на приём')
        self.setGeometry(300, 200, 300, 200)
        # Время в настоящий момент и нахождение интервала
        self.now = datetime.date.today()
        self.delta = dt.timedelta(weeks=12)
        self.max_date = self.now + self.delta
        self.min_time = dt.time(8, 0)
        self.max_time = dt.time(20, 30)

        # строки для ввода
        self.NameInput = QLineEdit(self)
        self.AnimalInput = QLineEdit(self)
        self.DateInput = QDateEdit(self.now)
        self.TimeInput = QTimeEdit(self)
        self.PhoneInput = QLineEdit(self)
        self.CodeInput = QLineEdit(self)

        layout = QFormLayout(self)
        layout.addRow('Придумайте логин', self.NameInput)
        layout.addRow('Введите вид процедуры', self.AnimalInput)
        layout.addRow('Удобнаяя для вас дата', self.DateInput)
        layout.addRow('Удобное для вас время', self.TimeInput)
        layout.addRow('Ваш номер телефона в формате +7xxxxxxxxxx', self.PhoneInput)
        layout.addRow('Кодовое слово для доступа к записи', self.CodeInput)

        # создание стандартных кнопок
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.count = True  # Проверка на изменение неправильно заполненной информации

    def accept(self):
        """Считывание информации"""

        self.Name_Input = self.NameInput.text()
        self.Animal_Input = self.AnimalInput.text()
        self.Date_Input = self.DateInput.date()
        self.Time_Input = self.TimeInput.time()
        self.Phone_Input = self.PhoneInput.text()
        self.Code_Input = self.CodeInput.text()
        self.Date_Input_dt = dt.date(self.Date_Input.year(), self.Date_Input.month(), self.Date_Input.day())
        self.Time_Input_dt = dt.time(self.Time_Input.hour(), self.Time_Input.minute())
        self.date_time = datetime.datetime.combine(
                datetime.date(self.Date_Input_dt.year, self.Date_Input_dt.month, self.Date_Input_dt.day),
                datetime.time(self.Time_Input_dt.hour, self.Time_Input_dt.minute))

        # вызов функций для проверки и записи в базу данных
        self.check_name_animal()
        self.check_datetime()
        self.check_phone()
        self.checkcode()
        self.input_in_base()

    def check_name_animal(self):
        """Проверка формата ввода Имени и Вида животного"""
        if not self.Animal_Input.isalpha():
            self.warning_Animal = QMessageBox(self)  # открытие окна сообщающего об ошибке
            self.warning_Animal.setIcon(QMessageBox.Warning)
            self.warning_Animal.setWindowTitle('Ошибка ввода')
            self.warning_Animal.setText('Проверьте написание Вида животного, оно должно состоять только из букв')
            self.warning_Animal.setStandardButtons(QMessageBox.Ok)
            self.warning_Animal.exec()
            self.count = False

        self.checkName = cur.execute("""SELECT * FROM Information
        WHERE Login = ?""", (self.Name_Input,)).fetchall()
        if len(self.checkName) != 0:
            self.warning_Name = QMessageBox(self)  # открытие окна сообщающего об ошибке
            self.warning_Name.setIcon(QMessageBox.Warning)
            self.warning_Name.setWindowTitle('Ошибка ввода')
            self.warning_Name.setText('Этот логин занят')
            self.warning_Name.setStandardButtons(QMessageBox.Ok)
            self.warning_Name.exec()
            self.count = False

    def check_phone(self):
        """Проверка формата ввода номера телефона"""
        if len(self.Phone_Input) != 12 or self.Phone_Input[:2] == [+7] or not self.Phone_Input[2:].isdigit():
            self.warning_Phone = QMessageBox(self)  # открытие окна сообщающего об ошибке
            self.warning_Phone.setIcon(QMessageBox.Warning)
            self.warning_Phone.setWindowTitle('Ошибка ввода')
            self.warning_Phone.setText('Телефон введен неверно')
            self.warning_Phone.setStandardButtons(QMessageBox.Ok)
            self.warning_Phone.exec()
            self.count = False

    def check_datetime(self):
        """Проверка даты, интервал не может превышать 12 недель"""
        if self.Date_Input_dt > self.max_date or self.Date_Input_dt < self.now:
            print(self.Date_Input_dt + self.delta, self.max_date)
            self.warning_Date = QMessageBox(self)  # открытие окна сообщающего об ошибке
            self.warning_Date.setIcon(QMessageBox.Warning)
            self.warning_Date.setWindowTitle('Ошибка ввода')
            self.warning_Date.setText('Интервал между записью и приемом не может превышать 12 недель')
            self.warning_Date.setStandardButtons(QMessageBox.Ok)
            self.warning_Date.exec()
            self.count = False

        """Проверка даты, запись возможна с 8:30 до 20:30"""
        if self.max_time < self.Time_Input_dt or self.min_time > self.Time_Input_dt:
            self.warning_Time = QMessageBox(self)  # открытие окна сообщающего об ошибке
            self.warning_Time.setIcon(QMessageBox.Warning)
            self.warning_Time.setWindowTitle('Ошибка ввода')
            self.warning_Time.setText('Вы можете записать на прием на время с 8:00 до 20:30')
            self.warning_Time.setStandardButtons(QMessageBox.Ok)
            self.warning_Time.exec()
            self.count = False

        self.checkTime = cur.execute("""SELECT * FROM Information
        WHERE Date = ?""", (self.date_time,)).fetchall()
        """Проверка занято ли время"""
        if len(self.checkTime) != 0:
            self.warning_DateTime = QMessageBox(self)  # открытие окна сообщающего об ошибке
            self.warning_DateTime.setIcon(QMessageBox.Warning)
            self.warning_DateTime.setWindowTitle('Ошибка ввода')
            self.warning_DateTime.setText('Это время занято')
            self.warning_DateTime.setStandardButtons(QMessageBox.Ok)
            self.warning_DateTime.exec()
            self.count = False

    def checkcode(self):
        """Проверка на наличие кодового слова"""
        if len(self.Code_Input) == 0:
            self.warning_Code = QMessageBox(self)
            self.warning_Code.setIcon(QMessageBox.Warning)  # открытие окна сообщающего об ошибке
            self.warning_Code.setWindowTitle('Ошибка ввода')
            self.warning_Code.setText('Введите кодовое слово')
            self.warning_Code.setStandardButtons(QMessageBox.Ok)
            self.warning_Code.exec()
            self.count = False

    def input_in_base(self):
        if self.count:
            """Помещаем информацию в базу данных"""
            cur.execute("""INSERT INTO Information
            (Login, Animal, Date, Phone, Code)
            VALUES
            (?, ?, ?, ?, ?)""",
                        (self.Name_Input, self.Animal_Input, self.date_time,
                         self.Phone_Input, self.Code_Input))

            self.information = QMessageBox(self)
            self.information.setWindowTitle('Запись')
            self.information.setText(f'Вы записали {self.Animal_Input} на {self.date_time},\n'
                                     f'Ваш номер телефона {self.Phone_Input}\n'
                                     f'Ваш логин {self.Name_Input},\n'
                                     f'Кодовое слово {self.Code_Input}\n'
                                     f'Запомниете их, они вам могут понадобятся при отмене или изменении записи!!!!')
            self.information.setStandardButtons(QMessageBox.Ok)
            self.information.exec()
            self.reject()
        self.count = True


class CancelDialog(QDialog):
    """Диалоговое окно для отмены записи"""
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Отмена записи')
        self.setGeometry(300, 200, 300, 50)

        self.IdInput = QLineEdit(self)
        self.CodeInput = QLineEdit(self)

        layout = QFormLayout(self)
        layout.addRow('Введите ваш логин', self.IdInput)
        layout.addRow('Введите ваше кодовое слово', self.CodeInput)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def accept(self):
        """Считывание информации"""
        self.Login_input = self.IdInput.text()
        self.Code_Input = self.CodeInput.text()

        self.check()

    def check(self):
        """Проверка логина и кодового слова"""
        self.BaseLoginCode = cur.execute("""SELECT * FROM Information
        WHERE Login = ? AND Code = ?""", (self.Login_input, self.Code_Input)).fetchall()
        if len(self.BaseLoginCode) == 0:
            self.warning = QMessageBox(self)  # открытие окна сообщающего об ошибке
            self.warning.setIcon(QMessageBox.Warning)
            self.warning.setWindowTitle('Ошибка ввода')
            self.warning.setText('Логин или кодовое слово неверное')
            self.warning.setStandardButtons(QMessageBox.Ok)
            self.warning.exec()
        else:
            self.delit()

    def delit(self):
        """Удаление записи из базы данных"""
        cur.execute("""DELETE FROM Information WHERE 
        Login = ? AND Code = ?""", (self.Login_input, self.Code_Input))
        self.delit_ = QMessageBox(self)
        self.delit_.setIcon(QMessageBox.Warning)
        self.delit_.setWindowTitle('Запись удалена')
        self.delit_.setText('Ваша запись удалена')
        self.delit_.setStandardButtons(QMessageBox.Ok)
        self.delit_.exec()

        self.reject()


class Change(QDialog):
    """Диалоговое окно для изменение записи"""

    def __init__(self, Login_input, parent=None):
        """Создание окна"""
        super(Change, self).__init__(parent)

        self.info = Login_input  # передача информации из ChangeDialog

        self.allinfo = cur.execute("""SELECT * FROM Information
                WHERE Login = ?""", (self.info,)).fetchone()
        self.dt_ = datetime.datetime.strptime(self.allinfo[2], '%Y-%m-%d %H:%M:%S')

        self.setWindowTitle('Запись на приём')
        self.setGeometry(300, 200, 300, 200)
        # Время в настоящий момент и нахождение интервала
        self.now = datetime.date.today()
        self.delta = dt.timedelta(weeks=12)
        self.max_date = self.now + self.delta
        self.min_time = dt.time(8, 0)
        self.max_time = dt.time(20, 30)

        self.NameInput = QLineEdit(self)
        self.NameInput.setText(self.allinfo[0])
        self.AnimalInput = QLineEdit(self)
        self.AnimalInput.setText(self.allinfo[1])
        self.DateInput = QDateEdit(self.dt_.date())
        self.TimeInput = QTimeEdit(self.dt_.time())
        self.PhoneInput = QLineEdit(self.allinfo[3])
        self.CodeInput = QLineEdit(self.allinfo[4])

        layout = QFormLayout(self)
        layout.addRow('Придумайте логин', self.NameInput)
        layout.addRow('Введите вид вашего животново', self.AnimalInput)
        layout.addRow('Удобнаяя для вас дата', self.DateInput)
        layout.addRow('Удобное для вас время', self.TimeInput)
        layout.addRow('Ваш номер телефона в формате +7xxxxxxxxxx', self.PhoneInput)
        layout.addRow('Кодовое слово для доступа к записи', self.CodeInput)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.count = True  # Проверка на изменение неправильно заполненной информации

    def accept(self):
        """Считывание информации"""

        self.Name_Input = self.NameInput.text()
        self.Animal_Input = self.AnimalInput.text()
        self.Date_Input = self.DateInput.date()
        self.Time_Input = self.TimeInput.time()
        self.Phone_Input = self.PhoneInput.text()
        self.Code_Input = self.CodeInput.text()
        self.Date_Input_dt = dt.date(self.Date_Input.year(), self.Date_Input.month(), self.Date_Input.day())
        self.Time_Input_dt = dt.time(self.Time_Input.hour(), self.Time_Input.minute())
        self.date_time = datetime.datetime.combine(
                datetime.date(self.Date_Input_dt.year, self.Date_Input_dt.month, self.Date_Input_dt.day),
                datetime.time(self.Time_Input_dt.hour, self.Time_Input_dt.minute))

        self.check_name_animal()
        self.check_datetime()
        self.check_phone()
        self.checkcode()
        self.input_in_base()

    def check_name_animal(self):
        """Проверка формата ввода Имени и Вида животного"""
        if not self.Animal_Input.isalpha():
            self.warning_Animal = QMessageBox(self)
            self.warning_Animal.setIcon(QMessageBox.Warning)
            self.warning_Animal.setWindowTitle('Ошибка ввода')
            self.warning_Animal.setText('Проверьте написание Вида животного, оно должно состоять только из букв')
            self.warning_Animal.setStandardButtons(QMessageBox.Ok)
            self.warning_Animal.exec()
            self.count = False

        self.checkName = cur.execute("""SELECT Login FROM Information
        WHERE Login = ?""", (self.Name_Input,)).fetchone()
        if len(self.checkName) != 0 and self.checkName[0] != self.allinfo[0]:
            self.warning_Name = QMessageBox(self)
            self.warning_Name.setIcon(QMessageBox.Warning)
            self.warning_Name.setWindowTitle('Ошибка ввода')
            self.warning_Name.setText('Этот логин занят')
            self.warning_Name.setStandardButtons(QMessageBox.Ok)
            self.warning_Name.exec()
            self.count = False

    def check_phone(self):
        """Проверка формата ввода номера телефона"""
        if len(self.Phone_Input) != 12 or self.Phone_Input[:2] == [+7] or not self.Phone_Input[2:].isdigit():
            self.warning_Phone = QMessageBox(self)
            self.warning_Phone.setIcon(QMessageBox.Warning)
            self.warning_Phone.setWindowTitle('Ошибка ввода')
            self.warning_Phone.setText('Телефон введен неверно')
            self.warning_Phone.setStandardButtons(QMessageBox.Ok)
            self.warning_Phone.exec()
            self.count = False

    def check_datetime(self):
        """Проверка даты, интервал не может превышать 12 недель"""
        if self.Date_Input_dt > self.max_date or self.Date_Input_dt < self.now:
            self.warning_Date = QMessageBox(self)  # открытие окна сообщающего об ошибке
            self.warning_Date.setIcon(QMessageBox.Warning)
            self.warning_Date.setWindowTitle('Ошибка ввода')
            self.warning_Date.setText('Интервал между записью и приемом не может превышать 12 недель')
            self.warning_Date.setStandardButtons(QMessageBox.Ok)
            self.warning_Date.exec()
            self.count = False

        """Проверка даты, запись возможна с 8:30 до 20:30"""
        if self.max_time < self.Time_Input_dt or self.min_time > self.Time_Input_dt:
            self.warning_Time = QMessageBox(self)  # открытие окна сообщающего об ошибке
            self.warning_Time.setIcon(QMessageBox.Warning)
            self.warning_Time.setWindowTitle('Ошибка ввода')
            self.warning_Time.setText('Вы можете записать на прием на время с 8:00 до 20:30')
            self.warning_Time.setStandardButtons(QMessageBox.Ok)
            self.warning_Time.exec()
            self.count = False

        self.checkTime = cur.execute("""SELECT Date FROM Information
        WHERE Date = ?""", (self.date_time,)).fetchall()
        """Проверка занято ли время"""
        if len(self.checkTime) != 0 and self.date_time != self.dt_:
            self.warning_DateTime = QMessageBox(self)  # открытие окна сообщающего об ошибке
            self.warning_DateTime.setIcon(QMessageBox.Warning)
            self.warning_DateTime.setWindowTitle('Ошибка ввода')
            self.warning_DateTime.setText('Это время занято')
            self.warning_DateTime.setStandardButtons(QMessageBox.Ok)
            self.warning_DateTime.exec()
            self.count = False

    def checkcode(self):
        """Проверка на наличие кодового слова"""
        if len(self.Code_Input) == 0:
            self.warning_Code = QMessageBox(self)  # открытие окна сообщающего об ошибке
            self.warning_Code.setIcon(QMessageBox.Warning)
            self.warning_Code.setWindowTitle('Ошибка ввода')
            self.warning_Code.setText('Введите кодовое слово')
            self.warning_Code.setStandardButtons(QMessageBox.Ok)
            self.warning_Code.exec()
            self.count = False

    def input_in_base(self):
        if self.count:  # проверка на корректность заполнения
            """Помещаем информацию в базу данных"""
            cur.execute("""UPDATE Information
            SET Login = ?, Animal = ?, Date = ?, Phone = ?, Code = ?
            WHERE Login = ?""",
                        (self.Name_Input, self.Animal_Input, self.date_time,
                         self.Phone_Input, self.Code_Input, self.info))
            con.commit()

            # вызов окна с информацией о записе
            self.information = QMessageBox(self)
            self.information.setWindowTitle('Запись')
            self.information.setText(f'Вы записали {self.Animal_Input} на {self.date_time},\n'
                                     f'Ваш номер телефона {self.Phone_Input}\n'
                                     f'Ваш логин {self.Name_Input},\n'
                                     f'Кодовое слово {self.Code_Input}\n'
                                     f'Запомниете их, они вам могут понадобятся при отмене или изменении записи!!!!')
            self.information.setStandardButtons(QMessageBox.Ok)
            self.information.exec()
            self.reject()
        self.count = True


class ChangeDialog(QDialog):
    """Диалоговое окно для изменения данных в записи"""
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Изменение записи')
        self.setGeometry(300, 200, 300, 50)

        self.IdInput = QLineEdit(self)
        self.CodeInput = QLineEdit(self)

        layout = QFormLayout(self)
        layout.addRow('Введите ваш логин', self.IdInput)
        layout.addRow('Введите ваше кодовое слово', self.CodeInput)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def accept(self):
        """Считывание информации"""
        self.Login_input = self.IdInput.text()
        self.Code_Input = self.CodeInput.text()

        self.check()
        return cur.execute("""SELECT * FROM Information
                        WHERE Login = ? AND Code = ?""", (self.Login_input, self.Code_Input)).fetchall()

    def check(self):
        """Проверка логина и кодового слова"""
        self.BaseLoginCode = cur.execute("""SELECT * FROM Information
                WHERE Login = ? AND Code = ?""", (self.Login_input, self.Code_Input)).fetchall()
        if len(self.BaseLoginCode) == 0:
            self.warning = QMessageBox(self)  # открытие окна сообщающего об ошибке
            self.warning.setIcon(QMessageBox.Warning)
            self.warning.setWindowTitle('Ошибка ввода')
            self.warning.setText('Логин или кодовое слово неверное')
            self.warning.setStandardButtons(QMessageBox.Ok)
            self.warning.exec()
        else:
            self.change()

    def change(self):
        """передача логина в другой класс"""
        changedialog = Change(self.Login_input, self)
        changedialog.exec()


class MainWidget(QMainWindow):
    """Главный экран приложения"""
    def __init__(self):
        super().__init__()
        uic.loadUi('Проект.ui', self)

        # Открытие картинки для декора
        self.pixmap = QPixmap('лапа_.jpg')
        self.image = QLabel(self)
        self.image.move(350, 140)
        self.image.resize(287, 320)
        self.image.setPixmap(self.pixmap)

        # создание кнопок для записи, отмене и изменения
        self.ChangeButton = self.findChild(QtWidgets.QPushButton, 'ChangeButton')
        self.RecordButton = self.findChild(QtWidgets.QPushButton, 'RecordButton')
        self.CancelButton = self.findChild(QtWidgets.QPushButton, 'CancelButton')

        # вызов функции при нажатие
        self.ChangeButton.clicked.connect(self.change)
        self.RecordButton.clicked.connect(self.record)
        self.CancelButton.clicked.connect(self.cancel)

    def change(self):
        """Вызов класса для изменения записи"""
        changedialog = ChangeDialog()
        changedialog.exec()

    def record(self):
        """Вызов класса для создания записи"""
        recorddialog = RecordDialog()
        recorddialog.exec()

    def cancel(self):
        """Вызов класса для отмены записи"""
        canceldialog = CancelDialog()
        canceldialog.exec()


app = QApplication(sys.argv)
change = ChangeDialog()
ex = MainWidget()
ex.show()
app.exec()
