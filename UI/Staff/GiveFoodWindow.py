from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QGroupBox,
    QFormLayout,
)

from Database.Clients import search_clients
from Database.Inventory import (
    get_item_by_barcode,
    get_total_stock,
    remove_stock,
)
from Database.Distributions import (
    create_distribution,
    add_distribution_item,
)


class GiveFoodWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent_window = parent

        self.selected_client = None
        self.current_item = None

        # Items waiting to be given
        self.food_items = []

        self.setWindowTitle("Give Food")
        self.setMinimumSize(750, 650)

        self.setup_ui()

    # ============================================================
    # UI SETUP
    # ============================================================

    def setup_ui(self):

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        # --------------------------------------------------------
        # TITLE
        # --------------------------------------------------------

        title = QLabel("Give Food")
        title.setStyleSheet(
            """
            QLabel {
                font-size: 26px;
                font-weight: bold;
                padding: 10px;
            }
            """
        )

        main_layout.addWidget(title)

        # --------------------------------------------------------
        # CLIENT SECTION
        # --------------------------------------------------------

        client_group = QGroupBox("Select Client")

        client_layout = QVBoxLayout()

        self.client_search = QLineEdit()
        self.client_search.setPlaceholderText(
            "Search by client number, first name, or last name..."
        )

        self.client_search.textChanged.connect(
            self.search_for_clients
        )

        client_layout.addWidget(self.client_search)

        self.client_list = QListWidget()
        self.client_list.setMaximumHeight(150)

        self.client_list.itemClicked.connect(
            self.select_client
        )

        client_layout.addWidget(self.client_list)

        self.selected_client_label = QLabel(
            "No client selected"
        )

        self.selected_client_label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                padding: 5px;
            }
            """
        )

        client_layout.addWidget(
            self.selected_client_label
        )

        client_group.setLayout(client_layout)

        main_layout.addWidget(client_group)

        # --------------------------------------------------------
        # FOOD SECTION
        # --------------------------------------------------------

        food_group = QGroupBox("Add Food")

        food_layout = QVBoxLayout()

        barcode_layout = QHBoxLayout()

        barcode_label = QLabel("Barcode:")

        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText(
            "Scan or enter barcode..."
        )

        self.barcode_input.returnPressed.connect(
            self.scan_barcode
        )

        self.scan_button = QPushButton("Scan / Find")

        self.scan_button.clicked.connect(
            self.scan_barcode
        )

        barcode_layout.addWidget(barcode_label)
        barcode_layout.addWidget(
            self.barcode_input
        )
        barcode_layout.addWidget(
            self.scan_button
        )

        food_layout.addLayout(barcode_layout)

        # --------------------------------------------------------
        # ITEM INFORMATION
        # --------------------------------------------------------

        self.item_label = QLabel(
            "Item: None"
        )

        self.stock_label = QLabel(
            "Available: --"
        )

        self.item_label.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
            }
            """
        )

        food_layout.addWidget(
            self.item_label
        )

        food_layout.addWidget(
            self.stock_label
        )

        # --------------------------------------------------------
        # QUANTITY
        # --------------------------------------------------------

        quantity_layout = QHBoxLayout()

        quantity_label = QLabel("Quantity:")

        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(999999)
        self.quantity_input.setValue(1)

        quantity_layout.addWidget(
            quantity_label
        )

        quantity_layout.addWidget(
            self.quantity_input
        )

        quantity_layout.addStretch()

        self.add_food_button = QPushButton(
            "Add Food"
        )

        self.add_food_button.clicked.connect(
            self.add_food
        )

        self.add_food_button.setEnabled(False)

        quantity_layout.addWidget(
            self.add_food_button
        )

        food_layout.addLayout(
            quantity_layout
        )

        food_group.setLayout(
            food_layout
        )

        main_layout.addWidget(
            food_group
        )

        # --------------------------------------------------------
        # FOOD LIST
        # --------------------------------------------------------

        list_group = QGroupBox(
            "Food Being Given"
        )

        list_layout = QVBoxLayout()

        self.food_list = QListWidget()

        list_layout.addWidget(
            self.food_list
        )

        self.remove_food_button = QPushButton(
            "Remove Selected Food"
        )

        self.remove_food_button.clicked.connect(
            self.remove_selected_food
        )

        list_layout.addWidget(
            self.remove_food_button
        )

        self.total_label = QLabel(
            "Items in this visit: 0"
        )

        self.total_label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                padding: 5px;
            }
            """
        )

        list_layout.addWidget(
            self.total_label
        )

        list_group.setLayout(
            list_layout
        )

        main_layout.addWidget(
            list_group
        )

        # --------------------------------------------------------
        # BUTTONS
        # --------------------------------------------------------

        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.cancel_button.clicked.connect(
            self.close_window
        )

        button_layout.addWidget(
            self.cancel_button
        )

        button_layout.addStretch()

        self.give_food_button = QPushButton(
            "GIVE FOOD"
        )

        self.give_food_button.setMinimumHeight(
            45
        )

        self.give_food_button.setStyleSheet(
            """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 8px 25px;
            }
            """
        )

        self.give_food_button.clicked.connect(
            self.give_food
        )

        button_layout.addWidget(
            self.give_food_button
        )

        main_layout.addLayout(
            button_layout
        )

        self.setLayout(
            main_layout
        )

    # ============================================================
    # CLIENT SEARCH
    # ============================================================

    def search_for_clients(self):

        search_text = self.client_search.text().strip()

        self.client_list.clear()

        if not search_text:
            return

        try:
            clients = search_clients(
                search_text
            )

            for client in clients:

                display_text = (
                    f"{client['client_number']} - "
                    f"{client['first_name']} "
                    f"{client['last_name']}"
                )

                item = QListWidgetItem(
                    display_text
                )

                item.setData(
                    Qt.UserRole,
                    client
                )

                self.client_list.addItem(
                    item
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"Could not search clients:\n\n{error}",
            )

    # ============================================================
    # SELECT CLIENT
    # ============================================================

    def select_client(self, list_item):

        client = list_item.data(
            Qt.UserRole
        )

        self.selected_client = client

        self.selected_client_label.setText(
            f"Selected: "
            f"{client['client_number']} - "
            f"{client['first_name']} "
            f"{client['last_name']}"
        )

    # ============================================================
    # BARCODE
    # ============================================================

    def scan_barcode(self):

        barcode = (
            self.barcode_input.text()
            .strip()
        )

        if not barcode:
            QMessageBox.warning(
                self,
                "Barcode Required",
                "Please scan or enter a barcode.",
            )

            return

        try:

            item = get_item_by_barcode(
                barcode
            )

            if item is None:

                QMessageBox.warning(
                    self,
                    "Item Not Found",
                    f"No active inventory item "
                    f"was found with barcode:\n\n"
                    f"{barcode}",
                )

                self.current_item = None
                self.add_food_button.setEnabled(
                    False
                )

                return

            total_stock = get_total_stock(
                item["id"]
            )

            self.current_item = item

            self.item_label.setText(
                f"Item: {item['name']}"
            )

            self.stock_label.setText(
                f"Available: "
                f"{total_stock} "
                f"{item['unit']}"
            )

            self.quantity_input.setMaximum(
                max(1, total_stock)
            )

            if total_stock > 0:

                self.add_food_button.setEnabled(
                    True
                )

            else:

                self.add_food_button.setEnabled(
                    False
                )

                QMessageBox.warning(
                    self,
                    "Out of Stock",
                    f"{item['name']} "
                    f"is currently out of stock.",
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"Could not find item:\n\n{error}",
            )

    # ============================================================
    # ADD FOOD TO VISIT
    # ============================================================

    def add_food(self):

        if self.selected_client is None:

            QMessageBox.warning(
                self,
                "Client Required",
                "Please select a client first.",
            )

            return

        if self.current_item is None:

            QMessageBox.warning(
                self,
                "Food Required",
                "Please scan a food item first.",
            )

            return

        quantity = (
            self.quantity_input.value()
        )

        item_id = self.current_item["id"]

        try:

            available = get_total_stock(
                item_id
            )

            # Check how much of this item is
            # already waiting in the visit.
            already_added = sum(
                food["quantity"]
                for food in self.food_items
                if food["item_id"] == item_id
            )

            remaining_available = (
                available - already_added
            )

            if quantity > remaining_available:

                QMessageBox.warning(
                    self,
                    "Not Enough Stock",
                    f"Only "
                    f"{remaining_available} "
                    f"{self.current_item['unit']} "
                    f"of {self.current_item['name']} "
                    f"is available.",
                )

                return

            # Add it to the temporary list.
            self.food_items.append(
                {
                    "item_id": item_id,
                    "item_name": self.current_item["name"],
                    "unit": self.current_item["unit"],
                    "quantity": quantity,
                }
            )

            self.refresh_food_list()

            # Reset barcode field
            self.barcode_input.clear()

            self.current_item = None

            self.item_label.setText(
                "Item: None"
            )

            self.stock_label.setText(
                "Available: --"
            )

            self.quantity_input.setValue(
                1
            )

            self.add_food_button.setEnabled(
                False
            )

            self.barcode_input.setFocus()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"Could not add food:\n\n{error}",
            )

    # ============================================================
    # REFRESH FOOD LIST
    # ============================================================

    def refresh_food_list(self):

        self.food_list.clear()

        total_items = 0

        for food in self.food_items:

            text = (
                f"{food['item_name']}    "
                f"{food['quantity']} "
                f"{food['unit']}"
            )

            item = QListWidgetItem(
                text
            )

            item.setData(
                Qt.UserRole,
                food
            )

            self.food_list.addItem(
                item
            )

            total_items += food["quantity"]

        self.total_label.setText(
            f"Items in this visit: "
            f"{total_items}"
        )

    # ============================================================
    # REMOVE FOOD
    # ============================================================

    def remove_selected_food(self):

        selected = (
            self.food_list.currentItem()
        )

        if selected is None:

            QMessageBox.warning(
                self,
                "Nothing Selected",
                "Select a food item to remove.",
            )

            return

        food = selected.data(
            Qt.UserRole
        )

        self.food_items.remove(
            food
        )

        self.refresh_food_list()

    # ============================================================
    # GIVE FOOD
    # ============================================================

    def give_food(self):

        if self.selected_client is None:

            QMessageBox.warning(
                self,
                "Client Required",
                "Please select a client.",
            )

            return

        if not self.food_items:

            QMessageBox.warning(
                self,
                "No Food",
                "Please add at least one food item.",
            )

            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Distribution",
            (
                f"Give {len(self.food_items)} "
                f"different food item(s) to "
                f"{self.selected_client['first_name']} "
                f"{self.selected_client['last_name']}?"
            ),
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirmation != QMessageBox.Yes:
            return

        try:

            # ----------------------------------------------------
            # Verify ALL stock before changing anything.
            # ----------------------------------------------------

            for food in self.food_items:

                available = get_total_stock(
                    food["item_id"]
                )

                if available < food["quantity"]:

                    raise ValueError(
                        f"Not enough stock for "
                        f"{food['item_name']}.\n\n"
                        f"Requested: {food['quantity']}\n"
                        f"Available: {available}"
                    )

            # ----------------------------------------------------
            # Create the distribution record.
            # ----------------------------------------------------

            distribution_id = create_distribution(
                self.selected_client["id"]
            )

            # ----------------------------------------------------
            # Remove stock and record each item.
            # ----------------------------------------------------

            for food in self.food_items:

                remove_stock(
                    food["item_id"],
                    food["quantity"],
                )

                add_distribution_item(
                    distribution_id,
                    food["item_id"],
                    food["quantity"],
                )

            # ----------------------------------------------------
            # Success
            # ----------------------------------------------------

            QMessageBox.information(
                self,
                "Food Given",
                (
                    "Food was successfully "
                    "given to the client.\n\n"
                    f"Distribution #: "
                    f"{distribution_id}"
                ),
            )

            self.reset_form()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Distribution Error",
                (
                    "The food could not be given.\n\n"
                    f"{error}"
                ),
            )

    # ============================================================
    # RESET
    # ============================================================

    def reset_form(self):

        self.selected_client = None
        self.current_item = None
        self.food_items.clear()

        self.client_search.clear()
        self.client_list.clear()

        self.selected_client_label.setText(
            "No client selected"
        )

        self.barcode_input.clear()

        self.item_label.setText(
            "Item: None"
        )

        self.stock_label.setText(
            "Available: --"
        )

        self.quantity_input.setValue(
            1
        )

        self.food_list.clear()

        self.total_label.setText(
            "Items in this visit: 0"
        )

        self.add_food_button.setEnabled(
            False
        )

        self.barcode_input.setFocus()

    # ============================================================
    # CLOSE
    # ============================================================

    def close_window(self):

        self.close()