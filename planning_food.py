"""
Script will try to find some balanced food combinations
"""

import codecs
import sys, os
from itertools import combinations
from itertools import permutations

def initialise():
    """ """
    global dfv
    global food_nutri_connection
    global nutri_values
    global dpers2

    dfv = {}
    food_nutri_connection = []
    nutri_values = []
    dpers2 = {}

    fnc = ['Calories',
    'Fiber', 'Calcium', 'Iron', 'Magnesium', 'Phosphorus', 'Potassium',
    'Zinc', 'Copper', 'Manganese', 'Selenium', 'Retinol',
    'Vitamin A', 'Vitamin C', 'Thiamin', 'Riboflavin',
    'Niacin', 'Vitamin B6', 'Folate', 'Choline',
    'Vitamin K1', 'ALA', 'Omega-6']

    f = codecs.open('food_values.txt', 'r', 'utf8')
    for i, line in enumerate(f, 0):
        if i == 0: continue
        line = line.strip()
        l = line.split('|')
        dfv[l[0]] = l

    #print(dfv)

    with codecs.open('cipher.txt', 'r', 'utf8') as f:
        for i, line in enumerate(f, 0):
            line = line.strip()
            if '|' in line:
                if '#' in line:
                    line = line.split('#')[0].strip()
                l = line.split('|')
                if l[1] in fnc:
                    if l[3].lower() != 'sk':
                        food_nutri_connection.append((i, l[0], l[1], l[2], l[3]))
                        nutri_values.append(0)
            if ':' in line:
                #pers_names[line.split(':')[0]] = line.split(':')[1]
                dpers2.setdefault(line.split(':')[1], line.split(':')[0])
                # {'9040': 'bananas', '9200': 'oranges', '9295'}

    #print(dpers2)
    #print(food_nutri_connection)
    #print(nutri_values)
    """
    [(13, 'ENERC_KCAL', 'Calories', 'kc', '2000'), (29, 'CA', 'Calcium', 'mg', '1300'), (30, 'FE', 'Iron', 'mg', '18'), (31, 'MG', 'Magnesium', 'mg', '420'), (32, 'P', 'Phosphorus', 'mg', '1250'), (33, 'K', 'Potassium', 'mg', '3400'), (35, 'ZN', 'Zinc', 'mg', '11'), (36, 'CU', 'Copper', 'mg', '0.9'), (38, 'MN', 'Manganese', 'mg', '2.3'), (39, 'SE', 'Selenium', 'mcg', '55'), (42, 'VITA_RAE', 'Vitamin A', 'mcg', '900'), (60, 'VITC', 'Vitamin C', 'mg', '90'), (61, 'THIA', 'Thiamin', 'mg', '1.2'), (62, 'RIBF', 'Riboflavin', 'mg', '1.3'), (63, 'NIA', 'Niacin', 'mg', '16'), (65, 'VITB6A', 'Vitamin B6', 'mg', '1.7'), (66, 'FOL', 'Folate', 'mcg', '400'), (68, 'CHOLN', 'Choline', 'mg', '550'), (71, 'VITK1', 'Vitamin K1', 'mcg', '120'), (165, 'ALA', 'ALA', 'g', '1.6'), (168, 'OMEGA6', 'Omega-6', 'g', '17')]
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    """

def parse(num, lifn, gl, gr, step, nt):
    """ """
    global nutri_values
    global indexes
    global daily_values

    litemp = list(range(gl, gr + 1, step))
    lgrams = [(x, y, z) for x in litemp for y in litemp for z in litemp if (x + y + z) == nt ]
    # [(50, 50, 900), (50, 100, 850)]
    #print(lifn)
    print(lgrams)
    
    for tun in lifn:
        for tug in lgrams:
            k = 0
            for j in indexes:
                for ab in range(0, num):
                    try:
                        nutri_values[k] += float(dfv[tun[ab]][j]) * tug[ab] / 100
                    except:
                        pass
                k += 1
            break
        break
    daily_values_test()
    print('-' * 100)

def daily_values_test():
    """ """
    global nutri_values
    
    left_limit = 0.7
    right_limit = 1.5
    el_exceptions = []

    print(nutri_values)
    #sys.exit()


def main():
    """ """
    global indexes
    global nutri_values
    global daily_values

    indexes = [l[0] for l in food_nutri_connection]
    daily_values = [l[4] for l in food_nutri_connection]
    # [13, 29, 30, 31, 32, 33, 35, 36, 38, 39, 42, 60, 61, 62, 63, 65, 66, 68, 71, 165, 168]
    # ['2000', '1300', '18', '420', '1250', '3400', '11', '0.9', '2.3', '55', '900', '90', '1.2', '1.3', '16', '1.7', '400', '550', '120', '1.6', '17']

    """
    ['Fruits and Fruit Juices', '9003', '9021', '9037', '9040', '9070', '9079', '9089', '9132', '9148', '9152', '9176', '9181', '9190', '9191', '9195', '9200', '9218', '9226', '9236', '9252', '9263', '9279', '9286', '9295', '9296', '9299', '9316', '9326', '9421']
    """

    num_of_fruits = 3
    fruits = list(combinations(di['900'][1:], num_of_fruits))
    # [('9299', '9326', '9421'), ('9316', '9326', '9421')]
    #print(fruits)
    
    num_of_veggies = 3
    veggies = list(combinations(di['1100'][1:], num_of_veggies))
    
    num_of_spices = 3
    spices = list(combinations(di['200'][1:], num_of_spices))
    
    num_of_grains = 3
    grains = list(combinations(di['540'][1:], num_of_grains))
    
    num_of_legumes = 3
    legumes = list(combinations(di['1600'][1:], num_of_legumes))
    
    num_of_nuts_seeds = 3
    nuts_seeds = list(combinations(di['1200'][1:], num_of_nuts_seeds))

    parse(num_of_fruits, fruits, 100, 801, 100, 800)
    parse(num_of_veggies, veggies, 100, 301, 100, 300)
    parse(num_of_spices, spices, 10, 21, 5, 20)
    parse(num_of_grains, grains, 100, 201, 50, 200)
    parse(num_of_legumes, legumes, 100, 201, 50, 100)
    parse(num_of_nuts_seeds, nuts_seeds, 10, 41, 10, 40)

if __name__ == '__main__':
    di = {

'900': ['Fruits and Fruit Juices', '9003', '9021', '9037', '9040', '9070', '9079', '9089', '9132', '9148', '9152', '9176', '9181', '9190', '9191', '9195', '9200', '9218', '9226', '9236', '9252', '9263', '9279', '9286', '9295', '9296', '9299', '9316', '9326', '9421'],
'1100': ['Vegetables and Vegetable Products', '11052', '11080', '11109', '11112', '11124', '11135', '11143', '11147', '11206', '11209', '11215', '11246', '11253', '11260', '11297', '11311', '11312', '11333', '11352', '11423', '11429', '11457', '11477', '11529', '11540', '11740', '11819', '11821'],
'200': ['Spices and Herbs', '2003', '2027', '2030', '2031', '2036', '2042', '2043', '2047', '2048', '2068', '2069'],
'540': ['Grains', '18060', '18075', '18412', '28295', '20033', '20031', '20035', '20040', '20054', '20124', '20133'],
'1600': ['Legumes and Legume Products', '16027', '16033', '16055', '16056', '16069', '16137', '16144', '16398', '16432'],
'1200': ['Nuts and Seed Products', '12006', '12014', '12036', '12063', '12078', '12085', '12098', '12122', '12152', '12157', '12201', '12220', '12698']
}

    initialise()
    main()
