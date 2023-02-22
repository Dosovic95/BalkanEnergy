import numpy as np
import string
import csv
import os
from subprocess import call
from matplotlib import pyplot as plt
import pysftp
from subprocess import call
import time
import csv
import os.path
import datetime
import pandas
from selenium import webdriver
import shutil
import pandas as pd
start_time = time.time()
def pad_dict_list(dict_list, padel):
    lmax = 0
    for lname in dict_list.keys():
        lmax = max(lmax, len(dict_list[lname]))
    for lname in dict_list.keys():
        ll = len(dict_list[lname])
        if  ll < lmax:
            dict_list[lname] += [padel] * (lmax - ll)
    return dict_list
def intersect(x1, y1, x2, y2):
    n = len(x1)
    m = len(x2)

    i = n - 1
    j = 0
    ind = 2
    while (i >= 0 and j < m):
        if (y1[i] < y2[j]):
            if(ind == 2):
                return y2[j], x2[j]
            if(ind == 1):
                return y1[i], x1[i]
        if (x1[i] < x2[j]):
            i-=1
            ind = 2
        else:
            j+=1
            ind = 1
    return -500, 0

def brisanje_space(df):
    df['Timestamp'] = df['Timestamp'].str.strip()
    return df
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def prestupna(year):
    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                return 1
            else:
                return 0
        else:
            return 1
    else:
        return 0
def all_occurences(file, str):
    initial = 0
    while True:
        initial = file.find(str, initial)
        if initial == -1: return
        yield initial
        initial += len(str)

date_format = "%d.%m.%Y"
def br_dana(a,b):
    a = datetime.datetime.strptime(a, date_format)
    b = datetime.datetime.strptime(b, date_format)
    delta = b - a
    return delta

def next_day(dan,me,god):
    day = dan
    month = me
    year = god
    if (year % 400 == 0):
        leap_year = True
    elif (year % 100 == 0):
        leap_year = False
    elif (year % 4 == 0):
        leap_year = True
    else:
        leap_year = False



    if month in (1, 3, 5, 7, 8, 10, 12):
        month_length = 31
    elif month == 2:
        if leap_year:
            month_length = 29
        else:
            month_length = 28
    else:
        month_length = 30




    if day < month_length:
        day += 1
    else:
        day = 1
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
    return day, month, year
def skidanje(za_koji_sat):
    global start_time
    
    
    unazad = -1
    unapred = +1
    popravka_unazad = 0
    popravka_unapred = 0
    now = datetime.datetime.now() + datetime.timedelta(days=int(unapred) + 1 + int(popravka_unapred))
    enddd = datetime.datetime.now() + datetime.timedelta(days=int(unazad) + int(popravka_unazad))
    dan1 = enddd.day
    mesec1 = enddd.month
    god1 = enddd.year
    startp = 100000000 * god1 + mesec1 * 1000000 + dan1 * 10000
    dan2 = now.day
    mesec2 = now.month
    god2 = now.year
    endp = 100000000 * god2 + mesec2 * 1000000 + dan2 * 10000
    datum1 = "%02d.%02d.%04d"%(dan1,mesec1,god1)
    datum1 = datum1.replace(' ', '')
    datum2 = "%02d.%02d.%04d"%(dan2,mesec2,god2)
    datum2 = datum2.replace(' ', '')

    
    c = []

    d = {}
    colors1 = ["lightblue", "blue" , "darkblue"]
    colors2 = ["lightcoral", "red" , "darkred"]
    daaaaa = 0
    for brdd in range(br_dana(datum1, datum2).days):

        
        datum = god1 * 10000 + mesec1 * 100 + dan1
        host = 'sftp2.hupx.hu'
        user = 'balkan_energy'
        password = 'markohupx22'
        
        # Loads .ssh/known_hosts
        cnopts = pysftp.CnOpts()
        hostkeys = None
        
        if cnopts.hostkeys.lookup(host) == None:
            # Backup loaded .ssh/known_hosts file
            hostkeys = cnopts.hostkeys
            # And do not verify host key of the new host
            cnopts.hostkeys = None
        with pysftp.Connection(host, username = user, password = password, cnopts = cnopts, port = 222) as sftp:
            if hostkeys != None:
                hostkeys.add(host, sftp.remote_server_key.get_name(), sftp.remote_server_key)
                hostkeys.save(pysftp.helpers.known_hosts())
            sftp.get("/HUPX_DAM_MarketData/" + str(god1) + "/aggregated_curves/HUPX_DAM_Aggregated_Curve_" + str(datum) + ".xml")
            sftp.close()
        shutil.move("HUPX_DAM_Aggregated_Curve_" + str(datum) + ".xml", "C:\\Users\\User\\Anaconda2\\HUPX-sensitivity\\HUPX_DAM_Aggregated_Curve_" + str(datum) + ".xml")
        #C:\Users\User\Anaconda2\Scripts\\
        
            
        
        call(["C:\\Users\\User\\anaconda3\\Scripts\\xml2csv", "--input", "C:\\Users\\User\\Anaconda2\\HUPX-sensitivity\\HUPX_DAM_Aggregated_Curve_" + str(datum) + ".xml", "--output", "C:\\Users\\User\\Anaconda2\\HUPX-sensitivity\\1.csv", "--tag", "Purchase"])
        call(["C:\\Users\\User\\anaconda3\\Scripts\\xml2csv", "--input", "C:\\Users\\User\\Anaconda2\\HUPX-sensitivity\\HUPX_DAM_Aggregated_Curve_" + str(datum) + ".xml", "--output", "C:\\Users\\User\\Anaconda2\\HUPX-sensitivity\\2.csv", "--tag", "Sell"])

        with open("C:\\Users\\User\\Anaconda2\\HUPX-sensitivity\\1.csv") as csvfile1:
            reader1 = csv.DictReader(csvfile1)
            with open("C:\\Users\\User\\Anaconda2\\HUPX-sensitivity\\2.csv") as csvfile2:
                reader2 = csv.DictReader(csvfile2)
                cene = np.zeros(24)
                cene_plus = np.zeros(24)
                cene_minus = np.zeros(24)
                koliko_fali1 = np.zeros(24)
                koliko_fali = np.zeros(24)
                koliko_fali2 = np.zeros(24)
                nadji_x = np.zeros(24)
                for i in range(24):
                    datumu = "%04d.%02d.%02d %02d:%02d:%02d"%(god1,mesec1,dan1,int(i+1) , 0, 0)
                    kupovina_cena = []
                    kupovina_MW = []
                    prodaja_cena = []
                    prodaja_MW = []
                    kupovina_MWplus100 = []
                    kupovina_MWplus200 = []
                    kupovina_MWplus300 = []
                    kupovina_MWplus400 = []
                    kupovina_MWplus500 = []
                    kupovina_MWminus100 = []
                    kupovina_MWminus200 = []
                    kupovina_MWminus300 = []
                    kupovina_MWminus400 = []
                    kupovina_MWminus500 = []

                    prodaja_MWplus100 = []
                    prodaja_MWplus200 = []
                    prodaja_MWplus300 = []
                    prodaja_MWplus400 = []
                    prodaja_MWplus500 = []
                    prodaja_MWminus100 = []
                    prodaja_MWminus200 = []
                    prodaja_MWminus300 = []
                    prodaja_MWminus400 = []
                    prodaja_MWminus500 = []
                    row1 = next(reader1)
                    row2 = next(reader2)

                    while row1["Price"] != "":
                        kupovina_cena.append(float(row1["Price"]))
                        kupovina_MWminus500.append(float(row1["Volume"]) - 500.00)
                        kupovina_MWminus400.append(float(row1["Volume"]) - 400.00)
                        kupovina_MWminus300.append(float(row1["Volume"]) - 300.00)
                        kupovina_MWminus200.append(float(row1["Volume"]) - 200.00)
                        kupovina_MWminus100.append(float(row1["Volume"]) - 100.00)
                        kupovina_MWplus100.append(float(row1["Volume"]) + 100.00)
                        kupovina_MWplus200.append(float(row1["Volume"]) + 200.00)
                        kupovina_MWplus300.append(float(row1["Volume"]) + 300.00)
                        kupovina_MWplus400.append(float(row1["Volume"]) + 400.00)
                        kupovina_MWplus500.append(float(row1["Volume"]) + 500.00)
                        kupovina_MW.append(float(row1["Volume"]))
                        try:
                            row1 = next(reader1)
                        except StopIteration:
                            break



                    while row2["Price"] != "":
                        prodaja_cena.append(float(row2["Price"]))
                        prodaja_MWminus500.append(float(row2["Volume"]) - 500.00)
                        prodaja_MWminus400.append(float(row2["Volume"]) - 400.00)
                        prodaja_MWminus300.append(float(row2["Volume"]) - 300.00)
                        prodaja_MWminus200.append(float(row2["Volume"]) - 200.00)
                        prodaja_MWminus100.append(float(row2["Volume"]) - 100.00)
                        prodaja_MWplus100.append(float(row2["Volume"]) + 100.00)
                        prodaja_MWplus200.append(float(row2["Volume"]) + 200.00)
                        prodaja_MWplus300.append(float(row2["Volume"]) + 300.00)
                        prodaja_MWplus400.append(float(row2["Volume"]) + 400.00)
                        prodaja_MWplus500.append(float(row2["Volume"]) + 500.00)
                        prodaja_MW.append(float(row2["Volume"]))
                        try:
                            row2 = next(reader2)
                        except StopIteration:
                            break
                    if i == za_koji_sat - 1:
                        cene[i], koliko_fali[i] = intersect(kupovina_MW,kupovina_cena,prodaja_MW,prodaja_cena)
                        d.update({str(datum) + "Buy Volume": kupovina_MW})
                        c.append(str(datum) + "Buy Volume")
                        d.update({str(datum) + "Buy Price": kupovina_cena})
                        c.append(str(datum) + "Buy Price")
                        d.update({str(datum) + "Sell Volume": prodaja_MW})
                        c.append(str(datum) + "Sell Volume")
                        d.update({str(datum) + "Sell Price": prodaja_cena})
                        c.append(str(datum) + "Sell Price")
                        plt.plot(kupovina_MW, kupovina_cena, label = str(datum) + "Buy", marker='o', c = colors1[daaaaa])
                        plt.plot(prodaja_MW, prodaja_cena, label = str(datum) + "Sell", marker='o', c = colors2[daaaaa])

        daaaaa += 1
        dan1,mesec1,god1 = next_day(dan1, mesec1, god1)



    plt.xlim(koliko_fali[za_koji_sat - 1] - 0.3 * koliko_fali[za_koji_sat - 1], koliko_fali[za_koji_sat - 1] + 0.3 * koliko_fali[za_koji_sat - 1])
    plt.ylim(cene[za_koji_sat - 1] - 0.5 * cene[za_koji_sat - 1],cene[za_koji_sat - 1] + 0.5 * cene[za_koji_sat - 1])
    plt.title('H' + str(za_koji_sat))
    plt.xlabel("Volume [MW]")
    plt.ylabel("Price [EUR/MWh]")
    plt.legend()
    plt.savefig("H" + str(za_koji_sat) + "_HUPX.jpg", dpi = 300)

    d = pad_dict_list(d, '')
    df1 = pd.DataFrame(data=d, columns=c)
    df1.to_excel("SELL-BUY_HUPX_H" + str(za_koji_sat)+".xlsx",  encoding = 'utf8', index=False)
    
    plt.close()
    






skidanje(za_koji_sat = 3)
skidanje(za_koji_sat = 12)
skidanje(za_koji_sat = 20)


