import tkinter as tk

from os import path
from config import Config
from helpers import timestamp_to_date, open_file
from tkinter import filedialog

def get_data():
    config = Config()
    files = sorted(config.files, key=lambda f: f['last-update'] if 'last-update' in f else 0, reverse=True)
    return list(map(lambda f: {
        'name': f['name'],
        'timestamp': timestamp_to_date(f['last-update']) if 'last-update' in f else 'N/A',
        'path': path.join(config.target_dir, f['name'])
        }, files))

def remove_file(file_name, table_frame):
    config = Config()
    config.files = list(filter(lambda f: f['name'] != file_name, config.files))
    config.update_config()
    refresh_table(table_frame)

        
def refresh_table(table_frame):
    for widget in table_frame.winfo_children():
        widget.destroy()
    create_table(table_frame)

def create_table(frame):
    data = get_data()
    for i, row in enumerate(data):
        bg_col = "white" if i % 2 == 0 else "lightgrey"

        label_name = tk.Label(frame, text=row['name'], padx=25, pady=5, borderwidth=0, relief="solid",bg=bg_col, anchor="w", font=("Arial", 16))
        label_name.grid(row=i, column=0, sticky="nsew")

        label_name.bind("<Enter>", lambda e, lbl=label_name: lbl.config(fg="blue"))
        label_name.bind("<Leave>", lambda e, lbl=label_name: lbl.config(fg="black"))
        label_name.bind("<Button-1>", lambda e, path=row['path']: open_file(path))

        label_timestamp = tk.Label(frame, text=row['timestamp'], padx=25, pady=5, borderwidth=0, relief="solid", bg=bg_col, anchor="w", font=("Arial", 16))
        label_timestamp.grid(row=i, column=1, sticky="nsew")

        label_remove = tk.Button(frame, text="X", padx=25, pady=1, borderwidth=0, relief="solid")
        label_remove.config(bg=bg_col, fg="red", font=("Arial", 10, "bold"))
        label_remove.grid(row=i, column=2, sticky="nsew")
        label_remove.bind("<Button-1>", lambda e, row=row: remove_file(row['name'], frame))

    frame.grid_columnconfigure(0, weight=8)
    frame.grid_columnconfigure(1, weight=3)
    frame.grid_columnconfigure(2, weight=1)


def resize_table(event):
    canvas_width = event.width
    canvas.itemconfig(table_window, width=canvas_width)

def update_scrollregion(_):
    canvas.configure(scrollregion=canvas.bbox("all"))

def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

root = tk.Tk()
root.title("Active files")
root.geometry("600x400")
canvas = tk.Canvas(root)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
table_frame = tk.Frame(canvas)
table_window = canvas.create_window((0, 0), window=table_frame, anchor="nw")

# add button to the bottom right corner with small margin
refresh_button = tk.Button(canvas, text="Refresh", padx=10, pady=5, command=lambda: refresh_table(table_frame))
refresh_button.pack(side=tk.BOTTOM, anchor="se", padx=10, pady=10)

canvas.bind("<Configure>", resize_table)
table_frame.bind("<Configure>", update_scrollregion)
canvas.bind_all("<MouseWheel>", on_mouse_wheel)

create_table(table_frame)

root.mainloop()
