import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QTreeView, 
    QVBoxLayout, QWidget, 
    QFileDialog, 
    QMessageBox, QInputDialog, QMenu, QAction)
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QIcon
from PyQt5.QtCore import Qt

class TreeEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Molybdenum')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(self.load_resource('molybdenum.ico'))  # Используем встроенную иконку

        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Создание QTreeView и модели
        self.tree_view = QTreeView()
        layout.addWidget(self.tree_view)

        # Модель для QTreeView
        self.model = QStandardItemModel()
        self.tree_view.setModel(self.model)

        # Инициализация корневого элемента
        self.root_item = QStandardItem("Root")
        self.model.appendRow(self.root_item)

        # Создание меню
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("File")

        # Кнопки в меню
        self.new_action = QAction("New Tree", self)
        self.save_action = QAction("Save Tree", self)
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.save_action)

        # Подключение действий к методам
        self.new_action.triggered.connect(self.create_new_tree)
        self.save_action.triggered.connect(self.save_tree)

        # Контекстное меню
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

        # Установка стилей
        self.set_styles()

    def load_resource(self, filename):
        """Загружаем ресурс из папки molybdenum или из встроенного архива."""

        if hasattr(sys, '_MEIPASS'):  
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        # Строим полный путь к файлу
        return QIcon(os.path.join(base_path, 'molybdenum', filename))

    def set_styles(self):
        style = """
        /* Здесь можно добавить CSS стили для вашего приложения */
        """
        self.setStyleSheet(style)

    def create_new_tree(self):
        self.root_item.removeRows(0, self.root_item.rowCount())  # Очистка дерева
        self.populate_tree_view({})

    def show_context_menu(self, pos):
        index = self.tree_view.indexAt(pos)
        if not index.isValid():
            return

        menu = QMenu()
        add_text_action = QAction("Add Text", self)
        add_int_action = QAction("Add Integer", self)
        add_float_action = QAction("Add Float", self)
        add_bool_action = QAction("Add Boolean", self)
        add_obj_action = QAction("Add Object", self)
        add_array_action = QAction("Add Array", self)
        delete_action = QAction("Delete Item", self)

        add_text_action.triggered.connect(lambda: self.add_item(index, 'Text'))
        add_int_action.triggered.connect(lambda: self.add_item(index, 'Integer'))
        add_float_action.triggered.connect(lambda: self.add_item(index, 'Float'))
        add_bool_action.triggered.connect(lambda: self.add_item(index, 'Boolean'))
        add_obj_action.triggered.connect(lambda: self.add_item(index, 'Object'))
        add_array_action.triggered.connect(lambda: self.add_item(index, 'Array'))
        delete_action.triggered.connect(lambda: self.remove_item(index))

        menu.addAction(add_text_action)
        menu.addAction(add_int_action)
        menu.addAction(add_float_action)
        menu.addAction(add_bool_action)
        menu.addAction(add_obj_action)
        menu.addAction(add_array_action)
        menu.addAction(delete_action)
        menu.exec(self.tree_view.viewport().mapToGlobal(pos))

    def add_item(self, index, item_type):
        item_key, ok = QInputDialog.getText(self, "New Item", "Enter item name:")
        if not ok or not item_key:
            return

        parent_item = self.model.itemFromIndex(index)
        if parent_item is None:
            QMessageBox.warning(self, "Warning", "Failed to determine parent item.")
            return

        new_item = QStandardItem(item_key)
        parent_item.appendRow(new_item)

        if item_type == 'Object':
            self.populate_tree_view({}, new_item)
        elif item_type == 'Array':
            self.populate_tree_view([], new_item)
        # For 'Text', 'Integer', 'Float', 'Boolean' no further action needed as these are leaf nodes

    def remove_item(self, index):
        if QMessageBox.question(self, "Remove Item", "Are you sure you want to remove this item?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            parent_item = index.parent()
            if parent_item.isValid():
                parent_item.internalPointer().removeRow(index.row())
            else:
                self.root_item.removeRow(index.row())

    def save_tree(self):
        options = QFileDialog.Option.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Tree", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_name:
            try:
                with open(file_name, 'w') as file:
                    json.dump(self.tree_to_json(self.root_item), file, indent=4)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save tree:\n{str(e)}")

    def populate_tree_view(self, data, parent=None):
        if parent is None:
            parent = self.root_item

        if isinstance(data, dict):
            for key, value in data.items():
                item = QStandardItem(key)
                parent.appendRow(item)
                self.populate_tree_view(value, item)
        elif isinstance(data, list):
            for index, value in enumerate(data):
                item = QStandardItem(f'[{index}]')
                parent.appendRow(item)
                self.populate_tree_view(value, item)
        else:
            item = QStandardItem(str(data))
            parent.appendRow(item)

    def tree_to_json(self, item):
        if item.hasChildren():
            if item.text().startswith('['):
                return [self.tree_to_json(item.child(i)) for i in range(item.rowCount())]
            else:
                return {item.child(i).text(): self.tree_to_json(item.child(i)) for i in range(item.rowCount())}
        else:
            text = item.text()
            try:
                if text.lower() == "true" or text.lower() == "false":
                    return text.lower() == "true"
                elif '.' in text:
                    return float(text)
                else:
                    return int(text)
            except ValueError:
                return text

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = TreeEditor()
    editor.show()
    sys.exit(app.exec())
