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

def open_file(file_name):
    config = Config()
    file_path = path.join(config.target_dir, file_name)
    helpers.open_file(file_path)

def remove_file(file_name, table_frame, root):
    print(f'Removing file {file_name}...')
    global timer
    timer.cancel()

    config = Config()
    deleted_file = next(filter(lambda f: f['name'] == file_name, config.files), None)
    if deleted_file:
        config.files.remove(deleted_file)
        config.update_config()
    config.update_config()
    timer = get_new_timer(table_frame, root)



# force is used on add/remove since config is already updated there
def refresh_table(table_frame, root, force_refresh_window=False):
    if update_files() or force_refresh_window:
        for widget in table_frame.winfo_children():
            widget.destroy()
        create_table(table_frame, root)
        refresh_unsynced_files()

def create_table(frame, root):
    data = get_data()

    # Define Treeview
    tree = ttk.Treeview(frame, columns=("Name", "Timestamp", "Remove"), show="headings")
    tree.heading("Name", text="Name")
    tree.heading("Timestamp", text="Timestamp")
    tree.heading("Remove", text="Remove")

    tree.column("Name", width=300, anchor="w")
    tree.column("Timestamp", width=150, anchor="w")
    tree.column("Remove", width=50, anchor="center")
    # Insert Data
    for row in data:
        tree.insert("", "end", values=(row["name"], row["timestamp"], "X"))

    tree.pack(fill=tk.BOTH, expand=True)

    # Bind Events
    def on_click(event):
        item = tree.identify_row(event.y)
        if item:
            column = tree.identify_column(event.x)
            if column == "#1":  # Name column clicked
                open_file(tree.item(item, "values")[0])
            elif column == "#3":  # Remove column clicked
                remove_file(tree.item(item, "values")[0], frame, root)
                tree.delete(item)

    tree.bind("<Button-1>", on_click)

    # Add Button
    add_button = tk.Button(frame, text="Add File", font=("Arial", 16), command=lambda: handle_add_file(frame, root))
    add_button.pack(fill=tk.X)


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

def refresh_unsynced_files():
    global listbox
    listbox.delete(0, tk.END)
    dir, unsynced_files = get_unsynced_files()
    for file in unsynced_files:
        listbox.insert(tk.END, file)

def main():
    root = tk.Tk()
    root.geometry("600x400")

    paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)


    synced_files_frame = tk.Frame(paned_window)
    create_table(synced_files_frame, root)
    paned_window.add(synced_files_frame)


    global listbox
    unsynced_files_frame = tk.Frame(paned_window)
    listbox = tk.Listbox(unsynced_files_frame)
    listbox.pack(fill=tk.BOTH, expand=True)
    paned_window.add(unsynced_files_frame)
    refresh_unsynced_files()

    global timer
    timer = get_new_timer(synced_files_frame, root)

    root.mainloop()

if __name__ == "__main__":
    main()

