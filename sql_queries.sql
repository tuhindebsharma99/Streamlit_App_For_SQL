SELECT * FROM products
SELECT * FROM reorders
SELECT * FROM shipments
SELECT * FROM stock_entries
SELECT * FROM suppliers

-- 1 Total Suppliers
SELECT COUNT(*) AS total_suppliers FROM suppliers

-- 2 Total Products
SELECT COUNT(*) AS total_products FROM products

-- 3 Total unique Categories
SELECT COUNT(DISTINCT category) AS total_categories FROM products

-- 4 Total sales value of last 3 months
SELECT ROUND(SUM(ABS(se.change_quantity)*p.price),2) AS total_sales_3_months
FROM stock_entries as se
LEFT JOIN products as p
ON se.product_id = p.product_id
WHERE se.change_type = "Sale"
AND se.entry_date>=
	(SELECT date_sub(MAX(entry_date), interval 3 month) FROM stock_entries)
    
-- 5 Total Restock value of last 3 months
SELECT ROUND(SUM(ABS(se.change_quantity)*p.price),2) AS total_restock_3_months
FROM stock_entries as se
LEFT JOIN products as p
ON se.product_id = p.product_id
WHERE se.change_type = "Restock"
AND se.entry_date>=
	(SELECT date_sub(MAX(entry_date), interval 3 month) FROM stock_entries)
    
-- 6 Below reorder & No Pending reorders
SELECT COUNT(*) AS below_reorder
FROM products AS p
WHERE p.stock_quantity<p.reorder_level
AND product_id NOT IN
(
SELECT DISTINCT product_id FROM reorders WHERE status = "Pending"
)  
SELECT DATABASE();

-- 7 Suppliers and their contact details
SELECT supplier_name, contact_name, email, phone FROM suppliers

-- 8 Product with their Suppliers and Current stock
SELECT p.product_id, p.product_name, p.price, p.stock_quantity, s.supplier_name
FROM products AS p
LEFT JOIN suppliers AS s
ON p.supplier_id=s.supplier_id

-- 9 Product needing Reorder
SELECT product_id, product_name, stock_quantity, reorder_level
FROM products
WHERE stock_quantity<reorder_level

-- 10 Add a new product to the database
delimiter $$
create procedure AddNewProductManualID(
	in p_name varchar(255),
    in p_category varchar(100),
    in p_price decimal(10,2),
    in p_stock int,
    in p_reorder int,
    in p_supplier int
)

Begin
	declare new_prod_id int;
    declare new_shipment_id int;
    declare new_entry_id int;

	#Making changes in product table

	#Generating New Product id for New Prodcut
	SELECT MAX(product_id)+1 into new_prod_id FROM products;

	INSERT INTO products(product_id, product_name, category, price, stock_quantity, reorder_level, supplier_id)
	VALUES(new_prod_id, p_name, p_category, p_price, p_stock, p_reorder, p_supplier);


	#Making changes in shipment table

	#Generating New shipment id for New Prodcut
	SELECT MAX(shipment_id)+1 into new_shipment_id FROM shipments;

	INSERT INTO shipments(shipment_id, product_id, supplier_id, quantity_received, shipment_date)
	VALUES(new_shipment_id, new_prod_id, p_supplier, p_stock, curdate());


	#Making changes in stock_entries table

	#Generating New entry id for New Prodcut
	SELECT MAX(entry_id)+1 into new_entry_id FROM stock_entries;

	INSERT INTO stock_entries(entry_id, product_id, change_quantity, change_type, entry_date)
	VALUES(new_entry_id, new_prod_id, p_stock, "Restock", curdate());
end $$
Delimiter ;

select * from shipments

-- 11 Product History (Finding shipment, sales, purchase)
create or replace view product_history as
select shipstock.*, p.supplier_id from
(
select product_id,
"Shipment" as record_type,
shipment_date as record_date,
quantity_received as quantity,
null change_type
from shipments
union all
select product_id,
"Stock Entry" as record_type,
entry_date as record_date,
change_quantity as quantity,
change_type
from stock_entries
) as shipstock
LEFT JOIN
products as p
ON shipstock.product_id = p.product_id

-- 12 Place a reorder
select * from reorders
insert into reorders(reorder_id, product_id, reorder_quantity,reorder_date, status)

-- 13 Receive reorders
delimiter $$
create procedure MarkReorderAsReceived( in in_reorder_id int)
begin
declare prod_id int;
declare qty int;
declare sup_id int;
declare new_shipment_id int;
declare new_entry_id int;

start Transaction;
# Getting product_id, quantity from reorders
select product_id, reorder_quantity
into prod_id, qty
from reorders
where reorder_id = in_reorder_id;

# Getting supplier_id from products
select supplier_id
into sup_id
from products
where product_id = prod_id;

#Updating reorders table to "Received"
update reorders
set status = "Received"
where reorder_id = in_reorder_id;

#Updating quantity in products table
update products
set stock_quantity = stock_quantity+qty
where product_id = prod_id;

#Updating shipments table
select max(shipment_id)+1 into new_shipment_id from shipments;
insert into shipments(shipment_id, product_id, supplier_id, quantity_received, shipment_date)
values(new_shipment_id, prod_id, sup_id, qty, curdate());

#Updating stock_entries table
select max(entry_id)+1 into new_entry_id from stock_entries;
insert into stock_entries(entry_id, product_id, change_quantity, change_type, entry_date)
values(new_entry_id, prod_id, qty, "Restock", curdate());

commit;
end $$

Delimiter ;









    
    
    
    




























    