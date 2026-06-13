import streamlit as st
import numpy as np
import pandas as pd
from streamlit import exception

from db_functions import (
    connect_to_db,
    get_basic_info,
    get_tables,
    add_new_manualid,
    get_categories,
    get_suppliers,
    get_all_products,
    get_product_history,
    place_reorder,
    get_pending_reorders,
    mark_reorder_as_received
)

# sidebar
st.sidebar.title("Inventory Management Dashboard")
option = st.sidebar.radio("Select Option:", ["Basic Information","Operational Tasks"])

# main space
st.title("Inventory & Supply Chain Dashboard")
db = connect_to_db()
cursor = db.cursor(dictionary=True)

# Basic Information page
if option == "Basic Information":
    st.header("Basic Metrics")

    #get basic info from database
    basic_info = get_basic_info(cursor)

    cols=st.columns(3)
    keys=list(basic_info.keys())

    for i in range(3):
        cols[i].metric(label=keys[i], value=basic_info[keys[i]])

    cols=st.columns(3)
    for i in range(3,6):
        cols[i-3].metric(label=keys[i], value=basic_info[keys[i]])


    st.divider()

    #displaying tables
    tables = get_tables(cursor)
    for label, data in tables.items():
        st.header(label)
        df = pd.DataFrame(data)
        st.dataframe(df)
        st.divider()

# Operational Task page

elif option == "Operational Tasks":
    st.header("Operational Tasks")
    selected_task = st.selectbox(" Choose a Task",["Add New Product","Product History","Place Reorder","Receive Reorder"])


    # Adding new Product
    if selected_task == "Add New Product":
        st.header("Add New Product")
        categories = get_categories(cursor)
        suppliers = get_suppliers(cursor)

        with st.form("Add_Product"):
            product_name = st.text_input("Enter Product Name")
            product_category = st.selectbox("Select Category",categories)
            product_price = st.number_input("Enter Product Price", min_value = 0)
            product_stock = st.number_input("Enter Product Quantity", min_value = 0, step=1)
            product_level = st.number_input("Enter Reorder level", min_value = 0, step=1)
            selected_supplier = st.selectbox("Choose a Supplier",
                                       options = suppliers,
                                       format_func = lambda s: f"ID: {s['supplier_id']} | Name: {s['supplier_name']}"
                                       )
            supplier_id = selected_supplier["supplier_id"]

            submitted = st.form_submit_button("Add Product", type="primary")

            if submitted:
                if not product_name:
                    st.error("Product Name is required")
                else:
                    try:
                        add_new_manualid(cursor,
                                         db,
                                         product_name,
                                         product_category,
                                         product_price,
                                         product_stock,
                                         product_level,
                                         supplier_id)
                        st.success(f"Product {product_name} Added Successfully")
                    except exception as e:
                        st.error(f"Error adding product: {e}")


    # Checking Product history
    elif selected_task == "Product History":
        st.header("Product Inventory History")
        products=get_all_products(cursor)
        selected_product = st.selectbox("Select a Product",
                                        options = products,
                                        format_func=lambda x:f"ID: {x['product_id']} | Name: {x['product_name']}"
                                        )
        product_id = selected_product['product_id']
        history = get_product_history(cursor, product_id)
        st.subheader(f"Product History for {selected_product['product_name']}")
        st.dataframe(history)


    # Placing reorder
    elif selected_task == "Place Reorder":
        st.header("Place a Reorder")
        products = get_all_products(cursor)
        selected_product = st.selectbox("Select a Product",
                                        options=products,
                                        format_func=lambda x: f"ID: {x['product_id']} | Name: {x['product_name']}"
                                        )
        reorder_quantity = st.number_input("Enter Reorder Quantity", min_value = 0, step=1)

        if st.button("Place Reorder", type="primary"):
            if not selected_product:
                st.error("Product Name is required")
            elif reorder_quantity <= 0:
                st.error("Reorder quantity must be greater than 0")
            else:
                try:
                    product_id = selected_product['product_id']
                    place_reorder(cursor, db, product_id, reorder_quantity)
                    st.success(f"Successfully ordered {reorder_quantity} units of {selected_product['product_name']}")
                except Exception as e:
                    st.error(f"Error placing reorder: {e}")
        else:
            pass


    # Receiving reorders
    elif selected_task == "Receive Reorder":
        st.header("Mark Reorder as Received")
        pending_reorder = get_pending_reorders(cursor)
        selected_reorder = st.selectbox("Select a Pending Reorder",
                                        options=pending_reorder,
                                        format_func=lambda x: f"Reorder ID: {x['reorder_id']} | Name: {x['product_name']}"
                                        )
        if st.button("Mark Rorder as Received", type="primary"):
            try:
                reorder_id = selected_reorder['reorder_id']
                mark_reorder_as_received(cursor, db, reorder_id)
                st.success(f"Successfully accepted reorder {reorder_id} for {selected_reorder['product_name']}")
                st.rerun # To clear the processed orders from the list
            except Exception as e:
                st.error(f"Error accepting reorder: {e}")
        else:
            pass

    else:
        st.warning("Please select an option")



























