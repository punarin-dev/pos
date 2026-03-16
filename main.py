import tkinter as tk
from gui.app import BookstoreApp

def main():
    root = tk.Tk()
    
    # ดึงคลาส BookstoreApp จากโฟลเดอร์ gui มาสร้างหน้าต่าง
    app = BookstoreApp(root) 
    
    root.mainloop()

if __name__ == "__main__":
    main()