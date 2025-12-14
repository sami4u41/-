import socket
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading

class PortScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("أداة مسح المنافذ")
        self.root.geometry("600x500")
        
        # عنوان الهدف
        tk.Label(root, text="الهدف:").pack(pady=5)
        self.target_entry = tk.Entry(root, width=40)
        self.target_entry.pack(pady=5)
        self.target_entry.insert(0, "192.168.1.1")
        
        # المنافذ المطلوب فحصها
        tk.Label(root, text="المنافذ (مفصولة بفواصل):").pack(pady=5)
        self.ports_entry = tk.Entry(root, width=40)
        self.ports_entry.pack(pady=5)
        self.ports_entry.insert(0, "80,443,22,21,25,53,110,135,139,143,445,993,995,1723,3306,3389,5900,8080")
        
        # زر البدء
        self.scan_btn = tk.Button(root, text="بدء المسح", command=self.start_scan, bg="green", fg="white")
        self.scan_btn.pack(pady=10)
        
        # شريط التقدم
        self.progress = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
        self.progress.pack(pady=5)
        
        # منطقة النتائج
        self.result_text = scrolledtext.ScrolledText(root, width=70, height=20)
        self.result_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    def start_scan(self):
        target = self.target_entry.get()
        ports_str = self.ports_entry.get()
        
        if not target:
            messagebox.showerror("خطأ", "يرجى إدخال عنوان الهدف")
            return
        
        try:
            ports = [int(port.strip()) for port in ports_str.split(",")]
        except ValueError:
            messagebox.showerror("خطأ", "المنافذ يجب أن تكون أرقاماً مفصولة بفواصل")
            return
        
        # تعطيل الزر أثناء المسح
        self.scan_btn.config(state=tk.DISABLED, text="جاري المسح...")
        self.progress['maximum'] = len(ports)
        self.progress['value'] = 0
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"بدء مسح المنافذ على {target}...\n")
        
        # تشغيل المسح في thread منفصل
        threading.Thread(target=self.run_scan, args=(target, ports)).start()
    
    def run_scan(self, target, ports):
        open_ports = []
        for i, port in enumerate(ports):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target, port))
                if result == 0:
                    self.result_text.insert(tk.END, f"المنفذ {port} مفتوح\n")
                    open_ports.append(port)
                else:
                    self.result_text.insert(tk.END, f"المنفذ {port} مغلق\n")
                sock.close()
            except Exception as e:
                self.result_text.insert(tk.END, f"خطأ في فحص المنفذ {port}: {str(e)}\n")
            
            # تحديث شريط التقدم
            self.progress['value'] = i + 1
            self.result_text.see(tk.END)
            self.root.update_idletasks()
        
        # إظهار النتيجة النهائية
        self.result_text.insert(tk.END, f"\n----- المسح اكتمل -----\n")
        self.result_text.insert(tk.END, f"عدد المنافذ المفتوحة: {len(open_ports)}\n")
        if open_ports:
            self.result_text.insert(tk.END, f"المنافذ المفتوحة: {', '.join(map(str, open_ports))}\n")
        
        # إعادة تمكين الزر
        self.scan_btn.config(state=tk.NORMAL, text="بدء المسح")

# تشغيل التطبيق
if __name__ == "__main__":
    root = tk.Tk()
    app = PortScannerApp(root)
    root.mainloop()