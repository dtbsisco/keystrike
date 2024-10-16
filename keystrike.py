import keyboard
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk, filedialog
import threading
import webbrowser
from plyer import notification

class ToolTip:
    """Tooltip class for pop-up information"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window is not None:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(self.tooltip_window, text=self.text, relief="solid", borderwidth=1, background="#FFFFFF")
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class KeySenderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Keystrike v1")
        self.master.configure(bg="#FFFFFF")
        self.master.resizable(False, False)

        self.running_event = threading.Event()

        style = ttk.Style()
        style.configure('TFrame', background="#FFFFFF")
        style.configure('TLabel', background="#FFFFFF", font=("Arial", 12))
        style.configure('TButton', font=("Arial", 12), padding=4)
        style.configure('TEntry', font=("Arial", 12), padding=4)

        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)

        self.credits_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.credits_menu.add_command(label="GitHub", command=self.open_github)
        self.credits_menu.add_command(label="Discord", command=self.open_discord)
        
        self.menu_bar.add_cascade(label="Credits", menu=self.credits_menu)

        self.frame = ttk.Frame(self.master, padding="5")
        self.frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.title_label = ttk.Label(self.frame, text="Keystrike v1", font=("Arial", 24, "bold"), foreground="#2E86C1")
        self.title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        self.delay_entry = self.create_label_and_entry("Delay (s):", "3", 2,
                                                       "The delay before sending the first message.") 
         
        self.send_delay_entry = self.create_label_and_entry("Delay after sending (s):", "3", 3,
                                                       "The delay between sending messages.")

        self.count_entry = self.create_label_and_entry("Number of messages:", "100", 4,
                                                       "The number of messages you want to send.")

        self.text_entry = self.create_label_and_textbox("Text to send (one per line):", "Your Message", 5,
                                                       "The text you want to send, each message on a new line.")

        self.load_button = ttk.Button(self.frame, text="Load Messages", command=self.load_messages)
        self.load_button.grid(row=6, column=0, columnspan=3, pady=(10, 5))

        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=5)

        self.start_button = ttk.Button(button_frame, text="Start (F8)", command=self.send_keys_wrapper)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop (F9)", command=self.stop_operation, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)

        exit_button = ttk.Button(button_frame, text="Exit", command=self.exit_app)
        exit_button.grid(row=0, column=2, padx=5)

        keyboard.add_hotkey('F8', self.send_keys_wrapper)
        keyboard.add_hotkey('F9', self.stop_operation)

    def open_github(self):
        webbrowser.open("https://github.com/dtbsisco")

    def open_discord(self):
        webbrowser.open("https://discord.com/users/1180583624567967786")

    def create_label_and_input(self, label_text, default_value, row, tooltip_text, is_textbox=False):
        label = ttk.Label(self.frame, text=label_text)
        label.grid(row=row, column=0, padx=5, pady=5, sticky="e")

        if is_textbox:
            input_widget = tk.Text(self.frame, height=10, width=40, bg="#F8F8F8", wrap='word')
            input_widget.grid(row=row, column=1, padx=5, pady=5)
            input_widget.insert("1.0", default_value)
        else:
            input_widget = ttk.Entry(self.frame, justify='center')
            input_widget.grid(row=row, column=1, padx=5, pady=5)
            input_widget.insert(0, default_value)

        info_icon = ttk.Label(self.frame, text="ℹ️", font=("Arial", 12), foreground="#2E86C1")
        info_icon.grid(row=row, column=2, padx=5)

        ToolTip(info_icon, tooltip_text)

        return input_widget

    def create_label_and_entry(self, label_text, default_value, row, tooltip_text):
        return self.create_label_and_input(label_text, default_value, row, tooltip_text, is_textbox=False)

    def create_label_and_textbox(self, label_text, default_value, row, tooltip_text):
        return self.create_label_and_input(label_text, default_value, row, tooltip_text, is_textbox=True)

    def load_messages(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                messages = file.readlines()
            self.text_entry.delete("1.0", tk.END)
            self.text_entry.insert("1.0", ''.join(messages))

    def validate_inputs(self):
        try:
            delay = float(self.delay_entry.get())
            count = int(self.count_entry.get())
            send_delay = int(self.send_delay_entry.get())
            text = self.text_entry.get("1.0", tk.END).strip()

            if delay < 0 or count <= 0 or send_delay < 0 or not text:
                raise ValueError("Delay cannot be negative, the number of messages must be at least 1, and text cannot be empty!")

            return delay, count, text, send_delay
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return None

    def send_keys(self, text, count, delay, send_delay):
        time.sleep(delay)
        messages = text.splitlines()
        messages = [message.strip() for message in messages if message.strip()]

        if messages:
            for _ in range(count):
                if not self.running_event.is_set():
                    break
                for message in messages:
                    if not self.running_event.is_set():
                        return
                    keyboard.write(message)
                    keyboard.press_and_release('enter')
                    time.sleep(send_delay)
                    keyboard.press_and_release('enter')

    def send_keys_wrapper(self):
        validated_inputs = self.validate_inputs()
        if validated_inputs:
            delay, count, text, send_delay = validated_inputs

            self.running_event.set()
            self.start_button['state'] = tk.DISABLED
            self.stop_button['state'] = tk.NORMAL

            threading.Thread(target=self.send_keys, args=(text, count, delay, send_delay), daemon=True).start()

            notification.notify(
                title="Keystrike",
                message="Keystrike has started sending messages",
                app_name="Keystrike",
                timeout=5
            )

    def stop_operation(self):
        self.running_event.clear()
        self.start_button['state'] = tk.NORMAL
        self.stop_button['state'] = tk.DISABLED
        
        notification.notify(
            title="Keystrike",
            message="Keystrike has stopped sending messages",
            app_name="Keystrike",
            timeout=5
        )

    def exit_app(self):
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = KeySenderApp(root)
    root.mainloop()