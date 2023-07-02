#!/usr/bin/env python3
# Program for dealing with todos, nutrition
# Author: Aleksandar Josifoski https://about.me/josifsk
# 2018 June; 2019 February; March; 2023 July+;
# Licence GPL

import os
import sys
import codecs
import json
import datetime
import calendar
import numpy as np
import shutil

import getpass
username = getpass.getuser()

if username == 'josifoski':
    dir_in = '/home/josifoski/Dropbox/pytodos/pytodos/'
elif username == 'mfp':
    dir_in = '/home/' + username + '/Dropbox/pytodos/'
dir_backup = dir_in + 'pytodos_backup/'


def dump_json():
    ''' function to dump json file '''
    global d
    with codecs.open(dir_in + 'todos.json', 'w', 'utf-8') as fdump:
        json.dump(d, fdump, ensure_ascii=False, indent=4, sort_keys=True)


weekdays = ('sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday')
dweekdays = {'su': 'sunday', 'mo': 'monday', 'tu': 'tuesday', 'we': 'wednesday', 'th': 'thursday', 'fr': 'friday', 'sa': 'saturday'}
dlongwtoshort = {v : k for k, v in dweekdays.items()}
daysinmonth = list(range(1, 32))
dnumweekday = {6: 'sunday', 0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday', 4: 'friday', 5: 'saturday'}
dmonths = {1: '01-January', 2: '02-February', 3: '03-March', 4: '04-April', 5: '05-May', 6: '06-June',
           7: '07-July', 8: '08-August', 9: '09-September', 10: '10-Octobar', 11: '11-November', 12: '12-December'}
dshortrec = {'every_day': '[ ed]', 'weekly': '[  w]', 'dayinmonth': '[dim]'}


def check_priority_time(text):
    ''' function to check validity of input
    This was old function to parse priority and time, I've dropped it later '''
    text = text.strip()
    return text


def addyear(year):
    ''' function to add year structure to json '''
    global d
    # check other years existance
    #if year != Year:
    d[year] = {}
    for n1 in range(1, 13):
        d[year][dmonths[n1]] = {}
        days_in_month = calendar.monthrange(int(year), n1)[1]
        for n2 in range(1, days_in_month + 1):
            d[year][dmonths[n1]]['%02d' % n2] = []
    dump_json()


def initialise():
    ''' function to initialise dictionary '''
    global d
    global Year
    global todaymonth
    global todayday
    global rawfooditems
    global num_of_days
    global dfv
    global pricesum
    global print_later
    print_later = []
    pricesum = 0
    rawfooditems = []
    dfv = {}

    num_of_days = 1
    todaystring = str(datetime.date.today())[:10].replace('-', '')
    Year = todaystring[0:4]
    todaymonth = todaystring[4:6]
    todayday = todaystring[6:8]

    try:
        mo, day = modification_date(dir_in + 'rdone')
        if mo != todaymonth or day != todayday:
            os.remove(dir_in + 'rdone')
    except:
        pass

    try:
        with codecs.open(dir_in + 'todos.json', 'r', 'utf-8') as json_data:
            d = json.load(json_data)
    except:
        year = Year
        d = {}
        d['weekly_plan'] = []
        d['monthly_plan'] = []
        d['3months_plan'] = []
        d['yearly_plan'] = []
        d['5years_plan'] = []
        d['recurrent'] = {}
        d['recurrent']['weekly'] = {}
        for wd in weekdays:
            d['recurrent']['weekly'][wd] = []
        d['recurrent']['dayinmonth'] = {}
        for dim in daysinmonth:
            d['recurrent']['dayinmonth']['%02d' % dim] = []
        d['recurrent']['every_day'] = []
        d[year] = {}
        for n1 in range(1, 13):
            d[year][dmonths[n1]] = {}
            days_in_month = calendar.monthrange(int(year), n1)[1]
            for n2 in range(1, days_in_month + 1):
                d[year][dmonths[n1]]['%02d' % n2] = []
        dump_json()


def get_by_date(y, m, day):
    ''' function to get by date '''
    global rawfooditems
    global num_of_days

    swd = dnumweekday[datetime.date(int(y), int(m.lstrip('0')), int(day)).weekday()]
    sdate = y + m + day
    if len(d[y][dmonths[int(m.lstrip('0'))]][day]) > 0 or len(d['recurrent']['weekly'][swd]) > 0 \
    or len(d['recurrent']['dayinmonth'][sdate[-2:]]) > 0 or  len(d['recurrent']['every_day']) > 0:
        if not sys.argv[1] in ('cf', 'calcfood', 'ea', 'fa', 'foodsanalysis'):
            print(y + m + day + ' ' + swd)
        get_by_weekday_and_date(swd, y, m, day)
        for ind, item in enumerate(d[y][dmonths[int(m.lstrip('0'))]][day], 0):
            if not sys.argv[1] in ('cf', 'calcfood', 'ea', 'fa', 'foodsanalysis'):
                if ind < 10:
                    sind = ' ' + str(ind)
                else:
                    sind = str(ind)
                if sys.argv[1] in ('rf', 'readfull'):
                    print('     [' + sind + '] ' + item)
                elif sys.argv[1] in ('r', 'read'):
                    if not item[0] == '+':
                        print('     [' + sind + '] ' + item)
                elif sys.argv[1] in ('rh', 'readhigh'):
                    if not item[0] == '+':
                        if parse_priority(item) == 'high':
                            print('     [' + sind + '] ' + item)
                elif sys.argv[1] in ('rmh', 'readmedhigh'):
                    if not item[0] == '+':
                        if parse_priority(item) in ('med', 'medium', 'high'):
                            print('     [' + sind + '] ' + item)
            else:
                # here comes part for calculating food nutrition
                if 'fd:' in item:
                    if not sys.argv[1] in ('fa', 'foodsanalysis'):
                        rawfooditems.extend(item.split('fd:')[1].strip().split(','))
        if sys.argv[1] in ('cf', 'calcfood', 'ea', 'fa', 'foodsanalysis') and not sys.argv[2].lower() in ('dr', 'drange', 'daterange'):
            # here continues part for calculating food nutrition
            convert_raw_food_items_to_nutritional_values()


def compact_rawfooditems():
    """ """
    global rawfooditems
    global pnkeys
    global pers_names
    global dpers2
    global print_later

    di = {}
    for i, rawitem in enumerate(rawfooditems, 0):
        bpass = False
        pname = rawitem.split()[0].strip().lower()
        # print(pname)
        grams = float(rawitem.split()[1])

        for j, pnkey in enumerate(pnkeys, 0):
            if pnkey.lower().startswith(pname):
                try:
                    di.setdefault(pers_names[pnkey], 0)
                    di[pers_names[pnkey]] += grams
                    bpass = True
                except:
                    pass
                break
        if not bpass:
            print_later.append('*' * 5 + pname + ' is not included in cipher.txt')

    # convert dict di to rawfooditems
    rawfooditems = []
    for key in list(di.keys()):
        rawfooditems.append(dpers2[key] + ' ' + str(di[key]))
    # print(di)


def convert_raw_food_items_to_nutritional_values():
    ''' takes rawfooditems list and converts in nutritional values '''
    global rawfooditems
    global food_nutri_connection
    global nutri_values
    global pers_names
    global dfv
    global pnkeys
    global num_of_days
    global prices
    global pricesum

    load_cipher()
    convert_food_values_to_dict()
    # print(rawfooditems)
    compact_rawfooditems()

    if sys.argv[1] in ('ea',):
        if sys.argv[2].lower() in ('dr', 'drange', 'daterange'):
            try:
                elarg = ' '.join(sys.argv[5:])
            except Exception as e:
                print(str(e))
                print('Example: t ea dr 0318 0322 Selenium')
                sys.exit()
        elif sys.argv[2].lower() in ('d', 'date'):
            try:
                elarg = ' '.join(sys.argv[4:])
            except Exception as e:
                print(str(e))
                print('Example: t ea d 0322 Selenium')
                sys.exit()
        else:
            # Example: t ea t sele will give element analysis for selenium
            elarg = ' '.join(sys.argv[3:])

        ltempel = [el[0].lower() for el in food_nutri_connection]
        lfind = [el[0].lower() for el in food_nutri_connection if el[0].lower().startswith(elarg.lower())]

        if len(lfind) > 0:
            elind = ltempel.index(lfind[0])
            print(lfind[0])
            print()
        else:
            print(elarg + ' not found in ' + os.linesep)
            ltempel.sort()
            for item in ltempel:
                if item != '/':
                    print(item, end=', ')
            print()
            sys.exit()

    eastr = ''
    for i, rawitem in enumerate(rawfooditems, 0):
        pname = rawitem.split()[0].strip().lower()
        grams = float(rawitem.split()[1])

        bpass = False
        for j, pnkey in enumerate(pnkeys, 0):

            if pnkey.lower().startswith(pname.lower()):
                if sys.argv[1] not in ('ea',):
                    print(pnkey.ljust(20) + str(grams).rjust(9) + 'g', end='')
                    pricesum += prices[pnkey] * grams / 1000
                else:
                    eastr += pnkey.ljust(20) + str(grams).rjust(9) + 'g'
                # here needs calculation
                # print(dfv[pers_names[pnkey]])
                for k in range(9, 175):
                    if nutri_values[k] != '/':
                        try:
                            nutri_values[k] += float(dfv[pers_names[pnkey]][k]) * grams / 100
                            if sys.argv[1] in ('cf', 'calcfood', 'fa', 'foodsanalysis'):
                                if k == 13:
                                    print(f'{(float(dfv[pers_names[pnkey]][k]) * grams / 100):20.3f}' + ' kc')
                            if sys.argv[1] in ('ea',):
                                if k == elind:
                                    eastr += f'{float(dfv[pers_names[pnkey]][k]) * grams / 100:20.3f}' + ' ' + food_nutri_connection[k][1] + os.linesep

                            bpass = True
                        except Exception as e2:
                            pass

                break
        if not bpass:
            print('*' * 5 + pname + ' is not included in cipher.txt')

    if sys.argv[1] in ('ea',):
        eal = eastr.splitlines()
        eal = [x.split() for x in eal]
        for ind, row in enumerate(eal, 0):
            eal[ind][2] = float(eal[ind][2])
        eal.sort(key=lambda x: x[2], reverse=True)

        for ind, row in enumerate(eal, 0):
            print(eal[ind][0].ljust(20) + eal[ind][1].rjust(9) +
                  f'{eal[ind][2]:20.3f}' + ' ' + eal[ind][3])

    print()
    output_format_for_nutri_values()


def output_format_for_nutri_values():
    ''' design for output format for nutritional values '''
    global food_nutri_connection
    global nutri_values

    output_order = [13, 11, 28, 162, 9,
                    10, 99, 126, 127, 168, 163, 164, 165, 166, 167, 171, 97,
                    42, 61, 62, 63, 64, 65, 66, 67, 68, 60, 49, 174, 71,
                    29, 36, 30, 31, 38, 32, 33, 39, 34, 35]

    total_calories = nutri_values[11] * 4 + \
                    nutri_values[9] * 4 + \
                    nutri_values[10] * 9
    if total_calories > 0:
        carbs_part = int(nutri_values[11] * 4 / total_calories * 100)
        proteins_part = int(nutri_values[9] * 4 / total_calories * 100)
    else:
        carbs_part = 0
        proteins_part = 0
    fats_part = 100 - carbs_part - proteins_part
    if sys.argv[1] in ('cf', 'calcfood', 'fa', 'foodsanalysis'):
        print('Carbs : Proteins : Fats  ' + str(carbs_part) + ' : ' +
              str(proteins_part) + ' : ' + str(fats_part))
    print()

    try:
        omega63_ratio = nutri_values[168] / nutri_values[171]
    except Exception as e:
        omega63_ratio = 1

    # for k in range(9, 172):
    if sys.argv[1] in ('cf', 'calcfood', 'fa', 'foodsanalysis'):
        for k in output_order:
            if nutri_values[k] != '/':
                if food_nutri_connection[k][2] != 'sk':
                    if sys.argv[2] in ('dr', 'drange', 'daterange'):
                        print(food_nutri_connection[k][0].ljust(24) + ' ' +
                              f'{round(nutri_values[k], 4):11.4f}' + ' ' +
                              food_nutri_connection[k][1].ljust(5) +
                              ' RV-' + str(num_of_days) + 'd ' + f'{num_of_days * float(food_nutri_connection[k][2]):10.2f}' + '  ' + \
                              f'{round(nutri_values[k], 4)/float(food_nutri_connection[k][2])*100/num_of_days:7.2f}' + ' %')
                    else:
                        #food_nutri_connection.append((l[1], l[2], l[3], l[4]))
                        if food_nutri_connection[k][3].isdigit():
                            if num_of_days == 1:
                                if round(nutri_values[k], 4) >= float(food_nutri_connection[k][3]):
                                    print('!' + '*' * 5 + ' ' + food_nutri_connection[k][0] + ' went over allowed upper limit ' + f'{float(food_nutri_connection[k][3]):0.2f}' + ' ' + food_nutri_connection[k][1].ljust(5) + ' ' + '*' * 5 + '!')
                        print(food_nutri_connection[k][0].ljust(24) + ' ' +
                              f'{round(nutri_values[k], 4):11.4f}' + ' ' +
                              food_nutri_connection[k][1].ljust(5) +
                              ' DV  ' + f'{float(food_nutri_connection[k][2]):7.2f}' + '  ' +
                              f'{round(nutri_values[k], 4)/float(food_nutri_connection[k][2])*100/num_of_days:7.2f}' + ' %')
                    if k in (97, 71):
                        print('-' * 75)
                else:
                    if k == 171:
                        print(food_nutri_connection[k][0].ljust(24) + ' ' +
                              f'{round(nutri_values[k], 4):11.4f}' + ' ' +
                              food_nutri_connection[k][1].ljust(5) +
                              ' Omega-6/3 ratio ' + f'{omega63_ratio:5.3f}')
                    else:
                        print(food_nutri_connection[k][0].ljust(24) + ' ' +
                              f'{round(nutri_values[k], 4):11.4f}' + ' ' +
                              food_nutri_connection[k][1].ljust(5))

    # printing total price
    print('Total price: ' + str(round(pricesum)))
    if print_later != []:
        for item in print_later:
            print(item)


def convert_food_values_to_dict():
    ''' convert food_values.txt file to dictionary '''
    global dfv
    with codecs.open(dir_in + 'food_values.txt', 'r', 'utf8') as f:
        for i, line in enumerate(f, 0):
            if i == 0:
                continue
            line = line.strip()
            l = line.split('|')
            for j in range(6, 175):
                if l[j].strip() == '':
                    l[j] = '0'
            dfv[l[0]] = l


def load_cipher():
    ''' function to get index based connection with nutritional values '''
    global food_nutri_connection
    global nutri_values
    global pers_names
    global pnkeys
    global dpers2
    global prices

    food_nutri_connection = []
    nutri_values = []
    pers_names = {}
    dpers2 = {}
    prices = {}

    # dfnc is for using in foods_nutrient_conn.py, fnc is some temp list
    dfnc = {}
    fnc = ['Protein', 'Total Fat', 'Total Carb', 'Calories', 'Caffeine',
           'Fiber', 'Calcium', 'Iron', 'Magnesium', 'Phosphorus', 'Potassium',
           'Sodium', 'Zinc', 'Copper', 'Manganese', 'Selenium', 'Retinol',
           'Vitamin A', 'Vitamin D', 'Vitamin E', 'Vitamin C', 'Thiamin', 'Riboflavin',
           'Niacin', 'Panto. Acid', 'Vitamin B6', 'Folate', 'Vitamin B12', 'Choline',
           'Vitamin K1', 'Cholesterol', 'Non-Fiber Carb', 'ALA', 'EPA', 'DHA', 'Omega-6']

    with codecs.open(dir_in + 'cipher.txt', 'r', 'utf8') as f:
        for i, line in enumerate(f, 0):
            line = line.strip()
            if '|' in line:
                if '#' in line:
                    line = line.split('#')[0].strip()
                l = line.split('|')
                # print(line)
                food_nutri_connection.append((l[1], l[2], l[3], l[4]))
                nutri_values.append(0)
                if l[1] in fnc:
                    dfnc[l[1]] = l[0]
            else:
                if i <= 174:
                    food_nutri_connection.append('/')
                    nutri_values.append('/')
                else:
                    if ':' in line:
                        if '#' in line:
                            line = line.split('#')[0].strip()
                        pers_names[line.split(':')[0]] = line.split(':')[1]
                        dpers2.setdefault(line.split(':')[1], line.split(':')[0])
                        try:
                            prices[line.split(':')[0]] = int(line.split(':')[2])
                        except:
                            prices[line.split(':')[0]] = 0

    pnkeys = list(pers_names.keys())
    # print(dfnc)
    # print(pers_names)
    # print(dpers2)
    # print(list(dpers2.keys()))
    # print(pnkeys)
    # print(food_nutri_connection)
    # print([x for x in food_nutri_connection if x != '/'])


def print_recurrents_by_date(item, rec, scount):
    ''' function to print recurrent items by date '''
    global rdone
    if sys.argv[1] in ('rf', 'readfull'):
        if scount not in rdone:
            print(dshortrec[rec] + '[' + scount + '] ' + item)
        else:
            print(dshortrec[rec] + '[' + scount + '] + ' + item)
    elif sys.argv[1] in ('r', 'read'):
        if scount not in rdone:
            print(dshortrec[rec] + '[' + scount + '] ' + item)
    elif sys.argv[1] in ('rh', 'readhigh'):
        if scount not in rdone:
            if parse_priority(item) == 'high':
                print(dshortrec[rec] + '[' + scount + '] ' + item)
    elif sys.argv[1] in ('rmh', 'readmedhigh'):
        if scount not in rdone:
            if parse_priority(item) in ('med', 'medium', 'high'):
                print(dshortrec[rec] + '[' + scount + '] ' + item)


def get_by_weekday_and_date(swd, y, m, day):
    ''' function to print read results by string date and string week day '''
    global d
    global rdone
    rdone = []
    try:
        f = codecs.open(dir_in + 'rdone', 'r', 'utf8')
        for snum in f:
            snum = snum.strip()
            if len(snum) == 1:
                snum = ' ' + snum
            rdone.append(snum)
    except:
        pass

    try:
        if y > Year:
            brec = True
            rdone = []
        elif y == Year:
            if m > todaymonth:
                brec = True
                rdone = []
            elif m == todaymonth:
                if day > todayday:
                    brec = True
                    rdone = []
                elif day == todayday:
                    brec = True
                else:
                    brec = False
            elif m < todaymonth:
                brec = False
        else:
            brec = False
    except Exception as e:
        print(str(e))
        brec = False

    if brec:
        count = -1
        # reccrs = ('every_day', 'weekly', 'dayinmonth')
        if len(d['recurrent']['every_day']) > 0:
            for item in d['recurrent']['every_day']:
                count += 1
                if count < 10:
                    scount = ' ' + str(count)
                else:
                    scount = str(count)
                print_recurrents_by_date(item, 'every_day', scount)
        if len(d['recurrent']['weekly'][swd]) > 0:
            for item in d['recurrent']['weekly'][swd]:
                count += 1
                if count < 10:
                    scount = ' ' + str(count)
                else:
                    scount = str(count)
                print_recurrents_by_date(item, 'weekly', scount)
        if len(d['recurrent']['dayinmonth'][day]) > 0:
            for item in d['recurrent']['dayinmonth'][day]:
                count += 1
                if count < 10:
                    scount = ' ' + str(count)
                else:
                    scount = str(count)
                print_recurrents_by_date(item, 'dayinmonth', scount)


def modification_date(filepath):
    ''' file modification date in human readable format '''
    t = os.path.getmtime(filepath)
    datestring = str(datetime.datetime.fromtimestamp(t)).replace('-', '')
    mo = datestring[4:6]
    day = datestring[6:8]
    return mo, day


def getymday(text):
    ''' function to split date '''
    if len(text.strip()) == 4:
        y = Year
        m = text[0:2]
        day = text[2:4]
    else:
        y = text[:4]
        m = text[4:6]
        day = text[6:8]
    return y, m, day


def print_from_bellow(prefix, key, i, item):
    ''' simplifying prints from bellow print_list function '''
    if len(str(i)) > 1:
        print(prefix + key + '[' + str(i) + '] ' + ' ' + item)
    else:
        print(prefix + key + '[ ' + str(i) + '] ' + ' ' + item)


def print_list(prefix, key, mylist, pri):
    ''' function to print some list with prefix '''
    for i, item in enumerate(mylist, 0):
        if pri == 'all':
            print_from_bellow(prefix, key, i, item)
        elif pri == 'high':
            if parse_priority(item) == 'high':
                print_from_bellow(prefix, key, i, item)
        elif pri == 'medhigh':
            if parse_priority(item) in ('med', 'medium', 'high'):
                print_from_bellow(prefix, key, i, item)


def shift_list(lsk, ifrom, ito):
    ''' function to make shifts in list '''
    global d

    li = getFromDict(d, lsk)

    from_value = li[ifrom]
    del li[ifrom]
    li[ito:ito] = [from_value]

    setInDict(d, lsk, li)


def getFromDict(dataDict, maplist):
    ''' get from dictionary
    https://stackoverflow.com/a/47723336/2397101 '''
    first, rest = maplist[0], maplist[1:]

    if rest:
        # if `rest` is not empty, run the function recursively
        return getFromDict(dataDict[first], rest)
    else:
        return dataDict[first]


def setInDict(dataDict, maplist, value):
    ''' set in dictionary '''
    first, rest = maplist[0], maplist[1:]

    if rest:
        setInDict(dataDict[first], rest, value)
    else:
        dataDict[first] = value


def archive_plan_item(text):
    ''' function to append to pytodos_archive.txt
    plan items like weekly_plan, monthly_plan, 3months_plan, yearly_plan, 5years_plan
    '''
    now = str(datetime.datetime.now())[:16].replace('-', '')
    with codecs.open(dir_in + 'pytodos_archive.txt', 'a', 'utf8') as f:
        f.write(now + ' ' + text + os.linesep)


def parse_priority(text):
    ''' function to get priority level from text '''
    try:
        priority = text.split('p=')[1].lower()
        if priority.startswith('med'):
            priority = 'med'
        elif priority.startswith('high'):
            priority = 'high'
        else:
            priority = 'low'
    except:
        priority = 'low'
    return priority


def print_plans(pri, item, ind):
    ''' function to print plans items based on priority '''
    if item[0] != '+':
        if pri == 'all':
            if sys.argv[1] in ('r', 'read'):
                print('[' + str(ind) + '] ' + item)
        elif pri == 'high':
            if parse_priority(item).lower() == 'high':
                print('[' + str(ind) + '] ' + item)
        elif pri == 'medhigh':
            if parse_priority(item).lower() in ('med', 'medium', 'high'):
                print('[' + str(ind) + '] ' + item)
    if sys.argv[1] in ('rf', 'readfull'):
        print('[' + str(ind) + '] ' + item)


def read_records(pri):
    ''' function to read items '''
    global d
    global num_of_days

    if sys.argv[2].lower() in ('wp', 'weeklyplan', 'weekly_plan'):
        if len(d['weekly_plan']) > 0:
            print('weekly plan')
        for ind, item in enumerate(d['weekly_plan'], 0):
            print_plans(pri, item, ind)

    if sys.argv[2].lower() in ('mp', 'monthlyplan', 'monthly_plan'):
        if len(d['monthly_plan']) > 0:
            print('monthly plan')
        for ind, item in enumerate(d['monthly_plan'], 0):
            print_plans(pri, item, ind)

    if sys.argv[2].lower() in ('3mp', '3monthsplan', '3months_plan'):
        if len(d['3months_plan']) > 0:
            print('3months_plan')
        for ind, item in enumerate(d['3months_plan'], 0):
            print_plans(pri, item, ind)

    if sys.argv[2].lower() in ('yp', 'yearlyplan', 'yearly_plan'):
        if len(d['yearly_plan']) > 0:
            print('yearly_plan')
        for ind, item in enumerate(d['yearly_plan'], 0):
            print_plans(pri, item, ind)

    if sys.argv[2].lower() in ('5yp', '5yearsplan', '5years_plan'):
        if len(d['5years_plan']) > 0:
            print('5years_plan')
        for ind, item in enumerate(d['5years_plan'], 0):
            print_plans(pri, item, ind)

    if sys.argv[2].lower() in ('t', 'to', 'tod', 'today'):
        stoday = str(datetime.date.today())[:10].replace('-', '')
        y, m, day = getymday(stoday)
        get_by_date(y, m, day)

    if sys.argv[2].lower() in ('tom', 'tomorrow'):
        tomobj = datetime.date.today() + datetime.timedelta(days=1)
        stomorrow = str(tomobj).replace('-', '')[:8]
        y, m, day = getymday(stomorrow)
        get_by_date(y, m, day)

    if sys.argv[2].lower() in ('y', 'yest', 'yesterday'):
        yestobj = datetime.date.today() + datetime.timedelta(days= -1)
        syest = str(yestobj).replace('-', '')[:8]
        y, m, day = getymday(syest)
        get_by_date(y, m, day)

    if sys.argv[2].lower() in ('d', 'date'):
        dtw = sys.argv[3]
        y, m, day = getymday(dtw)
        get_by_date(y, m, day)

    if sys.argv[2].lower() in ('dr', 'drange', 'daterange'):
        leftdate = sys.argv[3]
        rightdate = sys.argv[4]
        y, m, day = getymday(leftdate)
        datestart = datetime.datetime(int(y), int(m), int(day))
        y, m, day = getymday(rightdate)
        delta = datetime.timedelta(days=1)
        dateend = datetime.datetime(int(y), int(m), int(day)) + delta
        dates = np.arange(datestart, dateend, delta).astype(datetime.datetime)
        for date in dates:
            date = str(date).replace('-', '')[:8]
            y, m, day = getymday(date)
            get_by_date(y, m, day)
        num_of_days = len(dates)
        if sys.argv[1] in ('cf', 'calcfood', 'ea'):
            convert_raw_food_items_to_nutritional_values()

    if sys.argv[2].lower() in ('rec', 'recurrent'):
        if sys.argv[3].lower() in ('dim', 'dayinmonth'):
            for key in d['recurrent']['dayinmonth'].keys():
                if len(d['recurrent']['dayinmonth'][key]) > 0:
                    print_list('[dim]', key, d['recurrent']['dayinmonth'][key], pri)
        if sys.argv[3].lower() in ('w', 'weekly'):
            for key in d['recurrent']['weekly'].keys():
                if len(d['recurrent']['weekly'][key]) > 0:
                    print_list('[w]', dlongwtoshort[key], d['recurrent']['weekly'][key], pri)
        if sys.argv[3].lower() in ('ed', 'everyday', 'every_day'):
            print_list('[ed]', '', d['recurrent']['every_day'], pri)


def argv_numbers_to_list(text):
    ''' function to parse numbers given in argv list by comma/space or dash
    for example 2, 8, 15-20 will be transformed in 2, 8, 15, 16, 17, 18, 19, 20'''
    text = text.replace(' ', ',')
    text = text.replace(',-', '-')
    text = text.replace('-,', '-')
    lin = text.split(',')
    linexp = []
    for linitem in lin:
        if '-' in linitem:
            for i in range(int(linitem.split('-')[0].strip()), int(linitem.split('-')[1].strip()) + 1):
                linexp.append(str(i))
        else:
            if linitem.strip() != '' and linitem.isdigit():
                linexp.append(linitem)
    return linexp


def search(path, dloc, l):
    ''' function to search for text in dictionary '''
    global lsearchout
    for k, v in dloc.items():
        if isinstance(v, dict):
            search(path + '/' + k, v, l)
        elif isinstance(v, list):
            i = -1
            for item in v:
                found = True
                i += 1
                for word in l:
                    if word.lower() not in item.lower():
                        found = False
                        break
                if found:
                    lsearchout.append(path + '/' + k + '/ ' + v[i])
                    # print(path + '/' + k + '/ ' + v[i])


def fa():
    """ """
    global rawfooditems
    global food_nutri_connection
    global nutri_values
    global pers_names
    global pnkeys
    global num_of_days
    try:
        num_of_days = int(sys.argv[2])
    except:
        print("You've skipped interval of days")
        sys.exit()
    if sys.argv[3].lower() == 'fafile':
        rawfooditems = []
        try:
            with codecs.open(dir_in + 'fafile.txt', 'r', 'utf8') as fafile:
                s = fafile.read()
                lshfafile = s.split('>>>')[1].split('<<<')[0].splitlines()
                #print(lshfafile)
                for line in lshfafile:
                    line = line.strip(' ,')
                    if line == '':
                        continue
                    if line[0] != '#':
                        rawfooditems.extend(line.split(','))
        except Exception as e:
            print(str(e))
            sys.exit()
    else:
        rawfooditems = ' '.join(sys.argv[3:]).split(',')

    for i in range(len(rawfooditems)):
        rawfooditems[i] = rawfooditems[i].strip()
        if rawfooditems[i] == '':
            del rawfooditems[i]

    # print(rawfooditems)
    stoday = str(datetime.date.today())[:10].replace('-', '')
    y, m, day = getymday(stoday)

    get_by_date(y, m, day)


def pld():
    """ """
    global food_nutri_connection
    global nutri_values
    global pers_names
    global pnkeys
    global dpers2
    global rawfooditems
    global dfv

    rawfooditems = ' '.join(sys.argv[2:]).split(',')

    load_cipher()
    compact_rawfooditems()
    convert_food_values_to_dict()
    # print(dfv)
    # print(rawfooditems)
    # print(pnkeys)
    # print(pers_names)
    # print(dpers2)

    maxitemlen = max(len(x.split()[0]) for x in rawfooditems)
    # print(maxitemlen)

    for i, item in enumerate(rawfooditems, 0):
        itemname = item.split()[0]
        itemgrams = float(item.split()[1])
        q = 1 - float(dfv[pers_names[itemname]][5]) / 100
        print(itemname.ljust(maxitemlen) + f'({q:4.2f})' + f' {q * itemgrams:5.0f}g')


def main():
    ''' main function for pytodos program '''

    global lsearchout

    if sys.argv[1].lower() in ('b', 'backup'):
        try:
            shutil.copy2(dir_in + 'todos.json', dir_backup + 'todos-' + Year + '-' + todaymonth + '.json')
        except Exception as e:
            print(str(e))
        try:
            shutil.copy2(dir_in + 'pytodos.py', dir_backup + 'pytodos.py')
        except Exception as e:
            print(str(e))
        try:
            shutil.copy2(dir_in + 'pytodos_archive.txt', dir_backup + 'pytodos_archive.txt')
        except Exception as e:
            print(str(e))
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() == 'addyear':
        addyear(sys.argv[2])
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('arc', 'archive'):
        if sys.argv[2].lower() in ('wp', 'weeklyplan', 'weekly_plan'):
            text = 'weekly_plan ' + d['weekly_plan'][int(sys.argv[3])]
        if sys.argv[2].lower() in ('mp', 'monthlyplan', 'monthly_plan'):
            text = 'monthly_plan ' + d['monthly_plan'][int(sys.argv[3])]
        if sys.argv[2].lower() in ('3mp', '3monthsplan', '3months_plan'):
            text = '3months_plan ' + d['3months_plan'][int(sys.argv[3])]
        if sys.argv[2].lower() in ('yp', 'yearlyplan', 'yearly_plan'):
            text = 'yearly_plan ' + d['yearly_plan'][int(sys.argv[3])]
        if sys.argv[2].lower() in ('5yp', '5yearsplan', '5years_plan'):
            text = '5years_plan ' + d['5years_plan'][int(sys.argv[3])]
        archive_plan_item(text)
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('%', 'perc', 'percentage'):
        if sys.argv[2].lower() in ('wp', 'weeklyplan', 'weekly_plan'):
            d['weekly_plan'][int(sys.argv[3])] = '% ' + d['weekly_plan'][int(sys.argv[3])].lstrip('+-').strip()

        if sys.argv[2].lower() in ('mp', 'monthlyplan', 'monthly_plan'):
            d['monthly_plan'][int(sys.argv[3])] = '% ' + d['monthly_plan'][int(sys.argv[3])].lstrip('+-').strip()

        if sys.argv[2].lower() in ('3mp', '3monthsplan', '3months_plan'):
            d['3months_plan'][int(sys.argv[3])] = '% ' + d['3months_plan'][int(sys.argv[3])].lstrip('+-').strip()

        if sys.argv[2].lower() in ('yp', 'yearlyplan', 'yearly_plan'):
            d['yearly_plan'][int(sys.argv[3])] = '% ' + d['yearly_plan'][int(sys.argv[3])].lstrip('+-').strip()

        if sys.argv[2].lower() in ('5yp', '5yearsplan', '5years_plan'):
            d['5years_plan'][int(sys.argv[3])] = '% ' + d['5years_plan'][int(sys.argv[3])].lstrip('+-').strip()

        if sys.argv[2].lower() in ('t', 'to', 'tod', 'today'):
            stoday = str(datetime.date.today())[:10].replace('-', '')
            y, m, day = getymday(stoday)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = '% ' + \
                d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])].lstrip('+-').strip()
            os.system('clear')
            dump_json()
            os.system(f'python3 f{dir_in} pytodos.py r t')
            sys.exit()

        if sys.argv[2].lower() in ('tom', 'tomorrow'):
            tomobj = datetime.date.today() + datetime.timedelta(days=1)
            stom = str(tomobj).replace('-', '')[:8]
            y, m, day = getymday(stom)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = '% ' + \
                d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])].lstrip('+-').strip()

        if sys.argv[2].lower() in ('y', 'yest', 'yesterday'):
            yestobj = datetime.date.today() + datetime.timedelta(days=-1)
            syest = str(yestobj).replace('-', '')[:8]
            y, m, day = getymday(syest)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = '% ' + \
                d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])].lstrip('+-').strip()

        if sys.argv[2].lower() in ('d', 'date'):
            dtw = sys.argv[3]
            y, m, day = getymday(dtw)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[4])] = '% ' + \
                d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[4])].lstrip('+-').strip()
        dump_json()
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('-', 'minus'):
        if sys.argv[2].lower() in ('wp', 'weeklyplan', 'weekly_plan'):
            d['weekly_plan'][int(sys.argv[3])] = '- ' + d['weekly_plan'][int(sys.argv[3])].lstrip('+%').strip()

        if sys.argv[2].lower() in ('mp', 'monthlyplan', 'monthly_plan'):
            d['monthly_plan'][int(sys.argv[3])] = '- ' + d['monthly_plan'][int(sys.argv[3])].lstrip('+%').strip()

        if sys.argv[2].lower() in ('3mp', '3monthsplan', '3months_plan'):
            d['3months_plan'][int(sys.argv[3])] = '- ' + d['3months_plan'][int(sys.argv[3])].lstrip('+%').strip()

        if sys.argv[2].lower() in ('yp', 'yearlyplan', 'yearly_plan'):
            d['yearly_plan'][int(sys.argv[3])] = '- ' + d['yearly_plan'][int(sys.argv[3])].lstrip('+%').strip()

        if sys.argv[2].lower() in ('5yp', '5yearsplan', '5years_plan'):
            d['5years_plan'][int(sys.argv[3])] = '- ' + d['5years_plan'][int(sys.argv[3])].lstrip('+%').strip()

        if sys.argv[2].lower() in ('t', 'to', 'tod', 'today'):
            stoday = str(datetime.date.today())[:10].replace('-', '')
            y, m, day = getymday(stoday)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = '- ' + \
                d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])].lstrip('+%').strip()
            os.system('clear')
            dump_json()
            os.system(f'python3 f{dir_in} pytodos.py r t')
            sys.exit()

        if sys.argv[2].lower() in ('tom', 'tomorrow'):
            tomobj = datetime.date.today() + datetime.timedelta(days=1)
            stom = str(tomobj).replace('-', '')[:8]
            y, m, day = getymday(stom)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = '- ' + \
                d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])].lstrip('+%').strip()

        if sys.argv[2].lower() in ('y', 'yest', 'yesterday'):
            yestobj = datetime.date.today() + datetime.timedelta(days= -1)
            syest = str(yestobj).replace('-', '')[:8]
            y, m, day = getymday(syest)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = '- ' + \
                d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])].lstrip('+%').strip()

        if sys.argv[2].lower() in ('d', 'date'):
            dtw = sys.argv[3]
            y, m, day = getymday(dtw)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[4])] = '- ' + \
                d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[4])].lstrip('+%').strip()
        dump_json()
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('+', 'done', 'plus'):
        if sys.argv[2].lower() in ('wp', 'weeklyplan', 'weekly_plan'):
            value = d['weekly_plan'][int(sys.argv[3])]
            new_value = '+' + ' ' + value.lstrip('%-').strip()
            d['weekly_plan'][int(sys.argv[3])] = new_value

        if sys.argv[2].lower() in ('mp', 'monthlyplan', 'monthly_plan'):
            value = d['monthly_plan'][int(sys.argv[3])]
            new_value = '+' + ' ' + value.lstrip('%-').strip()
            d['monthly_plan'][int(sys.argv[3])] = new_value

        if sys.argv[2].lower() in ('3mp', '3monthsplan', '3months_plan'):
            value = d['3months_plan'][int(sys.argv[3])]
            new_value = '+' + ' ' + value.lstrip('%-').strip()
            d['3months_plan'][int(sys.argv[3])] = new_value

        if sys.argv[2].lower() in ('yp', 'yearlyplan', 'yearly_plan'):
            value = d['yearly_plan'][int(sys.argv[3])]
            new_value = '+' + ' ' + value.lstrip('%-').strip()
            d['yearly_plan'][int(sys.argv[3])] = new_value

        if sys.argv[2].lower() in ('5yp', '5yearsplan', '5years_plan'):
            value = d['5years_plan'][int(sys.argv[3])]
            new_value = '+' + ' ' + value.lstrip('%-').strip()
            d['5years_plan'][int(sys.argv[3])] = new_value

        if sys.argv[2].lower() in ('t', 'to', 'tod', 'today'):
            stoday = str(datetime.date.today())[:10].replace('-', '')
            y, m, day = getymday(stoday)
            value = d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])]
            new_value = '+' + ' ' + value.lstrip('%-').strip()
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = new_value
            os.system('clear')
            dump_json()
            os.system(f'python3 f{dir_in} pytodos.py r t')
            sys.exit()

        if sys.argv[2].lower() in ('tom', 'tomorrow'):
            tomobj = datetime.date.today() + datetime.timedelta(days=1)
            stom = str(tomobj).replace('-', '')[:8]
            y, m, day = getymday(stom)
            value = d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])]
            new_value = '+' + ' ' + value.lstrip('%-').strip()
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = new_value

        if sys.argv[2].lower() in ('y', 'yest', 'yesterday'):
            yestobj = datetime.date.today() + datetime.timedelta(days= -1)
            syest = str(yestobj).replace('-', '')[:8]
            y, m, day = getymday(syest)
            value = d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])]
            new_value = '+' + ' ' + value.lstrip('%-').strip()
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = new_value

        if sys.argv[2].lower() in ('d', 'date'):
            dtw = sys.argv[3]
            y, m, day = getymday(dtw)
            value = d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[4])]
            new_value = '+' + ' ' + value.lstrip('%-').strip()
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[4])] = new_value
        dump_json()
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('rd', 'rdone', 'recdone', 'recurrentdone'):
        l = argv_numbers_to_list(''.join(sys.argv[2:]))
        with codecs.open(dir_in + 'rdone', 'a', 'utf8') as f:
            for item in l:
                f.write(item + os.linesep)
        os.system('clear')
        os.system(f'python3 f{dir_in} pytodos.py r t')
        sys.exit()
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('sh', 'shift'):
        if sys.argv[2].lower() in ('rec', 'recurrent'):
            if sys.argv[3].lower() in ('w', 'weekly'):
                if sys.argv[4] in ('su', 'mo', 'tu', 'we', 'th', 'fr', 'sa'):
                    shift_list(['recurrent', 'weekly', dweekdays[sys.argv[4]]], int(sys.argv[5]), int(sys.argv[6]))
            if sys.argv[3].lower() in ('dim', 'dayinmonth'):
                if len(sys.argv[4]) == 1:
                    sys.argv[4] = '0' + sys.argv[4]
                shift_list(['recurrent', 'dayinmonth', sys.argv[4]], int(sys.argv[5]), int(sys.argv[6]))

            if sys.argv[3].lower() in ('ed', 'everyday', 'every_day'):
                shift_list(['recurrent', 'every_day'], int(sys.argv[4]), int(sys.argv[5]))

        if sys.argv[2].lower() in ('wp', 'weeklyplan', 'weekly_plan'):
            shift_list(['weekly_plan'], int(sys.argv[3]), int(sys.argv[4]))

        if sys.argv[2].lower() in ('mp', 'monthlyplan', 'monthly_plan'):
            shift_list(d['monthly_plan'],  int(sys.argv[3]), int(sys.argv[4]))

        if sys.argv[2].lower() in ('3mp', '3monthsplan', '3months_plan'):
            shift_list(d['3months_plan'],  int(sys.argv[3]), int(sys.argv[4]))

        if sys.argv[2].lower() in ('yp', 'yearlyplan', 'yearly_plan'):
            shift_list(d['yearly_plan'],  int(sys.argv[3]), int(sys.argv[4]))

        if sys.argv[2].lower() in ('5yp', '5yearsplan', '5years_plan'):
            shift_list(d['5years_plan'],  int(sys.argv[3]), int(sys.argv[4]))

        if sys.argv[2].lower() in ('t', 'to', 'tod', 'today'):
            stoday = str(datetime.date.today())[:10].replace('-', '')
            y, m, day = getymday(stoday)
            shift_list([y, dmonths[int(m.lstrip('0'))], day], int(sys.argv[3]), int(sys.argv[4]))
            os.system('clear')
            dump_json()
            os.system(f'python3 {dir_in} + pytodos.py r t')
            sys.exit()

        if sys.argv[2].lower() in ('tom', 'tomorrow'):
            tomobj = datetime.date.today() + datetime.timedelta(days=1)
            stom = str(tomobj).replace('-', '')[:8]
            y, m, day = getymday(stom)
            shift_list([y, dmonths[int(m.lstrip('0'))], day], int(sys.argv[3]), int(sys.argv[4]))

        if sys.argv[2].lower() in ('y', 'yest', 'yesterday'):
            yestobj = datetime.date.today() + datetime.timedelta(days= -1)
            syest = str(yestobj).replace('-', '')[:8]
            y, m, day = getymday(syest)
            shift_list([y, dmonths[int(m.lstrip('0'))], day], int(sys.argv[3]), int(sys.argv[4]))

        if sys.argv[2].lower() in ('d', 'date'):
            dtw = sys.argv[3]
            y, m, day = getymday(dtw)
            shift_list([y, dmonths[int(m.lstrip('0'))], day], int(sys.argv[4]), int(sys.argv[5]))
        dump_json()
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('a', 'app', 'append'):
        if sys.argv[2].lower() in ('rec', 'recurrent'):
            if sys.argv[3].lower() in ('w', 'weekly'):
                if sys.argv[4] in ('su', 'mo', 'tu', 'we', 'th', 'fr', 'sa'):
                    text = check_priority_time(' '.join(sys.argv[5:]))
                    d['recurrent']['weekly'][dweekdays[sys.argv[4]]].append(text)
            if sys.argv[3].lower() in ('dim', 'dayinmonth'):
                if len(sys.argv[4]) == 1:
                    sys.argv[4] = '0' + sys.argv[4]
                text = check_priority_time(' '.join(sys.argv[5:]))
                d['recurrent']['dayinmonth'][sys.argv[4]].append(text)
            if sys.argv[3].lower() in ('ed', 'everyday', 'every_day'):
                text = check_priority_time(' '.join(sys.argv[4:]))
                d['recurrent']['every_day'].append(text)

        if sys.argv[2].lower() in ('wp', 'weeklyplan', 'weekly_plan'):
            text = check_priority_time(' '.join(sys.argv[3:]))
            d['weekly_plan'].append(text)

        if sys.argv[2].lower() in ('mp', 'monthlyplan', 'monthly_plan'):
            text = check_priority_time(' '.join(sys.argv[3:]))
            d['monthly_plan'].append(text)

        if sys.argv[2].lower() in ('3mp', '3monthsplan', '3months_plan'):
            text = check_priority_time(' '.join(sys.argv[3:]))
            d['3months_plan'].append(text)

        if sys.argv[2].lower() in ('yp', 'yearlyplan', 'yearly_plan'):
            text = check_priority_time(' '.join(sys.argv[3:]))
            d['yearly_plan'].append(text)

        if sys.argv[2].lower() in ('5yp', '5yearsplan', '5years_plan'):
            text = check_priority_time(' '.join(sys.argv[3:]))
            d['5years_plan'].append(text)

        if sys.argv[2].lower() in ('t', 'to', 'tod', 'today'):
            stoday = str(datetime.date.today())[:10].replace('-', '')
            y, m, day = getymday(stoday)
            text = check_priority_time(' '.join(sys.argv[3:]))
            d[y][dmonths[int(m.lstrip('0'))]][day].append(text)
            os.system('clear')
            dump_json()
            os.system(f'python3 {dir_in} + pytodos.py r t')
            sys.exit()

        if sys.argv[2].lower() in ('tom', 'tomorrow'):
            tomobj = datetime.date.today() + datetime.timedelta(days=1)
            stom = str(tomobj).replace('-', '')[:8]
            y, m, day = getymday(stom)
            text = check_priority_time(' '.join(sys.argv[3:]))
            d[y][dmonths[int(m.lstrip('0'))]][day].append(text)

        if sys.argv[2].lower() in ('y', 'yest', 'yesterday'):
            yestobj = datetime.date.today() + datetime.timedelta(days=-1)
            syest = str(yestobj).replace('-', '')[:8]
            y, m, day = getymday(syest)
            text = check_priority_time(' '.join(sys.argv[3:]))
            d[y][dmonths[int(m.lstrip('0'))]][day].append(text)

        if sys.argv[2].lower() in ('d', 'date'):
            dtw = sys.argv[3]
            y, m, day = getymday(dtw)
            text = check_priority_time(' '.join(sys.argv[4:]))
            d[y][dmonths[int(m.lstrip('0'))]][day].append(text)
        dump_json()
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('r', 'read', 'rf', 'readfull', 'cf', 'calcfood', 'ea'):
        read_records(pri='all')

    if sys.argv[1].lower() in ('rh', 'readhigh'):
        read_records(pri='high')

    if sys.argv[1].lower() in ('rmh', 'readmedhigh'):
        read_records(pri='medhigh')
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('del', 'delete', 'remove'):
        if sys.argv[2].lower() in ('wp', 'weeklyplan', 'weekly_plan'):
            if sys.argv[3] == 'all':
                d['weekly_plan'] = []
            else:
                del d['weekly_plan'][int(sys.argv[3])]

        if sys.argv[2].lower() in ('mp', 'monthlyplan', 'monthly_plan'):
            if sys.argv[3] == 'all':
                d['monthly_plan'] = []
            else:
                del d['monthly_plan'][int(sys.argv[3])]

        if sys.argv[2].lower() in ('3mp', '3monthsplan', '3months_plan'):
            if sys.argv[3] == 'all':
                d['3months_plan'] = []
            else:
                del d['3months_plan'][int(sys.argv[3])]

        if sys.argv[2].lower() in ('yp', 'yearlyplan', 'yearly_plan'):
            if sys.argv[3] == 'all':
                d['yearly_plan'] = []
            else:
                del d['yearly_plan'][int(sys.argv[3])]

        if sys.argv[2].lower() in ('5yp', '5yearsplan', '5years_plan'):
            if sys.argv[3] == 'all':
                d['5years_plan'] = []
            else:
                del d['5years_plan'][int(sys.argv[3])]

        if sys.argv[2].lower() in ('t', 'to', 'tod', 'today'):
            stoday = str(datetime.date.today())[:10].replace('-', '')
            y, m, day = getymday(stoday)
            del d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])]
            os.system('clear')
            dump_json()
            os.system(f'python3 f{dir_in} pytodos.py r t')
            sys.exit()

        if sys.argv[2].lower() in ('tom', 'tomorrow'):
            tomobj = datetime.date.today() + datetime.timedelta(days=1)
            stomorrow = str(tomobj).replace('-', '')[:8]
            y, m, day = getymday(stomorrow)
            del d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])]

        if sys.argv[2].lower() in ('y', 'yest', 'yesterday'):
            yestobj = datetime.date.today() + datetime.timedelta(days= -1)
            syest = str(yestobj).replace('-', '')[:8]
            y, m, day = getymday(syest)
            del d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])]

        if sys.argv[2].lower() in ('d', 'day', 'date'):
            dtw = sys.argv[3]
            y, m, day = getymday(dtw)
            del d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[4])]
        if sys.argv[2].lower() in ('rec', 'recurrent'):
            if sys.argv[3].lower() in ('ed', 'everyday', 'every_day'):
                del d['recurrent']['every_day'][int(sys.argv[4])]
            if sys.argv[3].lower() in ('w', 'weekly'):
                if sys.argv[4] in ('su', 'mo', 'tu', 'we', 'th', 'fr', 'sa'):
                    del d['recurrent']['weekly'][dweekdays[sys.argv[4]]][int(sys.argv[5])]
            if sys.argv[3].lower() in ('dim', 'dayinmonth'):
                if len(sys.argv[4]) == 1:
                    sys.argv[4] = '0' + sys.argv[4]
                del d['recurrent']['dayinmonth'][sys.argv[4]][int(sys.argv[5])]
        if sys.argv[2].lower() in ('rd', 'rdone',):
            os.remove(dir_in + 'rdone')
        dump_json()
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('c', 'change'):
        if sys.argv[2].lower() in ('wp', 'weeklyplan', 'weekly_plan'):
            text = check_priority_time(' '.join(sys.argv[4:]))
            d['weekly_plan'][int(sys.argv[3])] = text

        if sys.argv[2].lower() in ('mp', 'monthlyplan', 'monthly_plan'):
            text = check_priority_time(' '.join(sys.argv[4:]))
            d['monthly_plan'][int(sys.argv[3])] = text

        if sys.argv[2].lower() in ('3mp', '3monthsplan', '3months_plan'):
            text = check_priority_time(' '.join(sys.argv[4:]))
            d['3months_plan'][int(sys.argv[3])] = text

        if sys.argv[2].lower() in ('yp', 'yearlyplan', 'yearly_plan'):
            text = check_priority_time(' '.join(sys.argv[4:]))
            d['yearly_plan'][int(sys.argv[3])] = text

        if sys.argv[2].lower() in ('5yp', '5yearsplan', '5years_plan'):
            text = check_priority_time(' '.join(sys.argv[4:]))
            d['5years_plan'][int(sys.argv[3])] = text

        if sys.argv[2].lower() in ('t', 'to', 'tod', 'today'):
            stoday = str(datetime.date.today())[:10].replace('-', '')
            y, m, day = getymday(stoday)
            text = check_priority_time(' '.join(sys.argv[4:]))
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = text
            os.system('clear')
            dump_json()
            os.system(f'python3 f{dir_in} pytodos.py r t')
            sys.exit()

        if sys.argv[2].lower() in ('tom', 'tomorrow'):
            tomobj = datetime.date.today() + datetime.timedelta(days=1)
            stomorrow = str(tomobj).replace('-', '')[:8]
            y, m, day = getymday(stomorrow)
            text = check_priority_time(' '.join(sys.argv[4:]))
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = text

        if sys.argv[2].lower() in ('y', 'yest', 'yesterday'):
            yestobj = datetime.date.today() + datetime.timedelta(days= -1)
            syest = str(yestobj).replace('-', '')[:8]
            y, m, day = getymday(syest)
            text = check_priority_time(' '.join(sys.argv[4:]))
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = text

        if sys.argv[2].lower() in ('d', 'day', 'date'):
            dtw = sys.argv[3]
            y, m, day = getymday(dtw)
            text = check_priority_time(' '.join(sys.argv[5:]))
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[4])] = text

        if sys.argv[2].lower() in ('rec', 'recurrent'):
            if sys.argv[3].lower() in ('ed', 'everyday', 'every_day'):
                text = check_priority_time(' '.join(sys.argv[5:]))
                d['recurrent']['every_day'][int(sys.argv[4])] = text
            if sys.argv[3].lower() in ('w', 'weekly'):
                if sys.argv[4] in ('su', 'mo', 'tu', 'we', 'th', 'fr', 'sa'):
                    text = check_priority_time(' '.join(sys.argv[6:]))
                    d['recurrent']['weekly'][dweekdays[sys.argv[4]]][int(sys.argv[5])] = text
            if sys.argv[3].lower() in ('dim', 'dayinmonth'):
                if len(sys.argv[4]) == 1:
                    sys.argv[4] = '0' + sys.argv[4]
                text = check_priority_time(' '.join(sys.argv[6:]))
                d['recurrent']['dayinmonth'][sys.argv[4]][int(sys.argv[5])] = text
        dump_json()
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('ca', 'changeappend'):
        text = check_priority_time(' '.join(sys.argv[4:]))
        def pre(text):
            if text[0] == ',':
                s = ',' + text[1:]
            else:
                s = ' ' + text
            return s
        if sys.argv[2].lower() in ('wp', 'weeklyplan', 'weekly_plan'):
            d['weekly_plan'][int(sys.argv[3])] += pre(text)

        if sys.argv[2].lower() in ('mp', 'monthlyplan', 'monthly_plan'):
            d['monthly_plan'][int(sys.argv[3])] += pre(text)

        if sys.argv[2].lower() in ('3mp', '3monthsplan', '3months_plan'):
            d['3months_plan'][int(sys.argv[3])] += pre(text)

        if sys.argv[2].lower() in ('yp', 'yearlyplan', 'yearly_plan'):
            d['yearly_plan'][int(sys.argv[3])] += pre(text)

        if sys.argv[2].lower() in ('5yp', '5yearsplan', '5years_plan'):
            d['5years_plan'][int(sys.argv[3])] += pre(text)

        if sys.argv[2].lower() in ('t', 'to', 'tod', 'today'):
            stoday = str(datetime.date.today())[:10].replace('-', '')
            y, m, day = getymday(stoday)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] += pre(text)
            os.system('clear')
            dump_json()
            os.system(f'python3 f{dir_in} pytodos.py r t')
            sys.exit()

        if sys.argv[2].lower() in ('tom', 'tomorrow'):
            tomobj = datetime.date.today() + datetime.timedelta(days=1)
            stomorrow = str(tomobj).replace('-', '')[:8]
            y, m, day = getymday(stomorrow)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] += pre(text)

        if sys.argv[2].lower() in ('y', 'yest', 'yesterday'):
            yestobj = datetime.date.today() + datetime.timedelta(days= -1)
            syest = str(yestobj).replace('-', '')[:8]
            y, m, day = getymday(syest)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] += pre(text)

        if sys.argv[2].lower() in ('d', 'day', 'date'):
            dtw = sys.argv[3]
            y, m, day = getymday(dtw)
            text = check_priority_time(' '.join(sys.argv[5:]))
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[4])] += pre(text)

        if sys.argv[2].lower() in ('rec', 'recurrent'):
            if sys.argv[3].lower() in ('ed', 'everyday', 'every_day'):
                text = check_priority_time(' '.join(sys.argv[5:]))
                d['recurrent']['every_day'][int(sys.argv[4])] += pre(text)
            if sys.argv[3].lower() in ('w', 'weekly'):
                if sys.argv[4] in ('su', 'mo', 'tu', 'we', 'th', 'fr', 'sa'):
                    text = check_priority_time(' '.join(sys.argv[6:]))
                    d['recurrent']['weekly'][dweekdays[sys.argv[4]]][int(sys.argv[5])] += pre(text)
            if sys.argv[3].lower() in ('dim', 'dayinmonth'):
                if len(sys.argv[4]) == 1:
                    sys.argv[4] = '0' + sys.argv[4]
                text = check_priority_time(' '.join(sys.argv[6:]))
                d['recurrent']['dayinmonth'][sys.argv[4]][int(sys.argv[5])] += pre(text)
        dump_json()
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('s', 'search'):
        lsearchout = []
        search('', d, sys.argv[2:])
        lsearchout.sort()
        for item in lsearchout:
            print(item)
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('fa', 'foodsanalysis'):
        fa()
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('fg',):
        terms = sys.argv[2:]
        with codecs.open(dir_in + 'food_values.txt', 'r', 'utf8') as grepfile:
            for line in grepfile:
                linetitle = line.split('|')[2]
                bskip = False
                for term in terms:
                    if term.lower() not in linetitle.lower():
                        bskip = True
                        break
                if not bskip:
                    print(line.split('|')[0] + '|' + line.split('|')[1] + '|' + linetitle)
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('cg',):
        terms = sys.argv[2:]
        with codecs.open(dir_in + 'cipher.txt', 'r', 'utf8') as grepfile:
            for line in grepfile:
                line = line.strip()
                bskip = False
                for term in terms:
                    if term.lower() not in line.lower():
                        bskip = True
                        break
                if not bskip:
                    print(line)
    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('pld',):
        pld()
    # --------------------------------------------------------------------------
    def smallril(text):
        """ convert command line text using ^ as separator for
        replacewith and replaceto strings, 4^ should be used"""
        qind = [i for i, ltr in enumerate(text) if ltr == '^']
        if len(qind) != 4:
            print('you should use 4^ for annotating replacewith and replaceto')
            sys.exit()
        return text[qind[0]+1:qind[1]], text[qind[2]+1:qind[3]]

    if sys.argv[1].lower() in ('ril',):
        text = check_priority_time(' '.join(sys.argv[4:]))
        replacewith, replaceto = smallril(text)
        if sys.argv[2].lower() in ('wp', 'weeklyplan', 'weekly_plan'):
            d['weekly_plan'][int(sys.argv[3])] = d['weekly_plan'][int(sys.argv[3])].replace(replacewith, replaceto, 1)

        if sys.argv[2].lower() in ('mp', 'monthlyplan', 'monthly_plan'):
            d['monthly_plan'][int(sys.argv[3])] = d['monthly_plan'][int(sys.argv[3])].replace(replacewith, replaceto, 1)

        if sys.argv[2].lower() in ('3mp', '3monthsplan', '3months_plan'):
            d['3months_plan'][int(sys.argv[3])] = d['3months_plan'][int(sys.argv[3])].replace(replacewith, replaceto, 1)

        if sys.argv[2].lower() in ('yp', 'yearlyplan', 'yearly_plan'):
            d['yearly_plan'][int(sys.argv[3])] = d['yearly_plan'][int(sys.argv[3])].replace(replacewith, replaceto, 1)

        if sys.argv[2].lower() in ('5yp', '5yearsplan', '5years_plan'):
            d['5years_plan'][int(sys.argv[3])] = d['5years_plan'][int(sys.argv[3])].replace(replacewith, replaceto, 1)

        if sys.argv[2].lower() in ('t', 'to', 'tod', 'today'):
            stoday = str(datetime.date.today())[:10].replace('-', '')
            y, m, day = getymday(stoday)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])].replace(replacewith, replaceto, 1)
            os.system('clear')
            dump_json()
            os.system(f'python3 f{dir_in} pytodos.py r t')
            sys.exit()

        if sys.argv[2].lower() in ('tom', 'tomorrow'):
            tomobj = datetime.date.today() + datetime.timedelta(days=1)
            stomorrow = str(tomobj).replace('-', '')[:8]
            y, m, day = getymday(stomorrow)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])].replace(replacewith, replaceto, 1)

        if sys.argv[2].lower() in ('y', 'yest', 'yesterday'):
            yestobj = datetime.date.today() + datetime.timedelta(days= -1)
            syest = str(yestobj).replace('-', '')[:8]
            y, m, day = getymday(syest)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])] = d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[3])].replace(replacewith, replaceto, 1)

        if sys.argv[2].lower() in ('d', 'day', 'date'):
            dtw = sys.argv[3]
            y, m, day = getymday(dtw)
            text = check_priority_time(' '.join(sys.argv[5:]))
            replacewith, replaceto = smallril(text)
            d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[4])] = d[y][dmonths[int(m.lstrip('0'))]][day][int(sys.argv[4])].replace(replacewith, replaceto, 1)

        if sys.argv[2].lower() in ('rec', 'recurrent'):
            if sys.argv[3].lower() in ('ed', 'everyday', 'every_day'):
                text = check_priority_time(' '.join(sys.argv[5:]))
                replacewith, replaceto = smallril(text)
                d['recurrent']['every_day'][int(sys.argv[4])] = d['recurrent']['every_day'][int(sys.argv[4])].replace(replacewith, replaceto, 1)
            if sys.argv[3].lower() in ('w', 'weekly'):
                if sys.argv[4] in ('su', 'mo', 'tu', 'we', 'th', 'fr', 'sa'):
                    text = check_priority_time(' '.join(sys.argv[6:]))
                    replacewith, replaceto = smallril(text)
                    d['recurrent']['weekly'][dweekdays[sys.argv[4]]][int(sys.argv[5])] = d['recurrent']['weekly'][dweekdays[sys.argv[4]]][int(sys.argv[5])].replace(replacewith, replaceto, 1)
            if sys.argv[3].lower() in ('dim', 'dayinmonth'):
                if len(sys.argv[4]) == 1:
                    sys.argv[4] = '0' + sys.argv[4]
                text = check_priority_time(' '.join(sys.argv[6:]))
                replacewith, replaceto = smallril(text)
                d['recurrent']['dayinmonth'][sys.argv[4]][int(sys.argv[5])] = d['recurrent']['dayinmonth'][sys.argv[4]][int(sys.argv[5])].replace(replacewith, replaceto, 1)
        dump_json()

    # --------------------------------------------------------------------------
    if sys.argv[1].lower() in ('h', 'help'):
        print('examples:')
        print('append recurrent weekly every monday')
        print('t a rec w mo do something')
        print('append recurrent every 5.th in month')
        print('t a rec dim 5 do something')
        print('append today')
        print('t a tod do something')
        print('append tomorrow')
        print('t a tom do something')
        print('append in specified date')
        print('t a d 0623 do something')
        print('read today')
        print('t r t')
        print('read tomorrow')
        print('t r tom')
        print('read by date june 23')
        print('t r d 0623')
        print('t r d 20180623')
        print('read by daterange may 30 till june 15')
        print('t r dr 0530 0615')
        print('t r dr 20180530 20180615')
        print('read recurrents')
        print('t r rec')
        print('delete in json by date june 23 item with index 1 (starts with 0)')
        print('t del d 0623 1')
        print('delete in json recurrent weekly sunday with index 1 (starts with 0)')
        print('t del rec w su 1')
        print('delete in json recurrent by dayinmonth 5 with index 1 (starts with 0)')
        print('t del rec dim 5 1')
        print('change in recurrent weekly for sunday at index 0')
        print('t c rec weekly su 0 this is change')
        print('change june 23 on index 0')
        print('t c day 0623 0 another change')


if __name__ == '__main__':
    initialise()
    main()
