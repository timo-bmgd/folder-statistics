import os
import sys
import time
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import calmap
import tkinter as tk
from tkinter import filedialog


def load_env(file_path='.env'):
    """
    Load environment variables from a .env file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'{file_path} does not exist.')

    with open(file_path, 'r') as file:
        for line in file:
            # Remove any leading/trailing whitespace and skip empty lines
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Parse the key-value pair
            key, value = line.split('=', 1)
            os.environ[key] = value


def get_file_creation_time(file_path):
    """
    Get the creation time of a file in a human-readable format.
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(file_path)))


def get_files(folder_path, file_extension):
    """
    Get a list of all files with the specified extension in a folder.
    """
    files = []
    for file in os.listdir(folder_path):
        if file.endswith(file_extension):
            files.append(os.path.join(folder_path, file))
    return files


def generate_heatmap(folder_path, file_extension, cmap):
    # Get the files with the specified file extension
    files = get_files(folder_path, file_extension)
    if not files:
        print(f'No {file_extension.upper()} files found in the specified folder.')
        sys.exit(1)

    # Get creation times of files
    creation_times = [get_file_creation_time(file) for file in files]

    # Convert creation times to a pandas Series with counts per day
    creation_dates = [time.split(' ')[0] for time in creation_times]
    creation_series = pd.Series(creation_dates).value_counts().sort_index()
    creation_series.index = pd.to_datetime(creation_series.index)

    # Determine the unique years in the data
    years = creation_series.index.year.unique()

    # Create subplots: one row per year
    fig, axes = plt.subplots(len(years), 1, figsize=(16, 4 * len(years)), constrained_layout=True)

    if len(years) == 1:
        axes = [axes]  # Ensure axes is iterable if only one subplot

    # Plot each year's data on a separate subplot
    for ax, year in zip(axes, years):
        year_data = creation_series[creation_series.index.year == year]
        calmap.yearplot(year_data, fillcolor='lightgray', cmap=cmap, linewidth=0.5, year=year, ax=ax)
        ax.set_title(f'{file_extension.upper()} Files Creation Dates Heatmap for {year}')

    # Add a colorbar to the plot
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=creation_series.max()))
    sm._A = []
    cbar = fig.colorbar(sm, ax=axes, orientation='horizontal', pad=0.05)
    cbar.set_label('Number of Files')

    plt.show()


def browse_folder():
    folder_path = filedialog.askdirectory()
    entry_folder.delete(0, tk.END)
    entry_folder.insert(0, folder_path)


def generate_heatmap_from_gui():
    folder_path = entry_folder.get()
    file_extension = entry_extension.get().lower()
    cmap = cmap_var.get()  # Get the selected colormap from the dropdown menu

    if not os.path.isdir(folder_path):
        tk.messagebox.showerror("Error", "Invalid folder path.")
        return

    if not file_extension:
        tk.messagebox.showerror("Error", "Please enter a file extension.")
        return

    generate_heatmap(folder_path, file_extension, cmap)


# Create the main Tkinter window
root = tk.Tk()
root.title("File Creation Date Heatmap")

# Folder Path
label_folder = tk.Label(root, text="Folder Path:")
label_folder.grid(row=0, column=0, padx=5, pady=5)
entry_folder = tk.Entry(root, width=50)
entry_folder.grid(row=0, column=1, padx=5, pady=5)
button_browse = tk.Button(root, text="Browse", command=browse_folder)
button_browse.grid(row=0, column=2, padx=5, pady=5)

# File Extension
label_extension = tk.Label(root, text="File Extension:")
label_extension.grid(row=1, column=0, padx=5, pady=5)
entry_extension = tk.Entry(root, width=10)
entry_extension.grid(row=1, column=1, padx=5, pady=5)
default_extension = "mp3"
entry_extension.insert(tk.END, default_extension)

# Colormap Selection
label_cmap = tk.Label(root, text="Colormap:")
label_cmap.grid(row=2, column=0, padx=5, pady=5)
cmap_var = tk.StringVar(root)
cmap_var.set('coolwarm')
cmap_choices = ['coolwarm', 'viridis', 'inferno']  # List of available colormap options
option_menu_cmap = tk.OptionMenu(root, cmap_var, *cmap_choices)
option_menu_cmap.grid(row=2, column=1, padx=5, pady=5)


# Generate Heatmap Button
button_generate = tk.Button(root, text="Generate Heatmap", command=generate_heatmap_from_gui)
button_generate.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()
