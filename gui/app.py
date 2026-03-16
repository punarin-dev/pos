import tkinter as tk
from tkinter import ttk, messagebox

# Import module จากโฟลเดอร์ database
from database import setup_db, controller 

class BookstoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("POS ร้านหนังสือออนไลน์")
        self.root.geometry("1100x600")
        
        self.cart = {} 
        
        # เช็ค/สร้างฐานข้อมูลตอนเปิดแอป
        setup_db.init_db() 
        
        self.create_widgets()
        self.refresh_book_list()

    def create_widgets(self):
        menu_frame = tk.Frame(self.root)
        menu_frame.pack(fill="x", padx=5, pady=5)
        
        self.mb = tk.Menubutton(menu_frame, text="⚙️ จัดการข้อมูล (Menu)", relief=tk.RAISED)
        self.mb.menu = tk.Menu(self.mb, tearoff=0)
        self.mb["menu"] = self.mb.menu
        self.mb.menu.add_command(label="➕ เพิ่มหนังสือใหม่", command=self.open_add_book_window)
        self.mb.menu.add_command(label="❌ ลบหนังสือ (ซ่อนข้อมูล)", command=self.delete_book_gui)
        self.mb.pack(side="left")

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ---------------- เฟรม 1 ----------------
        frame1 = tk.LabelFrame(main_frame, text="1. รายการหนังสือ", padx=10, pady=10)
        frame1.pack(side="left", fill="both", expand=True, padx=5)

        columns1 = ("id", "name", "price", "stock")
        self.book_tree = ttk.Treeview(frame1, columns=columns1, show="headings", height=15)
        for col, text in zip(columns1, ["ID", "ชื่อหนังสือ", "ราคา", "คงเหลือ"]):
            self.book_tree.heading(col, text=text)
        self.book_tree.column("id", width=30, anchor="center")
        self.book_tree.column("name", width=150)
        self.book_tree.column("price", width=50, anchor="e")
        self.book_tree.column("stock", width=50, anchor="center")
        self.book_tree.pack(fill="both", expand=True)

        tk.Button(frame1, text="เพิ่มเข้าตะกร้า ➡️", bg="#4CAF50", fg="white", command=self.add_to_cart).pack(fill="x", pady=5)

        # ---------------- เฟรม 2 ----------------
        frame2 = tk.LabelFrame(main_frame, text="2. ตะกร้าสินค้า", padx=10, pady=10)
        frame2.pack(side="left", fill="both", expand=True, padx=5)

        columns2 = ("id", "name", "qty", "subtotal")
        self.cart_tree = ttk.Treeview(frame2, columns=columns2, show="headings", height=15)
        for col, text in zip(columns2, ["ID", "ชื่อหนังสือ", "จำนวน", "รวม"]):
            self.cart_tree.heading(col, text=text)
        self.cart_tree.column("id", width=30, anchor="center")
        self.cart_tree.column("name", width=150)
        self.cart_tree.column("qty", width=50, anchor="center")
        self.cart_tree.column("subtotal", width=60, anchor="e")
        self.cart_tree.pack(fill="both", expand=True)

        tk.Button(frame2, text="❌ ลบจากตะกร้า", bg="#f44336", fg="white", command=self.remove_from_cart).pack(fill="x", pady=5)

        # ---------------- เฟรม 3 ----------------
        frame3 = tk.LabelFrame(main_frame, text="3. ยืนยันการสั่งซื้อและจัดส่ง", padx=10, pady=10)
        frame3.pack(side="left", fill="both", expand=True, padx=5)

        self.lbl_total = tk.Label(frame3, text="ยอดรวม: 0.00 ฿", font=("Arial", 14, "bold"), fg="blue")
        self.lbl_total.pack(anchor="w", pady=5)

        self.wrap_var = tk.IntVar()
        tk.Checkbutton(frame3, text="ห่อของขวัญ (+20 ฿)", variable=self.wrap_var, command=self.update_cart_display).pack(anchor="w")

        tk.Label(frame3, text="ช่องทางการชำระเงิน:").pack(anchor="w", pady=(10,0))
        self.pay_var = tk.StringVar(value="โอนเงิน")
        tk.Radiobutton(frame3, text="โอนเงินผ่านธนาคาร", variable=self.pay_var, value="โอนเงิน").pack(anchor="w")
        tk.Radiobutton(frame3, text="เก็บเงินปลายทาง", variable=self.pay_var, value="ปลายทาง").pack(anchor="w")

        tk.Label(frame3, text="ข้อมูลผู้ซื้อและที่อยู่จัดส่ง:").pack(anchor="w", pady=(10,0))
        self.txt_address = tk.Text(frame3, height=5, width=30)
        self.txt_address.pack(fill="x", pady=5)

        tk.Button(frame3, text="✅ ยืนยันคำสั่งซื้อ", bg="#2196F3", fg="white", font=("Arial", 12, "bold"), command=self.checkout_gui).pack(fill="x", pady=10)

    # ================= ฟังก์ชันเชื่อมโยง =================
    def refresh_book_list(self):
        for row in self.book_tree.get_children():
            self.book_tree.delete(row)
            
        books = controller.get_active_books()
        for row in books:
            self.book_tree.insert("", "end", values=row)

    def add_to_cart(self):
        selected = self.book_tree.focus()
        if not selected:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกหนังสือจากรายการ")
            return
            
        item = self.book_tree.item(selected)["values"]
        book_id, name, price, stock = item

        if stock <= 0:
            messagebox.showerror("ข้อผิดพลาด", "สินค้าหมด!")
            return

        if book_id in self.cart:
            if self.cart[book_id]['qty'] < stock:
                self.cart[book_id]['qty'] += 1
            else:
                messagebox.showwarning("แจ้งเตือน", "สินค้าในสต๊อกไม่เพียงพอ")
        else:
            self.cart[book_id] = {'name': name, 'price': float(price), 'qty': 1, 'stock': int(stock)}

        self.update_cart_display()

    def remove_from_cart(self):
        selected = self.cart_tree.focus()
        if not selected:
            return
        book_id = self.cart_tree.item(selected)["values"][0]
        
        if book_id in self.cart:
            self.cart[book_id]['qty'] -= 1
            if self.cart[book_id]['qty'] <= 0:
                del self.cart[book_id]
        self.update_cart_display()

    def update_cart_display(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)

        total_amount = sum(info['qty'] * info['price'] for info in self.cart.values())
        
        for b_id, info in self.cart.items():
            subtotal = info['qty'] * info['price']
            self.cart_tree.insert("", "end", values=(b_id, info['name'], info['qty'], f"{subtotal:,.2f}"))

        if self.wrap_var.get() == 1:
            total_amount += 20 
            
        self.lbl_total.config(text=f"ยอดรวม: {total_amount:,.2f} ฿")

    def checkout_gui(self):
        if not self.cart:
            messagebox.showwarning("แจ้งเตือน", "ตะกร้าสินค้าว่างเปล่า")
            return
            
        address = self.txt_address.get("1.0", tk.END).strip()
        if not address:
            messagebox.showwarning("แจ้งเตือน", "กรุณากรอกข้อมูลจัดส่ง")
            return

        total_amount = sum(item['qty'] * item['price'] for item in self.cart.values())
        if self.wrap_var.get() == 1: total_amount += 20

        payment = self.pay_var.get()
        customer_info = f"ที่อยู่: {address}\nชำระเงิน: {payment}\nห่อของขวัญ: {'ใช่' if self.wrap_var.get() else 'ไม่'}"

        success, message = controller.process_checkout(self.cart, total_amount, customer_info)

        if success:
            messagebox.showinfo("สำเร็จ", message)
            self.cart.clear()
            self.update_cart_display()
            self.txt_address.delete("1.0", tk.END)
            self.wrap_var.set(0)
            self.refresh_book_list()
        else:
            messagebox.showerror("ข้อผิดพลาด", message)

    def open_add_book_window(self):
        top = tk.Toplevel(self.root)
        top.title("เพิ่มหนังสือ")
        top.geometry("300x250")
        
        tk.Label(top, text="ISBN:").pack()
        e_isbn = tk.Entry(top)
        e_isbn.pack()
        
        tk.Label(top, text="ชื่อหนังสือ:").pack()
        e_name = tk.Entry(top)
        e_name.pack()
        
        tk.Label(top, text="ราคา:").pack()
        e_price = tk.Entry(top)
        e_price.pack()
        
        tk.Label(top, text="จำนวน:").pack()
        e_qty = tk.Entry(top)
        e_qty.pack()
        
        def save_book():
            try:
                controller.add_book(e_isbn.get(), e_name.get(), float(e_price.get()), int(e_qty.get()))
                messagebox.showinfo("สำเร็จ", "เพิ่มข้อมูลสำเร็จ")
                self.refresh_book_list()
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        tk.Button(top, text="บันทึก", command=save_book).pack(pady=10)

    def delete_book_gui(self):
        selected = self.book_tree.focus()
        if not selected:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกหนังสือที่ต้องการลบจากเฟรมที่ 1")
            return
            
        book_id = self.book_tree.item(selected)["values"][0]
        if messagebox.askyesno("ยืนยัน", "ต้องการซ่อน/ลบหนังสือรายการนี้ใช่หรือไม่?"):
            controller.delete_book(book_id)
            self.refresh_book_list()