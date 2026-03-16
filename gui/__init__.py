import tkinter as tk
from tkinter import ttk, messagebox

class BookstorePOS:
    def __init__(self, root):
        self.root = root
        self.root.title("ระบบ POS ร้านหนังสือออนไลน์")
        self.root.geometry("850x500")
        self.root.config(padx=10, pady=10)

        # ข้อมูลจำลอง (Mock Data) สำหรับหนังสือและราคา
        self.books = {
            "Python 101 พื้นฐาน": 250,
            "เจาะลึก Data Science": 450,
            "พัฒนาเว็บด้วย Django": 350,
            "จิตวิทยาการลงทุน": 280,
            "มังงะ ผจญภัยต่างโลก Vol.1": 90
        }
        
        # ตะกร้าสินค้า {ชื่อหนังสือ: [จำนวน, ราคาต้อชิ้น]}
        self.cart = {} 

        self.create_widgets()

    def create_widgets(self):
        # --- สร้าง Frame หลัก ---
        left_frame = tk.LabelFrame(self.root, text="รายการหนังสือ", padx=10, pady=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=5)

        right_frame = tk.LabelFrame(self.root, text="ตะกร้าสินค้า", padx=10, pady=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=5)

        # ================= ส่วนซ้าย: รายการหนังสือ =================
        self.book_listbox = tk.Listbox(left_frame, font=("Arial", 12))
        self.book_listbox.pack(fill="both", expand=True, pady=5)

        # ใส่ข้อมูลหนังสือลงใน Listbox
        for book, price in self.books.items():
            self.book_listbox.insert(tk.END, f"{book} - {price} ฿")

        btn_add = tk.Button(left_frame, text="เพิ่มลงตะกร้า 🛒", bg="#4CAF50", fg="white", font=("Arial", 12), command=self.add_to_cart)
        btn_add.pack(fill="x", pady=5)

        # ================= ส่วนขวา: ตะกร้าสินค้า =================
        # ใช้ Treeview สำหรับแสดงตารางสินค้า
        columns = ("name", "qty", "price", "total")
        self.cart_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=10)
        self.cart_tree.heading("name", text="ชื่อหนังสือ")
        self.cart_tree.heading("qty", text="จำนวน")
        self.cart_tree.heading("price", text="ราคา/เล่ม")
        self.cart_tree.heading("total", text="รวม")
        
        self.cart_tree.column("name", width=150)
        self.cart_tree.column("qty", width=50, anchor="center")
        self.cart_tree.column("price", width=70, anchor="e")
        self.cart_tree.column("total", width=70, anchor="e")
        self.cart_tree.pack(fill="both", expand=True, pady=5)

        # แสดงยอดรวม
        self.lbl_total = tk.Label(right_frame, text="ยอดรวม: 0 ฿", font=("Arial", 16, "bold"), fg="red")
        self.lbl_total.pack(anchor="e", pady=10)

        # ปุ่มจัดการ
        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(fill="x")

        btn_clear = tk.Button(btn_frame, text="ล้างตะกร้า 🗑️", bg="#f44336", fg="white", font=("Arial", 12), command=self.clear_cart)
        btn_clear.pack(side="left", fill="x", expand=True, padx=2)

        btn_checkout = tk.Button(btn_frame, text="ชำระเงิน 💳", bg="#2196F3", fg="white", font=("Arial", 12), command=self.checkout)
        btn_checkout.pack(side="right", fill="x", expand=True, padx=2)

    # ================= ฟังก์ชันการทำงาน =================
    def add_to_cart(self):
        selected = self.book_listbox.curselection()
        if not selected:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกหนังสือที่ต้องการเพิ่มลงตะกร้า")
            return

        book_info = self.book_listbox.get(selected[0])
        book_name = book_info.split(" - ")[0]
        price = self.books[book_name]

        if book_name in self.cart:
            self.cart[book_name][0] += 1 # เพิ่มจำนวน
        else:
            self.cart[book_name] = [1, price] # [จำนวน, ราคา]

        self.update_cart_display()

    def update_cart_display(self):
        # ล้างข้อมูลเดิมในตารางก่อน
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)

        total_amount = 0
        # ใส่ข้อมูลใหม่ลงตาราง
        for name, info in self.cart.items():
            qty = info[0]
            price = info[1]
            total = qty * price
            total_amount += total
            self.cart_tree.insert("", "end", values=(name, qty, f"{price:,.0f}", f"{total:,.0f}"))

        self.lbl_total.config(text=f"ยอดรวม: {total_amount:,.2f} ฿")

    def clear_cart(self):
        self.cart.clear()
        self.update_cart_display()

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("แจ้งเตือน", "ตะกร้าสินค้าว่างเปล่า!")
            return
            
        messagebox.showinfo("สำเร็จ", "ทำรายการชำระเงินเรียบร้อยแล้ว!\nขอบคุณที่ใช้บริการ")
        self.clear_cart()

if __name__ == "__main__":
    root = tk.Tk()
    app = BookstorePOS(root)
    root.mainloop()