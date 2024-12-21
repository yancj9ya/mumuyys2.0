from PIL import Image, ImageTk


class Icons:
    @classmethod
    def creat_images(cls):
        cls.power_off = ImageTk.PhotoImage(Image.open("GUI/icons/power_off.png"))
        cls.power_on = ImageTk.PhotoImage(Image.open("GUI/icons/power_on.png"))
