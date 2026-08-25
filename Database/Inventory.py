from Database.Database import get_connection


# ============================================================
# CATEGORIES
# ============================================================

def add_category(name, description=None):
    """Add a new inventory category."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO categories (name, description)
            VALUES (?, ?)
            """,
            (name, description),
        )

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_category(category_id):
    """Get a category by its database ID."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT *
            FROM categories
            WHERE id = ?
            """,
            (category_id,),
        ).fetchone()

    finally:
        connection.close()


def find_category(name):
    """Find a category by its exact name."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT *
            FROM categories
            WHERE name = ?
            """,
            (name,),
        ).fetchone()

    finally:
        connection.close()


def get_all_categories():
    """Return all categories."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT *
            FROM categories
            ORDER BY name
            """
        ).fetchall()

    finally:
        connection.close()


# ============================================================
# ITEMS
# ============================================================

def add_item(
    name,
    barcode=None,
    description=None,
    category_id=None,
    unit="unit",
    minimum_stock=0,
    expiry_tracking=True,
):
    """Add a new food item."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO items (
                barcode,
                name,
                description,
                category_id,
                unit,
                minimum_stock,
                expiry_tracking
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                barcode,
                name,
                description,
                category_id,
                unit,
                minimum_stock,
                int(expiry_tracking),
            ),
        )

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_item(item_id):
    """Get an item by its database ID."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                items.*,
                categories.name AS category_name
            FROM items
            LEFT JOIN categories
                ON items.category_id = categories.id
            WHERE items.id = ?
            """,
            (item_id,),
        ).fetchone()

    finally:
        connection.close()


def get_item_by_barcode(barcode):
    """Find an item using its barcode."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                items.*,
                categories.name AS category_name
            FROM items
            LEFT JOIN categories
                ON items.category_id = categories.id
            WHERE items.barcode = ?
              AND items.active = 1
            """,
            (barcode,),
        ).fetchone()

    finally:
        connection.close()


def search_items(search_term):
    """Search items by name, description, or barcode."""

    connection = get_connection()

    try:
        search = f"%{search_term}%"

        return connection.execute(
            """
            SELECT
                items.*,
                categories.name AS category_name
            FROM items
            LEFT JOIN categories
                ON items.category_id = categories.id
            WHERE items.active = 1
              AND (
                    items.name LIKE ?
                    OR items.description LIKE ?
                    OR items.barcode LIKE ?
                  )
            ORDER BY items.name
            """,
            (search, search, search),
        ).fetchall()

    finally:
        connection.close()


def get_all_items(include_inactive=False):
    """Return all inventory items."""

    connection = get_connection()

    try:
        if include_inactive:
            return connection.execute(
                """
                SELECT
                    items.*,
                    categories.name AS category_name
                FROM items
                LEFT JOIN categories
                    ON items.category_id = categories.id
                ORDER BY items.name
                """
            ).fetchall()

        return connection.execute(
            """
            SELECT
                items.*,
                categories.name AS category_name
            FROM items
            LEFT JOIN categories
                ON items.category_id = categories.id
            WHERE items.active = 1
            ORDER BY items.name
            """
        ).fetchall()

    finally:
        connection.close()


def update_item(
    item_id,
    name,
    barcode=None,
    description=None,
    category_id=None,
    unit="unit",
    minimum_stock=0,
    expiry_tracking=True,
):
    """Update an existing item."""

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE items
            SET
                name = ?,
                barcode = ?,
                description = ?,
                category_id = ?,
                unit = ?,
                minimum_stock = ?,
                expiry_tracking = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                name,
                barcode,
                description,
                category_id,
                unit,
                minimum_stock,
                int(expiry_tracking),
                item_id,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def deactivate_item(item_id):
    """Deactivate an item without deleting its history."""

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE items
            SET
                active = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (item_id,),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def reactivate_item(item_id):
    """Reactivate a previously deactivated item."""

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE items
            SET
                active = 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (item_id,),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# STOCK / INVENTORY
# ============================================================

def add_stock(
    item_id,
    quantity,
    expiry_date=None,
    storage_location=None,
    lot_number=None,
):
    """Add a new batch of stock to inventory."""

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO inventory (
                item_id,
                quantity,
                expiry_date,
                storage_location,
                lot_number
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                item_id,
                quantity,
                expiry_date,
                storage_location,
                lot_number,
            ),
        )

        connection.commit()
        return cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_stock_batch(batch_id):
    """Get a single inventory batch."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                inventory.*,
                items.name AS item_name,
                items.barcode,
                items.unit
            FROM inventory
            JOIN items
                ON inventory.item_id = items.id
            WHERE inventory.id = ?
            """,
            (batch_id,),
        ).fetchone()

    finally:
        connection.close()


def get_stock_for_item(item_id):
    """Get all inventory batches for an item."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                inventory.*,
                items.name AS item_name,
                items.unit AS unit
            FROM inventory
            JOIN items
                ON inventory.item_id = items.id
            WHERE inventory.item_id = ?
              AND inventory.quantity > 0
            ORDER BY
                CASE
                    WHEN inventory.expiry_date IS NULL THEN 1
                    ELSE 0
                END,
                inventory.expiry_date,
                inventory.id
            """,
            (item_id,),
        ).fetchall()

    finally:
        connection.close()


def get_total_stock(item_id):
    """Get the total quantity currently in stock for an item."""

    connection = get_connection()

    try:
        result = connection.execute(
            """
            SELECT COALESCE(SUM(quantity), 0) AS total
            FROM inventory
            WHERE item_id = ?
            """,
            (item_id,),
        ).fetchone()

        return result["total"]

    finally:
        connection.close()


def get_all_stock():
    """Get all inventory currently in stock."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                inventory.*,
                items.name AS item_name,
                items.barcode,
                items.unit,
                categories.name AS category_name
            FROM inventory
            JOIN items
                ON inventory.item_id = items.id
            LEFT JOIN categories
                ON items.category_id = categories.id
            WHERE inventory.quantity > 0
            ORDER BY
                items.name,
                CASE
                    WHEN inventory.expiry_date IS NULL THEN 1
                    ELSE 0
                END,
                inventory.expiry_date
            """
        ).fetchall()

    finally:
        connection.close()


def get_low_stock_items():
    """Return items whose total stock is at or below their minimum."""

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                items.id,
                items.name,
                items.barcode,
                items.unit,
                items.minimum_stock,
                COALESCE(SUM(inventory.quantity), 0) AS current_stock
            FROM items
            LEFT JOIN inventory
                ON items.id = inventory.item_id
            WHERE items.active = 1
            GROUP BY
                items.id,
                items.name,
                items.barcode,
                items.unit,
                items.minimum_stock
            HAVING current_stock <= items.minimum_stock
            ORDER BY current_stock ASC, items.name
            """
        ).fetchall()

    finally:
        connection.close()


def get_expiring_stock(days=30):
    """Return stock that expires within the specified number of days."""

    if days < 0:
        raise ValueError("Days cannot be negative.")

    connection = get_connection()

    try:
        return connection.execute(
            """
            SELECT
                inventory.*,
                items.name AS item_name,
                items.barcode,
                items.unit
            FROM inventory
            JOIN items
                ON inventory.item_id = items.id
            WHERE inventory.quantity > 0
              AND inventory.expiry_date IS NOT NULL
              AND date(inventory.expiry_date)
                  <= date('now', '+' || ? || ' days')
            ORDER BY date(inventory.expiry_date)
            """,
            (days,),
        ).fetchall()

    finally:
        connection.close()


def update_stock_quantity(batch_id, quantity):
    """Set the quantity of an existing inventory batch."""

    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE inventory
            SET
                quantity = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (quantity, batch_id),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

def remove_stock(item_id, quantity):
    """
    Remove stock using FEFO:
    First Expiring, First Out.

    Returns a list of the inventory batches affected.
    """

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")

    connection = get_connection()

    try:
        # Get available batches in expiry order
        batches = connection.execute(
            """
            SELECT *
            FROM inventory
            WHERE item_id = ?
              AND quantity > 0
            ORDER BY
                CASE
                    WHEN expiry_date IS NULL THEN 1
                    ELSE 0
                END,
                expiry_date,
                id
            """,
            (item_id,),
        ).fetchall()

        total_available = sum(batch["quantity"] for batch in batches)

        if total_available < quantity:
            raise ValueError(
                f"Not enough stock available. "
                f"Requested: {quantity}, "
                f"Available: {total_available}"
            )

        remaining = quantity
        affected_batches = []

        for batch in batches:
            if remaining <= 0:
                break

            amount_to_remove = min(
                batch["quantity"],
                remaining,
            )

            new_quantity = batch["quantity"] - amount_to_remove

            connection.execute(
                """
                UPDATE inventory
                SET
                    quantity = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    new_quantity,
                    batch["id"],
                ),
            )

            affected_batches.append(
                {
                    "batch_id": batch["id"],
                    "item_id": item_id,
                    "quantity_removed": amount_to_remove,
                    "expiry_date": batch["expiry_date"],
                    "storage_location": batch["storage_location"],
                    "lot_number": batch["lot_number"],
                }
            )

            remaining -= amount_to_remove

        connection.commit()

        return affected_batches

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()