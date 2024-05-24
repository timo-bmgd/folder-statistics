import os
import time
import pandas as pd
import matplotlib.pyplot as plt
import calmap


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


def get_mp3_files(folder_path):
    """
    Get a list of all MP3 files in a folder.
    """
    mp3_files = []
    for file in os.listdir(folder_path):
        if file.endswith('.mp3'):
            mp3_files.append(os.path.join(folder_path, file))
    return mp3_files


def main():
    load_env()  # Load environment variables from .env file
    folder_path = os.getenv('MP3_FOLDER_PATH')
    if not folder_path:
        raise EnvironmentError('MP3_FOLDER_PATH environment variable not set.')

    mp3_files = get_mp3_files(folder_path)
    creation_times = [get_file_creation_time(file) for file in mp3_files]

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

    cmap = 'coolwarm'

    # Plot each year's data on a separate subplot
    for ax, year in zip(axes, years):
        year_data = creation_series[creation_series.index.year == year]
        calmap.yearplot(year_data, fillcolor='lightgray', cmap=cmap, linewidth=0.5, year=year, ax=ax)
        ax.set_title(f'MP3 Files Creation Dates Heatmap for {year}')

    # Add a colorbar to the plot
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=creation_series.max()))
    sm._A = []
    cbar = fig.colorbar(sm, ax=axes, orientation='horizontal', pad=0.05)
    cbar.set_label('Number of Files')

    plt.show()


if __name__ == "__main__":
    main()
