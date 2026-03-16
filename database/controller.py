import sqlite3

DB_NAME = "bookstore.db"

def get_active_books():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT id, bookname, price, qty FROM books WHERE is_active = 1")
    rows = cur.fetchall()
    con.close()
    return rows

def add_book(isbn, name, price, qty):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("INSERT INTO books (isbn, bookname, price, qty) VALUES (?, ?, ?, ?)", (isbn, name, price, qty))
    con.commit()
    con.close()

def delete_book(book_id):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("UPDATE books SET is_active = 0 WHERE id = ?", (book_id,))
    con.commit()
    con.close()

def process_checkout(cart, total_amount, customer_info):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO orders (total, customer_info) VALUES (?, ?)", (total_amount, customer_info))
        order_id = cur.lastrowid

        for b_id, info in cart.items():
            cur.execute("SELECT qty FROM books WHERE id = ?", (b_id,))
            current_stock = cur.fetchone()[0]
            
            if current_stock < info['qty']:
                raise ValueError(f"หนังสือ '{info['name']}' สต๊อกไม่พอ (เหลือ {current_stock})")

            subtotal = info['qty'] * info['price']
            cur.execute("""
                INSERT INTO order_items (order_id, book_id, qty, price, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, b_id, info['qty'], info['price'], subtotal))

            cur.execute("UPDATE books SET qty = qty - ? WHERE id = ?", (info['qty'], b_id))

        con.commit()
        return True, "บันทึกการขายและตัดสต๊อกเรียบร้อยแล้ว!"
    except Exception as e:
        con.rollback()
        return False, str(e)
    finally:
        con.close()