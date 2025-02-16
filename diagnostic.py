import tkinter as tk
from tkinter import ttk
from os import path
from os import remove as delete_file

from config import Config
import helpers
from add_file import handle_add_file
from settings import handle_settings_request
from helpers import timestamp_to_date, RepeatTimer, get_unsynced_files
from update_files import update_files

DEFAULT_CHECK_INTERVAL = 10

last_check = 0

DEFAULT_FONT = ("Arial", 10)

config = Config()

timer = None

def start_new_timer():
    global config
    global timer
    
    if timer:
        stop_timer()
    timer = RepeatTimer(config.update_frequency, refresh_table)
    timer.daemon = True
    timer.start()

def stop_timer():
    global timer
    if timer:
        timer.cancel()

def get_data():
    files = sorted(config.files, key=lambda f: f['last-update'] if 'last-update' in f else 0, reverse=True)
    return list(map(lambda f: {
        'name': f['name'],
        'timestamp': timestamp_to_date(f['last-update']) if 'last-update' in f else 'N/A',
        'path': path.join(config.target_dir, f['name'])
        }, files))

def open_file(file_name):
    file_path = path.join(config.target_dir, file_name)
    helpers.open_file(file_path)

def remove_files(files):
    with config.lock:
        stop_timer()
        config.read_config()
        deleted_files = [file for file in config.files if file['name'] in files]
        for file in deleted_files:
            config.files.remove(file)
        config.update_config()
        start_new_timer()

def refresh_table():
    global last_check
    global config
    update_files(config)
    if config.last_update > last_check:
        last_check = config.last_update
        synced_tree.delete(*synced_tree.get_children())
        create_table()
        target_dir_var.set(config.target_dir)
        start_new_timer()

    refresh_unsynced_files()
    # set last check to current time

def create_table():
    data = get_data()

    # Define Treeview
    tree = synced_tree
    # Insert Data
    for row in data:
        tree.insert("", "end", values=(row["name"], row["timestamp"]))

    tree.pack(fill=tk.BOTH, expand=True)

    def open_by_clique(event):
        item = tree.identify_row(event.y)
        if item:
            open_file(tree.item(item, "values")[0])

    tree.bind("<Double-Button-1>", open_by_clique)
    # if empty area is clicked, deselect all
    def empty_click_handler(event):
        item = tree.identify_row(event.y)
        if not item:
            tree.selection_remove(tree.selection())
    tree.bind("<Button-1>", empty_click_handler)

def open_selected():
    selected_files = [synced_tree.item(item, "values")[0] for item in synced_tree.selection()]
    for file in selected_files:
        open_file(file)

def remove_selected():
    selected_items = synced_tree.selection()
    selected_files = [synced_tree.item(item, "values")[0] for item in selected_items]
    remove_files(selected_files)
    for item in reversed(selected_items):
        synced_tree.delete(item)
    refresh_unsynced_files()
    

# delete uncynced files
def delete_unsynced_files():
    # show a popup asking if sure
    # delete all files that are not in the config
    response = tk.messagebox.askyesno("Delete Unsynced Files", "Are you sure you want to delete all unsynced files?")
    if not response:
        return
    
    dir, unsynced_files = get_unsynced_files(config)
    print(unsynced_files)
    for file in unsynced_files:
        delete_file(path.join(dir, file))
        print(f'Deleted file {file}')
    refresh_unsynced_files()

def refresh_unsynced_files():
    listbox.delete(0, tk.END)
    dir, unsynced_files = get_unsynced_files(config)
    for file in unsynced_files:
        listbox.insert(tk.END, file)


def on_add_file():
    stop_timer()
    try:
        handle_add_file(root, config)
    except Exception as e:
        print(e)
    refresh_table()
    start_new_timer()

def build_toolbar(toolbar):
    label = tk.Label(toolbar, text="Synced Files", font=('Arial', 8))
    label.pack(side=tk.LEFT, pady=1)
    btn_remove = tk.Button(toolbar, text="❌", font=("Arial", 6, "bold"), fg="red", command=remove_selected)
    btn_remove.pack(side=tk.RIGHT, padx=5)
    btn_add = tk.Button(toolbar, text="➕", font=("Arial", 6, "bold"), fg="green", command=on_add_file)
    btn_add.pack(side=tk.RIGHT, padx=5)

def create_synced_files_frame(window):
    synced_files_frame = tk.Frame(window)
    window.add(synced_files_frame)
    
    toolbar = tk.Frame(synced_files_frame, relief=tk.RAISED, bd=2)
    toolbar.pack(fill=tk.X)
    build_toolbar(toolbar)
    
    global synced_tree
    synced_tree = ttk.Treeview(synced_files_frame, columns=("Name", "Timestamp"), show="headings")
    
    synced_tree.heading("Name", text="Name")
    synced_tree.heading("Timestamp", text="Timestamp")
    synced_tree.column("Name", anchor="w")
    synced_tree.column("Timestamp", anchor="w")
    refresh_table()

def create_unsynced_files_frame(window):
    global listbox
    unsynced_files_frame = tk.Frame(window)

    label_frame = tk.Frame(unsynced_files_frame, relief=tk.RAISED, bd=2)
    label_frame.pack(fill=tk.X)
    label = tk.Label(label_frame, text="Unsynced Files", font=('Arial', 8))
    label.pack(pady=1)
    
    listbox = tk.Listbox(unsynced_files_frame, font=DEFAULT_FONT)
    listbox.pack(fill=tk.BOTH, expand=True)
    refresh_unsynced_files()
    window.add(unsynced_files_frame, minsize=175)

def on_settings_click():
    stop_timer()
    handle_settings_request(root, config)
    refresh_table()
    start_new_timer()

def main():
    global root
    root = tk.Tk()
    root.geometry("600x400")
    root.title("Auto-upload manager")
    root.bind("<Escape>", lambda e: root.destroy())
    root.bind("<Delete>", lambda e: remove_selected())
    root.bind("<Return>", lambda e: open_selected())

    global target_dir_var
    target_dir_var = tk.StringVar()

    ttk.Style().configure("Treeview", font=DEFAULT_FONT)
    paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)
    create_unsynced_files_frame(paned_window)
    create_synced_files_frame(paned_window)

    bottom_menu = tk.Frame(root)
    bottom_menu.pack(fill=tk.X)
    tk.Label(bottom_menu, text="Target Directory: ", font=DEFAULT_FONT).pack(side=tk.LEFT, padx=5)
    tk.Label(bottom_menu, textvariable=target_dir_var, font=DEFAULT_FONT).pack(side=tk.LEFT, padx=5)

    menu_bar = tk.Menu(root)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Add File", command=on_add_file)
    file_menu.add_command(label="Delete Unsynced", command=delete_unsynced_files)
    file_menu.add_separator()
    file_menu.add_command(label="Settings", command=on_settings_click)

    menu_bar.add_cascade(label="File", menu=file_menu)

    # ---- Attach Menu to Root Window ----
    root.config(menu=menu_bar)

    start_new_timer()
    root.mainloop()

if __name__ == "__main__":
    main()

