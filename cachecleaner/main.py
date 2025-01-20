import customtkinter as ctk
import os 
import math
import webbrowser
cache_path = os.getenv("TEMP")

app = ctk.CTk()
app.geometry("400x300")
app.title("Cache cleaner")





def update_cache():
    size()
    progressbar.set(0)
def get_files(path): # Replace with your actual method to list cache files 
    return [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile]

def get_directory_size(directory):
    total_size = 0
    # Walk through directory, including all subfolders and subfiles.
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            # Add file size to total size
            total_size += os.path.getsize(file_path)
    return total_size

def notification(size):
    notification = ctk.CTkToplevel()
    notification.geometry("300x100")
    notification.title("Success")
    label = ctk.CTkLabel(notification, height = 300, width = 100, text = f"Success {size} files were removed\n{convert_size(directory_size)} was cleaned")
    label.pack()
    progressbar.set(0)


def clear_cache_button():
    try:
        cache_files = get_files(cache_path)  # Retrieve all files in one call
        total_files = len(cache_files)

        if total_files == 0:
            return 

        for index, file in enumerate(cache_files):
            try:
                os.remove(file)
            except Exception as e:
                pass

            # Update progress bar based on the number of files processed
            progress_value = (index + 1) / total_files
            progressbar.set(progress_value)

        size()
        notification(total_files)

    except Exception as e:
        print(f"An error occurred: {e}")



# Specify your directory here
directory_path = r"C:\Users\i7\AppData\Local\Temp"
directory_size = get_directory_size(directory_path)

# Optionally, you can convert the size to a more readable format (KB, MB, GB)
def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"



info_frame = ctk.CTkFrame(app, width = 400, height = 150, fg_color = "#e1ecef")
info_frame.place(x = 0, y = 0)

def size():
    info_label = ctk.CTkLabel(info_frame, text = convert_size(directory_size), font = ("Montserrat", 25))
    info_label.place(x = 110, y = 70)
size()

button1 = ctk.CTkButton(app, text="Clear Cache",font = ("Montserrat", 18), command=clear_cache_button, height = 70, width = 120)
button1.place(x = 60, y = 150)

button2 = ctk.CTkButton(app, text="Refresh Button",font = ("Montserrat", 18), command=update_cache, height = 70, width = 120)
button2.place(x = 220, y = 150)




progressbar = ctk.CTkProgressBar(app, width = 280)
progressbar.place(x= 60, y = 250)
progressbar.set(0)


def open_link():
    webbrowser.open("https://www.youtube.com/@FIFA14PATCH24")

# Footer frame with improved styling
footer_frame = ctk.CTkFrame(app, fg_color="#f0f0f0", height=50)  # Slightly taller and with a soft grey background
footer_frame.pack(side="bottom", fill="x", pady=(10, 0))  # Added spacing above the footer

# Footer label for credits with better font styling
credit_label = ctk.CTkLabel(
    footer_frame, 
    text="Created by Asap", 
    text_color="#333333",  # Darker text color for better contrast
    font=("Arial", 12, "bold")  # Modern font with bold styling
)
credit_label.pack(side="left", padx=20)

# Footer button styled as a hyperlink
link_button = ctk.CTkButton(
    footer_frame, 
    text="Visit YouTube", 
    fg_color="transparent", 
    text_color="#1e90ff",  # Blue text color to resemble a link
    hover_color="#87ceeb",  # Lighter blue on hover
    font=("Arial", 12),  # Underlined text for link appearance
    command=open_link
)
link_button.pack(side="right", padx=20)

app.mainloop()