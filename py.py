import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

SERVER_NAME = "DESKTOP-8DFL4QA"  
DATABASE_NAME = "quanlybanhang"

def connect_db():
    try:
        conn_str = (
            f"Driver={{SQL Server}};"
            f"Server={SERVER_NAME};"
            f"Database={DATABASE_NAME};"
            "Trusted_Connection=yes;"
        )
        return pyodbc.connect(conn_str)
    except Exception as e:
        messagebox.showerror("Lỗi kết nối", f"Lỗi: {e}")
        return None

def configure_grid_weights(frame, cols=4):
    for i in range(cols):
        frame.columnconfigure(i, weight=1)

def create_product_tab(notebook):
    frame = tk.Frame(notebook)
    notebook.add(frame, text="  Sản Phẩm  ")

    info_frame = tk.LabelFrame(frame, text="Thông Tin Sản Phẩm", font=("Arial", 10, "bold"), padx=10, pady=10)
    info_frame.pack(fill="x", padx=10, pady=5)
    configure_grid_weights(info_frame, 4)

    entry_masp = tk.Entry(info_frame)
    entry_tensp = tk.Entry(info_frame)
    cbb_loai = ttk.Combobox(info_frame, values=["Điện tử", "Gia dụng", "Thực phẩm", "Thời trang"])
    entry_dongia = tk.Entry(info_frame)
    entry_soluong = tk.Entry(info_frame)

    tk.Label(info_frame, text="Mã SP:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    entry_masp.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    tk.Label(info_frame, text="Tên SP:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
    entry_tensp.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
    tk.Label(info_frame, text="Loại:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    cbb_loai.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    tk.Label(info_frame, text="Đơn giá:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
    entry_dongia.grid(row=1, column=3, sticky="ew", padx=5, pady=5)
    tk.Label(info_frame, text="Số lượng:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    entry_soluong.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    btn_frame = tk.Frame(frame); btn_frame.pack(pady=10)

    def load_data():
        for i in tree.get_children(): tree.delete(i)
        conn = connect_db()
        if conn:
            cursor = conn.cursor(); cursor.execute("SELECT * FROM sanpham")
            for row in cursor.fetchall():
                dongia = int(row[3]) if row[3] is not None else 0
                soluong = row[4] if row[4] is not None else 0
                tree.insert("", tk.END, values=(row[0], row[1], row[2], "{:,}".format(dongia), soluong))
            conn.close()

    def clear_input():
        entry_masp.delete(0, tk.END); entry_tensp.delete(0, tk.END); cbb_loai.set("")
        entry_dongia.delete(0, tk.END); entry_soluong.delete(0, tk.END)

    def on_select(event):
        sel = tree.selection()
        if sel:
            v = tree.item(sel)['values']
            clear_input()
            entry_masp.insert(0, v[0]); entry_tensp.insert(0, v[1]); cbb_loai.set(v[2])
            entry_dongia.insert(0, str(v[3]).replace(",", "")); entry_soluong.insert(0, v[4])

    def crud_action(action):
        masp, tensp, loai = entry_masp.get(), entry_tensp.get(), cbb_loai.get()
        dongia, soluong = entry_dongia.get(), entry_soluong.get()
        
        if dongia: dongia = dongia.replace('.', '').replace(',', '')
        else: dongia = 0
        if soluong: soluong = str(soluong).replace('.', '').replace(',', '')
        else: soluong = 0

        conn = connect_db()
        if not conn: return
        cursor = conn.cursor()
        try:
            if action == "add":
                if not masp or not tensp: raise Exception("Thiếu mã/tên SP")
                cursor.execute("INSERT INTO sanpham VALUES (?,?,?,?,?)", (masp, tensp, loai, dongia, soluong))
            elif action == "update":
                cursor.execute("UPDATE sanpham SET tensp=?, loai=?, dongia=?, soluong=? WHERE masp=?", (tensp, loai, dongia, soluong, masp))
            elif action == "delete":
                if messagebox.askyesno("Xóa", "Xóa SP này?"): cursor.execute("DELETE FROM sanpham WHERE masp=?", (masp,))
            conn.commit(); load_data(); clear_input(); messagebox.showinfo("OK", "Thành công!")
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

    tk.Button(btn_frame, text="Thêm", bg="#4CAF50", fg="white", command=lambda: crud_action("add")).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Sửa", bg="#FFC107", command=lambda: crud_action("update")).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Xóa", bg="#F44336", fg="white", command=lambda: crud_action("delete")).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Làm mới", command=clear_input).pack(side=tk.LEFT, padx=10)

    list_frame = tk.LabelFrame(frame, text="Danh Sách Sản Phẩm", font=("Arial", 10, "bold"), padx=5, pady=5)
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)
    tree = ttk.Treeview(list_frame, columns=("ma", "ten", "loai", "gia", "sl"), show="headings")
    for c, t in zip(["ma", "ten", "loai", "gia", "sl"], ["Mã SP", "Tên SP", "Loại", "Đơn giá", "SL"]):
        tree.heading(c, text=t)
    tree.pack(fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", on_select); load_data()

def create_customer_tab(notebook):
    frame = tk.Frame(notebook)
    notebook.add(frame, text="  Khách Hàng  ")

    info_frame = tk.LabelFrame(frame, text="Thông Tin Khách Hàng", font=("Arial", 10, "bold"), padx=10, pady=10)
    info_frame.pack(fill="x", padx=10, pady=5)
    configure_grid_weights(info_frame, 4)

    entry_makh = tk.Entry(info_frame); entry_tenkh = tk.Entry(info_frame)
    entry_sdt = tk.Entry(info_frame); entry_diachi = tk.Entry(info_frame)

    tk.Label(info_frame, text="Mã KH:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    entry_makh.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    tk.Label(info_frame, text="Tên KH:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
    entry_tenkh.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
    tk.Label(info_frame, text="SĐT:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    entry_sdt.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    tk.Label(info_frame, text="Địa Chỉ:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
    entry_diachi.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

    btn_frame = tk.Frame(frame); btn_frame.pack(pady=10)

    def load_data():
        for i in tree.get_children(): tree.delete(i)
        conn = connect_db()
        if conn:
            cur = conn.cursor(); cur.execute("SELECT * FROM khachhang")
            for row in cur.fetchall(): tree.insert("", tk.END, values=list(row))
            conn.close()
            
    def crud_action(action):
        ma, ten, sdt, dc = entry_makh.get(), entry_tenkh.get(), entry_sdt.get(), entry_diachi.get()
        conn = connect_db()
        if not conn: return
        cur = conn.cursor()
        try:
            if action == "add": cur.execute("INSERT INTO khachhang VALUES (?,?,?,?)", (ma, ten, sdt, dc))
            elif action == "update": cur.execute("UPDATE khachhang SET tenkh=?, sdt=?, diachi=? WHERE makh=?", (ten, sdt, dc, ma))
            elif action == "delete":
                if messagebox.askyesno("Xóa", "Xóa KH này?"): cur.execute("DELETE FROM khachhang WHERE makh=?", (ma,))
            conn.commit(); load_data(); messagebox.showinfo("OK", "Thành công!")
            entry_makh.delete(0, tk.END); entry_tenkh.delete(0, tk.END)
            entry_sdt.delete(0, tk.END); entry_diachi.delete(0, tk.END)
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

    def on_select(e):
        sel = tree.selection()
        if sel:
            v = tree.item(sel)['values']
            entry_makh.delete(0,tk.END); entry_makh.insert(0, v[0])
            entry_tenkh.delete(0,tk.END); entry_tenkh.insert(0, v[1])
            entry_sdt.delete(0,tk.END); entry_sdt.insert(0, str(v[2]))
            entry_diachi.delete(0,tk.END); entry_diachi.insert(0, v[3])

    tk.Button(btn_frame, text="Thêm", bg="#4CAF50", fg="white", command=lambda: crud_action("add")).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Sửa", bg="#FFC107", command=lambda: crud_action("update")).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Xóa", bg="#F44336", fg="white", command=lambda: crud_action("delete")).pack(side=tk.LEFT, padx=10)

    list_frame = tk.LabelFrame(frame, text="Danh Sách Khách Hàng", font=("Arial", 10, "bold"), padx=5, pady=5)
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)
    tree = ttk.Treeview(list_frame, columns=("ma","ten","sdt","dc"), show="headings")
    for c, t in zip(["ma","ten","sdt","dc"], ["Mã KH", "Tên KH", "SĐT", "Địa chỉ"]):
        tree.heading(c, text=t)
    tree.pack(fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", on_select); load_data()

def create_employee_tab(notebook):
    frame = tk.Frame(notebook)
    notebook.add(frame, text="  Nhân Viên  ")

    info_frame = tk.LabelFrame(frame, text="Thông Tin Nhân Viên", font=("Arial", 10, "bold"), padx=10, pady=10)
    info_frame.pack(fill="x", padx=10, pady=5)
    configure_grid_weights(info_frame, 4)

    entry_manv = tk.Entry(info_frame); entry_tennv = tk.Entry(info_frame)
    entry_chucvu = tk.Entry(info_frame); entry_sdt = tk.Entry(info_frame)

    tk.Label(info_frame, text="Mã NV:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    entry_manv.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
    tk.Label(info_frame, text="Tên NV:").grid(row=0, column=2, sticky="e", padx=5, pady=5)
    entry_tennv.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
    tk.Label(info_frame, text="Chức Vụ:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    entry_chucvu.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    tk.Label(info_frame, text="SĐT:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
    entry_sdt.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

    btn_frame = tk.Frame(frame); btn_frame.pack(pady=10)

    def load_data():
        for i in tree.get_children(): tree.delete(i)
        conn = connect_db()
        if conn:
            cur = conn.cursor(); cur.execute("SELECT * FROM nhanvien")
            for row in cur.fetchall(): tree.insert("", tk.END, values=list(row))
            conn.close()

    def crud_action(action):
        ma, ten, cv, sdt = entry_manv.get(), entry_tennv.get(), entry_chucvu.get(), entry_sdt.get()
        conn = connect_db()
        if not conn: return
        cur = conn.cursor()
        try:
            if action == "add": cur.execute("INSERT INTO nhanvien VALUES (?,?,?,?)", (ma, ten, cv, sdt))
            elif action == "update": cur.execute("UPDATE nhanvien SET tennv=?, chucvu=?, sdt=? WHERE manv=?", (ten, cv, sdt, ma))
            elif action == "delete":
                if messagebox.askyesno("Xóa", "Xóa NV này?"): cur.execute("DELETE FROM nhanvien WHERE manv=?", (ma,))
            conn.commit(); load_data(); messagebox.showinfo("OK", "Thành công!")
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()
    
    def on_select(e):
        sel = tree.selection()
        if sel:
            v = tree.item(sel)['values']
            entry_manv.delete(0,tk.END); entry_manv.insert(0, v[0])
            entry_tennv.delete(0,tk.END); entry_tennv.insert(0, v[1])
            entry_chucvu.delete(0,tk.END); entry_chucvu.insert(0, v[2])
            entry_sdt.delete(0,tk.END); entry_sdt.insert(0, str(v[3]))

    tk.Button(btn_frame, text="Thêm", bg="#4CAF50", fg="white", command=lambda: crud_action("add")).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Sửa", bg="#FFC107", command=lambda: crud_action("update")).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Xóa", bg="#F44336", fg="white", command=lambda: crud_action("delete")).pack(side=tk.LEFT, padx=10)

    list_frame = tk.LabelFrame(frame, text="Danh Sách Nhân Viên", font=("Arial", 10, "bold"), padx=5, pady=5)
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)
    tree = ttk.Treeview(list_frame, columns=("ma","ten","cv","sdt"), show="headings")
    for c, t in zip(["ma","ten","cv","sdt"], ["Mã NV", "Tên NV", "Chức vụ", "SĐT"]):
        tree.heading(c, text=t)
    tree.pack(fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", on_select); load_data()

def create_invoice_tab(notebook):
    frame = tk.Frame(notebook)
    notebook.add(frame, text="  Hóa Đơn  ")

    info_frame = tk.LabelFrame(frame, text="Thông Tin Hóa Đơn", font=("Arial", 10, "bold"), padx=10, pady=10)
    info_frame.pack(fill="x", padx=10, pady=5)
    configure_grid_weights(info_frame, 4)

    entry_mahd = tk.Entry(info_frame)
    entry_ngay = tk.Entry(info_frame)
    entry_tongtien = tk.Entry(info_frame) # Thêm ô nhập tổng tiền

    def get_list(table, col_id, col_name):
        conn = connect_db(); data = []
        if conn:
            cur = conn.cursor(); cur.execute(f"SELECT {col_id}, {col_name} FROM {table}")
            data = [f"{row[0]} - {row[1]}" for row in cur.fetchall()]
            conn.close()
        return data

    cbb_kh = ttk.Combobox(info_frame, values=get_list("khachhang", "makh", "tenkh"))
    cbb_nv = ttk.Combobox(info_frame, values=get_list("nhanvien", "manv", "tennv"))
    cbb_sp = ttk.Combobox(info_frame, values=get_list("sanpham", "masp", "tensp"))
    
    tk.Label(info_frame, text="Mã HĐ:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    entry_mahd.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(info_frame, text="Ngày (YYYY-MM-DD):").grid(row=0, column=2, sticky="e", padx=5, pady=5)
    entry_ngay.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

    tk.Label(info_frame, text="Khách Hàng:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    cbb_kh.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(info_frame, text="Nhân Viên:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
    cbb_nv.grid(row=1, column=3, sticky="ew", padx=5, pady=5)

    tk.Label(info_frame, text="Sản Phẩm:").grid(row=2, column=0, sticky="e", padx=5, pady=5) 
    cbb_sp.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    tk.Label(info_frame, text="Tổng Tiền:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    entry_tongtien.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    btn_frame = tk.Frame(frame); btn_frame.pack(pady=10)

    def load_data():

        cbb_kh['values'] = get_list("khachhang", "makh", "tenkh")
        cbb_nv['values'] = get_list("nhanvien", "manv", "tennv")
        cbb_sp['values'] = get_list("sanpham", "masp", "tensp")
        for i in tree.get_children(): tree.delete(i)
        conn = connect_db()
        if conn:
            cur = conn.cursor()
            sql = """SELECT hd.mahd, hd.ngaylap, kh.tenkh, nv.tennv, hd.tongtien 
                     FROM hoadon hd
                     LEFT JOIN khachhang kh ON hd.makh = kh.makh
                     LEFT JOIN nhanvien nv ON hd.manv = nv.manv
                     LEFT JOIN sanpham sp ON hd.masp = sp.masp"""
            cur.execute(sql)
            for row in cur.fetchall():
                tong = int(row[4]) if row[4] else 0
                tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], "{:,}".format(tong)))
            conn.close()

    def clear_input():
        entry_mahd.delete(0, tk.END); entry_ngay.delete(0, tk.END)
        cbb_kh.set(""); cbb_nv.set(""); entry_tongtien.delete(0, tk.END)

    def crud_action(action):
        ma, ngay = entry_mahd.get(), entry_ngay.get()
        kh_val, nv_val = cbb_kh.get(), cbb_nv.get()
        tong_str = entry_tongtien.get()

        if action == "add" and (not ma or not ngay or not kh_val or not nv_val):
            messagebox.showwarning("Thiếu", "Vui lòng nhập đủ thông tin!")
            return

        makh = kh_val.split(" - ")[0] if kh_val else None
        manv = nv_val.split(" - ")[0] if nv_val else None
        
        if tong_str: tong = tong_str.replace('.', '').replace(',', '')
        else: tong = 0

        conn = connect_db()
        if not conn: return
        cur = conn.cursor()
        try:
            if action == "add":
                cur.execute("INSERT INTO hoadon VALUES (?,?,?,?,?)", (ma, ngay, makh, manv, tong))
            elif action == "update":
                cur.execute("UPDATE hoadon SET ngaylap=?, makh=?, manv=?, tongtien=? WHERE mahd=?", (ngay, makh, manv, tong, ma))
            elif action == "delete":
                if messagebox.askyesno("Xóa", "Xóa hóa đơn này?"):
                    cur.execute("DELETE FROM hoadon WHERE mahd=?", (ma,))
            
            conn.commit(); load_data(); clear_input(); messagebox.showinfo("OK", "Thành công!")
        except Exception as e: messagebox.showerror("Lỗi", str(e))
        finally: conn.close()

    def on_select(e):
        sel = tree.selection()
        if sel:
            v = tree.item(sel)['values']
            clear_input()
            entry_mahd.insert(0, v[0])
            entry_ngay.insert(0, v[1])
            
            cbb_kh.set(v[2]); cbb_nv.set(v[3])
            entry_tongtien.insert(0, str(v[4]).replace(",", ""))

    tk.Button(btn_frame, text="Thêm", bg="#4CAF50", fg="white", command=lambda: crud_action("add")).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Sửa", bg="#FFC107", command=lambda: crud_action("update")).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Xóa", bg="#F44336", fg="white", command=lambda: crud_action("delete")).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Làm mới", command=clear_input).pack(side=tk.LEFT, padx=10)

    list_frame = tk.LabelFrame(frame, text="Danh Sách Hóa Đơn", font=("Arial", 10, "bold"), padx=5, pady=5)
    list_frame.pack(fill="both", expand=True, padx=10, pady=5)

    tree = ttk.Treeview(list_frame, columns=("ma", "ngay", "kh", "nv", "tong"), show="headings")
    tree.heading("ma", text="Mã HĐ"); tree.column("ma", width=80, anchor="center")
    tree.heading("ngay", text="Ngày Lập"); tree.column("ngay", width=100, anchor="center")
    tree.heading("kh", text="Khách Hàng"); tree.column("kh", width=200)
    tree.heading("nv", text="Nhân Viên"); tree.column("nv", width=150)
    tree.heading("tong", text="Tổng Tiền"); tree.column("tong", width=120, anchor="e")

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)

    tree.bind("<<TreeviewSelect>>", on_select); load_data()


root = tk.Tk()
root.title("HỆ THỐNG QUẢN LÝ BÁN HÀNG")
w, h = 1000, 600
ws, hs = root.winfo_screenwidth(), root.winfo_screenheight()
x, y = (ws/2) - (w/2), (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
style.configure("Treeview", font=("Arial", 10), rowheight=25)

tk.Label(root, text="PHẦN MỀM QUẢN LÝ BÁN HÀNG", font=("Arial", 20, "bold"), fg="#1565C0").pack(pady=10)

notebook = ttk.Notebook(root)
notebook.pack(pady=5, padx=10, expand=True, fill="both")

create_product_tab(notebook)   
create_customer_tab(notebook)  
create_employee_tab(notebook)  
create_invoice_tab(notebook)   

root.mainloop()