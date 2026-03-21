"""
โมดูลตั้งค่าและติดตั้งโครงสร้างฐานข้อมูล (Database Schema setup)
ถูกเรียกใช้ครั้งแรกเสมอตอนเริ่มต้นโปรแกรม
"""

import sqlite3

def init_db():
    """
    ตรวจสอบและสร้างตารางฐานข้อมูลที่จำเป็น หากยังไม่มีอยู่
    พร้อมกับเพิ่มข้อมูลทดสอบเบื้องต้น (Mock Data) หากตารางหนังสือว่างเปล่า
    """
    # จะถูกสร้างที่โฟลเดอร์นอกสุด (root) ตอนรัน main
    con = sqlite3.connect("bookstore.db") 
    cur = con.cursor()
    
    # รันสคริปต์ SQL เพื่อสร้างโครงสร้างตาราง
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT UNIQUE,
        bookname TEXT NOT NULL,
        price REAL NOT NULL CHECK(price >= 0),
        qty INTEGER NOT NULL DEFAULT 0 CHECK(qty >= 0),
        is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1))
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total REAL NOT NULL CHECK(total >= 0),
        customer_info TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        qty INTEGER NOT NULL CHECK(qty > 0),
        price REAL NOT NULL CHECK(price >= 0),
        subtotal REAL NOT NULL,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(book_id) REFERENCES books(id)
    );
    """)

    # หากเพิ่งสร้าง DB ครั้งแรก จะมีข้อมูลเบื้องต้นให้ 2 เล่ม
    if __name__ == "__main__":
        cur.execute("SELECT COUNT(*) FROM books")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO books (isbn, bookname, price, qty) VALUES ('9781234567890', 'Python Programming', 350, 10)")
            cur.execute("INSERT INTO books (isbn, bookname, price, qty) VALUES ('9780987654321', 'Database Design', 250, 5)")
        
        con.commit()
        con.close()
