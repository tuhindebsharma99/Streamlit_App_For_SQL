from idlelib import query
from unittest import result

import mysql.connector


def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="python_sql_project"
    )


def get_basic_info(cursor):
    queries = {
        "Total Suppliers" : "SELECT COUNT(*) AS total_suppliers FROM suppliers",

        "Total Products" : "SELECT COUNT(*) AS total_products FROM products",

        "Total unique Categories" : "SELECT COUNT(DISTINCT category) AS total_categories FROM products",

        "Total sales value of last 3 months" : """SELECT ROUND(SUM(ABS(se.change_quantity)*p.price),2) AS total_sales_3_months
                                                FROM stock_entries as se
                                                LEFT JOIN products as p
                                                ON se.product_id = p.product_id
                                                WHERE se.change_type = "Sale"
                                                AND se.entry_date>=
                                                    (SELECT date_sub(MAX(entry_date), interval 3 month) FROM stock_entries)""",
                                                                                                                           
        "Total Restock value of last 3 months" : """SELECT ROUND(SUM(ABS(se.change_quantity)*p.price),2) AS total_restock_3_months
                                                FROM stock_entries as se
                                                LEFT JOIN products as p
                                                ON se.product_id = p.product_id
                                                WHERE se.change_type = "Restock"
                                                AND se.entry_date>=
                                                    (SELECT date_sub(MAX(entry_date), interval 3 month) FROM stock_entries)""",
                                                                                                                           
        "Below reorder & No Pending reorders" : """SELECT COUNT(*) AS below_reorder
                                                FROM products AS p
                                                WHERE p.stock_quantity<p.reorder_level
                                                AND product_id NOT IN
                                                (
                                                SELECT DISTINCT product_id FROM reorders WHERE status = "Pending"
                                                )"""
            }
    result = {}
    for label, query in queries.items():
        cursor.execute(query)
        row=cursor.fetchone()
        result[label]=list(row.values())[0]

    return result


def get_tables(cursor):
    queries = {
        "Suppliers and their contact details" : "SELECT supplier_name, contact_name, email, phone FROM suppliers",

        "Product with their Suppliers and Current stock" : """SELECT p.product_id, p.product_name, p.price, p.stock_quantity, s.supplier_name
                                                            FROM products AS p
                                                            LEFT JOIN suppliers AS s
                                                            ON p.supplier_id=s.supplier_id""",

        "Product needing Reorder" : """SELECT product_id, product_name, stock_quantity, reorder_level
                                    FROM products
                                    WHERE stock_quantity<reorder_level"""

    }

    tables = {}
    for label, query in queries.items():
        cursor.execute(query)
        tables[label]=cursor.fetchall()

    return tables


def add_new_manualid(cursor, db, p_name, p_category, p_price, p_stock, p_reorder, p_supplier):
    proc_call = "call AddNewProductManualID(%s, %s, %s, %s, %s, %s)"
    params = (p_name, p_category, p_price, p_stock, p_reorder, p_supplier)
    cursor.execute(proc_call, params)
    db.commit()


def get_categories(cursor):
    cursor.execute("select distinct category from products order by category asc")
    rows = cursor.fetchall()
    return [row["category"] for row in rows]


def get_suppliers(cursor):
    cursor.execute("select supplier_id, supplier_name from suppliers order by supplier_name asc")
    return cursor.fetchall()

def get_all_products(cursor):
    cursor.execute("select product_id, product_name from products order by product_name asc")
    return cursor.fetchall()

def get_product_history(cursor, product_id):
    query = "select * from product_history where product_id = %s order by record_date desc"
    cursor.execute(query, (product_id,))
    return cursor.fetchall()

def place_reorder(cursor, db, product_id, reorder_quantity):
    query = """insert into reorders(reorder_id, product_id, reorder_quantity, reorder_date, status)
        select max(reorder_id)+1, %s, %s, curdate(), "Ordered"
        from reorders;"""
    cursor.execute(query, (product_id, reorder_quantity))
    db.commit()

def get_pending_reorders(cursor):
    cursor.execute("""select r.reorder_id, p.product_name from reorders as r
                    LEFT JOIN products as p
                    on r.product_id = p.product_id
                    where r.status = "Ordered"
                    """)
    return cursor.fetchall()

def mark_reorder_as_received(cursor, db, reorder_id):
    cursor.callproc("MarkReorderAsReceived", (reorder_id,))
    db.commit()



































