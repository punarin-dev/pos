"""
โมดูล UI สำหรับการจัดการหน้าจอคำสั่งซื้อ (Checkout)
ควบคุมฟอร์มกรอกข้อมูลลูกค้าและดำเนินการบันทึกคำสั่งซื้อ
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import controller

class CheckoutWindow:
    """คลาสจัดการหน้าต่างรับข้อมูลลูกค้าและยืนยันการชำระเงิน"""

    def __init__(self, parent, cart_manager, refresh_callback):
        """
        กำหนดค่าเริ่มต้นของหน้าต่างการสั่งซื้อ
        Args:
            parent (tk.Tk/tk.Frame): หน้าต่างหลักที่เรียกใช้งาน
            cart_manager (CartManager): อ็อบเจกต์จัดการตะกร้าเพื่อดึงราคารวม
            refresh_callback (function): ฟังก์ชันสำหรับรีเฟรช UI หลังสั่งซื้อสำเร็จ
        """
        self.top = tk.Toplevel(parent)
        self.top.title("ข้อมูลการจัดส่ง")
        self.top.geometry("600x450") 
        
        # ล็อกให้ผู้ใช้ต้องทำรายการหน้าต่างนี้ให้เสร็จก่อนกลับไปหน้าหลัก
        self.top.grab_set() 
        
        self.cart_manager = cart_manager
        self.refresh_callback = refresh_callback
        
        self.create_widgets()

    def create_widgets(self):
        """สร้างฟอร์มกรอกข้อมูลที่อยู่จัดส่งและแสดงสรุปยอดเงิน"""
        # --- ส่วนข้อมูลที่อยู่ ---
        frame_address = tk.LabelFrame(self.top, text="ที่อยู่จัดส่ง", padx=10, pady=10)
        frame_address.pack(fill="x", padx=10, pady=5)

        # แถว 0: เพศ (Radio Buttons) ย้ายขึ้นมาไว้บนสุด
        tk.Label(frame_address, text="เพศ:").grid(row=0, column=0, sticky="w", pady=2)
        
        self.gender_var = tk.StringVar(value="ชาย")
        frame_gender = tk.Frame(frame_address)
        frame_gender.grid(row=0, column=1, columnspan=3, sticky="w", pady=2)
        
        tk.Radiobutton(frame_gender, text="ชาย", variable=self.gender_var, value="ชาย").pack(side="left", padx=(0, 10))
        tk.Radiobutton(frame_gender, text="หญิง", variable=self.gender_var, value="หญิง").pack(side="left", padx=(0, 10))
        tk.Radiobutton(frame_gender, text="อื่นๆ", variable=self.gender_var, value="อื่นๆ").pack(side="left")

        # แถว 1: ชื่อ-นามสกุล (ย้ายลงมา)
        tk.Label(frame_address, text="ชื่อ-นามสกุล:").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_name = tk.Entry(frame_address, width=40)
        self.ent_name.grid(row=1, column=1, columnspan=3, sticky="w", pady=2)

        # แถว 2: ที่อยู่
        tk.Label(frame_address, text="ที่อยู่ (บ้านเลขที่, ซอย, ถนน):").grid(row=2, column=0, sticky="nw", pady=2)
        self.txt_address = tk.Text(frame_address, width=40, height=4)
        self.txt_address.grid(row=2, column=1, columnspan=3, sticky="w", pady=2)

        # แถว 3: จังหวัด
        tk.Label(frame_address, text="จังหวัด:").grid(row=3, column=0, sticky="w", pady=2)
        self.ent_province = tk.Entry(frame_address, width=20)
        self.ent_province.grid(row=3, column=1, sticky="w", pady=2)

        # แถว 4: รหัสไปรษณีย์
        tk.Label(frame_address, text="รหัสไปรษณีย์:").grid(row=4, column=0, sticky="w", pady=2)
        self.ent_zip = tk.Entry(frame_address, width=20)
        self.ent_zip.grid(row=4, column=1, sticky="w", pady=2)

        # --- ส่วนสรุปยอด ---
        frame_summary = tk.Frame(self.top, padx=10, pady=10)
        frame_summary.pack(fill="x", padx=10, pady=5)
        
        total = self.cart_manager.calculate_total()
        
        tk.Label(frame_summary, text=f"ราคารวม: {total:,.2f} บาท", font=("Arial", 12)).pack(anchor="w")
        tk.Label(frame_summary, text=f"ราคาสุทธิ: {total:,.2f} บาท", font=("Arial", 12, "bold")).pack(anchor="w")

        btn_confirm = tk.Button(
            self.top, text="ชำระเงิน", bg="#FFD700", width=20, 
            font=("Arial", 10, "bold"), command=self.confirm_order
        )
        btn_confirm.pack(pady=15)

    def confirm_order(self):
        """
        ตรวจสอบความถูกต้องของฟอร์มที่อยู่ และส่งคำสั่งบันทึกลง Database
        รวมถึงสั่งเคลียร์ตะกร้าเมื่อการสั่งซื้อเสร็จสมบูรณ์
        """
        name = self.ent_name.get().strip()
        gender = self.gender_var.get() # ดึงค่าเพศจาก Radio Button
        address = self.txt_address.get("1.0", tk.END).strip()
        province = self.ent_province.get().strip()
        
        # ตรวจสอบการกรอกข้อมูลขั้นต่ำ
        if not name or not address:
            messagebox.showwarning("แจ้งเตือน", "กรุณากรอกข้อมูลที่อยู่ให้ครบถ้วน")
            return

        # รวบรวมข้อมูลลูกค้าเป็นสตริงเดียว
        customer_info = f"เพศ: {gender}, ชื่อ: {name}, ที่อยู่: {address}, จังหวัด: {province}, ปณ: {self.ent_zip.get()}"
        total = self.cart_manager.calculate_total()
        
        # ดึงสินค้าในตะกร้า
        cart_items = self.cart_manager.get_all_items()

        # บันทึกลงฐานข้อมูลและจัดการตัดสต็อก
        success, msg = controller.save_order(total, customer_info, cart_items)
        if success:
            messagebox.showinfo("สำเร็จ", msg)
            
            try:
                self.cart_manager.clear_cart()
            except AttributeError:
                pass
                
            self.refresh_callback() # อัปเดต UI หน้าหลักผ่าน Callback
            self.top.destroy()      # ปิดหน้าต่าง Checkout
        else:
            messagebox.showerror("ข้อผิดพลาด", msg)