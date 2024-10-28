import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import QStringListModel
from MainWindow import Ui_MainWindow
from createTable import createTable
from refactTable import refactTable
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

class ExpenseTracer(QMainWindow):
    def __init__(self):
        super(ExpenseTracer, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.lV = self.ui.listView  # Исправлена переменная
        self.dbName = self.ui.dbName

        # Автоматическое подключение к базе данных при запуске приложения
        self.connect_and_query()

        # Подключение обработчика двойного клика
        self.lV.doubleClicked.connect(self.on_table_double_click)
        self.setGeometry(100, 100, 600, 400)
        self.UiComponents()

        # Подключение кнопки insertButton
        self.ui.insertButton.clicked.connect(self.open_create_table_dialog)

        # Подключение кнопки refactorButton
        self.ui.refactorButton.clicked.connect(self.open_refactor_table_dialog)

        # Подключение кнопки deleteButton
        self.ui.deleteButton.clicked.connect(self.delete_table)

        self.show()

    def connect_and_query(self):
        connection = connect_to_db()

        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                                SELECT table_name
                                FROM information_schema.tables
                                WHERE table_schema = 'public'
                                ORDER BY table_name;
                            """)
                tables = cursor.fetchall()
                table_names = [table[0] for table in tables]
                cursor.close()

                # Получение названия базы данных
                self.dbName.setText(connection.info.dbname)

                if not table_names:
                    QMessageBox.information(self, "Нет таблиц", "В базе данных нет таблиц.")
                else:
                    model = QStringListModel()
                    model.setStringList(table_names)
                    self.lV.setModel(model)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
                cursor.close()
                connection.close()

    def on_table_double_click(self, index):
        table_name = index.data()
        connection = connect_to_db()

        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(f"""
                                SELECT column_name
                                FROM information_schema.columns
                                WHERE table_name = '{table_name}'
                                ORDER BY ordinal_position;
                            """)
                columns = cursor.fetchall()
                cursor.close()

                # Преобразование данных в строки
                column_names = '\n'.join([column[0] for column in columns])

                QMessageBox.information(self, f"Столбцы таблицы: {table_name}", column_names)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
                cursor.close()
                connection.close()

    def UiComponents(self):
        combo_box_col = self.ui.comboBoxCol
        combo_box_col.addItems([str(i) for i in range(1, 101)])
        combo_box_col.setEditable(False)

        combo_box_3 = self.ui.comboBox_3
        combo_box_4 = self.ui.comboBox_4

        connection = connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                                SELECT table_name
                                FROM information_schema.tables
                                WHERE table_schema = 'public'
                                ORDER BY table_name;
                            """)
                tables = cursor.fetchall()
                table_names = [table[0] for table in tables]
                cursor.close()

                # Добавление названий таблиц в QComboBox
                combo_box_3.addItems(table_names)
                combo_box_4.addItems(table_names)

                combo_box_3.setEditable(False)
                combo_box_4.setEditable(False)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
                cursor.close()
                connection.close()

    def open_create_table_dialog(self):
        num_fields = int(self.ui.comboBoxCol.currentText())
        dialog = createTable(num_fields, self)
        dialog.exec()

    def open_refactor_table_dialog(self):
        selected_table = self.ui.listView.currentIndex().data()
        if selected_table:
            dialog = refactTable(selected_table, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Таблица не выбрана", "Пожалуйста, выберите таблицу для редактирования.")

    def delete_table(self):
        selected_table = self.ui.comboBox_4.currentText()
        if selected_table:
            reply = QMessageBox.question(self, "Подтверждение удаления", f"Вы уверены, что хотите удалить таблицу '{selected_table}'?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                connection = connect_to_db()
                if connection:
                    try:
                        cursor = connection.cursor()
                        cursor.execute(f"DROP TABLE {selected_table};")
                        connection.commit()
                        cursor.close()
                        QMessageBox.information(self, "Успех", f"Таблица '{selected_table}' успешно удалена.")
                        self.update_table_list()  # Обновление списка таблиц
                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
                        cursor.close()
                        connection.rollback()
                    finally:
                        connection.close()
        else:
            QMessageBox.warning(self, "Таблица не выбрана", "Пожалуйста, выберите таблицу для удаления.")

    def update_table_list(self):
        connection = connect_to_db()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                                SELECT table_name
                                FROM information_schema.tables
                                WHERE table_schema = 'public'
                                ORDER BY table_name;
                            """)
                tables = cursor.fetchall()
                table_names = [table[0] for table in tables]
                cursor.close()

                model = QStringListModel()
                model.setStringList(table_names)
                self.lV.setModel(model)
                self.ui.comboBox_3.clear()
                self.ui.comboBox_4.clear()
                self.ui.comboBox_3.addItems(table_names)
                self.ui.comboBox_4.addItems(table_names)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {e}")
                cursor.close()
                connection.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExpenseTracer()
    window.show()

    sys.exit(app.exec())