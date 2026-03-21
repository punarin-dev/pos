"""
โมดูลสำหรับจัดการลอจิก (Logic) ของตะกร้าสินค้า
ใช้สำหรับควบคุมการ เพิ่ม, ลด, ลบรายการสินค้า และคำนวณยอดรวม
"""

class CartManager:
    """คลาสตัวแทนตะกร้าสินค้าในหน่วยความจำชั่วคราว"""

    def __init__(self):
        """เริ่มต้นตะกร้าสินค้า โดยใช้ดิกชันนารีเพื่อจัดเก็บสินค้าตาม ID"""
        self.items = {}

    def add_item(self, book_id, name, price, stock):
        """
        เพิ่มสินค้าจากหน้าแรกลงในตะกร้า โดยมีเงื่อนไขตรวจสอบสต็อก
        
        Args:
            book_id (int): รหัสหนังสือ
            name (str): ชื่อหนังสือ
            price (float): ราคาหนังสือ
            stock (int): สต็อกที่เหลืออยู่
            
        Returns:
            tuple: (สถานะสำเร็จ True/False, ข้อความตอบกลับ)
        """
        book_id = int(book_id) # แปลงเป็นตัวเลขเพื่อป้องกันปัญหาตอนรับค่าจาก UI
        
        if book_id in self.items:
            # กรณีที่สินค้านี้มีในตะกร้าอยู่แล้ว เช็คว่าถ้าบวกเพิ่มอีก 1 จะเกินสต็อกไหม
            if self.items[book_id]['qty'] < stock:
                self.items[book_id]['qty'] += 1
                return True, f"เพิ่ม '{name}' ลงตะกร้าแล้ว"
            else:
                return False, f"สินค้ามีจำนวน {stock} ชิ้น"
        else:
            # กรณีที่สินค้านี้ยังไม่มีในตะกร้า
            if stock > 0:
                # เก็บ max_stock ไว้เพื่อเช็คตอนกดปุ่ม + ในตะกร้า
                self.items[book_id] = {
                    'id': book_id, 
                    'name': name, 
                    'price': float(price), 
                    'qty': 1, 
                    'max_stock': stock
                }
                return True, f"เพิ่ม '{name}' ลงตะกร้าแล้ว"
            else:
                return False, "สินค้าหมดสต็อก!"

    def increase_item(self, book_id):
        """
        เพิ่มจำนวนสินค้าขึ้น 1 ชิ้นในตะกร้า โดยห้ามเกิน Max Stock
        
        Args:
            book_id (int): รหัสหนังสือ
            
        Returns:
            tuple: (สถานะสำเร็จ True/False, ข้อความตอบกลับ)
        """
        book_id = int(book_id)
        
        if book_id in self.items:
            # เช็คสต็อกตอนกดปุ่มบวกในหน้าตะกร้า
            if self.items[book_id]['qty'] < self.items[book_id]['max_stock']:
                self.items[book_id]['qty'] += 1
                return True, ""
            else:
                max_st = self.items[book_id]['max_stock']
                return False, f"ไม่สามารถเพิ่มเกินจำนวน ({max_st} ชิ้น)"
        return False, "ไม่พบสินค้า"
    
    def decrease_item(self, book_id):
        """
        ลดจำนวนสินค้าลง 1 ชิ้น ถ้าเหลือศูนย์จะถูกนำออกจากตะกร้า
        
        Args:
            book_id (int): รหัสหนังสือ
        """
        book_id = int(book_id)
        
        if book_id in self.items:
            self.items[book_id]['qty'] -= 1
            # ถ้าเหลือ 0 ให้ลบออกจากตะกร้าไปเลย
            if self.items[book_id]['qty'] <= 0:
                self.remove_item(book_id)

    def remove_item(self, book_id):
        """
        ลบสินค้าที่ระบุออกจากตะกร้าทั้งหมด
        
        Args:
            book_id (int): รหัสหนังสือ
        """
        book_id = int(book_id)
        if book_id in self.items:
            del self.items[book_id]

    def get_all_items(self):
        """
        ดึงรายการสินค้าทั้งหมดในตะกร้า
        
        Returns:
            list: รายการหนังสือเป็นลิสต์ของดิกชันนารี
        """
        return list(self.items.values())

    def calculate_total(self):
        """
        คำนวณราคาสุทธิของสินค้าทั้งหมดในตะกร้า
        
        Returns:
            float: ยอดรวมเป็นตัวเลข
        """
        return sum(item['price'] * item['qty'] for item in self.items.values())

    def clear_cart(self):
        """ล้างรายการสินค้าทั้งหมดออกจากตะกร้า (ใช้หลังจากจ่ายเงินสำเร็จ)"""
        self.items.clear()