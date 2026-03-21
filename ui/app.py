"""
โมดูล UI หลักของระบบร้านหนังสือ (BookstoreApp)
จัดการการแสดงผลหน้าต่างหลัก แท็บหน้าแรก แท็บตะกร้าสินค้า และเมนูจัดการข้อมูล
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from modules.cart_manager import CartManager
from modules.checkout_ui import CheckoutWindow
from database import controller

class BookstoreApp:
    """คลาสจัดการหน้าต่างและส่วนติดต่อผู้ใช้ (UI) หลักของร้านหนังสือ"""

    def __init__(self, root):
        """
        กำหนดค่าเริ่มต้นของแอปพลิเคชัน
        
        Args:
            root (tk.Tk): หน้าต่างหลักของ Tkinter
        """
        self.root = root
        self.root.title("BookShop Online")
        self.root.geometry("1000x700")
        
        self.cart_manager = CartManager()
        # ดิกชันนารีสำหรับกันไม่ให้รูปภาพถูกล้างออกจากหน่วยความจำ (Garbage Collection)
        self.book_images = {} 
        
        # ตรวจสอบว่ามีโฟลเดอร์ images ไหม ถ้าไม่มีให้สร้างเพื่อใช้เก็บรูปปกหนังสือ
        if not os.path.exists("images"):
            os.makedirs("images")
            
        self.create_menu()
        self.create_widgets()
        self.load_books_to_home()

    def create_menu(self):
        """สร้างแถบเมนูด้านบน (Menu Bar) สำหรับจัดการระบบ"""
        menubar = tk.Menu(self.root)
        
        # หมวดหมู่เมนูจัดการข้อมูล
        manage_menu = tk.Menu(menubar, tearoff=0)
        manage_menu.add_command(label="เพิ่มหนังสือและรูปภาพ", command=self.open_add_book_window)
        manage_menu.add_command(label="จัดการสต็อกสินค้า", command=self.open_manage_stock_window)
        
        menubar.add_cascade(label="จัดการข้อมูล", menu=manage_menu)
        self.root.config(menu=menubar)

    def create_widgets(self):
        """สร้างและตั้งค่าโครงสร้างของ Notebook (ระบบแท็บ) สำหรับหน้าแรกและตะกร้า"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # แท็บ 1: หน้าแรก (Home)
        self.tab_home = tk.Frame(self.notebook, bg="white")
        self.notebook.add(self.tab_home, text="  หน้าแรก  ")

        # แท็บ 2: ตะกร้าสินค้า (Cart)
        self.tab_cart = tk.Frame(self.notebook, bg="#f0f0f0")
        self.notebook.add(self.tab_cart, text="  ตะกร้า  ")

        self.setup_home_tab()
        self.setup_cart_tab()

    # ================== แท็บ 1: หน้าแรก ==================

    def setup_home_tab(self):
        """จัดเตรียมโครงสร้าง UI ของหน้าแรก โดยใช้ Canvas เพื่อให้สามารถ Scroll ได้"""
        canvas = tk.Canvas(self.tab_home, bg="white")
        scrollbar = ttk.Scrollbar(self.tab_home, orient="vertical", command=canvas.yview)
        self.books_frame = tk.Frame(canvas, bg="white")

        # อัปเดตพื้นที่การเลื่อน (Scrollregion) เมื่อขนาด Frame เปลี่ยนไป
        self.books_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.books_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

    def load_books_to_home(self):
        """ดึงข้อมูลหนังสือจากฐานข้อมูลและแสดงผลเป็น Card บนหน้าแรก"""
        # ล้างข้อมูลเดิมก่อนโหลดใหม่
        for widget in self.books_frame.winfo_children():
            widget.destroy()
            
        self.book_images.clear() 

        # รับค่าหนังสือทั้งหมด (รวมถึงสต็อก) จาก Controller
        books = controller.get_active_books() 
        
        row_val = 0
        col_val = 0
        
        for book in books:
            b_id, isbn, name, price, stock = book # ข้อมูลที่ดึงมาจากฐานข้อมูล
            
            # กรอบของหนังสือแต่ละเล่ม (Card)
            card = tk.Frame(self.books_frame, bd=1, relief="solid", padx=10, pady=10, bg="white")
            card.grid(row=row_val, column=col_val, padx=15, pady=15, sticky="nsew")
            
            # โหลดรูปภาพ
            img_path = f"images/{isbn}.png"
            if os.path.exists(img_path):
                try:
                    img = tk.PhotoImage(file=img_path)
                    img = img.subsample(max(1, img.width() // 150), max(1, img.height() // 200)) 
                    self.book_images[b_id] = img
                    lbl_img = tk.Label(card, image=img, bg="white")
                except Exception:
                    lbl_img = tk.Label(card, text="[ รูปภาพขัดข้อง ]", bg="#e0e0e0", width=20, height=8)
            else:
                lbl_img = tk.Label(card, text="[ ไม่มีรูปภาพ ]", bg="#e0e0e0", width=20, height=8)
                
            lbl_img.pack(pady=(0,10))
            
            # รายละเอียดหนังสือ
            display_name = name if len(name) <= 25 else name[:22] + "..."
            tk.Label(card, text=display_name, font=("Arial", 10, "bold"), bg="white", wraplength=150).pack()
            tk.Label(card, text=f"฿ {price:,.2f}", fg="blue", bg="white", font=("Arial", 11, "bold")).pack(pady=2)
            
            # แสดงสต็อกให้ลูกค้าเห็น
            tk.Label(card, text=f"คงเหลือ: {stock} เล่ม", fg="gray", bg="white", font=("Arial", 9)).pack(pady=(0,5))
            
            # ปุ่มเพิ่มลงตะกร้า (ส่งค่า stock ไปเช็คความถูกต้อง)
            btn_add = tk.Button(card, text="ใส่ตะกร้า", bg="#e0e0e0", cursor="hand2",
                                command=lambda id=b_id, n=name, p=price, s=stock: self.add_to_cart(id, n, p, s))
            
            # ถ้าของหมดให้ปิดปุ่ม (กดไม่ได้)
            if stock <= 0:
                btn_add.config(state="disabled", text="สินค้าหมด", bg="#ffcccc")
                
            btn_add.pack(fill="x")

            # จัดเรียงขึ้นบรรทัดใหม่เมื่อครบ 4 เล่มในหนึ่งแถว
            col_val += 1
            if col_val > 3: 
                col_val = 0
                row_val += 1

    def add_to_cart(self, b_id, name, price, stock):
        """
        เพิ่มสินค้าลงในตะกร้าและตรวจสอบจำนวนสต็อก
        """
        success, msg = self.cart_manager.add_item(b_id, name, price, stock)
        if success:
            self.refresh_cart_display()
            messagebox.showinfo("สำเร็จ", msg, parent=self.root)
        else:
            messagebox.showwarning("แจ้งเตือนสต็อก", msg, parent=self.root)

    def cart_increase(self):
        """เพิ่มจำนวนสินค้าในตะกร้า +1 (ตรวจสอบสต็อกสูงสุดเสมอ)"""
        item = self.get_selected_cart_item()
        if item:
            # ใช้ index 1 เพราะคอลัมน์ 0 เป็น Checkbox ไปแล้ว
            success, msg = self.cart_manager.increase_item(item[1]) 
            if success:
                self.refresh_cart_display()
            else:
                messagebox.showwarning("แจ้งเตือน", msg, parent=self.root)

    # ================== หน้าต่างเพิ่มหนังสือ (เมนู) ==================

    def open_add_book_window(self):
        """เปิดหน้าต่าง Pop-up สำหรับเพิ่มข้อมูลหนังสือและอัปโหลดรูปภาพใหม่"""
        top = tk.Toplevel(self.root)
        top.title("เพิ่มหนังสือ")
        top.geometry("400x350")
        
        # ฟอร์มรับข้อมูล
        tk.Label(top, text="ISBN:").pack(pady=(10,0))
        e_isbn = tk.Entry(top, width=30)
        e_isbn.pack()
        
        tk.Label(top, text="ชื่อหนังสือ:").pack(pady=(5,0))
        e_name = tk.Entry(top, width=30)
        e_name.pack()
        
        tk.Label(top, text="ราคา:").pack(pady=(5,0))
        e_price = tk.Entry(top, width=30)
        e_price.pack()
        
        tk.Label(top, text="จำนวนสต๊อก:").pack(pady=(5,0))
        e_qty = tk.Entry(top, width=30)
        e_qty.pack()

        self.selected_image_path = None

        def select_image():
            """เปิดหน้าต่าง File Dialog ให้ผู้ใช้เลือกรูปภาพ (เฉพาะ .png)"""
            filepath = filedialog.askopenfilename(title="เลือกปกหนังสือ", filetypes=[("PNG Files", "*.png")])
            if filepath:
                self.selected_image_path = filepath
                lbl_img_path.config(text="เลือกรูปภาพแล้ว", fg="green")

        lbl_img_path = tk.Label(top, text="ยังไม่ได้เลือกรูป (ไฟล์.png)", fg="gray")
        lbl_img_path.pack(pady=5)
        
        tk.Button(top, text="เลือกรูปภาพปก", command=select_image).pack(pady=5)

        def save_book():
            """ดำเนินการบันทึกข้อมูลหนังสือใหม่และจัดการรูปภาพลงระบบ"""
            isbn = e_isbn.get().strip()
            name = e_name.get().strip()
            price_val = e_price.get().strip()
            qty_val = e_qty.get().strip()
            
            if not isbn or not name or not price_val or not qty_val:
                messagebox.showerror("Error", "กรุณากรอกข้อมูลให้ครบ")
                return

            try:
                # 1. บันทึกข้อมูลลงฐานข้อมูล
                success, msg = controller.add_book(isbn, name, float(price_val), int(qty_val))
                if not success:
                    messagebox.showerror("Error", msg)
                    return
                
                # 2. คัดลอกไฟล์รูปภาพไปเก็บในโฟลเดอร์ images ด้วยชื่อ ISBN
                if self.selected_image_path:
                    dest_path = f"images/{isbn}.png"
                    shutil.copy(self.selected_image_path, dest_path)

                messagebox.showinfo("สำเร็จ", "เพิ่มสินค้าสำเร็จ")
                self.load_books_to_home() # รีเฟรชหน้าแรก
                top.destroy()

            except ValueError:
                messagebox.showerror("Error", "ข้อมูลไม่ถูกต้อง")

        tk.Button(top, text="บันทึกข้อมูล", bg="#4CAF50", fg="white", command=save_book).pack(pady=15)
    
    # ================== หน้าต่างจัดการข้อมูล สต็อก และรูปภาพ ==================
    
    def open_manage_stock_window(self):
        """เปิดหน้าต่าง Pop-up สำหรับอัปเดตสต็อก แก้ไขชื่อ และเปลี่ยนรูปภาพหนังสือ"""
        top = tk.Toplevel(self.root)
        top.title("Stock Manager")
        top.geometry("600x450")
        
        # ตารางแสดงรายการหนังสือ
        columns = ("id", "isbn", "name", "qty")
        tree = ttk.Treeview(top, columns=columns, show="headings", height=8)
        for col, text in zip(columns, ["ID", "ISBN", "ชื่อหนังสือ", "จำนวน"]):
            tree.heading(col, text=text)
            
        tree.column("id", width=50, anchor="center")
        tree.column("isbn", width=120, anchor="center")
        tree.column("name", width=250)
        tree.column("qty", width=100, anchor="center")
        tree.pack(fill="both", expand=True, padx=15, pady=10)

        def load_stock_data():
            """โหลดข้อมูลล่าสุดเข้าตารางแสดงสินค้า"""
            for row in tree.get_children():
                tree.delete(row)
            books = controller.get_active_books()
            for b in books:
                tree.insert("", "end", values=(b[0], b[1], b[2], b[4]))

        load_stock_data()

        # --- พื้นที่สำหรับแก้ไขข้อมูล ---
        frame_edit = tk.LabelFrame(top, text="แก้ไขข้อมูลสินค้า", padx=10, pady=10)
        frame_edit.pack(fill="x", padx=15, pady=5)

        tk.Label(frame_edit, text="ชื่อสินค้าใหม่:").grid(row=0, column=0, sticky="e", pady=5)
        ent_name = tk.Entry(frame_edit, width=45, font=("Arial", 10))
        ent_name.grid(row=0, column=1, sticky="w", pady=5, padx=5)

        tk.Label(frame_edit, text="จำนวนสต็อกใหม่:").grid(row=1, column=0, sticky="e", pady=5)
        ent_qty = tk.Entry(frame_edit, width=15, font=("Arial", 10))
        ent_qty.grid(row=1, column=1, sticky="w", pady=5, padx=5)

        # --- ส่วนเปลี่ยนรูปภาพ ---
        self.edit_image_path = None
        lbl_edit_img = tk.Label(frame_edit, text="ยังไม่ได้เลือกรูปใหม่ (ถ้าไม่ต้องการเปลี่ยนไม่ต้องเลือก)", fg="gray")
        lbl_edit_img.grid(row=2, column=1, sticky="w", padx=5)

        def select_new_image():
            """เปิดหน้าต่างเลือกไฟล์เพื่ออัปเดตรูปภาพปกใหม่"""
            filepath = filedialog.askopenfilename(title="เลือกรูปปกหนังสือใหม่", filetypes=[("PNG Files", "*.png")])
            if filepath:
                self.edit_image_path = filepath
                lbl_edit_img.config(text="เลือกรูปภาพใหม่แล้ว", fg="green")

        tk.Button(frame_edit, text="เปลี่ยนรูปภาพ", command=select_new_image).grid(row=2, column=0, sticky="e", pady=5)

        def on_tree_select(event):
            """จัดการเหตุการณ์เมื่อมีการคลิกเลือกแถวในตาราง"""
            selected = tree.focus()
            if selected:
                item = tree.item(selected)["values"]
                # เติมข้อมูลเดิมลงในช่อง Entry
                ent_name.delete(0, tk.END)
                ent_name.insert(0, item[2])
                ent_qty.delete(0, tk.END)
                ent_qty.insert(0, item[3])
                
                # ล้างค่าการเลือกรูปภาพทุกครั้งที่คลิกเปลี่ยนหนังสือ
                self.edit_image_path = None
                lbl_edit_img.config(text="ยังไม่ได้เลือกรูปใหม่ (ถ้าไม่ต้องการเปลี่ยนไม่ต้องเลือก)", fg="gray")

        tree.bind("<<TreeviewSelect>>", on_tree_select)

        def save_changes():
            """บันทึกการเปลี่ยนแปลงทั้งหมด (ชื่อ, สต็อก, รุปภาพ) ลงฐานข้อมูลและระบบไฟล์"""
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("แจ้งเตือน", "กรุณาคลิกเลือกหนังสือ", parent=top)
                return
                
            item = tree.item(selected)["values"]
            book_id = item[0]
            isbn = item[1] # ดึง ISBN มาเพื่อใช้ตั้งชื่อไฟล์ภาพทับของเดิม
            new_name = ent_name.get().strip()
            new_qty_str = ent_qty.get().strip()

            if not new_name:
                messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกชื่อสินค้า", parent=top)
                return

            if not new_qty_str.isdigit() or int(new_qty_str) < 0:
                messagebox.showerror("ข้อผิดพลาด", "จำนวนไม่ถูกต้อง", parent=top)
                return
            
            new_qty = int(new_qty_str)
            # สั่งบันทึกลง Database
            success, msg = controller.update_book_info(book_id, new_name, new_qty)
            
            if success:
                # ถ้ายูสเซอร์กดเลือกรูปใหม่ ให้ก๊อปปี้ไปวางทับรูปเก่าด้วย ISBN เดิม
                if self.edit_image_path:
                    dest_path = f"images/{isbn}.png"
                    shutil.copy(self.edit_image_path, dest_path)

                messagebox.showinfo("สำเร็จ", "อัปเดตข้อมูลสำเร็จ", parent=top)
                load_stock_data() 
                self.load_books_to_home() # รีเฟรชหน้าแรก เพื่อให้รูปใหม่/ชื่อใหม่โชว์ทันที
                
                # เคลียร์ฟอร์ม
                ent_name.delete(0, tk.END)
                ent_qty.delete(0, tk.END)
                self.edit_image_path = None
                lbl_edit_img.config(text="ยังไม่ได้เลือกรูปใหม่ (ถ้าไม่ต้องการเปลี่ยนไม่ต้องเลือก)", fg="gray")
            else:
                messagebox.showerror("ข้อผิดพลาด", msg, parent=top)

        tk.Button(
            frame_edit, text="บันทึกการเปลี่ยนแปลง", bg="#4CAF50", fg="white", 
            font=("Arial", 10, "bold"), command=save_changes
        ).grid(row=3, column=0, columnspan=2, pady=10)

    # ================== แท็บ 2: ตะกร้า (แก้ไขระบบเลือกรายการจ่ายเงิน) ==================

    def setup_cart_tab(self):
        """จัดเตรียมโครงสร้าง UI สำหรับแท็บตะกร้าสินค้า (ตารางสรุปรายการ และปุ่มจัดการ)"""
        # แถบปุ่มจัดการด้านบนตาราง
        action_frame = tk.Frame(self.tab_cart, bg="#f0f0f0")
        action_frame.pack(fill="x", padx=20, pady=(20, 5))

        tk.Button(action_frame, text="เพิ่มจำนวน", width=12, command=self.cart_increase).pack(side="left", padx=5)
        tk.Button(action_frame, text="ลดจำนวน", width=12, command=self.cart_decrease).pack(side="left", padx=5)
        tk.Button(action_frame, text="ลบรายการ", width=12, bg="#ffcccc", command=self.cart_remove).pack(side="left", padx=5)

        # ตารางแสดงรายการตะกร้า (เพิ่มคอลัมน์ "select" สำหรับคลิก Checkbox เข้ามาด้านหน้าสุด)
        columns = ("select", "id", "name", "price", "qty", "subtotal")
        self.cart_tree = ttk.Treeview(self.tab_cart, columns=columns, show="headings", height=12)
        
        for col, text in zip(columns, ["เลือก", "ID", "ชื่อหนังสือ", "ราคาต่อหน่วย", "จำนวน", "รวม (บาท)"]):
            self.cart_tree.heading(col, text=text)
        
        self.cart_tree.column("select", width=50, anchor="center") # คอลัมน์ที่จำลอง Checkbox
        self.cart_tree.column("id", width=50, anchor="center")
        self.cart_tree.column("name", width=300)
        self.cart_tree.column("price", width=100, anchor="e")
        self.cart_tree.column("qty", width=80, anchor="center")
        self.cart_tree.column("subtotal", width=100, anchor="e")
        self.cart_tree.pack(fill="both", expand=True, padx=20, pady=5)

        # Event: จับการคลิกเมาส์ซ้ายเพื่อสลับสถานะเลือก (☑ และ ☐)
        self.cart_tree.bind('<ButtonRelease-1>', self.toggle_checkbox)

        # ส่วนสรุปยอดและปุ่มจ่ายเงิน
        bottom_frame = tk.Frame(self.tab_cart, bg="#f0f0f0")
        bottom_frame.pack(fill="x", padx=20, pady=10)

        self.lbl_total = tk.Label(bottom_frame, text="ยอดรวม: 0.00 บาท", font=("Arial", 14, "bold"), bg="#f0f0f0")
        self.lbl_total.pack(side="left")

        btn_checkout = tk.Button(bottom_frame, text="ดำเนินการสั่งซื้อ", bg="#FFD700", font=("Arial", 12, "bold"), command=self.open_checkout)
        btn_checkout.pack(side="right", ipadx=10, ipady=5)

    # --- ฟังก์ชันจัดการ Checkbox และคำนวณยอด ---

    def toggle_checkbox(self, event):
        """สลับสถานะ ☑ และ ☐ เมื่อคลิกที่คอลัมน์แรก"""
        region = self.cart_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.cart_tree.identify_column(event.x)
            if column == '#1': # ถ้าคลิกที่คอลัมน์ "เลือก"
                item_id = self.cart_tree.focus()
                if item_id:
                    values = list(self.cart_tree.item(item_id, "values"))
                    # สลับสถานะตัวอักษรเพื่อจำลองการติ๊ก
                    values[0] = "☐" if values[0] == "☑" else "☑"
                    self.cart_tree.item(item_id, values=values)
                    # คำนวณยอดใหม่
                    self.update_selected_total()

    def update_selected_total(self):
        """คำนวณยอดเงินรวมเฉพาะรายการที่มีเครื่องหมายติ๊กถูก ☑"""
        total = 0.0
        for row in self.cart_tree.get_children():
            values = self.cart_tree.item(row, "values")
            if values[0] == "☑": 
                # ดึงตัวเลข subtotal ลบลูกน้ำออก แล้วแปลงเป็น float มาบวกกัน
                subtotal = float(values[5].replace(",", ""))
                total += subtotal
        
        self.lbl_total.config(text=f"ยอดรวม: {total:,.2f} บาท")

    # --- ฟังก์ชันปุ่มกดในตะกร้า ---

    def get_selected_cart_item(self):
        """ดึงข้อมูลรายการที่ถูกกดคลุมดำ (Highlight) อยู่"""
        selected = self.cart_tree.focus()
        if not selected:
            messagebox.showwarning("แจ้งเตือน", "กรุณาคลิกเลือกรายการในตารางก่อน")
            return None
        return self.cart_tree.item(selected)["values"] 

    def cart_decrease(self):
        """ลดจำนวนสินค้าในตะกร้าลง 1 ชิ้น"""
        item = self.get_selected_cart_item()
        if item:
            self.cart_manager.decrease_item(item[1]) # ค่า ID เลื่อนไปอยู่ index 1
            self.refresh_cart_display()

    def cart_remove(self):
        """ลบรายการสินค้าออกจากตะกร้า"""
        item = self.get_selected_cart_item()
        if item:
            if messagebox.askyesno("ยืนยัน", f"ต้องการลบ '{item[2]}' ออกจากตะกร้าหรือไม่?"):
                self.cart_manager.remove_item(item[1]) 
                self.refresh_cart_display()

    def refresh_cart_display(self):
        """รีเฟรชตารางตะกร้า โดยจะจดจำรายการที่เคยติ๊กถูกเอาไว้ด้วย"""
        # 1. จำรายการเดิมที่เคยติ๊ก ☑ เอาไว้ก่อน
        checked_items = []
        for row in self.cart_tree.get_children():
            values = self.cart_tree.item(row, "values")
            if values[0] == "☑":
                checked_items.append(str(values[1])) 

        # 2. ล้างตาราง
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)

        # 3. โชว์ข้อมูลล่าสุด
        for item in self.cart_manager.get_all_items():
            sub = item['price'] * item['qty']
            item_id_str = str(item['id'])
            
            # ถ้าเป็นสินค้าใหม่ (หรือเคยโดนติ๊กไว้) ให้ค่าตั้งต้นเป็นติ๊กถูก ☑
            check_mark = "☑" if (item_id_str in checked_items or not checked_items) else "☐"

            self.cart_tree.insert("", "end", values=(
                check_mark, item['id'], item['name'], f"{item['price']:,.2f}", item['qty'], f"{sub:,.2f}"
            ))

        self.update_selected_total()

    def open_checkout(self):
        """เปิดหน้าต่างดำเนินการสั่งซื้อ โดยคัดไปเฉพาะรายการที่ติ๊กเลือก"""
        selected_items = []
        
        # กรองเฉพาะสินค้าที่ถูกติ๊ก ☑
        for row in self.cart_tree.get_children():
            values = self.cart_tree.item(row, "values")
            if values[0] == "☑":
                item_id = values[1]
                for item in self.cart_manager.get_all_items():
                    if str(item['id']) == str(item_id):
                        selected_items.append(item)
                        break

        if not selected_items:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกสินค้าเพื่อชำระเงินอย่างน้อย")
            return
            
        # สร้างคลาสจำลองสำหรับหน้า Checkout โดยเฉพาะ เพื่อไม่ให้โค้ดเก่าพัง
        class TempCartManager:
            def get_all_items(self):
                return selected_items
            def calculate_total(self):
                return sum(item['price'] * item['qty'] for item in selected_items)
                
        temp_cart = TempCartManager()
        
        def on_checkout_success():
            """ลบเฉพาะรายการที่จ่ายเงินสำเร็จออกจากตะกร้าหลัก"""
            for item in selected_items:
                self.cart_manager.remove_item(item['id'])
            self.refresh_cart_display()
            self.load_books_to_home()
            
        # ส่ง temp_cart (ที่มีเฉพาะของที่ติ๊กเลือก) ไปยังหน้าต่างชำระเงิน
        CheckoutWindow(self.root, temp_cart, on_checkout_success)