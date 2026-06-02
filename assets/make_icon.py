from PIL import Image

# Open your source PNG
logo = Image.open("icon.png")

# Save it as an ICO, explicitly telling it to bundle all the standard Windows sizes
logo.save(
    "icon.ico", 
    format="ICO", 
    sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
)
print("Successfully created icon.ico!")
