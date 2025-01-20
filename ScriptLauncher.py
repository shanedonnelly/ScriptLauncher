import os
import sys
import tkinter as tk
from tkinter import messagebox
import subprocess
import signal

SCRIPTS_FOLDER = "scripts"
MAX_COLUMNS = 5
BORDER_COLOR = "#87CEEB"

class ScriptLauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ShaneScriptLauncher")
        self.root.configure(highlightbackground=BORDER_COLOR, highlightthickness=2)
        self.next_position = 0  # Track next available position

        signal.signal(signal.SIGINT, self.exit_app)
        root.protocol("WM_DELETE_WINDOW", self.exit_app)

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        win_w = int(screen_w * 0.9)
        win_h = int(screen_h * 0.9)
        pos_x = (screen_w - win_w) // 2
        pos_y = (screen_h - win_h) // 2
        self.root.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

        os.makedirs(SCRIPTS_FOLDER, exist_ok=True)

        self.canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")
        self.canvas.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

        self.scripts_frame = tk.Frame(self.canvas, background="#ffffff")
        self.canvas.create_window((0, 0), window=self.scripts_frame, anchor="nw")

        self.scripts_frame.bind("<Configure>", self.on_frame_configure)

        self.plus_btn = tk.Button(
            self.scripts_frame,
            text="➕",
            width=20,
            height=5,
            command=self.open_add_dialog
        )

        self.load_existing_scripts()
        self.update_plus_position()

    def exit_app(self, *args):
        self.root.quit()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_plus_position(self):
        """Place the '+' button at the next available position"""
        row = self.next_position // MAX_COLUMNS
        col = self.next_position % MAX_COLUMNS
        self.plus_btn.grid(row=row, column=col, padx=5, pady=5)

    def add_script_button(self, title, file_name):
        self.plus_btn.grid_forget()
        
        frame = tk.Frame(self.scripts_frame, highlightbackground=BORDER_COLOR, highlightthickness=1)
        
        # Use current next_position for this script
        row = self.next_position // MAX_COLUMNS
        col = self.next_position % MAX_COLUMNS
        
        frame.grid(row=row, column=col, padx=5, pady=5)

        btn = tk.Button(frame, text=title, width=20, height=5,
                       command=lambda f=file_name: self.run_script(f))
        btn.pack(side=tk.LEFT)

        buttons_right_frame = tk.Frame(frame)
        buttons_right_frame.pack(side=tk.LEFT, padx=5)

        edit_btn = tk.Button(buttons_right_frame, text="✎", width=5, height=2,
                          command=lambda f=file_name, t=title: self.edit_script(f, t))
        edit_btn.pack(side=tk.TOP, pady=2)

        del_btn = tk.Button(buttons_right_frame, text="🗑", width=5, height=2,
                         command=lambda f=file_name: self.delete_script(f, frame))
        del_btn.pack(side=tk.TOP, pady=2)

        # Increment next_position for next item
        self.next_position += 1
        self.update_plus_position()

    def delete_script(self, file_name, frame):
        script_path = os.path.join(SCRIPTS_FOLDER, file_name)
        if os.path.exists(script_path):
            os.remove(script_path)
        
        frame.destroy()
        
        # Reposition all remaining scripts
        script_frames = [w for w in self.scripts_frame.winfo_children() if isinstance(w, tk.Frame)]
        self.next_position = 0
        
        for script_frame in script_frames:
            row = self.next_position // MAX_COLUMNS
            col = self.next_position % MAX_COLUMNS
            script_frame.grid(row=row, column=col, padx=5, pady=5)
            self.next_position += 1
        
        self.update_plus_position()

    def load_existing_scripts(self):
        self.next_position = 0
        for file in sorted(os.listdir(SCRIPTS_FOLDER)):
            if file.endswith(".txt"):
                script_path = os.path.join(SCRIPTS_FOLDER, file)
                with open(script_path, "r") as f:
                    lines = f.read().split('\n', 1)
                title = lines[0] if lines else file
                self.add_script_button(title, file)

    def save_script(self, file_name, title, content):
        script_path = os.path.join(SCRIPTS_FOLDER, file_name)
        with open(script_path, "w") as f:
            f.write(title + "\n" + content)

    def run_script(self, file_name):
        script_path = os.path.join(SCRIPTS_FOLDER, file_name)
        if os.path.exists(script_path):
            with open(script_path, 'r') as f:
                f.readline()  # skip title
                script_content = f.read().strip()
            temp_script = os.path.join(SCRIPTS_FOLDER, f"temp_{file_name}")
            with open(temp_script, 'w') as f:
                f.write(script_content)
            subprocess.run(["chmod", "777", temp_script])
            subprocess.run(["gnome-terminal", "--", "bash", "-c", f"'{temp_script}'; exec bash"])
            os.remove(temp_script)
        else:
            messagebox.showerror("Error", "Script not found!")

    def show_script_dialog(self, title="", content="", file_name=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Script" if file_name else "Add Script")
        dialog.geometry("800x600")
        dialog.transient(self.root)
        dialog.attributes('-alpha', 0.9)
        dialog.configure(highlightbackground=BORDER_COLOR, highlightthickness=2)

        title_label = tk.Label(dialog, text="Script Title:")
        title_label.pack(pady=10)
        title_entry = tk.Entry(dialog, width=80)
        title_entry.insert(0, title)
        title_entry.pack(pady=10)

        content_label = tk.Label(dialog, text="Script Content:")
        content_label.pack(pady=10)
        content_text = tk.Text(dialog, width=80, height=20)
        content_text.pack(pady=10)
        content_text.insert("1.0", content)

        def on_save():
            new_title = title_entry.get().strip()
            script_content = content_text.get("1.0", tk.END).strip()
            if not new_title or not script_content:
                messagebox.showerror("Error", "Please fill in both fields.")
                return

            if file_name:
                self.save_script(file_name, new_title, script_content)
                for widget in self.scripts_frame.winfo_children():
                    if isinstance(widget, tk.Frame):
                        script_btn = widget.winfo_children()[0]
                        if script_btn['text'] == title:
                            script_btn.configure(text=new_title)
            else:
                existing = [f for f in os.listdir(SCRIPTS_FOLDER)
                          if f.startswith("script") and f.endswith(".txt")]
                next_index = len(existing) + 1
                new_file_name = f"script{next_index}.txt"
                self.save_script(new_file_name, new_title, script_content)
                self.add_script_button(new_title, new_file_name)
            dialog.destroy()

        save_button = tk.Button(dialog, text="Save", command=on_save)
        save_button.pack(pady=10)

    def open_add_dialog(self):
        self.show_script_dialog()

    def edit_script(self, file_name, title):
        script_path = os.path.join(SCRIPTS_FOLDER, file_name)
        if os.path.exists(script_path):
            with open(script_path, 'r') as f:
                f.readline()  # skip title
                content = f.read().strip()
            self.show_script_dialog(title, content, file_name)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ScriptLauncherApp(root)
        root.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)