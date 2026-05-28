import sys
import tkinter as tk
from tkinter import scrolledtext
from pynput import mouse
from PIL import ImageGrab
import pyperclip

# Глобальная переменная для отслеживания состояния работы
is_running = True

# --- Перенаправление print в GUI ---
class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END) # Автопрокрутка вниз
        
    def flush(self):
        pass

# --- Функционал ---
def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def on_click(x, y, button, pressed):
    global is_running
    
    if pressed and button == mouse.Button.left:
        # Если захват поставлен на паузу, ничего не делаем
        if not is_running:
            return

        # Проверка, не кликнули ли мы по самому окну
        if root.winfo_exists() and \
           root.winfo_rootx() <= x <= root.winfo_rootx() + root.winfo_width() and \
           root.winfo_rooty() <= y <= root.winfo_rooty() + root.winfo_height():
            return

        try:
            bbox = (x, y, x + 1, y + 1)
            img = ImageGrab.grab(bbox=bbox)
            rgb = img.getpixel((0, 0))
            hex_color = rgb_to_hex(rgb).upper()
            
            pyperclip.copy(hex_color)
            print(f"Скопировано! HEX: {hex_color} | RGB: {rgb}")
            
            # Обновляем цветной квадратик и текст в GUI
            color_preview.config(bg=hex_color)
            color_label.config(text=hex_color)
            
        except Exception as e:
            print(f"Ошибка при захвате цвета: {e}")

# Кнопки
def stop_capture():
    global is_running
    if is_running:
        is_running = False
        status_label.config(text="Статус: Пауза", fg="red")
        print("Захват цвета приостановлен.")

def start_capture():
    global is_running
    if not is_running:
        is_running = True
        status_label.config(text="Статус: Работает", fg="green")
        print("Захват цвета возобновлен.")

# GUI
def start_app():
    global root, color_preview, color_label, status_label
    root = tk.Tk()
    root.title("Color Picker")
    root.geometry("450x300+100+100")
    root.attributes('-topmost', True)
    
    # --- Настройка корректного закрытия фонового потока pynput при закрытии окна ---
    def on_closing():
        root.destroy()
        sys.exit()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # --- Верхняя панель: Цвет и Статус ---
    top_frame = tk.Frame(root, pady=10)
    top_frame.pack(fill=tk.X)
    
    # Цветной квадратик
    color_preview = tk.Frame(top_frame, width=40, height=40, bg="#FFFFFF", relief=tk.SOLID, bd=1)
    color_preview.pack(side=tk.LEFT, padx=15)
    color_preview.pack_propagate(False)
    
    # Текстовый код цвета
    color_label = tk.Label(top_frame, text="#FFFFFF", font=("Courier", 14, "bold"))
    color_label.pack(side=tk.LEFT)
    
    # Текстовый статус работы
    status_label = tk.Label(top_frame, text="Статус: Работает", font=("Arial", 10, "bold"), fg="green")
    status_label.pack(side=tk.RIGHT, padx=15)
    
    # --- Средняя панель: Кнопки управления ---
    btn_frame = tk.Frame(root, pady=5)
    btn_frame.pack(fill=tk.X)
    
    btn_start = tk.Button(btn_frame, text="Включить (Старт)", command=start_capture, width=15, bg="#E1F5FE")
    btn_start.pack(side=tk.LEFT, padx=15)
    
    btn_stop = tk.Button(btn_frame, text="Выключить (Пауза)", command=stop_capture, width=15, bg="#FFEBEE")
    btn_stop.pack(side=tk.LEFT, padx=5)
    
    # --- Нижняя панель: Логи ---
    log_area = scrolledtext.ScrolledText(root, state='normal', height=8)
    log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    # Перенаправляем stdout
    sys.stdout = TextRedirector(log_area)

    print("=" * 30)
    print("Color Picker запущен!")
    print("ЛКМ в любом месте -> цвет в буфер")
    print("Клик по этому окну игнорируется.")
    print("=" * 30)
    
    listener_mouse = mouse.Listener(on_click=on_click)
    listener_mouse.start()
    
    root.mainloop()

if __name__ == "__main__":
    start_app()