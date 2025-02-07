# this file is used to generate random coordinates which obtained from gauss distribution.
# Created by <yancj> on 2024/12/25.

from random import gauss, randint


def random_num(mu: float, sigma: float, range: int = 7) -> float:
    """
    This function is used to generate random number from gauss distribution.
    :param mu: mean of the distribution
    :param sigma: standard deviation of the distribution
    :return: a random number from gauss distribution between given range.
    """

    while True:
        rand_num = gauss(mu, sigma)
        if rand_num >= -range and rand_num <= range:
            return rand_num


def RandomCoord(rect: list | tuple, mu=0, sigma=1, range=7) -> tuple:
    """
    This function is used to generate random coordinates from gauss distribution.
    :param rect: a list or tuple which contains the range of x and y coordinates.
    :param mu: mean of the distribution
    :param sigma: standard deviation of the distribution
    :param range: a number which contains the range [-range, range] of random number.
    :return: coordinate (x, y)
    """
    x = random_num(mu, sigma, range)
    y = random_num(mu, sigma, range)
    #
    coord_x = (rect[2] - rect[0]) * (x + range) / (range * 2) + rect[0]
    coord_y = (rect[3] - rect[1]) * (y + range) / (range * 2) + rect[1]
    return int(coord_x), int(coord_y)


if __name__ == "__main__":
    import customtkinter as ctk
    from time import sleep
    from threading import Thread

    root = ctk.CTk()
    root.geometry("400x400")
    root.title("Random Coord")
    canvas = ctk.CTkCanvas(master=root, width=400, height=400)
    canvas.pack(fill="both", expand=True)
    rect = (10, 10, 200, 200)
    canvas.create_rectangle(rect[0], rect[1], rect[2], rect[3], outline="black")

    def run():
        for i in range(1000):
            coord = RandomCoord(rect, sigma=2, range=7)
            # coord = randint(10, 200), randint(10, 200)
            canvas.create_oval(coord[0] - 2, coord[1] - 2, coord[0] + 2, coord[1] + 2, fill="red")
            sleep(0.01)

    t = Thread(target=run)
    t.start()
    root.mainloop()
