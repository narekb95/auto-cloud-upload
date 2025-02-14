import tkinter as tk
from tkinter import ttk
from os import path
from os import remove as delete_file

from config import Config
import helpers
from helpers import timestamp_to_date, RepeatTimer, get_unsynced_files
from add_file import open_add_file_dialog
from update_files import update_files

DEFAULT_CHECK_INTERVAL = 5

def start_new_timer():
    global timer
    timer = RepeatTimer(DEFAULT_CHECK_INTERVAL, refresh_table)
    timer.daemon = True
    timer.start()

def stop_timer():
    global timer
    timer.cancel()

def get_data():
    config = Config()
    files = sorted(config.files, key=lambda f: f['last-update'] if 'last-update' in f else 0, reverse=True)
    return list(map(lambda f: {
        'name': f['name'],
        'timestamp': timestamp_to_date(f['last-update']) if 'last-update' in f else 'N/A',
        'path': path.join(config.target_dir, f['name'])
        }, files))

def open_file(file_name):
    config = Config()
    file_path = path.join(config.target_dir, file_name)
    helpers.open_file(file_path)

def remove_files(files):
    stop_timer()
    config = Config()
    deleted_files = [file for file in config.files if file['name'] in files]
    for file in deleted_files:
        config.files.remove(file)
    config.update_config()
    start_new_timer()


# force is used on add/remove since config is already updated there
def refresh_table(force_refresh_window=False):
    if update_files() or force_refresh_window:
        synced_tree.delete(*synced_tree.get_children())
        create_table()
        refresh_unsynced_files()

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

def handle_add_file():
    stop_timer()
    
    dialog = tk.Toplevel()
    dialog.title("Add file")
    dialog.geometry("600x400")
    dialog.transient(root)
    dialog.grab_set()
    dialog.focus_set()
    open_add_file_dialog(dialog)
    root.wait_window(dialog)
    refresh_table(force_refresh_window=True)

    start_new_timer()
    

# delete uncynced files
def delete_unsynced_files():
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
    refresh_table(force_refresh_window=True)

def refresh_unsynced_files():
    listbox.delete(0, tk.END)
    dir, unsynced_files = get_unsynced_files()
    for file in unsynced_files:
        listbox.insert(tk.END, file)

def build_toolbar(toolbar):
    label = tk.Label(toolbar, text="Synced Files")
    label.pack(side=tk.LEFT, pady=5)
    btn_remove = tk.Button(toolbar, text="❌", font=("Arial", 6, "bold"), fg="red", command=remove_selected)
    btn_remove.pack(side=tk.RIGHT, padx=5, pady=3)
    btn_add = tk.Button(toolbar, text="➕", font=("Arial", 6, "bold"), fg="green", command=handle_add_file)
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
    create_table()

def create_unsynced_files_frame(window):
    global listbox
    unsynced_files_frame = tk.Frame(window)
    label = tk.Label(unsynced_files_frame, text="Unsynced Files")
    label.pack(side=tk.TOP, pady=5)
    listbox = tk.Listbox(unsynced_files_frame)
    listbox.pack(fill=tk.BOTH, expand=True)
    delete_unsynced_files_btn = tk.Button(unsynced_files_frame, text="Delete Unsynced Files", command=delete_unsynced_files)
    delete_unsynced_files_btn.pack(side=tk.BOTTOM)
    refresh_unsynced_files()
    window.add(unsynced_files_frame)

def main():
    global root
    root = tk.Tk()
    root.geometry("600x400")
    root.title("Auto-upload manager")
    root.bind("<Escape>", lambda e: root.destroy())
    # on delete clique handle remove
    root.bind("<Delete>", lambda e: remove_selected())
    root.bind("<Return>", lambda e: open_selected())

    paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)
    create_synced_files_frame(paned_window)
    create_unsynced_files_frame(paned_window)

    start_new_timer()

    root.mainloop()

if __name__ == "__main__":
    main()

