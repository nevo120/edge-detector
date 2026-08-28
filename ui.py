from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

# create main window
root = Tk()
image_path = StringVar()
root.configure(bg="#232227")

# main window
root.title("Edge Detector")
root.geometry("400x600")

# center frame
center_frame = Frame(root, bg="#1e1e1e")
center_frame.pack(expand=True)

#title
title_label = Label(
     center_frame,
    text="Edge Detector",
    font=("Arial", 28, "bold"),
    bg="#1e1e1e",
    fg="white"
)
title_label.pack(pady=20)


# image picker
def choose_image():
    file_path = filedialog.askopenfilename()

    if file_path:
        image_path.set(file_path)

        preview = Image.open(file_path)
        preview.thumbnail((250, 250))

        preview_tk = ImageTk.PhotoImage(preview)

        preview_label.config(image=preview_tk)
        preview_label.image = preview_tk

        print(image_path.get())


preview_frame = Frame(
    center_frame,
    bg="#2b2b2b",
    width=280,
    height=280,
    bd=1,
    relief="solid"
)
preview_frame.pack(pady=15)
preview_frame.pack_propagate(False)

# choose image button
choose_button = Button(
    center_frame,
    text="Choose Image",
    font=("Arial", 14),
    width=15,
    height=2,
    bg="#333333",
    fg="white",
    activebackground="#444444",
    activeforeground="white",
    command=choose_image
)
choose_button.pack()

#preview_label
preview_label = Label( preview_frame,bg="#2b2b2b")
preview_label.pack(expand=True)


# path label
selected_file_label = Label(
    center_frame,
    textvariable=image_path,
    bg="#1e1e1e",
    fg="#cccccc",
    wraplength=300
)

selected_file_label.pack(pady=10)

# start GUI loop
root.mainloop()