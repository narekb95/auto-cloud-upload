import tkinter as tk
from os import path
from os import remove as delete_file

from config import Config
from helpers import timestamp_to_date, open_file, RepeatTimer, get_unsynced_files
from add_file import open_add_file_dialog
from update_files import update_files

DEFAULT_CHECK_INTERVAL = 5

def get_new_timer(table_frame, root):
    timer = RepeatTimer(DEFAULT_CHECK_INTERVAL, refresh_table, [table_frame, root])
    timer.daemon = True
    timer.start()
    return timer


def get_data():
    config = Config()
    files = sorted(config.files, key=lambda f: f['last-update'] if 'last-update' in f else 0, reverse=True)
    return list(map(lambda f: {
        'name': f['name'],
        'timestamp': timestamp_to_date(f['last-update']) if 'last-update' in f else 'N/A',
        'path': path.join(config.target_dir, f['name'])
        }, files))

def remove_file(file_name, table_frame, root):
    print(f'Removing file {file_name}...')
    global timer
    timer.cancel()

    config = Config()
    config.files = list(filter(lambda f: f['name'] != file_name, config.files))
    config.update_config()
    refresh_table(table_frame, root, force_refresh_window=True)

    timer = get_new_timer(table_frame, root)



# force is used on add/remove since config is already updated there
def refresh_table(table_frame, root, force_refresh_window=False):
    print('Refreshing table...')
    if update_files() or force_refresh_window:
        for widget in table_frame.winfo_children():
            widget.destroy()
        create_table(table_frame, root)
        for widget in unsynced_files_frame.winfo_children():
            widget.destroy()
        refresh_unsynced_files(unsynced_files_frame)

def create_table(frame, root):
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

        label_remove = tk.Button(frame, text='X', padx=25, pady=1, borderwidth=0, relief="solid", command=lambda r=row: remove_file(r['name'], frame, root))
        label_remove.config(bg=bg_col, fg="red", font=("Arial", 10, "bold"))
        label_remove.grid(row=i, column=2, sticky="nsew")

    frame.grid_columnconfigure(0, weight=8)
    frame.grid_columnconfigure(1, weight=3)
    frame.grid_columnconfigure(2, weight=1)

    add_button = tk.Button(frame, text="Add File", padx=25, pady=5, borderwidth=0, relief="solid", font=("Arial", 16), command=lambda: handle_add_file(frame, root))
    add_button.grid(row=len(data), column=0, columnspan=3, sticky="nsew")

def handle_add_file(table_frame, root):
    global timer
    timer.cancel()
    
    dialog = tk.Toplevel()
    dialog.title("Add file")
    dialog.geometry("600x400")
    dialog.transient(root)
    open_add_file_dialog(dialog)
    root.wait_window(dialog)
    refresh_table(table_frame, root, force_refresh_window=True)

    timer = get_new_timer(table_frame, root)
    

# delete uncynced files
def delete_unsynced_files(table_frame):
    # show a popup asking if sure
    # delete all files that are not in the config
    response = tk.messagebox.askyesno("Delete Unsynced Files", "Are you sure you want to delete all unsynced files?")
    if not response:
        return
    
    dir, unsynced_files = get_unsynced_files()
    print(unsynced_files)
    for file in unsynced_files:
        delete_file(path.join(dir, file))
        print(f'Deleted file {file}')
    refresh_table(table_frame, root, force_refresh_window=True)

def resize_table(event, window):
    canvas_width = event.width
    canvas.itemconfig(window, width=canvas_width)

def update_scrollregion(_):
    canvas.configure(scrollregion=canvas.bbox("all"))

def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def refresh_unsynced_files(frame):
    dir, unsynced_files = get_unsynced_files()
    for file in unsynced_files:
        file_label = tk.Label(frame, text=file, padx=5, pady=5, borderwidth=0, relief="solid", font=("Arial", 10))
        file_label.pack(side=tk.LEFT, padx=5)
    frame.update_idletasks()


def create_unsynced_files_widget(canvas):
    unsynced_frame = tk.Frame(canvas)
    unsynced_frame.pack(side=tk.BOTTOM, fill=tk.X)

    unsynced_label = tk.Label(unsynced_frame, text="Unsynced Files:", font=("Arial", 12, "bold"))
    unsynced_label.pack(side=tk.LEFT, padx=10)

    unsynced_canvas = tk.Canvas(unsynced_frame, height=30)
    unsynced_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)

    unsynced_scrollbar = tk.Scrollbar(unsynced_frame, orient=tk.HORIZONTAL, command=unsynced_canvas.xview)
    unsynced_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    unsynced_canvas.configure(xscrollcommand=unsynced_scrollbar.set)
    unsynced_files_frame = tk.Frame(unsynced_canvas)
    unsynced_canvas.create_window((0, 0), window=unsynced_files_frame, anchor="nw")
    unsynced_canvas.configure(scrollregion=unsynced_canvas.bbox("all"))
    refresh_unsynced_files(unsynced_files_frame)
    return unsynced_canvas


def createTableWindow(root, canvas):
    table_frame = tk.Frame(canvas)
    table_window = canvas.create_window((0, 0), window=table_frame, anchor="nw")
    canvas.bind("<Configure>", lambda e, window=table_window: resize_table(e, window))
    table_frame.bind("<Configure>", update_scrollregion)
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)

    create_table(table_frame, root)
    global timer
    timer = get_new_timer(table_frame, root)
    return table_frame

root = tk.Tk()
root.title("Active files")
root.geometry("600x400")
canvas = tk.Canvas(root)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

table_frame = createTableWindow(root, canvas)
unsynced_files_frame = create_unsynced_files_widget(canvas)

delete_button = tk.Button(canvas, text="Delete Unsynced Files", padx=10, pady=5,\
                command= lambda table_frame = table_frame: delete_unsynced_files(table_frame))
delete_button.pack(side=tk.BOTTOM, anchor="se", padx=10, pady=10)


root.mainloop()
