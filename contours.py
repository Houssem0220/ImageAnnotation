# IMPORTS

import cv2
import numpy as np
import random as rd
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon


# TOOLS

def threshold(x):
    if x < 128:
        return 0
    return 1


def show_polygons(polygons_list, size):
    width, height = size
    fig = plt.figure()
    ax = plt.axes()
    height, width = size
    ax.set(xlim=(0, width), ylim=(0, height))
    for p in polygons_list:
        X = p[:, 0]
        Y = p[:, 1]
        print(f"Le polygone contient {len(X)} points.")
        plt.plot(X, Y)
    plt.show()


def generate_color():
    r = rd.random()
    g = rd.random()
    b = rd.random()
    a = 0.8
    return (r, g, b, a)


def is_in_contour(vertice, size, marge):
    w, h = size
    x, y = vertice
    return x >= marge and x <= w-marge and y >= marge and y <= h-marge

# FUNCTION


def get_contours_approx(mask, eps, marge=0):
    mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    height, width = mask_gray.shape
    threshold_vec = np.vectorize(threshold)
    mask_vec = threshold_vec(mask_gray)
    contours, hierarchy = cv2.findContours(
        image=mask_vec, mode=cv2.RETR_FLOODFILL, method=cv2.CHAIN_APPROX_SIMPLE)
    contours_approx = [cv2.approxPolyDP(
        contour, 1/eps, closed=True) for contour in contours]
    list_polygons_approx = []
    for contour in contours_approx:
        vertices = []
        for v in contour:
            x = v[0][0]
            y = height - v[0][1]
            if is_in_contour((x, y), (width, height), marge):
                vertices.append((x, y))
        color = generate_color()
        if len(vertices) > 2:
            p = Polygon(vertices, fill=False, color=color)
            list_polygons_approx.append(p)
            # print(vertices)
    return [list_polygons_approx[2*i].get_xy() for i in range(len(list_polygons_approx)//2)]

    # The length of the returned list is very often of 1 single polygon


# TEST


# def test():
#     mask = cv2.imread(
#         "D:/DISQUE_DUR_MATHIS/Projet_Segmentation_IA/Projet/images/output2.png")
#     mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
#     plt.imshow(mask_gray, cmap="gray")

#     polygons_list = get_contours_approx(mask, eps=0.15, marge=12)

#     size = (mask.shape[0], mask.shape[1])

#     show_polygons(polygons_list, size)


# if __name__ == "__main__":
#     test()
