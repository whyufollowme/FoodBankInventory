from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QSpinBox,
    QTextEdit,
    QHeaderView,
    QComboBox,
    QDateEdit,
    QCheckBox,
)
from PySide6.QtCore import Qt, QDate


# ============================================================
# CLIENT DATABASE
# ============================================================

from Database.Clients import (
    get_all_clients,
    get_client,
    search_clients,
    add_client,
    update_client,
    deactivate_client,
    reactivate_client,
)


# ============================================================
# INVENTORY DATABASE
# ============================================================

from Database.Inventory import (
    add_category,
    get_all_categories,
    add_item,
    get_item,
    get_item_by_barcode,
    search_items,
    get_all_items,
    update_item,
    deactivate_item,
    reactivate_item,
    add_stock,
    get_total_stock,
    remove_stock,
)


# ============================================================
# DISTRIBUTION DATABASE
# ============================================================

from Database.Distributions import (
    create_complete_distribution,
    get_client_distribution_history,
    get_client_distribution_summary,
    get_client_distribution_count,
    get_distribution_items,
)


class StaffWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Food Bank - Staff")
        self.resize(1250, 750)

        self.login_window = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.central_widget.setLayout(main_layout)

        # ====================================================
        # SIDEBAR
        # ====================================================

        sidebar = QWidget()
        sidebar.setFixedWidth(230)

        sidebar.setStyleSheet("""
            QWidget {
                background-color: #1f2937;
            }

            QLabel {
                color: white;
            }

            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                text-align: left;
                padding: 15px 20px;
                font-size: 16px;
            }

            QPushButton:hover {
                background-color: #3b82f6;
            }

            QPushButton:pressed {
                background-color: #2563eb;
            }
        """)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(5)

        sidebar.setLayout(sidebar_layout)

        title = QLabel("STAFF")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 20px 5px;
        """)

        sidebar_layout.addWidget(title)

        subtitle = QLabel("Food Bank System")
        subtitle.setAlignment(Qt.AlignCenter)

        subtitle.setStyleSheet("""
            font-size: 13px;
            color: #9ca3af;
            padding-bottom: 20px;
        """)

        sidebar_layout.addWidget(subtitle)

        # ====================================================
        # NAVIGATION
        # ====================================================

        give_button = QPushButton("🛒   Give Food")
        clients_button = QPushButton("👤   Clients")
        history_button = QPushButton("📜   History")
        inventory_button = QPushButton("📦   Inventory")
        receive_button = QPushButton("📥   Receive Food")

        sidebar_layout.addWidget(give_button)
        sidebar_layout.addWidget(clients_button)
        sidebar_layout.addWidget(history_button)
        sidebar_layout.addWidget(inventory_button)
        sidebar_layout.addWidget(receive_button)

        sidebar_layout.addStretch()

        logout_button = QPushButton("↩   Logout")

        logout_button.clicked.connect(self.logout)

        sidebar_layout.addWidget(logout_button)

        # ====================================================
        # PAGES
        # ====================================================

        self.pages = QStackedWidget()

        self.give_page = self.create_give_food_page()
        self.clients_page = self.create_clients_page()
        self.history_page = self.create_history_page()
        self.inventory_page = self.create_inventory_page()
        self.receive_page = self.create_receive_page()

        self.pages.addWidget(self.give_page)
        self.pages.addWidget(self.clients_page)
        self.pages.addWidget(self.history_page)
        self.pages.addWidget(self.inventory_page)
        self.pages.addWidget(self.receive_page)

        # ====================================================
        # NAVIGATION CONNECTIONS
        # ====================================================

        give_button.clicked.connect(self.open_give_food)

        clients_button.clicked.connect(
            self.open_clients
        )

        history_button.clicked.connect(
            self.open_history
        )

        inventory_button.clicked.connect(
            self.open_inventory
        )

        receive_button.clicked.connect(
            self.open_receive
        )

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)

        # Start on Give Food
        self.pages.setCurrentIndex(0)

    # ========================================================
    # GIVE FOOD PAGE
    # ========================================================

    def create_give_food_page(self):

        page = QWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 35, 40, 35)
        layout.setSpacing(15)

        page.setLayout(layout)

        title = QLabel("🛒 Give Food")

        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        description = QLabel(
            "Select a client and add the food they are receiving."
        )

        description.setStyleSheet("""
            font-size: 16px;
            color: #6b7280;
        """)

        layout.addWidget(description)

        # ====================================================
        # CLIENT SECTION
        # ====================================================

        client_group = QWidget()

        client_layout = QVBoxLayout()
        client_layout.setContentsMargins(0, 0, 0, 0)
        client_group.setLayout(client_layout)

        client_search_layout = QHBoxLayout()

        self.give_client_search = QLineEdit()
        self.give_client_search.setPlaceholderText(
            "Search client number, first name, or last name..."
        )
        self.give_client_search.setMinimumHeight(45)

        give_client_search_button = QPushButton("Search")
        give_client_search_button.setMinimumHeight(45)

        client_search_layout.addWidget(
            self.give_client_search
        )

        client_search_layout.addWidget(
            give_client_search_button
        )

        client_layout.addLayout(
            client_search_layout
        )

        self.give_client_combo = QComboBox()
        self.give_client_combo.setMinimumHeight(45)

        client_layout.addWidget(
            self.give_client_combo
        )

        self.give_client_info = QLabel(
            "No client selected"
        )

        self.give_client_info.setStyleSheet("""
            font-size: 16px;
            padding: 10px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
        """)

        client_layout.addWidget(
            self.give_client_info
        )

        layout.addWidget(
            client_group
        )

        # ====================================================
        # FOOD SECTION
        # ====================================================

        food_search_layout = QHBoxLayout()

        self.give_food_search = QLineEdit()
        self.give_food_search.setPlaceholderText(
            "Search food name, barcode, or description..."
        )
        self.give_food_search.setMinimumHeight(45)

        give_food_search_button = QPushButton("Search")
        give_food_search_button.setMinimumHeight(45)

        food_search_layout.addWidget(
            self.give_food_search
        )

        food_search_layout.addWidget(
            give_food_search_button
        )

        layout.addLayout(
            food_search_layout
        )

        food_select_layout = QHBoxLayout()

        self.give_food_combo = QComboBox()
        self.give_food_combo.setMinimumHeight(45)

        self.give_quantity = QSpinBox()
        self.give_quantity.setRange(1, 100000)
        self.give_quantity.setValue(1)
        self.give_quantity.setMinimumHeight(45)
        self.give_quantity.setMinimumWidth(120)

        add_food_button = QPushButton(
            "➕ Add Food"
        )
        add_food_button.setMinimumHeight(45)

        food_select_layout.addWidget(
            self.give_food_combo
        )

        food_select_layout.addWidget(
            self.give_quantity
        )

        food_select_layout.addWidget(
            add_food_button
        )

        layout.addLayout(
            food_select_layout
        )

        self.give_stock_label = QLabel(
            "Available stock: —"
        )

        self.give_stock_label.setStyleSheet("""
            font-size: 15px;
            color: #6b7280;
            padding: 5px;
        """)

        layout.addWidget(
            self.give_stock_label
        )

        # ====================================================
        # DISTRIBUTION TABLE
        # ====================================================

        self.give_food_table = QTableWidget()

        self.give_food_table.setColumnCount(4)

        self.give_food_table.setHorizontalHeaderLabels([
            "Food",
            "Quantity",
            "Unit",
            "Remove",
        ])

        self.give_food_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.give_food_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.give_food_table.verticalHeader().setVisible(
            False
        )

        self.give_food_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(
            self.give_food_table
        )

        # ====================================================
        # NOTES
        # ====================================================

        self.give_notes = QTextEdit()

        self.give_notes.setPlaceholderText(
            "Optional notes about this distribution..."
        )

        self.give_notes.setMaximumHeight(80)

        layout.addWidget(
            self.give_notes
        )

        # ====================================================
        # BUTTONS
        # ====================================================

        button_layout = QHBoxLayout()

        self.complete_distribution_button = QPushButton(
            "✅ Complete Distribution"
        )

        self.clear_distribution_button = QPushButton(
            "Clear"
        )

        self.complete_distribution_button.setMinimumHeight(
            55
        )

        self.clear_distribution_button.setMinimumHeight(
            55
        )

        button_layout.addWidget(
            self.complete_distribution_button
        )

        button_layout.addWidget(
            self.clear_distribution_button
        )

        layout.addLayout(
            button_layout
        )

        # ====================================================
        # CONNECTIONS
        # ====================================================

        give_client_search_button.clicked.connect(
            self.search_give_clients
        )

        self.give_client_search.returnPressed.connect(
            self.search_give_clients
        )

        self.give_client_combo.currentIndexChanged.connect(
            self.update_give_client_info
        )

        give_food_search_button.clicked.connect(
            self.search_give_food
        )

        self.give_food_search.returnPressed.connect(
            self.search_give_food
        )

        self.give_food_combo.currentIndexChanged.connect(
            self.update_give_stock
        )

        add_food_button.clicked.connect(
            self.add_give_food
        )

        self.complete_distribution_button.clicked.connect(
            self.complete_distribution
        )

        self.clear_distribution_button.clicked.connect(
            self.clear_give_food
        )

        self.give_distribution_items = []

        return page

    # ========================================================
    # GIVE FOOD FUNCTIONS
    # ========================================================

    def open_give_food(self):

        self.pages.setCurrentIndex(0)

        self.load_give_clients()
        self.load_give_food()

        self.give_client_search.setFocus()

    def load_give_clients(self):

        try:

            clients = get_all_clients()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load clients.\n\n{error}"
            )

            return

        self.populate_give_clients(clients)

    def populate_give_clients(self, clients):

        self.give_client_combo.blockSignals(True)

        self.give_client_combo.clear()

        self.give_client_combo.addItem(
            "-- Select Client --",
            None
        )

        for client in clients:

            if not client["active"]:
                continue

            text = (
                f"{client['client_number']} - "
                f"{client['first_name']} "
                f"{client['last_name']}"
            )

            self.give_client_combo.addItem(
                text,
                client["id"]
            )

        self.give_client_combo.blockSignals(False)

        self.update_give_client_info()

    def search_give_clients(self):

        search_term = (
            self.give_client_search.text().strip()
        )

        if not search_term:

            self.load_give_clients()

            return

        try:

            clients = search_clients(
                search_term
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to search clients.\n\n{error}"
            )

            return

        self.populate_give_clients(clients)

    def update_give_client_info(self):

        client_id = (
            self.give_client_combo.currentData()
        )

        if not client_id:

            self.give_client_info.setText(
                "No client selected"
            )

            return

        try:

            client = get_client(client_id)

        except Exception as error:

            self.give_client_info.setText(
                f"Unable to load client: {error}"
            )

            return

        if not client:
            return

        self.give_client_info.setText(
            f"<b>{client['first_name']} "
            f"{client['last_name']}</b>"
            f" &nbsp; | &nbsp; "
            f"Client #: {client['client_number']}"
            f" &nbsp; | &nbsp; "
            f"Household: {client['household_size']}"
            f" &nbsp; | &nbsp; "
            f"Adults: {client['adults']}"
            f" &nbsp; | &nbsp; "
            f"Children: {client['children']}"
        )

    def load_give_food(self):

        try:

            items = get_all_items()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load food items.\n\n{error}"
            )

            return

        self.populate_give_food(items)

    def populate_give_food(self, items):

        self.give_food_combo.blockSignals(True)

        self.give_food_combo.clear()

        self.give_food_combo.addItem(
            "-- Select Food --",
            None
        )

        for item in items:

            if not item["active"]:
                continue

            stock = get_total_stock(
                item["id"]
            )

            text = (
                f"{item['name']} "
                f"({stock} {item['unit']})"
            )

            self.give_food_combo.addItem(
                text,
                item["id"]
            )

        self.give_food_combo.blockSignals(False)

        self.update_give_stock()

    def search_give_food(self):

        search_term = (
            self.give_food_search.text().strip()
        )

        if not search_term:

            self.load_give_food()

            return

        try:

            items = search_items(
                search_term
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to search food.\n\n{error}"
            )

            return

        self.populate_give_food(items)

    def update_give_stock(self):

        item_id = (
            self.give_food_combo.currentData()
        )

        if not item_id:

            self.give_stock_label.setText(
                "Available stock: —"
            )

            return

        try:

            item = get_item(item_id)
            stock = get_total_stock(item_id)

        except Exception as error:

            self.give_stock_label.setText(
                f"Unable to check stock: {error}"
            )

            return

        self.give_stock_label.setText(
            f"Available stock: "
            f"{stock} {item['unit']}"
        )

    def add_give_food(self):

        client_id = (
            self.give_client_combo.currentData()
        )

        if not client_id:

            QMessageBox.warning(
                self,
                "Select Client",
                "Please select a client first."
            )

            return

        item_id = (
            self.give_food_combo.currentData()
        )

        if not item_id:

            QMessageBox.warning(
                self,
                "Select Food",
                "Please select a food item."
            )

            return

        quantity = self.give_quantity.value()

        try:

            item = get_item(item_id)
            stock = get_total_stock(item_id)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to check inventory.\n\n{error}"
            )

            return

        # ----------------------------------------------------
        # Check quantity already added
        # ----------------------------------------------------

        existing_quantity = 0

        for existing in self.give_distribution_items:

            if existing["item_id"] == item_id:

                existing_quantity += existing["quantity"]

        if existing_quantity + quantity > stock:

            QMessageBox.warning(
                self,
                "Not Enough Stock",
                f"Not enough stock for {item['name']}.\n\n"
                f"Available: {stock} {item['unit']}\n"
                f"Already added: {existing_quantity} {item['unit']}\n"
                f"Trying to add: {quantity} {item['unit']}"
            )

            return

        # ----------------------------------------------------
        # Combine duplicate item
        # ----------------------------------------------------

        found = False

        for existing in self.give_distribution_items:

            if existing["item_id"] == item_id:

                existing["quantity"] += quantity

                found = True

                break

        if not found:

            self.give_distribution_items.append({
                "item_id": item_id,
                "quantity": quantity,
                "name": item["name"],
                "unit": item["unit"],
            })

        self.refresh_give_food_table()

        self.give_quantity.setValue(1)

    def refresh_give_food_table(self):

        self.give_food_table.setRowCount(0)

        for index, item in enumerate(
            self.give_distribution_items
        ):

            row = self.give_food_table.rowCount()

            self.give_food_table.insertRow(row)

            self.give_food_table.setItem(
                row,
                0,
                QTableWidgetItem(
                    item["name"]
                )
            )

            self.give_food_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(item["quantity"])
                )
            )

            self.give_food_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    item["unit"]
                )
            )

            remove_button = QPushButton(
                "Remove"
            )

            remove_button.clicked.connect(
                lambda checked=False,
                item_index=index:
                self.remove_give_food(item_index)
            )

            self.give_food_table.setCellWidget(
                row,
                3,
                remove_button
            )

    def remove_give_food(self, index):

        if index < 0:
            return

        if index >= len(
            self.give_distribution_items
        ):
            return

        self.give_distribution_items.pop(index)

        self.refresh_give_food_table()

    def complete_distribution(self):

        client_id = (
            self.give_client_combo.currentData()
        )

        if not client_id:

            QMessageBox.warning(
                self,
                "Select Client",
                "Please select a client."
            )

            return

        if not self.give_distribution_items:

            QMessageBox.warning(
                self,
                "No Food Selected",
                "Please add at least one food item."
            )

            return

        client = get_client(client_id)

        item_count = len(
            self.give_distribution_items
        )

        summary_lines = []

        for item in self.give_distribution_items:

            summary_lines.append(
                f"• {item['name']}: "
                f"{item['quantity']} {item['unit']}"
            )

        summary = "\n".join(summary_lines)

        result = QMessageBox.question(
            self,
            "Complete Distribution",
            f"Give food to:\n"
            f"{client['first_name']} "
            f"{client['last_name']}\n\n"
            f"{summary}\n\n"
            f"Items: {item_count}\n\n"
            f"Complete this distribution?",
            QMessageBox.Yes |
            QMessageBox.No,
            QMessageBox.No
        )

        if result != QMessageBox.Yes:
            return

        database_items = []

        for item in self.give_distribution_items:

            database_items.append({
                "item_id": item["item_id"],
                "quantity": item["quantity"],
            })

        notes = (
            self.give_notes.toPlainText().strip()
            or None
        )

        try:

            distribution_id = create_complete_distribution(
                client_id,
                database_items,
                notes
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Distribution Failed",
                f"The distribution could not be completed.\n\n"
                f"{error}"
            )

            return

        QMessageBox.information(
            self,
            "Distribution Complete",
            f"Food was successfully given to\n"
            f"{client['first_name']} "
            f"{client['last_name']}.\n\n"
            f"Distribution #{distribution_id} was recorded."
        )

        self.clear_give_food()

        self.load_give_clients()
        self.load_give_food()

    def clear_give_food(self):

        self.give_distribution_items.clear()

        self.give_food_table.setRowCount(0)

        self.give_notes.clear()

        self.give_quantity.setValue(1)

        self.give_client_combo.setCurrentIndex(0)
        self.give_food_combo.setCurrentIndex(0)

        self.give_stock_label.setText(
            "Available stock: —"
        )

        self.give_client_info.setText(
            "No client selected"
        )

    # ========================================================
    # RECEIVE FOOD PAGE
    # ========================================================

    def create_receive_page(self):

        page = QWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)

        page.setLayout(layout)

        title = QLabel("📥 Receive Food")

        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        description = QLabel(
            "Scan a barcode to identify the food item."
        )

        description.setStyleSheet("""
            font-size: 16px;
            color: #6b7280;
        """)

        layout.addWidget(description)

        barcode_layout = QHBoxLayout()

        self.receive_barcode = QLineEdit()
        self.receive_barcode.setPlaceholderText(
            "Scan barcode..."
        )
        self.receive_barcode.setMinimumHeight(55)

        self.receive_barcode.setStyleSheet("""
            QLineEdit {
                font-size: 22px;
                padding: 10px;
            }
        """)

        scan_button = QPushButton("🔎 Find Item")
        scan_button.setMinimumHeight(55)
        scan_button.setMinimumWidth(150)

        barcode_layout.addWidget(
            self.receive_barcode
        )

        barcode_layout.addWidget(
            scan_button
        )

        layout.addLayout(barcode_layout)

        self.receive_item_label = QLabel(
            "No item scanned"
        )

        self.receive_item_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 20px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
        """)

        self.receive_item_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.receive_item_label
        )

        self.receive_stock_label = QLabel(
            "Current stock: —"
        )

        self.receive_stock_label.setStyleSheet("""
            font-size: 18px;
            padding: 10px;
        """)

        self.receive_stock_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.receive_stock_label
        )

        form = QFormLayout()

        self.receive_quantity = QSpinBox()
        self.receive_quantity.setRange(1, 100000)
        self.receive_quantity.setValue(1)
        self.receive_quantity.setMinimumHeight(45)

        self.receive_expiry_enabled = QCheckBox(
            "This batch has an expiry date"
        )

        self.receive_expiry_enabled.setChecked(True)

        self.receive_expiry = QDateEdit()
        self.receive_expiry.setCalendarPopup(True)
        self.receive_expiry.setDate(
            QDate.currentDate()
        )
        self.receive_expiry.setMinimumDate(
            QDate.currentDate()
        )
        self.receive_expiry.setMinimumHeight(45)

        self.receive_location = QLineEdit()
        self.receive_location.setPlaceholderText(
            "Example: Shelf A"
        )
        self.receive_location.setMinimumHeight(45)

        self.receive_lot = QLineEdit()
        self.receive_lot.setPlaceholderText(
            "Optional"
        )
        self.receive_lot.setMinimumHeight(45)

        form.addRow(
            "Quantity:",
            self.receive_quantity
        )

        form.addRow(
            "Expiry:",
            self.receive_expiry_enabled
        )

        form.addRow(
            "Expiry Date:",
            self.receive_expiry
        )

        form.addRow(
            "Storage Location:",
            self.receive_location
        )

        form.addRow(
            "Lot Number:",
            self.receive_lot
        )

        layout.addLayout(form)

        button_layout = QHBoxLayout()

        self.receive_add_button = QPushButton(
            "➕ Add Stock"
        )

        self.receive_clear_button = QPushButton(
            "Clear / Scan Next"
        )

        self.receive_add_button.setMinimumHeight(55)
        self.receive_clear_button.setMinimumHeight(55)

        button_layout.addWidget(
            self.receive_add_button
        )

        button_layout.addWidget(
            self.receive_clear_button
        )

        layout.addLayout(button_layout)

        layout.addStretch()

        scan_button.clicked.connect(
            self.find_receive_item
        )

        self.receive_barcode.returnPressed.connect(
            self.find_receive_item
        )

        self.receive_add_button.clicked.connect(
            self.add_received_stock
        )

        self.receive_clear_button.clicked.connect(
            self.clear_receive_form
        )

        self.receive_expiry_enabled.toggled.connect(
            self.receive_expiry.setEnabled
        )

        self.receive_add_button.setEnabled(False)

        self.receive_item_id = None

        return page

    # ========================================================
    # RECEIVE FUNCTIONS
    # ========================================================

    def open_receive(self):

        self.pages.setCurrentIndex(4)

        self.clear_receive_form()

        self.receive_barcode.setFocus()

    def find_receive_item(self):

        barcode = self.receive_barcode.text().strip()

        if not barcode:
            return

        try:

            item = get_item_by_barcode(barcode)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to search for barcode.\n\n{error}"
            )

            return

        if not item:

            self.receive_item_label.setText(
                "❌ Barcode not found"
            )

            self.receive_stock_label.setText(
                "No inventory item matches this barcode."
            )

            self.receive_add_button.setEnabled(False)

            QMessageBox.warning(
                self,
                "Item Not Found",
                f"No active food item was found with barcode:\n\n"
                f"{barcode}\n\n"
                f"Add the item to Inventory first."
            )

            return

        self.receive_item_id = item["id"]

        self.receive_item_label.setText(
            f"🥫 {item['name']}"
        )

        current_stock = get_total_stock(
            item["id"]
        )

        self.receive_stock_label.setText(
            f"Current stock: "
            f"{current_stock} "
            f"{item['unit']}"
        )

        self.receive_add_button.setEnabled(True)

        self.receive_quantity.setFocus()
        self.receive_quantity.selectAll()

    def add_received_stock(self):

        if not self.receive_item_id:

            QMessageBox.warning(
                self,
                "No Item Selected",
                "Scan a valid barcode first."
            )

            return

        quantity = self.receive_quantity.value()

        if self.receive_expiry_enabled.isChecked():

            expiry_date = (
                self.receive_expiry.date()
                .toString("yyyy-MM-dd")
            )

        else:

            expiry_date = None

        location = (
            self.receive_location.text().strip()
            or None
        )

        lot_number = (
            self.receive_lot.text().strip()
            or None
        )

        try:

            add_stock(
                self.receive_item_id,
                quantity,
                expiry_date,
                location,
                lot_number,
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to add stock.\n\n{error}"
            )

            return

        item = get_item(
            self.receive_item_id
        )

        QMessageBox.information(
            self,
            "Stock Added",
            f"Successfully added:\n\n"
            f"{quantity} {item['unit']} of "
            f"{item['name']}"
        )

        self.clear_receive_form()

        self.receive_barcode.setFocus()

    def clear_receive_form(self):

        self.receive_barcode.clear()

        self.receive_item_id = None

        self.receive_item_label.setText(
            "No item scanned"
        )

        self.receive_stock_label.setText(
            "Current stock: —"
        )

        self.receive_quantity.setValue(1)

        self.receive_expiry_enabled.setChecked(True)

        self.receive_expiry.setDate(
            QDate.currentDate()
        )

        self.receive_location.clear()
        self.receive_lot.clear()

        self.receive_add_button.setEnabled(False)

        self.receive_barcode.setFocus()

    # ========================================================
    # CLIENTS PAGE
    # ========================================================

    def create_clients_page(self):

        page = QWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        page.setLayout(layout)

        title = QLabel("Clients")

        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        search_layout = QHBoxLayout()

        self.client_search = QLineEdit()
        self.client_search.setPlaceholderText(
            "Search client number, first name, or last name..."
        )
        self.client_search.setMinimumHeight(45)

        search_button = QPushButton("Search")
        clear_button = QPushButton("Clear")

        search_button.setMinimumHeight(45)
        clear_button.setMinimumHeight(45)

        search_layout.addWidget(
            self.client_search
        )

        search_layout.addWidget(
            search_button
        )

        search_layout.addWidget(
            clear_button
        )

        layout.addLayout(search_layout)

        self.client_table = QTableWidget()
        self.client_table.setColumnCount(6)

        self.client_table.setHorizontalHeaderLabels([
            "Client Number",
            "First Name",
            "Last Name",
            "Phone",
            "Status",
            "Actions",
        ])

        self.client_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.client_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.client_table.verticalHeader().setVisible(
            False
        )

        self.client_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(
            self.client_table
        )

        button_layout = QHBoxLayout()

        add_button = QPushButton("+ Add Client")
        refresh_button = QPushButton("Refresh")
        history_button = QPushButton("📜 View History")

        add_button.setMinimumHeight(50)
        refresh_button.setMinimumHeight(50)
        history_button.setMinimumHeight(50)

        button_layout.addWidget(add_button)
        button_layout.addWidget(history_button)
        button_layout.addWidget(refresh_button)

        layout.addLayout(button_layout)

        search_button.clicked.connect(
            self.search_clients
        )

        self.client_search.returnPressed.connect(
            self.search_clients
        )

        clear_button.clicked.connect(
            self.clear_client_search
        )

        refresh_button.clicked.connect(
            self.load_clients
        )

        add_button.clicked.connect(
            self.show_add_client
        )

        history_button.clicked.connect(
            self.open_selected_client_history
        )

        return page

    # ========================================================
    # CLIENT FUNCTIONS
    # ========================================================

    def open_clients(self):

        self.pages.setCurrentIndex(1)

        self.load_clients()

    def load_clients(self):

        try:

            clients = get_all_clients()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load clients.\n\n{error}"
            )

            return

        self.populate_client_table(clients)

    def populate_client_table(self, clients):

        self.client_table.setRowCount(0)

        for client in clients:

            row = self.client_table.rowCount()

            self.client_table.insertRow(row)

            self.client_table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(client["client_number"])
                )
            )

            self.client_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(client["first_name"])
                )
            )

            self.client_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(client["last_name"])
                )
            )

            self.client_table.setItem(
                row,
                3,
                QTableWidgetItem(
                    str(client["phone"] or "")
                )
            )

            status = (
                "Active"
                if client["active"]
                else "Inactive"
            )

            self.client_table.setItem(
                row,
                4,
                QTableWidgetItem(status)
            )

            actions_widget = QWidget()

            actions_layout = QHBoxLayout(
                actions_widget
            )

            actions_layout.setContentsMargins(
                4, 2, 4, 2
            )

            edit_button = QPushButton("Edit")

            edit_button.clicked.connect(
                lambda checked=False,
                client_id=client["id"]:
                self.edit_client(client_id)
            )

            actions_layout.addWidget(
                edit_button
            )

            history_button = QPushButton("History")

            history_button.clicked.connect(
                lambda checked=False,
                client_id=client["id"]:
                self.show_client_history(client_id)
            )

            actions_layout.addWidget(
                history_button
            )

            if client["active"]:

                action_button = QPushButton(
                    "Remove"
                )

                action_button.clicked.connect(
                    lambda checked=False,
                    client_id=client["id"]:
                    self.remove_client(client_id)
                )

            else:

                action_button = QPushButton(
                    "Restore"
                )

                action_button.clicked.connect(
                    lambda checked=False,
                    client_id=client["id"]:
                    self.restore_client(client_id)
                )

            actions_layout.addWidget(
                action_button
            )

            self.client_table.setCellWidget(
                row,
                5,
                actions_widget
            )

    def search_clients(self):

        search_term = (
            self.client_search.text().strip()
        )

        if not search_term:

            self.load_clients()

            return

        try:

            clients = search_clients(
                search_term
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to search clients.\n\n{error}"
            )

            return

        self.populate_client_table(clients)

    def clear_client_search(self):

        self.client_search.clear()

        self.load_clients()

    # ========================================================
    # ADD CLIENT
    # ========================================================

    def show_add_client(self):

        dialog = QDialog(self)

        dialog.setWindowTitle("Add Client")
        dialog.resize(450, 500)

        layout = QFormLayout()
        dialog.setLayout(layout)

        client_number = QLineEdit()
        first_name = QLineEdit()
        last_name = QLineEdit()
        phone = QLineEdit()
        email = QLineEdit()

        household_size = QSpinBox()
        household_size.setRange(1, 50)
        household_size.setValue(1)

        adults = QSpinBox()
        adults.setRange(0, 50)
        adults.setValue(1)

        children = QSpinBox()
        children.setRange(0, 50)

        notes = QTextEdit()
        notes.setMaximumHeight(100)

        layout.addRow("Client Number:", client_number)
        layout.addRow("First Name:", first_name)
        layout.addRow("Last Name:", last_name)
        layout.addRow("Phone:", phone)
        layout.addRow("Email:", email)
        layout.addRow("Household Size:", household_size)
        layout.addRow("Adults:", adults)
        layout.addRow("Children:", children)
        layout.addRow("Notes:", notes)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        layout.addRow(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() != QDialog.Accepted:
            return

        if not client_number.text().strip():

            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter a client number."
            )

            return

        if not first_name.text().strip():

            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter a first name."
            )

            return

        if not last_name.text().strip():

            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter a last name."
            )

            return

        try:

            add_client(
                client_number.text().strip(),
                first_name.text().strip(),
                last_name.text().strip(),
                phone.text().strip() or None,
                email.text().strip() or None,
                household_size.value(),
                adults.value(),
                children.value(),
                notes.toPlainText().strip() or None,
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to add client.\n\n{error}"
            )

            return

        QMessageBox.information(
            self,
            "Client Added",
            "The client was successfully added."
        )

        self.load_clients()

    # ========================================================
    # EDIT CLIENT
    # ========================================================

    def edit_client(self, client_id):

        try:

            client = get_client(client_id)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load client.\n\n{error}"
            )

            return

        if not client:
            return

        dialog = QDialog(self)

        dialog.setWindowTitle("Edit Client")
        dialog.resize(450, 500)

        layout = QFormLayout()
        dialog.setLayout(layout)

        client_number = QLineEdit(
            str(client["client_number"])
        )

        client_number.setReadOnly(True)

        first_name = QLineEdit(
            str(client["first_name"] or "")
        )

        last_name = QLineEdit(
            str(client["last_name"] or "")
        )

        phone = QLineEdit(
            str(client["phone"] or "")
        )

        email = QLineEdit(
            str(client["email"] or "")
        )

        household_size = QSpinBox()
        household_size.setRange(1, 50)
        household_size.setValue(
            int(client["household_size"] or 1)
        )

        adults = QSpinBox()
        adults.setRange(0, 50)
        adults.setValue(
            int(client["adults"] or 0)
        )

        children = QSpinBox()
        children.setRange(0, 50)
        children.setValue(
            int(client["children"] or 0)
        )

        notes = QTextEdit()
        notes.setMaximumHeight(100)
        notes.setPlainText(
            str(client["notes"] or "")
        )

        layout.addRow("Client Number:", client_number)
        layout.addRow("First Name:", first_name)
        layout.addRow("Last Name:", last_name)
        layout.addRow("Phone:", phone)
        layout.addRow("Email:", email)
        layout.addRow("Household Size:", household_size)
        layout.addRow("Adults:", adults)
        layout.addRow("Children:", children)
        layout.addRow("Notes:", notes)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save |
            QDialogButtonBox.Cancel
        )

        layout.addRow(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() != QDialog.Accepted:
            return

        try:

            update_client(
                client_id,
                first_name.text().strip(),
                last_name.text().strip(),
                phone.text().strip() or None,
                email.text().strip() or None,
                household_size.value(),
                adults.value(),
                children.value(),
                notes.toPlainText().strip() or None,
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to update client.\n\n{error}"
            )

            return

        self.load_clients()

    # ========================================================
    # REMOVE / RESTORE CLIENT
    # ========================================================

    def remove_client(self, client_id):

        try:

            client = get_client(client_id)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load client.\n\n{error}"
            )

            return

        if not client:
            return

        name = (
            f"{client['first_name']} "
            f"{client['last_name']}"
        )

        result = QMessageBox.question(
            self,
            "Remove Client",
            f"Are you sure you want to remove\n"
            f"{name}?\n\n"
            f"The client's history will NOT be deleted.",
            QMessageBox.Yes |
            QMessageBox.No,
            QMessageBox.No
        )

        if result != QMessageBox.Yes:
            return

        try:

            deactivate_client(client_id)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to remove client.\n\n{error}"
            )

            return

        self.load_clients()

    def restore_client(self, client_id):

        try:

            reactivate_client(client_id)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to restore client.\n\n{error}"
            )

            return

        self.load_clients()

    # ========================================================
    # HISTORY PAGE
    # ========================================================

    def create_history_page(self):

        page = QWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(
            40, 40, 40, 40
        )
        layout.setSpacing(15)

        page.setLayout(layout)

        title = QLabel("📜 Client History")

        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        description = QLabel(
            "View the food distribution history for a client."
        )

        description.setStyleSheet("""
            font-size: 16px;
            color: #6b7280;
        """)

        layout.addWidget(description)

        search_layout = QHBoxLayout()

        self.history_client_search = QLineEdit()

        self.history_client_search.setPlaceholderText(
            "Search client number, first name, or last name..."
        )

        self.history_client_search.setMinimumHeight(45)

        history_search_button = QPushButton(
            "Search"
        )

        history_clear_button = QPushButton(
            "Clear"
        )

        history_search_button.setMinimumHeight(45)
        history_clear_button.setMinimumHeight(45)

        search_layout.addWidget(
            self.history_client_search
        )

        search_layout.addWidget(
            history_search_button
        )

        search_layout.addWidget(
            history_clear_button
        )

        layout.addLayout(search_layout)

        self.history_client_table = QTableWidget()

        self.history_client_table.setColumnCount(4)

        self.history_client_table.setHorizontalHeaderLabels([
            "Client Number",
            "First Name",
            "Last Name",
            "Status",
        ])

        self.history_client_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.history_client_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.history_client_table.verticalHeader().setVisible(
            False
        )

        self.history_client_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(
            self.history_client_table
        )

        select_button = QPushButton(
            "📜 View Selected Client History"
        )

        select_button.setMinimumHeight(50)

        layout.addWidget(
            select_button
        )

        history_search_button.clicked.connect(
            self.search_history_clients
        )

        self.history_client_search.returnPressed.connect(
            self.search_history_clients
        )

        history_clear_button.clicked.connect(
            self.clear_history_search
        )

        select_button.clicked.connect(
            self.open_selected_client_history
        )

        self.history_client_table.cellDoubleClicked.connect(
            lambda row, column:
            self.open_history_for_row(row)
        )

        return page

    def open_history(self):

        self.pages.setCurrentIndex(2)

        self.load_history_clients()

        self.history_client_search.setFocus()

    def load_history_clients(self):

        try:

            clients = get_all_clients()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load clients.\n\n{error}"
            )

            return

        self.populate_history_client_table(
            clients
        )

    def populate_history_client_table(
        self,
        clients
    ):

        self.history_client_table.setRowCount(0)

        for client in clients:

            row = self.history_client_table.rowCount()

            self.history_client_table.insertRow(row)

            self.history_client_table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(client["client_number"])
                )
            )

            self.history_client_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(client["first_name"])
                )
            )

            self.history_client_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(client["last_name"])
                )
            )

            status = (
                "Active"
                if client["active"]
                else "Inactive"
            )

            self.history_client_table.setItem(
                row,
                3,
                QTableWidgetItem(status)
            )

            self.history_client_table.item(
                row,
                0
            ).setData(
                Qt.UserRole,
                client["id"]
            )

    def search_history_clients(self):

        search_term = (
            self.history_client_search.text().strip()
        )

        if not search_term:

            self.load_history_clients()

            return

        try:

            clients = search_clients(
                search_term
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to search clients.\n\n{error}"
            )

            return

        self.populate_history_client_table(
            clients
        )

    def clear_history_search(self):

        self.history_client_search.clear()

        self.load_history_clients()

    def open_selected_client_history(self):

        row = (
            self.history_client_table.currentRow()
        )

        if row < 0:

            QMessageBox.information(
                self,
                "Select Client",
                "Please select a client first."
            )

            return

        self.open_history_for_row(row)

    def open_history_for_row(self, row):

        item = self.history_client_table.item(
            row,
            0
        )

        if not item:
            return

        client_id = item.data(
            Qt.UserRole
        )

        if not client_id:
            return

        self.show_client_history(
            client_id
        )

    # ========================================================
    # CLIENT HISTORY DIALOG
    # ========================================================

    def show_client_history(self, client_id):

        try:

            client = get_client(
                client_id
            )

            summary = get_client_distribution_summary(
                client_id
            )

            visit_count = get_client_distribution_count(
                client_id
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load client history.\n\n{error}"
            )

            return

        if not client:
            return

        dialog = QDialog(self)

        dialog.setWindowTitle(
            "Client Food History"
        )

        dialog.resize(
            900,
            650
        )

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        name = (
            f"{client['first_name']} "
            f"{client['last_name']}"
        )

        client_label = QLabel(
            f"👤 {name}"
        )

        client_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        layout.addWidget(
            client_label
        )

        number_label = QLabel(
            f"Client Number: "
            f"{client['client_number']}"
        )

        number_label.setStyleSheet("""
            font-size: 16px;
            color: #6b7280;
        """)

        layout.addWidget(
            number_label
        )

        visits_label = QLabel(
            f"Total Visits: {visit_count}"
        )

        visits_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 10px 0;
        """)

        layout.addWidget(
            visits_label
        )

        table = QTableWidget()

        table.setColumnCount(3)

        table.setHorizontalHeaderLabels([
            "Date",
            "Items",
            "Total Quantity",
        ])

        table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        table.verticalHeader().setVisible(
            False
        )

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(
            table
        )

        for distribution in summary:

            row = table.rowCount()

            table.insertRow(row)

            table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(
                        distribution[
                            "distribution_date"
                        ]
                    )
                )
            )

            table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(
                        distribution[
                            "item_types"
                        ]
                    )
                )
            )

            table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(
                        distribution[
                            "total_quantity"
                        ]
                    )
                )
            )

            table.item(
                row,
                0
            ).setData(
                Qt.UserRole,
                distribution[
                    "distribution_id"
                ]
            )

        instructions = QLabel(
            "Double-click a visit to see the food that was given."
        )

        instructions.setStyleSheet("""
            color: #6b7280;
            padding: 5px;
        """)

        layout.addWidget(
            instructions
        )

        close_button = QPushButton(
            "Close"
        )

        close_button.setMinimumHeight(45)

        layout.addWidget(
            close_button
        )

        close_button.clicked.connect(
            dialog.accept
        )

        def view_distribution(row, column):

            item = table.item(row, 0)

            if not item:
                return

            distribution_id = item.data(
                Qt.UserRole
            )

            if distribution_id:

                self.show_distribution_details(
                    distribution_id
                )

        table.cellDoubleClicked.connect(
            view_distribution
        )

        dialog.exec()

    # ========================================================
    # DISTRIBUTION DETAILS
    # ========================================================

    def show_distribution_details(
        self,
        distribution_id
    ):

        try:

            items = get_distribution_items(
                distribution_id
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load distribution details.\n\n{error}"
            )

            return

        dialog = QDialog(self)

        dialog.setWindowTitle(
            "Food Distribution Details"
        )

        dialog.resize(
            650,
            450
        )

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        title = QLabel(
            "📦 Food Given"
        )

        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
        """)

        layout.addWidget(
            title
        )

        table = QTableWidget()

        table.setColumnCount(3)

        table.setHorizontalHeaderLabels([
            "Food",
            "Quantity",
            "Unit",
        ])

        table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        table.verticalHeader().setVisible(
            False
        )

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(
            table
        )

        for item in items:

            row = table.rowCount()

            table.insertRow(row)

            table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(item["item_name"])
                )
            )

            table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(item["quantity"])
                )
            )

            table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(item["unit"])
                )
            )

        close_button = QPushButton(
            "Close"
        )

        close_button.setMinimumHeight(45)

        layout.addWidget(
            close_button
        )

        close_button.clicked.connect(
            dialog.accept
        )

        dialog.exec()

    # ========================================================
    # INVENTORY PAGE
    # ========================================================

    def create_inventory_page(self):

        page = QWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(
            40, 40, 40, 40
        )
        layout.setSpacing(15)

        page.setLayout(layout)

        title = QLabel("Inventory")

        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        search_layout = QHBoxLayout()

        self.inventory_search = QLineEdit()

        self.inventory_search.setPlaceholderText(
            "Search food name, barcode, or description..."
        )

        self.inventory_search.setMinimumHeight(45)

        search_button = QPushButton("Search")
        clear_button = QPushButton("Clear")

        search_button.setMinimumHeight(45)
        clear_button.setMinimumHeight(45)

        search_layout.addWidget(
            self.inventory_search
        )

        search_layout.addWidget(
            search_button
        )

        search_layout.addWidget(
            clear_button
        )

        layout.addLayout(search_layout)

        self.inventory_table = QTableWidget()

        self.inventory_table.setColumnCount(7)

        self.inventory_table.setHorizontalHeaderLabels([
            "Food",
            "Barcode",
            "Category",
            "Quantity",
            "Unit",
            "Expiry Tracking",
            "Actions",
        ])

        self.inventory_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.inventory_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.inventory_table.verticalHeader().setVisible(
            False
        )

        self.inventory_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(
            self.inventory_table
        )

        button_layout = QHBoxLayout()

        add_button = QPushButton("+ Add Item")
        receive_button = QPushButton("📥 Receive Stock")
        remove_button = QPushButton("📤 Remove Stock")
        category_button = QPushButton("📂 Categories")
        refresh_button = QPushButton("🔄 Refresh")

        for button in (
            add_button,
            receive_button,
            remove_button,
            category_button,
            refresh_button,
        ):
            button.setMinimumHeight(50)

        button_layout.addWidget(add_button)
        button_layout.addWidget(receive_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(category_button)
        button_layout.addWidget(refresh_button)

        layout.addLayout(button_layout)

        search_button.clicked.connect(
            self.search_inventory
        )

        self.inventory_search.returnPressed.connect(
            self.search_inventory
        )

        clear_button.clicked.connect(
            self.clear_inventory_search
        )

        add_button.clicked.connect(
            self.show_add_item
        )

        receive_button.clicked.connect(
            self.open_receive
        )

        remove_button.clicked.connect(
            self.show_remove_stock
        )

        category_button.clicked.connect(
            self.show_categories
        )

        refresh_button.clicked.connect(
            self.load_inventory
        )

        return page

    # ========================================================
    # INVENTORY FUNCTIONS
    # ========================================================

    def open_inventory(self):

        self.pages.setCurrentIndex(3)

        self.load_inventory()

    def load_inventory(self):

        try:

            items = get_all_items()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load inventory.\n\n{error}"
            )

            return

        self.populate_inventory_table(items)

    def populate_inventory_table(self, items):

        self.inventory_table.setRowCount(0)

        for item in items:

            row = self.inventory_table.rowCount()

            self.inventory_table.insertRow(row)

            self.inventory_table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(item["name"])
                )
            )

            self.inventory_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(item["barcode"] or "")
                )
            )

            self.inventory_table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(item["category_name"] or "")
                )
            )

            try:

                quantity = get_total_stock(
                    item["id"]
                )

            except Exception:

                quantity = 0

            self.inventory_table.setItem(
                row,
                3,
                QTableWidgetItem(
                    str(quantity)
                )
            )

            self.inventory_table.setItem(
                row,
                4,
                QTableWidgetItem(
                    str(item["unit"] or "unit")
                )
            )

            expiry = (
                "Yes"
                if item["expiry_tracking"]
                else "No"
            )

            self.inventory_table.setItem(
                row,
                5,
                QTableWidgetItem(expiry)
            )

            actions_widget = QWidget()

            actions_layout = QHBoxLayout(
                actions_widget
            )

            actions_layout.setContentsMargins(
                4, 2, 4, 2
            )

            edit_button = QPushButton("Edit")

            edit_button.clicked.connect(
                lambda checked=False,
                item_id=item["id"]:
                self.edit_item(item_id)
            )

            actions_layout.addWidget(
                edit_button
            )

            if item["active"]:

                action_button = QPushButton(
                    "Remove"
                )

                action_button.clicked.connect(
                    lambda checked=False,
                    item_id=item["id"]:
                    self.deactivate_inventory_item(
                        item_id
                    )
                )

            else:

                action_button = QPushButton(
                    "Restore"
                )

                action_button.clicked.connect(
                    lambda checked=False,
                    item_id=item["id"]:
                    self.restore_inventory_item(
                        item_id
                    )
                )

            actions_layout.addWidget(
                action_button
            )

            self.inventory_table.setCellWidget(
                row,
                6,
                actions_widget
            )

    def search_inventory(self):

        search_term = (
            self.inventory_search.text().strip()
        )

        if not search_term:

            self.load_inventory()

            return

        try:

            items = search_items(
                search_term
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to search inventory.\n\n{error}"
            )

            return

        self.populate_inventory_table(items)

    def clear_inventory_search(self):

        self.inventory_search.clear()

        self.load_inventory()

    # ========================================================
    # ADD ITEM
    # ========================================================

    def show_add_item(self):

        dialog = QDialog(self)

        dialog.setWindowTitle(
            "Add Food Item"
        )

        dialog.resize(450, 500)

        layout = QFormLayout()
        dialog.setLayout(layout)

        name = QLineEdit()
        barcode = QLineEdit()

        description = QTextEdit()
        description.setMaximumHeight(80)

        category = QComboBox()

        category.addItem(
            "No Category",
            None
        )

        try:

            categories = get_all_categories()

            for cat in categories:

                category.addItem(
                    str(cat["name"]),
                    cat["id"]
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load categories.\n\n{error}"
            )

            return

        unit = QLineEdit("unit")

        minimum_stock = QSpinBox()
        minimum_stock.setRange(0, 100000)

        expiry_tracking = QCheckBox()
        expiry_tracking.setChecked(True)

        layout.addRow("Food Name:", name)
        layout.addRow("Barcode:", barcode)
        layout.addRow("Description:", description)
        layout.addRow("Category:", category)
        layout.addRow("Unit:", unit)
        layout.addRow("Minimum Stock:", minimum_stock)
        layout.addRow("Track Expiry:", expiry_tracking)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        layout.addRow(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() != QDialog.Accepted:
            return

        if not name.text().strip():

            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter a food name."
            )

            return

        try:

            add_item(
                name.text().strip(),
                barcode.text().strip() or None,
                description.toPlainText().strip() or None,
                category.currentData(),
                unit.text().strip() or "unit",
                minimum_stock.value(),
                expiry_tracking.isChecked(),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to add item.\n\n{error}"
            )

            return

        QMessageBox.information(
            self,
            "Item Added",
            "The food item was successfully added."
        )

        self.load_inventory()

    # ========================================================
    # EDIT ITEM
    # ========================================================

    def edit_item(self, item_id):

        try:

            item = get_item(item_id)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load item.\n\n{error}"
            )

            return

        if not item:
            return

        dialog = QDialog(self)

        dialog.setWindowTitle(
            "Edit Food Item"
        )

        dialog.resize(450, 500)

        layout = QFormLayout()
        dialog.setLayout(layout)

        name = QLineEdit(
            str(item["name"] or "")
        )

        barcode = QLineEdit(
            str(item["barcode"] or "")
        )

        description = QTextEdit()
        description.setMaximumHeight(80)

        description.setPlainText(
            str(item["description"] or "")
        )

        category = QComboBox()

        category.addItem(
            "No Category",
            None
        )

        try:

            categories = get_all_categories()

            for cat in categories:

                category.addItem(
                    str(cat["name"]),
                    cat["id"]
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load categories.\n\n{error}"
            )

            return

        if item["category_id"] is not None:

            index = category.findData(
                item["category_id"]
            )

            if index >= 0:
                category.setCurrentIndex(index)

        unit = QLineEdit(
            str(item["unit"] or "unit")
        )

        minimum_stock = QSpinBox()
        minimum_stock.setRange(0, 100000)

        minimum_stock.setValue(
            int(item["minimum_stock"] or 0)
        )

        expiry_tracking = QCheckBox()

        expiry_tracking.setChecked(
            bool(item["expiry_tracking"])
        )

        layout.addRow("Food Name:", name)
        layout.addRow("Barcode:", barcode)
        layout.addRow("Description:", description)
        layout.addRow("Category:", category)
        layout.addRow("Unit:", unit)
        layout.addRow("Minimum Stock:", minimum_stock)
        layout.addRow("Track Expiry:", expiry_tracking)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save |
            QDialogButtonBox.Cancel
        )

        layout.addRow(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() != QDialog.Accepted:
            return

        try:

            update_item(
                item_id,
                name.text().strip(),
                barcode.text().strip() or None,
                description.toPlainText().strip() or None,
                category.currentData(),
                unit.text().strip() or "unit",
                minimum_stock.value(),
                expiry_tracking.isChecked(),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to update item.\n\n{error}"
            )

            return

        self.load_inventory()

    # ========================================================
    # DEACTIVATE / RESTORE ITEM
    # ========================================================

    def deactivate_inventory_item(self, item_id):

        try:

            item = get_item(item_id)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load item.\n\n{error}"
            )

            return

        if not item:
            return

        result = QMessageBox.question(
            self,
            "Deactivate Item",
            f"Are you sure you want to deactivate\n"
            f"{item['name']}?\n\n"
            f"Existing stock and history will not be deleted.",
            QMessageBox.Yes |
            QMessageBox.No,
            QMessageBox.No
        )

        if result != QMessageBox.Yes:
            return

        try:

            deactivate_item(item_id)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to deactivate item.\n\n{error}"
            )

            return

        self.load_inventory()

    def restore_inventory_item(self, item_id):

        try:

            reactivate_item(item_id)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to restore item.\n\n{error}"
            )

            return

        self.load_inventory()

    # ========================================================
    # CATEGORIES
    # ========================================================

    def show_categories(self):

        dialog = QDialog(self)

        dialog.setWindowTitle(
            "Manage Categories"
        )

        dialog.resize(
            550,
            450
        )

        layout = QVBoxLayout()
        dialog.setLayout(layout)

        title = QLabel(
            "Inventory Categories"
        )

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        category_table = QTableWidget()

        category_table.setColumnCount(2)

        category_table.setHorizontalHeaderLabels([
            "Category",
            "Description",
        ])

        category_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        category_table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        category_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        category_table.verticalHeader().setVisible(
            False
        )

        layout.addWidget(
            category_table
        )

        def load_categories():

            try:

                categories = get_all_categories()

            except Exception as error:

                QMessageBox.critical(
                    dialog,
                    "Database Error",
                    f"Unable to load categories.\n\n{error}"
                )

                return

            category_table.setRowCount(0)

            for category in categories:

                row = category_table.rowCount()

                category_table.insertRow(row)

                category_table.setItem(
                    row,
                    0,
                    QTableWidgetItem(
                        str(category["name"])
                    )
                )

                category_table.setItem(
                    row,
                    1,
                    QTableWidgetItem(
                        str(category["description"] or "")
                    )
                )

        button_layout = QHBoxLayout()

        add_button = QPushButton(
            "+ Add Category"
        )

        close_button = QPushButton(
            "Close"
        )

        button_layout.addWidget(
            add_button
        )

        button_layout.addStretch()

        button_layout.addWidget(
            close_button
        )

        layout.addLayout(
            button_layout
        )

        def add_new_category():

            add_dialog = QDialog(dialog)

            add_dialog.setWindowTitle(
                "Add Category"
            )

            add_dialog.resize(
                400,
                220
            )

            form = QFormLayout()

            add_dialog.setLayout(form)

            name = QLineEdit()

            description = QLineEdit()

            form.addRow(
                "Category Name:",
                name
            )

            form.addRow(
                "Description:",
                description
            )

            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok |
                QDialogButtonBox.Cancel
            )

            form.addRow(buttons)

            buttons.accepted.connect(
                add_dialog.accept
            )

            buttons.rejected.connect(
                add_dialog.reject
            )

            if add_dialog.exec() != QDialog.Accepted:
                return

            category_name = (
                name.text().strip()
            )

            if not category_name:

                QMessageBox.warning(
                    add_dialog,
                    "Missing Information",
                    "Please enter a category name."
                )

                return

            try:

                add_category(
                    category_name,
                    description.text().strip() or None
                )

            except Exception as error:

                QMessageBox.critical(
                    add_dialog,
                    "Unable to Add Category",
                    str(error)
                )

                return

            load_categories()

        add_button.clicked.connect(
            add_new_category
        )

        close_button.clicked.connect(
            dialog.accept
        )

        load_categories()

        dialog.exec()

    # ========================================================
    # REMOVE STOCK
    # ========================================================

    def show_remove_stock(self):

        try:

            items = get_all_items()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                f"Unable to load inventory items.\n\n{error}"
            )

            return

        if not items:

            QMessageBox.information(
                self,
                "No Items",
                "There are no active food items."
            )

            return

        dialog = QDialog(self)

        dialog.setWindowTitle(
            "Remove Stock"
        )

        dialog.resize(
            450,
            250
        )

        layout = QFormLayout()

        dialog.setLayout(layout)

        item_combo = QComboBox()

        for item in items:

            if not item["active"]:
                continue

            current_stock = get_total_stock(
                item["id"]
            )

            item_combo.addItem(
                f"{item['name']} "
                f"({current_stock} "
                f"{item['unit']})",
                item["id"]
            )

        quantity = QSpinBox()

        quantity.setRange(
            1,
            100000
        )

        layout.addRow(
            "Food Item:",
            item_combo
        )

        layout.addRow(
            "Quantity to Remove:",
            quantity
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok |
            QDialogButtonBox.Cancel
        )

        layout.addRow(buttons)

        buttons.accepted.connect(
            dialog.accept
        )

        buttons.rejected.connect(
            dialog.reject
        )

        if dialog.exec() != QDialog.Accepted:
            return

        try:

            removed = remove_stock(
                item_combo.currentData(),
                quantity.value()
            )

        except Exception as error:

            QMessageBox.warning(
                self,
                "Unable to Remove Stock",
                str(error)
            )

            return

        total_removed = sum(
            batch["quantity_removed"]
            for batch in removed
        )

        QMessageBox.information(
            self,
            "Stock Removed",
            f"Successfully removed "
            f"{total_removed} unit(s) of stock.\n\n"
            f"The earliest-expiring stock was used first."
        )

        self.load_inventory()

    # ========================================================
    # LOGOUT
    # ========================================================

    def logout(self):

        from UI.MainWindow import MainWindow

        self.login_window = MainWindow()

        self.login_window.show()

        self.close()