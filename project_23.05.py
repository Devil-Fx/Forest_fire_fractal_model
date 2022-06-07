import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib import colors
import cv2
import math
from yaweather import YaWeather



#Присваивает значение 0 ПУСТОМУ, 1 ДЕРЕВУ и 2 ОГНЮ. Каждая ячейка в сетке представляет собой
# aприсвоено одно из этих значений.
EMPTY, TREE, FIRE, WATER, ASH = 0, 1, 2, 3, 4
#colors_list = [(0.2,0,0), (0,0.5,0), (1,0,0), 'red', 'blue', 'gray']
colors_list = [(0.2,0,0), (0,0.5,0),  'red', 'blue', 'gray']
cmap = colors.ListedColormap(colors_list)
# Список границ должен быть на единицу больше, чем количество различных значений в сеточном массив.
bounds = [0, 1, 2, 3, 4, 5]
# Сопоставляет цвета в colors_list с ячейками, определенными границами; данные внутри ячейки сопоставляется цвету с тем же индексом.
norm = colors.BoundaryNorm(bounds, cmap.N)

def get_weather():

    y = YaWeather(api_key='key')
    #координаты впадения реки Олёмка в Лену
    res = y.informers(coordinates=(60.420501, 120.936266))
    direct=res.fact.wind_dir
    #Ветер Вправо вверх, 2Вправо, 3Вправо вниз, 4Вниз, 5Влево вниз, 6Влево, 7Влево вверх, 8Верх
    
    direct_to_NZ = {
        # Northwest
        'nw' : ([0.1, 0.1, 0.1, 0.1, 0.1, 0.5, 1, 0.5]),
        # North
        'n' : ([0.5, 0.1, 0.1, 0.1, 0.1, 0.1, 0.5, 1]),
        # Northeast
        'ne' : ([1, 0.5, 0.1, 0.1, 0.1, 0.5, 0.1, 0.5]),
        # East
        'e' : ([0.5, 1, 0.5, 0.1, 0.1, 0.5, 1, 0.1]),
        # Southeast
        'se' : ([0.1, 0.5, 1, 0.5, 0.1, 0.5, 0.1, 0.1]),
        # South
        's' : ([0.1, 0.1, 0.5, 1, 0.5, 0.1, 0.1, 0.1]),
        # Southwest
        'sw' : ([0.1, 0.1, 0.1, 0.5, 1, 0.5, 0.1, 0.1]),
        # West
        'w' : ([0.1, 0.1, 0.1, 0.1, 0.5, 1, 0.5, 0.1]),
        # Calm
        'c' : ([1, 1, 1, 1, 1, 1, 1, 1]),
        }
    NZ = direct_to_NZ[direct]
    return NZ

def craate_test_forest():
    X = np.zeros((ny, nx))
    X[1:ny-1, 1:nx-1] = np.random.randint(0, 2, size=(ny-2, nx-2))
    X[1:ny-1, 1:nx-1] = np.random.random(size=(ny-2, nx-2)) < forest_fraction
    X[int(nx/2),int(ny/2)] = FIRE
    #генерируем препятсвия огню
    #X[10:90, 25:30] = WATER
    #X[10:90, 80:85] = WATER
    return X



def eden_b_step(array):

    list_var = []
    for ix in range(1, nx-1):
        for iy in range(1, ny-1):
            if array[ix,iy] == FIRE:
                if array[ix][iy+1] == TREE:
                    list_var.append([ix, iy+1])
                if array[ix][iy-1] == TREE:
                    list_var.append([ix, iy-1])
                if array[ix+1][iy] == TREE:
                    list_var.append([ix+1, iy])
                if array[ix-1][iy] == TREE:
                    list_var.append([ix-1, iy])
    if list_var == []:
        for ix in range(0, nx):
            for iy in range(0, ny):
                if array[ix,iy] == FIRE:
                    array[ix,iy] = ASH
        return array
    else:
        __t = tuple(random.choice(list_var))  # convert to tuple
        array[__t] = FIRE
        return array

def parts_per_radius(sq1,r):
    M=0
    size = sq1.shape
    for i in range(0, size[0]-1):
        for j in range(0, size[1]-1):
            if (((size[0]/2-i)**2 + (size[1]/2-j)**2)**0.5 < r) and sq1[i][j] == FIRE:
                M += 1
            elif (((size[0]/2-i)**2 + (size[1]/2-j)**2)**0.5 < r) and sq1[i][j] == ASH:
                M += 1
    return M

def readimage():
    input = cv2.imread('1.jpg')
    area_image = cv2.resize(input, [nx,ny])
    area_hsv = cv2.cvtColor(area_image, cv2.COLOR_BGR2HSV)
    tree_color_low = (24,68,0) #зеленый снизу
    tree_color_high = (76,220,184) #зеленый сверху
    water_color_low = (61,180,14) #тёмно синий снизу
    water_color_high = (156,255,255) #тёмно синий сверху
    only_tree_hsv = cv2.inRange(area_hsv, tree_color_low, tree_color_high)
    only_water_hsv = cv2.inRange(area_hsv, water_color_low, water_color_high)
    #cv2.imshow('forest_color_hsv', area_image)
    size = area_image.shape
    zone = np.zeros((size[0], size[1]))
    for ix in range(0, size[0]):
        for iy in range(0, size[1]):
            if only_tree_hsv[ix,iy] == 255:
                zone[ix,iy] = TREE
            if only_water_hsv[ix,iy] == 255:
                zone[ix,iy] = 3
    zone[int(nx/2), int(ny/2)] = FIRE
    return zone
 
def animate(i):
     im.set_data(animate.X)
     animate.X = iterate(animate.X)

def show_forest():
    #fig = plt.figure(figsize=(25/3, 6.25))
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_axis_off()
    zone = readimage()
    global im
    im = ax.imshow(zone, cmap=cmap, norm=norm, interpolation='nearest')
    animate.X = zone
    interval = 10
    anim = animation.FuncAnimation(fig, animate, interval=interval, save_count=1500)
    #anim.save('anim.gif', fps=360)
    plt.show()
    
def show_graph():
    zone = craate_test_forest()
    time = 150
    xlist = []
    ylist = []
    for i in range(0, time):
        zone = iterate(zone)
    for i in range(1, 50):
        M = parts_per_radius(zone,i)
        xlist.append(math.log(i))
        ylist.append(math.log(M))
    plot = plt.imshow(zone, cmap=cmap, norm=norm, interpolation='nearest')
    plt.show()
    plt.xlabel(' Ln(r)')
    plt.ylabel('Ln[M(r)]')
    plt.plot(xlist, ylist)
    plt.show()

#определяем соседей и ветер, начинаем слева сверху и идем против часовой
NX=([-1, -1, -1, 0, 1, 1, 1, 0])
NY=([1, 0, -1, -1, -1, 0, 1, 1])
#Ветер Вправо вверх, 2Вправо, 3Вправо вниз, 4Вниз, 5Влево вниз, 6Влево, 7Влево вверх, 8Верх
#NZ=([1, 0.1, 0.1, 0,1, 0,1, 0,1, 0,1, 0,1])
#NZ=([1, 1, 1, 0.1, 0.1, 0.1, 0.1, 0.1])
#Если необходимо получить погоду с API
NZ = get_weather()

#плотность леса для тестовой области
forest_fraction = 1
# Размер леса (количество ячеек в направлениях x и y) для тестовой области.
nx, ny = 200, 200
#размер леса в распознаном изображении (необходимо для сжатия изображения)
# Настраивает размер фигуры.

show_forest()
