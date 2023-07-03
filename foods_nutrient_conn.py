"""
Top foods from connections for nutrient in 100 grams
"""

import codecs
import pandas as pd
import numpy as np
import os
from pytodos import load_cipher

num_of_tops = 500

##################################################
# choise = 1 extreme_all, 2 pro vegan, 3 frutarian, 4 fruits_only, 5 veggies_only, 6 nutsseeds_only
choise = 7
##################################################

pd.options.display.max_rows=10000
df = pd.read_csv("food_values.txt", sep='|', low_memory=False)
# allowed_groups = ['100', '200', '400', '800', '900', '1100', '1200', '1400', '1500', '1600', '1800', '2000', '530']

use_food_values = True
# extreme_all
if choise == 1:
    allowed_groups = ['100', '200', '300', '400', '500', '600', '700', '800',
    '900', '1000', '1100', '1200', '1300', '1400', '1500', '1600', '1700',
    '1800', '1900', '2000', '2100', '2200', '2500', '3500', '3600', '530']
    foutput_name = 'list_extreme_all'
# pro vegan
if choise == 2:
    allowed_groups = ['100', '200', '400', '800', '900', '1100', '1200',
                      '1400', '1500', '1600', '1800', '2000', '530']
    foutput_name = 'list_pro_vegan'
# frutarian
if choise == 3:
    allowed_groups = ['200', '900', '1100', '1200']
    foutput_name = 'list_frutarian'
# fruits_only
if choise == 4:
    allowed_groups = ['900']
    foutput_name = 'list_fruits_only'
# veggies_only
if choise == 5:
    allowed_groups = ['1100']
    foutput_name = 'list_veggies_only'
# nutsseeds_only
if choise == 6:
    allowed_groups = ['1200']
    foutput_name = 'list_nutsseeds_only'
# my_tiny
if choise == 7:
    allowed_groups = ['100', '200', '300', '400', '500', '600', '700', '800',
    '900', '1000', '1100', '1200', '1300', '1400', '1500', '1600', '1700',
    '1800', '1900', '2000', '2100', '2200', '2500', '3500', '3600', '530']
    foutput_name = 'list_my_tiny'
    use_food_values = False

"""
'100': ['Dairy and Egg Products'],
'200': ['Spices and Herbs'],
'400': ['Fats and Oils'],
'800': ['Breakfast Cereals'],
'900': ['Fruits and Fruit Juices'],
'1100': ['Vegetables and Vegetable Products'],
'1200': ['Nuts and Seed Products'],
'1400': [Beverages'],
'1500': ['Finfish and Shellfish Products']
'1600': ['Legumes and Legume Products'],
'1800': ['Baked Products'],
'2000': ['Cereal Grains and Pasta'],
'2100': ['Fast foods'],
'530': ['personal']
"""


lels = [('Protein', 'g', '57'), ('Total Fat', 'g', '90'), ('Total Carb', 'g', '377'),
('Fiber', 'g', '32'), ('Calcium', 'mg', '1300'), ('Iron', 'mg', '18'),
('Magnesium', 'mg', '420'), ('Phosphorus', 'mg', '1250'), ('Potassium', 'mg', '3400'),
('Sodium', 'mg', '2300'), ('Zinc', 'mg', '11'), ('Copper', 'mg', '0.9'), ('Manganese', 'mg', '2.3'),
('Selenium', 'mcg', '55'), ('Vitamin A', 'mcg', '900'),
('Vitamin D', 'mcg', '20'), ('Vitamin E', 'mg', '15'), ('Vitamin C', 'mg', '90'), ('Thiamin', 'mg', '1.2'),
('Riboflavin', 'mg', '1.3'), ('Niacin', 'mg', '16'), ('Panto. Acid', 'mg', '5'), ('Vitamin B6', 'mg', '1.7'),
('Folate', 'mcg', '400'), ('Vitamin B12', 'mcg', '6'), ('Choline', 'mg', '550'),
('Vitamin K1', 'mcg', '120'), ('Cholesterol', 'mg', '300'),
('Non-Fiber Carb', 'g', '344'), ('ALA', 'g', '1.6'), ('EPA', 'g', '0.25'), ('DHA', 'g', '0.25'),
('Omega-6', 'g', '17')]

# if narrowing to one element, create list with that only one element,
# like lels = [('Phosphorus', 'mg', '1250')]
#lels = [('Calcium', 'mg', '1300')]

d10 = {'Protein': 'PROCNT', 'Total Fat': 'FAT', 'Total Carb': 'CHOCDF',
'Calories': 'ENERC_KCAL', 'Caffeine': 'CAFFN', 'Fiber': 'FIBTG',
'Calcium': 'CA', 'Iron': 'FE', 'Magnesium': 'MG', 'Phosphorus': 'P',
'Potassium': 'K', 'Sodium': 'NA', 'Zinc': 'ZN', 'Copper': 'CU',
'Manganese': 'MN', 'Selenium': 'SE', 'Retinol': 'RETOL',
'Vitamin A': 'VITA_RAE', 'Vitamin D': 'VITD_BOTH', 'Vitamin E': 'VITE', 'Vitamin C': 'VITC',
'Thiamin': 'THIA', 'Riboflavin': 'RIBF', 'Niacin': 'NIA', 'Panto. Acid':'PANTAC',
'Vitamin B6': 'VITB6A', 'Folate': 'FOL', 'Vitamin B12': 'VITB12',
'Choline': 'CHOLN', 'Vitamin K1': 'VITK1',
'Cholesterol': 'CHOLE', 'Non-Fiber Carb': 'CHO_NONFIB', 'ALA': 'ALA',
'EPA': 'EPA', 'DHA': 'DHA', 'Omega-6': 'OMEGA6'}

#print([x[0] for x in lels])

def main():
    """ """
    global lcip

    f = codecs.open(foutput_name + '.txt', 'w', 'utf8')
    
    f.write('Top foods per element' + os.linesep)
    f.write('per 100 grams of product' + os.linesep)
    f.write('nutrition value is on right side' + os.linesep)
    f.write('You can check daily values here: https://www.consumerlab.com/RDAs/' + os.linesep * 2)
    
    own_df = df.loc[df['NDB_No'].isin(lcip)].copy()
    
    for j, tup in enumerate(lels, 0):
        print(tup[0])
        sorted_df = own_df.sort_values(by=[d10[tup[0]]], ascending=False).copy()
        filtered_df = sorted_df[['NDB_No', 'FdGrp_Cd', 'Long_Desc', d10[tup[0]]]].copy()
        if j > 3:
            f.write(tup[0] + ' DailyValue ' + tup[2] + ' (metric=%s)' % tup[1] + os.linesep * 2)
        else:
            f.write(tup[0] + ' (metric=%s)' % tup[1] + os.linesep * 2)
        #f.write(str(filtered_df.iloc[:num_of_tops, 2:]))
        for index, row in filtered_df.iloc[:num_of_tops,].iterrows():
            #print row['c1'], row['c2']
            f.write(row['Long_Desc'][:79].ljust(80) + f'{row[d10[tup[0]]]:10.3f}' + os.linesep)
        f.write('-' * 90 + os.linesep)
        
    f.close()


def connect_with_food_categories():
    """ """
    global dproducts_to_group
    global lcipall

    dcip = {}
    dproducts_to_group = {}
    f = codecs.open('food_values.txt', 'r', 'utf8')
    for i, line in enumerate(f, 0):
        if i == 0: continue
        nutri_code = line.split('|')[0]
        nutri_group = line.split('|')[1]
        if nutri_code in lcipall:
            dcip.setdefault(nutri_group, [])
            dcip[nutri_group].append(nutri_code)
            dproducts_to_group[nutri_code] = nutri_group

    #print(dcip)
    #print(dproducts_to_group)

def generate_lcip():
    """ from filtered groups """
    global lcipall
    global allowed_groups
    global lcip
    global dproducts_to_group

    lcip = []
    for item in lcipall:
        if dproducts_to_group[item] in allowed_groups:
            lcip.append(item)

def get_personal_keys():
    """ """
    l = []
    if use_food_values:
        f = codecs.open('food_values.txt', 'r', 'utf8')
        for i, line in enumerate(f, 0):
            if i == 0:
                continue
            line = line.strip()
            sp = line.split('|')
            l.append(sp[0])
    else:
        f = codecs.open('cipher.txt', 'r', 'utf8')
        for line in f:
            line = line.strip()
            if '#' in line:
                line = line.split('#')[0]
            if ':' in line:
                l.append(line.split(':')[1])
        l = list(set(l))
    f.close()
    return l
            

if __name__ == '__main__':

    lcipall = get_personal_keys()
    print(lcipall)
    print('Number of products in list: ' + str(len(lcipall)))

    dgroup_products = {'100': ['Dairy and Egg Products', '1116', '1129'],
'200': ['Spices and Herbs', '2003', '2027', '2030', '2031', '2036', '2042', '2043', '2047', '2048', '2068', '2069'],
'400': ['Fats and Oils', '4053'],
'900': ['Fruits and Fruit Juices', '9003', '9021', '9037', '9040', '9070', '9079', '9089', '9132', '9148', '9152', '9176', '9181', '9190', '9191', '9195', '9200', '9218', '9226', '9236', '9252', '9263', '9279', '9286', '9295', '9296', '9299', '9316', '9326', '9421'],
'1100': ['Vegetables and Vegetable Products', '11052', '11080', '11109', '11112', '11124', '11135', '11143', '11147', '11206', '11209', '11215', '11246', '11253', '11260', '11297', '11311', '11312', '11333', '11352', '11423', '11429', '11457', '11477', '11529', '11540', '11740', '11819', '11821'],
'1200': ['Nuts and Seed Products', '12006', '12014', '12036', '12063', '12078', '12085', '12098', '12122', '12152', '12157', '12201', '12220', '12698'],
'1400': ['Beverages', '14639'],
'1500': ['Finfish and Shellfish Products', '15046', '15076', '15088', '15119'],
'1600': ['Legumes and Legume Products', '16027', '16033', '16055', '16056', '16069', '16137', '16144', '16398', '16432'],
'1800': ['Baked Products', '18060', '18075', '18412', '28295'],
'1900': ['Sweets', '19334'],
'2000': ['Cereal Grains and Pasta', '20033', '20031', '20035', '20040', '20054', '20124', '20133'],
'530': ['personal', '97001', '97002', '97003']}

    '''
    for planning
'200': ['Spices and Herbs', '2003', '2027', '2030', '2031', '2036', '2042', '2043', '2047', '2048', '2068', '2069'],
'900': ['Fruits and Fruit Juices', '9003', '9021', '9037', '9040', '9070', '9079', '9089', '9132', '9148', '9152', '9176', '9181', '9190', '9191', '9195', '9200', '9218', '9226', '9236', '9252', '9263', '9279', '9286', '9295', '9296', '9299', '9316', '9326', '9421'],
'1100': ['Vegetables and Vegetable Products', '11052', '11080', '11109', '11112', '11124', '11135', '11143', '11147', '11206', '11209', '11215', '11246', '11253', '11260', '11297', '11311', '11312', '11333', '11352', '11423', '11429', '11457', '11477', '11529', '11540', '11740', '11819', '11821'],
'1200': ['Nuts and Seed Products', '12006', '12014', '12036', '12063', '12078', '12085', '12098', '12122', '12152', '12157', '12201', '12220', '12698'],
'1600': ['Legumes and Legume Products', '16027', '16033', '16055', '16056', '16069', '16137', '16144', '16398', '16432'],
'1800': ['Baked Products', '18060', '18075', '18412', '28295'],
'2000': ['Cereal Grains and Pasta', '20033', '20031', '20035', '20040', '20054', '20124', '20133'],
    '''

    connect_with_food_categories()
    generate_lcip()
    main()
    print('Done.')
