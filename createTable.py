import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QListView, QVBoxLayout, QWidget, QMessageBox, QComboBox, QLabel, QDialog, QLineEdit, QCheckBox, QHBoxLayout, QPushButton
from PySide6.QtCore import QStringListModel, Qt
from MainWindow import Ui_MainWindow
import psycopg2


def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname="Bases",
            user="postgres",
            password="1234",
            host="127.0.0.1",
            port="5432"
        )

        return connection
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

class createTable(QDialog):
    connect_to_db()
    def __init__(self, num_fields, parent=None):
        super(createTable, self).__init__(parent)

        # Создание вертикального слоя для строк
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # LineEdit для имени таблицы
        self.tableNameLineEdit = QLineEdit()
        self.tableNameLineEdit.setPlaceholderText("Имя таблицы")
        self.layout.addWidget(self.tableNameLineEdit)

        # Добавление строк в зависимости от количества полей
        for _ in range(num_fields):
            self.add_row()

        # Кнопка создания таблицы
        self.createButton = QPushButton("Создать таблицу")
        self.createButton.clicked.connect(self.create_table)
        self.layout.addWidget(self.createButton)

    def add_row(self):
        row_layout = QHBoxLayout()

        # LineEdit для имени столбца
        column_name_edit = QLineEdit()
        column_name_edit.setPlaceholderText("Имя столбца")
        row_layout.addWidget(column_name_edit)

        # ComboBox для типа данных
        data_type_combo = QComboBox()
        data_type_combo.addItems([
            "INTEGER", "VARCHAR", "TEXT", "DATE", "TIMESTAMP", "BOOLEAN", "FLOAT", "DECIMAL"
        ])
        row_layout.addWidget(data_type_combo)

        # CheckBox для автоинкремента
        ai_checkbox = QCheckBox("A_I")
        row_layout.addWidget(ai_checkbox)

        # CheckBox для первичного ключа
        pk_checkbox = QCheckBox("P_K")
        row_layout.addWidget(pk_checkbox)

        # CheckBox для вторичного ключа
        fk_checkbox = QCheckBox("F_K")
        row_layout.addWidget(fk_checkbox)

        # LineEdit для ссылки на таблицу и столбец (для FK)
        fk_table_edit = QLineEdit()
        fk_table_edit.setPlaceholderText("Ссылка на таблицу")
        row_layout.addWidget(fk_table_edit)

        fk_column_edit = QLineEdit()
        fk_column_edit.setPlaceholderText("Ссылка на столбец")
        row_layout.addWidget(fk_column_edit)

        self.layout.addLayout(row_layout)

    def create_table(self):
        table_name = self.tableNameLineEdit.text()
        if not table_name:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, введите имя таблицы.")
            return

        column_definitions = []
        for i in range(1, self.layout.count() - 1):  # Исключаем первый и последний элементы (имя таблицы и кнопку)
            row_layout = self.layout.itemAt(i).layout()
            if row_layout:
                column_name_edit = row_layout.itemAt(0).widget()
                data_type_combo = row_layout.itemAt(1).widget()
                ai_checkbox = row_layout.itemAt(2).widget()
                pk_checkbox = row_layout.itemAt(3).widget()
                fk_checkbox = row_layout.itemAt(4).widget()
                fk_table_edit = row_layout.itemAt(5).widget()
                fk_column_edit = row_layout.itemAt(6).widget()

                column_name = column_name_edit.text()
                data_type = data_type_combo.currentText()
                is_ai = ai_checkbox.isChecked()
                is_pk = pk_checkbox.isChecked()
                is_fk = fk_checkbox.isChecked()
                ref_table = fk_table_edit.text()
                ref_column = fk_column_edit.text()

                if not column_name or not data_type:
                    QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните все поля для каждой строки.")
                    return

                column_definition = f"{column_name} {data_type}"
                if is_ai:
                    column_definition += " AUTO_INCREMENT"
                if is_pk:
                    column_definition += " PRIMARY KEY"
                if is_fk:
                    if not ref_table or not ref_column:
                        QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните поля ссылки на внешний ключ.")
                        return
                    column_definition += f", FOREIGN KEY ({column_name}) REFERENCES {ref_table}({ref_column})"

                column_definitions.append(column_definition)

        if not column_definitions:
            QMessageBox.warning(self, "Ошибка ввода", "Не определены столбцы.")
            return

        connection = connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                create_table_query = f"CREATE TABLE {table_name} ({', '.join(column_definitions)});"
                cursor.execute(create_table_query)
                connection.commit()
                cursor.close()
                QMessageBox.information(self, "Успех", f"Таблица '{table_name}' успешно создана.")
                self.parent().update_table_list()  # Обновление списка таблиц
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
                cursor.close()
                connection.rollback()
            finally:
                connection.close()