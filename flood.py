import keyboard
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk, filedialog
import threading

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
        label = ttk.Label(self.tooltip_window, text=self.text, relief="solid", borderwidth=1, background="lightyellow")
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class KeySenderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Keystrike v1")
        self.master.configure(bg="#FFFFFF")  # Background color
        self.master.resizable(False, False)

        self.running = False  # Track the process state
        self.lock = threading.Lock()  # Thread safety for running flag

        # Style settings
        style = ttk.Style()
        style.configure('TFrame', background="#FFFFFF")  # Frame background
        style.configure('TLabel', background="#FFFFFF", font=("Arial", 12))
        style.configure('TButton', font=("Arial", 12), padding=4)
        style.configure('TEntry', font=("Arial", 12), padding=4)

        # Main frame
        self.frame = ttk.Frame(self.master, padding="5")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create title label
        self.title_label = ttk.Label(self.frame, text="Keystrike v1", font=("Arial", 24, "bold"), foreground="#2E86C1")
        self.title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # Delay (in seconds)
        self.delay_entry = self.create_label_and_entry("Delay (s):", "3", 1,
                                                       "The delay before sending the first message.") 
         
        # Delay after message sending
        self.send_delay_entry = self.create_label_and_entry("Delay after sending (s):", "3", 2,
                                                       "The delay between sending messages.")

        # Number of messages
        self.count_entry = self.create_label_and_entry("Number of messages:", "100", 3,
                                                       "The number of messages you want to send.")

        # Text to send (multi-line input)
        self.text_entry = self.create_label_and_textbox("Text to send (one per line):", "Text", 4,
                                                       "The text you want to send, each message on a new line.")

        # Load messages from file button
        self.load_button = ttk.Button(self.frame, text="Load Messages", command=self.load_messages)
        self.load_button.grid(row=5, column=0, columnspan=3, pady=(10, 5))

        # Buttons side by side
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=5)

        # Start button
        self.start_button = ttk.Button(button_frame, text="Start", command=self.send_keys_wrapper)
        self.start_button.grid(row=0, column=0, padx=5)

        # Stop button
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_operation)
        self.stop_button.grid(row=0, column=1, padx=5)

        # Exit button
        exit_button = ttk.Button(button_frame, text="Exit", command=self.exit_app)
        exit_button.grid(row=0, column=2, padx=5)

        # Contact and author name
        self.author_label = ttk.Label(self.frame, text="Discord: xosisco", font=("Arial", 10))
        self.author_label.grid(row=7, column=0, columnspan=3, pady=(5, 0))

        # Automatic resizing
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=2)

    def create_label_and_input(self, label_text, default_value, row, tooltip_text, is_textbox=False):
        label = ttk.Label(self.frame, text=label_text)
        label.grid(row=row, column=0, padx=5, pady=5, sticky="e")

        if is_textbox:
            input_widget = tk.Text(self.frame, height=10, width=40, bg="#F8F8F8", wrap='word')  # Bigger text area for input
            input_widget.grid(row=row, column=1, padx=5, pady=5)
            input_widget.insert("1.0", default_value)
        else:
            input_widget = ttk.Entry(self.frame, justify='center')
            input_widget.grid(row=row, column=1, padx=5, pady=5)
            input_widget.insert(0, default_value)

        # Adding info icon
        info_icon = ttk.Label(self.frame, text="ℹ️", font=("Arial", 12), foreground="blue")
        info_icon.grid(row=row, column=2, padx=5)

        # Creating tooltip for the info icon
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
            self.text_entry.delete("1.0", tk.END)  # Clear existing text
            self.text_entry.insert("1.0", ''.join(messages))  # Load messages into the text area

    def validate_inputs(self):
        try:
            delay = int(self.delay_entry.get())
            count = int(self.count_entry.get())
            send_delay = int(self.send_delay_entry.get())
            text = self.text_entry.get("1.0", tk.END).strip()  # Retrieve multi-line text

            if delay < 0 or count <= 0 or send_delay < 0 or not text:
                raise ValueError("Delay cannot be negative, the number of messages must be at least 1, and text cannot be empty.")

            return delay, count, text, send_delay
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return None

    def send_keys(self, text, count, delay, send_delay):
        time.sleep(delay)
        start_time = time.time()

        # Split messages by lines
        messages = text.splitlines()
        messages = [message.strip() for message in messages if message.strip()]  # Clean up the messages

        # Send messages in a single operation
        if messages:  # Only proceed if there are valid messages
            for _ in range(count):
                with self.lock:  # Ensure thread safety
                    if not self.running:
                        break
                for message in messages:
                    with self.lock:  # Ensure thread safety
                        if not self.running:
                            return  # Exit if not running
                    keyboard.write(message)  # Send message
                    keyboard.press_and_release('enter')  # New line after each message
                    time.sleep(send_delay)  # Wait after sending the message

    def send_keys_wrapper(self):
        inputs = self.validate_inputs()
        if inputs:
            delay, count, text, send_delay = inputs
            self.start_operation()  # Set running state to True
            threading.Thread(target=self.send_keys, args=(text, count, delay, send_delay), daemon=True).start()

    def start_operation(self):
        with self.lock:
            self.running = True

    def stop_operation(self):
        with self.lock:
            self.running = False

    def exit_app(self):
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = KeySenderApp(root)
    root.mainloop()
