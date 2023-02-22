from subprocess import call
import time
import csv
import os.path
import datetime
import numpy as np
import zipfile
import pysftp
from datetime import date, timedelta
import pandas as pd

import os
import shutil

    
def brisanje_space(df):
    df['Timestamp'] = df['Timestamp'].str.strip()
    return df

fo = open('putanje-price.txt')
putanja_dl =  fo.readline()[10:-1]
putanja_a = fo.readline()[10:-1]
putanja_t = fo.readline()[6:-1]
putanja_o = fo.readline()[8:-1]
userr = fo.readline()[6:-1]
passw = fo.readline()[6:-1]
    
if not os.path.exists(putanja_dl[:-1]):
    os.mkdir(putanja_dl[:-1])
if not os.path.exists(putanja_a[:-1]):
    os.mkdir(putanja_a[:-1])
if not os.path.exists(putanja_t[:-1]):
    os.mkdir(putanja_t[:-1])
if not os.path.exists(putanja_o[:-1]):
    os.mkdir(putanja_o[:-1])
    
fo.close()


def napravi_source_csv(drzava1, drzava2, year, month, day, drz, kod, rezolucija):
    
    g = year
    m = month
    datumm = format(g, '04d') + '-' + format(m, '02d') + '-' + format(day, '02d')
    if not os.path.exists(str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.zip"):
        host = 'sftp-transparency.entsoe.eu'
        user = userr
        password = passw
            
        # Loads .ssh/known_hosts
        cnopts = pysftp.CnOpts(knownhosts= putanja_dl[:-9] + '.ssh\\known_hosts')
        hostkeys = None
            
        if cnopts.hostkeys.lookup(host) == None:
            # Backup loaded .ssh/known_hosts file
            hostkeys = cnopts.hostkeys
            # And do not verify host key of the new host
            cnopts.hostkeys = None
        with pysftp.Connection(host, username = user, password = password, cnopts = cnopts, port = 22) as vf:
            if hostkeys != None:
                hostkeys.add(host, vf.remote_server_key.get_name(), vf.remote_server_key)
                hostkeys.save(pysftp.helpers.known_hosts())
            vf.get("/TP_export/zip/DayAheadPrices_12.1.D/" + str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.zip")
    
    with zipfile.ZipFile(str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.zip", 'r') as zip_ref:
        zip_ref.extractall(putanja_a)
    
                

    vt =pd.read_csv(str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.csv", encoding = 'utf-8', sep = '\t')
    
    year = g
    month = m
    day = day
    
    odgovor, br1, br2, o = datum_izmedju(year, month, day, drz)
    if o[0] == 's':
        odgovor = int(odgovor)
    else:
        odgovor = int(odgovor)
    dani = 0
    fout = open(putanja_t + 'source.csv', 'w', newline='')
    wtr= csv.writer( fout )
    wtr.writerow(('x','y'))
    if br1 == 0 and month == 3:
        odgovor -= 1
    if br1 == 0 and month == 10:
        odgovor += 1
    if rezolucija == 24:
        vt_jedan_smer = vt.query('ResolutionCode == "PT60M" & AreaCode == "' + drzava1 + '" & AreaTypeCode == "' + kod + '"')
        vt_jedan_smer = vt_jedan_smer[vt_jedan_smer["DateTime"].str.contains(datumm)]
    
        if odgovor > 0:
            
            year, month, day = str((date(year, month, day)-timedelta(1))).split('-')
            g = int(year)
            m = int(month)
            day = int(day)
            datumm = format(g, '04d') + '-' + format(m, '02d') + '-' + format(day, '02d')
            if not os.path.exists(str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.zip"):
                host = 'sftp-transparency.entsoe.eu'
                user = userr
                password = passw
                    
                # Loads .ssh/known_hosts
                cnopts = pysftp.CnOpts(knownhosts= putanja_dl[:-9] + '.ssh\\known_hosts')
                hostkeys = None
                    
                if cnopts.hostkeys.lookup(host) == None:
                    # Backup loaded .ssh/known_hosts file
                    hostkeys = cnopts.hostkeys
                    # And do not verify host key of the new host
                    cnopts.hostkeys = None
                with pysftp.Connection(host, username = user, password = password, cnopts = cnopts, port = 22) as vf:
                    if hostkeys != None:
                        hostkeys.add(host, vf.remote_server_key.get_name(), vf.remote_server_key)
                        hostkeys.save(pysftp.helpers.known_hosts())
                    vf.get("/TP_export/zip/DayAheadPrices_12.1.D/" + str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.zip")
            
            with zipfile.ZipFile(str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.zip", 'r') as zip_ref:
                zip_ref.extractall(putanja_a)
            
                        
        
            vt2 =pd.read_csv(str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.csv", encoding = 'utf-8', sep = '\t')
            
            vt2_jedan_smer = vt2.query('ResolutionCode == "PT60M" & AreaCode == "' + drzava1 + '" & AreaTypeCode == "' + kod + '"')
            vt2_jedan_smer = vt2_jedan_smer[vt2_jedan_smer["DateTime"].str.contains(datumm)]
            
            year = int(year)
            month = int(month)
            day = int(day)
            for i in range(odgovor):
                if month == 10 and i == odgovor - 1:
                    continue
                
                red = []
                red.append(dani)
                
                nasao = False
                for j in range(len(vt2_jedan_smer['DateTime'])):
                    if vt2_jedan_smer['DateTime'][vt2_jedan_smer['DateTime'].keys()[j]] == "%04d-%02d-%02d %02d:00:00.000"%(year,month,day,((24 - odgovor) + i)%24):
                        total = (vt2_jedan_smer['Price'][vt2_jedan_smer['DateTime'].keys()[j]])
                        nasao = True
                if not nasao:
                    total = 'N/A'
                red.append(total)
                
                
                

                
                
                wtr.writerow(red)
                dani += 1
            year, month, day = str((date(year, month, day)+timedelta(1))).split('-')
            year = int(year)
            month = int(month)
            day = int(day)
        if br1 == 0 and month == 10:
            odgovor -= 1
        for i in range(24 - odgovor):
            
            red = []
            red.append(dani)
            
            
            nasao = False
            for j in range(len(vt_jedan_smer['DateTime'])):
                if vt_jedan_smer['DateTime'][vt_jedan_smer['DateTime'].keys()[j]] == "%04d-%02d-%02d %02d:00:00.000"%(year,month,day,i%24):
                    total = (vt_jedan_smer['Price'][vt_jedan_smer['DateTime'].keys()[j]])
                    nasao = True
            if not nasao:
                total = 'N/A'
            red.append(total)
            
            
            
                
            
            
            wtr.writerow(red)
            dani += 1
            if dani == 24:
                break
            
    
    
    if rezolucija == 48:
        vt_jedan_smer = vt.query('ResolutionCode == "PT30M" & AreaCode == "' + drzava1 + '" & AreaTypeCode == "' + kod + '"')
        vt_jedan_smer = vt_jedan_smer[vt_jedan_smer["DateTime"].str.contains(datumm)]
    
        if odgovor > 0:
            year, month, day = str((date(year, month, day)-timedelta(1))).split('-')
            g = int(year)
            m = int(month)
            day = int(day)
            datumm = format(g, '04d') + '-' + format(m, '02d') + '-' + format(day, '02d')
            if not os.path.exists(str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.zip"):
                host = 'sftp-transparency.entsoe.eu'
                user = userr
                password = passw
                    
                # Loads .ssh/known_hosts
                cnopts = pysftp.CnOpts(knownhosts= putanja_dl[:-9] + '.ssh\\known_hosts')
                hostkeys = None
                    
                if cnopts.hostkeys.lookup(host) == None:
                    # Backup loaded .ssh/known_hosts file
                    hostkeys = cnopts.hostkeys
                    # And do not verify host key of the new host
                    cnopts.hostkeys = None
                with pysftp.Connection(host, username = user, password = password, cnopts = cnopts, port = 22) as vf:
                    if hostkeys != None:
                        hostkeys.add(host, vf.remote_server_key.get_name(), vf.remote_server_key)
                        hostkeys.save(pysftp.helpers.known_hosts())
                    vf.get("/TP_export/zip/DayAheadPrices_12.1.D/" + str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.zip")
            
            with zipfile.ZipFile(str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.zip", 'r') as zip_ref:
                zip_ref.extractall(putanja_a)
            
            
                        
        
            vt2 =pd.read_csv(str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.csv", encoding = 'utf-8', sep = '\t')
            
            vt2_jedan_smer = vt2.query('ResolutionCode == "PT30M" & AreaCode == "' + drzava1 + '" & AreaTypeCode == "' + kod + '"')
            vt2_jedan_smer = vt2_jedan_smer[vt2_jedan_smer["DateTime"].str.contains(datumm)]
            
            year = int(year)
            month = int(month)
            day = int(day)
            minuti = 0
            for i in range(odgovor * 2):
                if month == 10 and i == odgovor - 1:
                    continue
                
                red = []
                red.append(dani)
                
                nasao = False
                for j in range(len(vt2_jedan_smer['DateTime'])):
                    if vt2_jedan_smer['DateTime'][vt2_jedan_smer['DateTime'].keys()[j]] == "%04d-%02d-%02d %02d:%02d:00.000"%(year,month,day,((24 - odgovor) + int(i/2))%24, minuti):
                        total = (vt2_jedan_smer['Price'][vt2_jedan_smer['DateTime'].keys()[j]])
                        nasao = True
                if not nasao:
                    total = 'N/A'
                red.append(total)
                
                
                

                
                if minuti > 0:
                    minuti = 0
                else:
                    minuti = 30
                print(red, drzava1)
                wtr.writerow(red)
                dani += 1
            year, month, day = str((date(year, month, day)+timedelta(1))).split('-')
            year = int(year)
            month = int(month)
            day = int(day)
        if br1 == 0 and month == 10:
            odgovor -= 1
        for i in range(48 - 2 * odgovor):
            
            red = []
            red.append(dani)
            
            
            nasao = False
            for j in range(len(vt_jedan_smer['DateTime'])):
                if vt_jedan_smer['DateTime'][vt_jedan_smer['DateTime'].keys()[j]] == "%04d-%02d-%02d %02d:%02d:00.000"%(year,month,day,(int(i/2))%24, minuti):
                    total = (vt_jedan_smer['Price'][vt_jedan_smer['DateTime'].keys()[j]])
                    nasao = True
            if not nasao:
                total = 'N/A'
            red.append(total)
            
            
            
            
            if minuti > 0:
                minuti = 0
            else:
                minuti = 30
            wtr.writerow(red)
            dani += 1
            if dani == 48:
                break
    
    
    if rezolucija == 96:
        vt_jedan_smer = vt.query('ResolutionCode == "PT15M" & AreaCode == "' + drzava1 + '" & AreaTypeCode == "' + kod + '"')
        vt_jedan_smer = vt_jedan_smer[vt_jedan_smer["DateTime"].str.contains(datumm)]
    
        if odgovor > 0:
            year, month, day = str((date(year, month, day)-timedelta(1))).split('-')
            g = int(year)
            m = int(month)
            day = int(day)
            datumm = format(g, '04d') + '-' + format(m, '02d') + '-' + format(day, '02d')
            if not os.path.exists(str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.zip"):
                host = 'sftp-transparency.entsoe.eu'
                user = userr
                password = passw
                    
                # Loads .ssh/known_hosts
                cnopts = pysftp.CnOpts(knownhosts= putanja_dl[:-9] + '.ssh\\known_hosts')
                hostkeys = None
                    
                if cnopts.hostkeys.lookup(host) == None:
                    # Backup loaded .ssh/known_hosts file
                    hostkeys = cnopts.hostkeys
                    # And do not verify host key of the new host
                    cnopts.hostkeys = None
                with pysftp.Connection(host, username = user, password = password, cnopts = cnopts, port = 22) as vf:
                    if hostkeys != None:
                        hostkeys.add(host, vf.remote_server_key.get_name(), vf.remote_server_key)
                        hostkeys.save(pysftp.helpers.known_hosts())
                    vf.get("/TP_export/zip/DayAheadPrices_12.1.D/" + str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.zip")
            
            with zipfile.ZipFile(str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.zip", 'r') as zip_ref:
                zip_ref.extractall(putanja_a)
            
                        
        
            vt2 =pd.read_csv(str(g) + "_" + format(m, '02d') + "_DayAheadPrices_12.1.D.csv", encoding = 'utf-8', sep = '\t')
            
            vt2_jedan_smer = vt2.query('ResolutionCode == "PT15M" & AreaCode == "' + drzava1 + '" & AreaTypeCode == "' + kod + '"')
            vt2_jedan_smer = vt2_jedan_smer[vt2_jedan_smer["DateTime"].str.contains(datumm)]
            
            year = int(year)
            month = int(month)
            day = int(day)
            minuti = 0
            for i in range(odgovor * 4):
                if month == 10 and i == odgovor - 1:
                    continue
                
                red = []
                red.append(dani)
                
                nasao = False
                for j in range(len(vt2_jedan_smer['DateTime'])):
                    if vt2_jedan_smer['DateTime'][vt2_jedan_smer['DateTime'].keys()[j]] == "%04d-%02d-%02d %02d:%02d:00.000"%(year,month,day,((24 - odgovor) + int(i/4))%24, minuti):
                        total = (vt2_jedan_smer['Price'][vt2_jedan_smer['DateTime'].keys()[j]])
                        nasao = True
                if not nasao:
                    total = 'N/A'
                red.append(total)
                
                

                
                if minuti == 0:
                    minuti = 15
                elif minuti == 15:
                    minuti = 30
                elif minuti == 30:
                    minuti = 45
                else:
                    minuti = 0
                wtr.writerow(red)
                dani += 1
            year, month, day = str((date(year, month, day)+timedelta(1))).split('-')
            year = int(year)
            month = int(month)
            day = int(day)
        if br1 == 0 and month == 10:
            odgovor -= 1
        for i in range(96 - 4 * odgovor):
            
            red = []
            red.append(dani)
            
            
            nasao = False
            for j in range(len(vt_jedan_smer['DateTime'])):
                if vt_jedan_smer['DateTime'][vt_jedan_smer['DateTime'].keys()[j]] == "%04d-%02d-%02d %02d:%02d:00.000"%(year,month,day,(int(i/4))%24, minuti):
                    total = (vt_jedan_smer['Price'][vt_jedan_smer['DateTime'].keys()[j]])
                    nasao = True
            if not nasao:
                total = 'N/A'
            red.append(total)
            
            
            
                
            
            if minuti == 0:
                minuti = 15
            elif minuti == 15:
                minuti = 30
            elif minuti == 30:
                minuti = 45
            else:
                minuti = 0
            wtr.writerow(red)
            dani += 1
            if dani == 96:
                break
    fout.close()
  
def datum_izmedju(g, m, d, drz):
    
    d0 = date(g, m, d)
    f = open('time-convert.txt')
    line = f.readline()
    line = f.readline()
    line = f.readline()
    while '*' not in line:
        l = line.split()
        d1 = date(int(l[0].split('.')[2]), int(l[0].split('.')[1]), int(l[0].split('.')[0]))
        d2 = date(int(l[3].split('.')[2]), int(l[3].split('.')[1]), int(l[3].split('.')[0]))
        br_dana1 = (d1 - d0).days
        br_dana2 = (d2 - d0).days
        if br_dana1*br_dana2 < 0 or br_dana1 == 0:
            br1 = br_dana1
            br2 = br_dana2
            odgovor = l[5][1:-1]
        line = f.readline()
    line = f.readline()
    while line:
        if drz in line[0:2]:
            leto_zima = line.split(':')[1].split(', ')
            if odgovor[0] == 's':
                odgovor2 = leto_zima[0][6:]
            else:
                odgovor2 = leto_zima[1][6:]
        line = f.readline()
    f.close()
    return odgovor2, br1, br2, odgovor




start_time = time.time()
def brisi_sve_csv(f):
    import os
    test = os.listdir(f)
    for item in test:
        if item.endswith("DayAheadPrices_12.1.D.csv") or item.endswith("DayAheadPrices_12.1.D.zip"):
            os.remove(os.path.join(f, item))
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
def skidanje():
    brisi_sve_csv(putanja_dl)
    brisi_sve_csv(putanja_a)
    filepath = 'Prices.txt'
    with open(filepath) as fp:
       line = fp.readline()
       line = line.replace('\n','')
       if "Auto" in line:
           auto = 1
       else:
           auto = 0
       cnt = 1
       line = fp.readline()
       while cnt < 5:
           

           if (cnt == 1):
               line = line.replace('-', ' ')
               dan1 = int(line[0] + line[1])
               mesec1 = int(line[3] + line[4])
               god1 = int(line[6] + line[7] + line[8] + line[9])
               daaa1 = datetime.date(god1, mesec1, dan1) + datetime.timedelta(days= -1)
               dan1 = daaa1.day
               mesec1 = daaa1.month
               god1 = daaa1.year
               startp = 100000000 * god1 + mesec1 * 1000000 + dan1 * 10000
               datum1 = "%02d.%02d.%04d"%(dan1,mesec1,god1)
               datum1 = datum1.replace(' ', '')


           if (cnt == 2):
               line = line.replace(':', ' ')
               sat1 = int(line[0] + line[1])
               min1 = int(line[3] + line[4])
               startp += sat1 * 100 + min1

           if (cnt == 3):
               line = line.replace('-', ' ')
               dan2 = int(line[0] + line[1])
               mesec2 = int(line[3] + line[4])
               god2 = int(line[6] + line[7] + line[8] + line[9])
               daaa2 = datetime.date(god2, mesec2, dan2) + datetime.timedelta(days=1)
               dan2 = daaa2.day
               mesec2 = daaa2.month
               god2 = daaa2.year
               endp = 100000000 * god2 + mesec2 * 1000000 + dan2 * 10000
               datum2 = "%02d.%02d.%04d"%(dan2,mesec2,god2)
               datum2 = datum2.replace(' ', '')

           if (cnt == 4):
               line = line.replace(':', ' ')
               sat2 = int(line[0] + line[1])
               min2 = int(line[3] + line[4])
               endp += sat2 * 100 + min2

           cnt += 1
           line = fp.readline()
    fp.close()
    if auto == 1:
        broj_dani = line.split(",")
        unazad = broj_dani[0]
        unapred = broj_dani[1]
        popravka_unazad = broj_dani[2]
        popravka_unapred = broj_dani[3]
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
    
    
    
            
    
    
    

    for brdd in range(br_dana(datum1, datum2).days):
        k1 = 1
        k2 = 1
        k3 = 1
        broj_prvih = 0
        fp.close()
        fp = open(filepath)
        line = fp.readline()
        cnt = 1
        heder = open(putanja_t + "heder", "w")

        niz_opcija4a = []
        niz_opcija4b = []
        niz_opcija5 = []
        niz_indeksi = []
        zone = []
        while line:
           dan2, mesec2, god2 = next_day(dan1, mesec1, god1)
           if (cnt == 16):
               line1b = 'XXX,X'
               line1a = 'XXX,X'
               broj_prvih += 1
               drzava = line.replace('\n', '')

           if (cnt > 16 and cnt < 100):
               if (line[0] != '*'):
                   if 'A-CTA' in line:
                       kodA = 'CTA'
                       line = fp.readline()
                       drzavaA = line.replace('\n','')
                       line = fp.readline()
                       drzavaA2 = line.replace('\n','')
                       line = fp.readline()
                       drzavaA3 = line.replace('\n','')
                   if 'B-BZN' in line:
                       kodB = 'BZN'
                       line = fp.readline()
                       drzavaB = line.replace('\n','')
                       line = fp.readline()
                       drzavaB2 = line.replace('\n','')
                       line = fp.readline()
                       drzavaB3 = line.replace('\n','')
                   if 'C-CTY' in line:
                       kodC = 'CTY'
                       line = fp.readline()
                       drzavaC = line.replace('\n','')
                       line = fp.readline()
                       drzavaC2 = line.replace('\n','')
                       line = fp.readline()
                       drzavaC3 = line.replace('\n','')
                   if cnt == 22:
                       line = line.replace('\n', '')
                       osnova_h = line[0:2]
                       line1b = fp.readline()
                       sifra2 = line1b.split(',')[1]
                       sifra2 = sifra2.replace('\n', '')
                       zona = line1b.split(',')[2]
                       zona = zona.replace('\n', '')

                       if sifra2 != 'X':
                           print (line, '\t',file = heder, end = '')
                       line2b = fp.readline()
                       line3b = fp.readline()
                       line4b = fp.readline()
                       line5b = fp.readline()
                       line6b = fp.readline()
                       line = fp.readline()
                       if (line[0] != '*'):
                           line = line.replace('\n', '')
                           line1a = fp.readline()
                           sifra1 = line1a.split(',')[1]
                           sifra1 = sifra1.replace('\n', '')
                           zona = line1a.split(',')[2]
                           zona = zona.replace('\n', '')

                           
                           line2a = fp.readline()
                           line3a = fp.readline()
                           line4a = fp.readline()
                           line5a = fp.readline()
                           line6a = fp.readline()
                           line = fp.readline()
                           if (line[0] == '*' and len(line) > 3):
                               cnt = 100
                           else:
                               if line[0] =='*':
                                   cnt = 15
                       else:
                           if (len(line) > 3):
                               cnt = 100
                           else:
                               cnt = 15


               else:
                   if (len(line) > 3):
                       cnt = 100
                   else:
                       cnt = 15
               if cnt < 22 and cnt > 16:
                   cnt += 1
                   line = fp.readline()
                   continue

               if sifra1 == 'X' and sifra2 == 'X':
                   line = fp.readline()
                   cnt += 1
                   continue
               if sifra2 != 'X':
                   if line5b[0] == 'N':
                       niz_opcija4b.append(0)
                       niz_opcija4a.append(0)
                   else:
                       niz_opcija4b.append(int(line5b.split(',')[1]))
                       niz_opcija4a.append(int(line5a.split(',')[1]))
               if sifra1 != 'X':
                   if line5a[0] == 'N':
                       niz_opcija4a.append(0)
                       niz_opcija4b.append(0)
                   else:
                       niz_opcija4a.append(int(line5a.split(',')[1]))
                       niz_opcija4b.append(int(line5b.split(',')[1]))
                   if line6a[0] == 'N' or sifra2 == 'X':
                       niz_opcija5.append(0)
                       niz_indeksi.append([-1, -1])
                   else:
                       niz_opcija5.append(int(line6a.split(',')[1]))
                       niz_indeksi.append([k1,k2])
               if sifra2 != 'X':
                   if line5b[0] == 'N':
                       niz_opcija4b.append(0)
                       niz_opcija4a.append(0)
                   else:
                       niz_opcija4b.append(int(line5b.split(',')[1]))
                       niz_opcija4a.append(int(line5a.split(',')[1]))

               datum = "%02d.%02d.%04d"%(dan1,mesec1,god1)
               datum = datum.replace(' ', '')
               print(datum, "PRICE")
               indika = 0
               savedindika = -1
               lastindika = -1
               sta_skida_a = line4a[0]
               sta_skida_b = line4b[0]
               if zona in 'UTC':

                   if sifra2 != 'X':
                       zone.append(-2)
               if zona in 'WET':

                   if sifra2 != 'X':
                       zone.append(-1)
               if zona in 'CET':

                   if sifra2 != 'X':
                       zone.append(0)
               if zona in 'EET':

                   if sifra2 != 'X':
                       zone.append(1)
               if zona in 'GET':
          

                   if sifra2 != 'X':
                       zone.append(2)
               if line1a[0] != 'Y' and line1b[0] != 'Y':
                   indika = 100
               while indika < len(line3a) - 1:

                   if sifra1 != 'X':
                       if line3a[indika] == 'A':
                           kod = kodA
                           drzava = drzavaA
                           drzava2 = drzavaA2
                           drzava3 = drzavaA3
                       if line3a[indika] == 'B':
                           kod = kodB
                           drzava = drzavaB
                           drzava2 = drzavaB2
                           drzava3 = drzavaB3
                       if line3a[indika] == 'C':
                           kod = kodC
                           drzava = drzavaC
                           drzava2 = drzavaC2
                           drzava3 = drzavaC3
                   else:
                       if line3b[indika] == 'A':
                           kod = kodA
                           drzava = drzavaA
                           drzava2 = drzavaA2
                           drzava3 = drzavaA3
                       if line3b[indika] == 'B':
                           kod = kodB
                           drzava = drzavaB
                           drzava2 = drzavaB2
                           drzava3 = drzavaB3
                       if line3b[indika] == 'C':
                           kod = kodC
                           drzava = drzavaC
                           drzava2 = drzavaC2
                           drzava3 = drzavaC3
                   
                   napravi_source_csv(drzava3, drzava2, god1, mesec1, dan1, osnova_h, kod, int(line2b[:2]))
                   
                   
                   
                  
                  
                   if(sifra1 != 'X' and line2a[0] == '4') or (sifra2 != 'X' and line2b[0] == '4'):
    
                       with open(putanja_t + "source.csv","r") as obrada:
                           rdr= csv.reader( obrada )
                           with open(putanja_t + str(k1) + "_" + str(indika) + ".csv","w", newline='') as out_o:
                               wtr= csv.writer( out_o )
                               
                               i = -1
                               r2 = 0
                               
                               brojnaf = 0
                               brojna = 0
                               prethodni_sat = ''
                               for r in rdr:
                                   if prethodni_sat == r[0]:
                                       continue
                                   prethodni_sat = r[0]
                                   
                                   
                                   if i == -1:
                                           
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'Y':
                                           wtr.writerow( (r[0], r[1]) )
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'N':
                                           if sifra2 == 'X':
                                               wtr.writerow( (r[0], r[1]) )
                                           else: 
                                               wtr.writerow( (r[0], sifra2) )
                                       
                                       if line1a[0] == 'N' and line1b[0] == 'Y':
                                           if sifra1 == 'X':
                                               wtr.writerow( (r[0], r[1]) )
                                           else:
                                               wtr.writerow( (r[0], sifra1) )
                                           
                                       i += 1
                                       continue
                                   datumu = "%04d.%02d.%02d %02d:%02d:%02d"%(god1,mesec1,dan1,int(i / 2), 0, 0)
                                   if (i + 1) % 2 == 1 and line2a[3] == '1':
                                       
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'Y':
                                           wtr.writerow( (datumu, r[1]) )
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'N':
                                           if sifra2 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else: 
                                               wtr.writerow( (datumu, sifra2) )
                                       
                                       if line1a[0] == 'N' and line1b[0] == 'Y':
                                           if sifra1 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else:
                                               wtr.writerow( (datumu, sifra1) )
                                           
                                       
                                  
                                   if (i + 1) % 2 == 0 and line2a[3] == '5':
                                      
                                       for mmm in range(1):
                                           if r[mmm + 1] == 'n/e' or r[mmm + 1] == 'N/A' or r[mmm + 1] == "" or r[mmm + 1] == "-":
                                               r[mmm + 1]= -100000
                                           else:
                                               r[mmm + 1] = float(r[mmm + 1])
                                       r2 += r[1]
                                       
                                       if r2 == -1:
                                           brojnaf += 1

                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'Y':
                                           wtr.writerow( (datumu, r2 / 2.0) )
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'N':
                                           if sifra2 == 'X':
                                               wtr.writerow( (datumu, r2 / 2.0) )
                                           else: 
                                               wtr.writerow( (datumu, sifra2) )
                                       
                                       if line1a[0] == 'N' and line1b[0] == 'Y':
                                           if sifra1 == 'X':
                                               wtr.writerow( (datumu, r2 / 2.0) )
                                           else:
                                               wtr.writerow( (datumu, sifra1) )
                                       r2 = 0
                                       
                                       i += 1
                                       
                                      
                                   if (i + 1) % 2 == 0 and line2a[3] == '2':
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'Y':
                                           wtr.writerow( (datumu, r[1]) )
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'N':
                                           if sifra2 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else: 
                                               wtr.writerow( (datumu, sifra2) )
                                       
                                       if line1a[0] == 'N' and line1b[0] == 'Y':
                                           if sifra1 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else:
                                               wtr.writerow( (datumu, sifra1) )
                                       
                                   
    
                                       
                                       i += 1
                                       continue
    
    
    
    
                                   for mmm in range(1):
                                       if r[mmm + 1] == 'n/e' or r[mmm + 1] == 'N/A' or r[mmm + 1] == "" or r[mmm + 1] == "-":
                                           r[mmm + 1]= -100000
                                       else:
                                           r[mmm + 1] = float(r[mmm + 1])
                                   r2 += r[1]
                                   
    
    
                                   i += 1
                   if(sifra1 != 'X' and line2a[0] == '9') or (sifra2 != 'X' and line2b[0] == '9'):

                       with open(putanja_t + "source.csv","r") as obrada:
                           rdr= csv.reader( obrada )
                           with open(putanja_t + str(k1) + "_" + str(indika) + ".csv","w", newline='') as out_o:
                               wtr= csv.writer( out_o )
                               
                               i = -1
                               r2 = 0
                               
                               brojnaf = 0
                               brojna = 0
                               prethodni_sat = ''
                               for r in rdr:
                                   if prethodni_sat == r[0]:
                                       continue
                                   prethodni_sat = r[0]
                                   
                                   
                                   if i == -1:
                                           
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'Y':
                                           wtr.writerow( (r[0], r[1]) )
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'N':
                                           if sifra2 == 'X':
                                               wtr.writerow( (r[0], r[1]) )
                                           else: 
                                               wtr.writerow( (r[0], sifra2) )
                                       
                                       if line1a[0] == 'N' and line1b[0] == 'Y':
                                           if sifra1 == 'X':
                                               wtr.writerow( (r[0], r[1]) )
                                           else:
                                               wtr.writerow( (r[0], sifra1) )
                                           
                                       i += 1
                                       continue
                                   datumu = "%04d.%02d.%02d %02d:%02d:%02d"%(god1,mesec1,dan1,int(i / 4), 0, 0)
                                   if (i + 1) % 4 == 1 and line2a[3] == '1':
                                       
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'Y':
                                           wtr.writerow( (datumu, r[1]) )
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'N':
                                           if sifra2 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else: 
                                               wtr.writerow( (datumu, sifra2) )
                                       
                                       if line1a[0] == 'N' and line1b[0] == 'Y':
                                           if sifra1 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else:
                                               wtr.writerow( (datumu, sifra1) )
                                           
                                   if (i + 1) % 4 == 2 and line2a[3] == '2':
                                       
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'Y':
                                           wtr.writerow( (datumu, r[1]) )
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'N':
                                           if sifra2 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else: 
                                               wtr.writerow( (datumu, sifra2) )
                                       
                                       if line1a[0] == 'N' and line1b[0] == 'Y':
                                           if sifra1 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else:
                                               wtr.writerow( (datumu, sifra1) )
                                   if (i + 1) % 4 == 3 and line2a[3] == '3':
                                       
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'Y':
                                           wtr.writerow( (datumu, r[1]) )
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'N':
                                           if sifra2 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else: 
                                               wtr.writerow( (datumu, sifra2) )
                                       
                                       if line1a[0] == 'N' and line1b[0] == 'Y':
                                           if sifra1 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else:
                                               wtr.writerow( (datumu, sifra1) )
                                  
                                   if (i + 1) % 4 == 0 and line2a[3] == '5':
                                      
                                       for mmm in range(1):
                                           if r[mmm + 1] == 'n/e' or r[mmm + 1] == 'N/A' or r[mmm + 1] == "" or r[mmm + 1] == "-":
                                               r[mmm + 1]= -100000
                                           else:
                                               r[mmm + 1] = float(r[mmm + 1])
                                       r2 += r[1]
                                       
                                       if r2 == -1:
                                           brojnaf += 1

                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'Y':
                                           wtr.writerow( (datumu, r2 / 2.0) )
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'N':
                                           if sifra2 == 'X':
                                               wtr.writerow( (datumu, r2 / 2.0) )
                                           else: 
                                               wtr.writerow( (datumu, sifra2) )
                                       
                                       if line1a[0] == 'N' and line1b[0] == 'Y':
                                           if sifra1 == 'X':
                                               wtr.writerow( (datumu, r2 / 2.0) )
                                           else:
                                               wtr.writerow( (datumu, sifra1) )
                                       r2 = 0
                                       
                                       i += 1
                                       
                                      
                                   if (i + 1) % 4 == 0 and line2a[3] == '4':
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'Y':
                                           wtr.writerow( (datumu, r[1]) )
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'N':
                                           if sifra2 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else: 
                                               wtr.writerow( (datumu, sifra2) )
                                       
                                       if line1a[0] == 'N' and line1b[0] == 'Y':
                                           if sifra1 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else:
                                               wtr.writerow( (datumu, sifra1) )
                                       
                                   
    
                                       
                                       i += 1
                                       continue
    
    
    
    
                                   for mmm in range(1):
                                       if r[mmm + 1] == 'n/e' or r[mmm + 1] == 'N/A' or r[mmm + 1] == "" or r[mmm + 1] == "-":
                                           r[mmm + 1]= -100000
                                       else:
                                           r[mmm + 1] = float(r[mmm + 1])
                                   r2 += r[1]
                                   
    
    
                                   i += 1
    
                   else:
                       if (sifra1 != 'X' and line2a[0] == '2') or (sifra2 != 'X' and line2b[0] == '2'):
                           with open(putanja_t + "source.csv","r") as source:
                               rdr= csv.reader( source )
                               with open(putanja_t + str(k1) + "_" + str(indika) + ".csv","w", newline='') as result:
                                   wtr = csv.writer( result )
                                   
                                   brojna = 0
                                   brojnaf = 0
                                   i = -1
                                   prethodni_sat = ''
                                   for r in rdr:
                                       if prethodni_sat == r[0]:
                                           continue
                                       prethodni_sat = r[0]
                                       if i == -1:
                                           
                                           
                                           
                                           if line1a[0] == 'Y' and line1b[0] == 'Y':
                                               wtr.writerow( (r[0], r[1]) )
                                           
                                           if line1a[0] == 'Y' and line1b[0] == 'N':
                                               if sifra2 == 'X':
                                                   wtr.writerow( (r[0], r[1]) )
                                               else: 
                                                   wtr.writerow( (r[0], sifra2) )
                                           
                                           if line1a[0] == 'N' and line1b[0] == 'Y':
                                               if sifra1 == 'X':
                                                   wtr.writerow( (r[0], r[1]) )
                                               else:
                                                   wtr.writerow( (r[0], sifra1) )
                                           
                                           i += 1
                                           continue
                                       datumu = "%04d.%02d.%02d %02d:%02d:%02d"%(god1,mesec1,dan1,i, 0, 0)
                                       i += 1

                                       if (r[1] == 'n/e' or r[1] == 'n/a' or r[1] == 'N/A' or r[1] == "" or r[1] == "-"):
                                           brojnaf += 1
                                       for mmm in range(1):
                                           if r[mmm + 1] == 'n/e' or r[mmm + 1] == 'N/A' or r[mmm + 1] == "" or r[mmm + 1] == "-":
                                               r[mmm + 1] = -100000
                                           else:
                                               if i != 0:
                                                   r[mmm + 1] = float(r[mmm + 1])
                                       
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'Y':
                                           wtr.writerow( (datumu, r[1]) )
                                       
                                       if line1a[0] == 'Y' and line1b[0] == 'N':
                                           if sifra2 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else: 
                                               wtr.writerow( (datumu, sifra2) )
                                       
                                       if line1a[0] == 'N' and line1b[0] == 'Y':
                                           if sifra1 == 'X':
                                               wtr.writerow( (datumu, r[1]) )
                                           else:
                                               wtr.writerow( (datumu, sifra1) )
                   
                   
                   if brojnaf != 24 and savedindika == -1:
                       savedindika = indika
                   if indika == 2 and savedindika == -1:
                       savedindika = 2
                   if brojna == 24:
                       indika += 1
                   else:
                       
                       if lastindika == -1:
                           lastindika = indika
                       if savedindika != -1:
                           indika = 10
                       else:
                           indika += 1
               
               if indika == 10 and indika != 100:
                   call(["move", putanja_t + str(k1) + "_" + str(lastindika) + ".csv", putanja_t + str(k1) + ".csv"], shell=True)
               else:
                   if lastindika == -1:
                           lastindika = indika - 1 
                   call(["move", putanja_t + str(k1) + "_" + str(lastindika) + ".csv",  putanja_t + str(k1) + ".csv"], shell=True)
               if sifra1 != 'X':
                   if indika == 100:
                       with open(putanja_t + str(k1) + ".csv", "w", newline='') as result:
                           for jk in range(25):
                               wtr = csv.writer( result )
                               datumu = "%04d.%02d.%02d %02d:%02d:%02d"%(god1,mesec1,dan1,jk - 1, 0, 0)
                              
                               wtr.writerow( (datumu, -1, -1) )
               k1 += 1
                   
                   
           line = fp.readline()
           
           cnt += 1
        
        out = open(putanja_t + "" + str(brdd) + "merge.csv","w", newline='')
        fp.close()

        print ( '',file = heder)

        heder.close()


        col = []
        h = open(putanja_t + "heder", "r")
        hi = h.readline()
        hi = hi.replace("\n", "")
        col.append('Timestamp')
        name = hi.split('\t')
        for i in range(len(name)):
            if name[i].replace(' ', '') not in col:
                col.append(name[i].replace(' ', ''))
        if (brdd == 0):

            print ( 'Timestamp\t', hi, file = out)
        h.close()

        #f = [open("{}.csv".format(x + 1),'r') for x in range(k - 1)]
        for i in range(1,25):
            f = [open(putanja_t + "{}.csv".format(x + 1),'r') for x in range(k1 - 1)]
            for j in range(k1 - 1):

                reader = csv.reader(f[j])
                ind = 0
                for row in reader:


                    if (ind != i):
                        ind += 1
                        continue
                    ind += 1
                    for l in range(len(row)):

                        if ((l !=0 and j > 0) or (l != 0) or (j == 0)):
                            print("%s\t"%(row[l].strip()), file = out, end = '')

                f[j].close()
            print('', file = out)
        out.close()
        
        
        
        dan1,mesec1,god1 = next_day(dan1, mesec1, god1)
                   
                   
        






    with open(putanja_t + 'Prices.csv', 'w') as outfile:
        for i in range(br_dana(datum1, datum2).days):
            ulaz = putanja_t + "" + str(i) + "merge.csv"
            ulaz = ulaz.replace('\r','')
            infile = open(ulaz, 'r')

            for line in infile:
                
                outfile.write(line)


    
    filepath = putanja_t + 'Prices.csv'
    v1 = pd.read_csv(putanja_t + 'Prices.csv', delimiter = '\t')
    
    for i in range(len(zone)):
        if zone[i] > 0:
            for j in range(len(v1[v1.keys()[i+1]]) - zone[i]):
                v1[v1.keys()[i+1]][j] = v1[v1.keys()[i+1]][j+zone[i]]
        if zone[i] < 0:
            for j in range(len(v1[v1.keys()[i+1]]) + zone[i]):
                v1[v1.keys()[i+1]][len(v1[v1.keys()[i+1]]) - 1 - j] = v1[v1.keys()[i+1]][len(v1[v1.keys()[i+1]]) - 1 - j+zone[i]]
    
    v1.to_csv(putanja_t + 'Prices.csv', sep = "\t", index = False)
    ex = pd.read_csv(putanja_t + 'Prices.csv', delimiter = '\t')
    ex.columns = ex.columns.str.replace(' ', '')
    col = col[:-1]
    ex = brisanje_space(ex)
    ex.to_csv(putanja_t + 'Prices.csv', sep = "\t", index = False)
    
    O4(niz_opcija4a, filepath)
    


            
            





    with open(putanja_t + 'Prices.xls', 'w') as outfile:
        ulaz = putanja_t + 'Prices.csv'
        ulaz = ulaz.replace('\r','')
        infile = open(ulaz, 'r')
        if auto != 1:
            popravka_unazad = -1
            popravka_unapred = 1
        i = 0
        for line in infile:
            if (i > 0 and i < 1 - 24 * int(popravka_unazad)) or (i > 24 * (br_dana(datum1, datum2).days - int(popravka_unapred))):
                i += 1
                continue
            i += 1
            line = line.replace('\t\n', '\n')
            outfile.write(line)
        infile.close()


    













    
    




    ex1 = pd.read_csv(putanja_t + 'Prices.xls', delimiter = '\t')
    ex1.columns = ex1.columns.str.replace(' ', '')
    ex1 = brisanje_space(ex1)
    writer = pd.ExcelWriter(putanja_o + 'Prices-final-1.xls', engine='xlsxwriter',
                        options={'strings_to_numbers': True})
    


    for r in ex1.index:
        for c in ex1.columns:
            if 'Timestamp' in c:
                ex1.at[r,c] = ex1.at[r,c].strip()
   


    ex1 = brisanje_space(ex1)
    ex1.to_excel(writer, index=False, columns = col)
    call(["del", '/Q',putanja_t + '*'], shell=True)
    writer.save()
    brisi_sve_csv(putanja_dl)
    brisi_sve_csv(putanja_a)
    if os.path.exists(putanja_t + 'TEMPLATE'):
        shutil.rmtree(putanja_t + 'TEMPLATE')
    os.mkdir(putanja_t + 'TEMPLATE')
    source = putanja_t + ''
    dest1 = putanja_t + 'TEMPLATE\\'
    
    files = os.listdir(source)
    
    for f in files:
        shutil.move(source+f, dest1)


def O3(niz, f):
    indikatori = 1
    ulaz = f
    ulaz = ulaz.replace('\r','')
    infile = open(ulaz, 'r')
    outfile = open(putanja_t + "temp", 'w', newline='')
    reader = csv.reader(infile, delimiter="\t")
    x = list(reader)
    for ii in range (len(x)):
        for jj in range(len(x[ii])):
            if jj == len(x[ii]) - 1:
                continue

            if ii <= indikatori:
                print(x[ii][jj], '\t', end = '', file = outfile)
            else:
                if jj >= 1:
                    #print(len(x), len(x[ii]), len(niz), ii, jj, x[ii][jj])
                    if (is_number(x[ii][jj]) and is_number(x[ii - 1][jj]) and niz[jj - 1] >= np.abs(float(x[ii][jj]) - float(x[ii - 1][jj]))):
                        print(float(x[ii][jj]), '\t', end = '', file = outfile)
                    else:
                        if is_number(x[ii][jj]) and (not is_number(x[ii - 1][jj]) or float(x[ii - 1][jj])< -99999):
                            print(float(x[ii][jj]), '\t', end = '', file = outfile)
                        else:
                            print(0, '\t', end = '', file = outfile)
                else:
                    print(x[ii][jj], '\t', end = '', file = outfile)
                           

        print('', file = outfile)
    outfile.close()
    infile.close()
    shutil.move(putanja_t + 'temp',  f)
    return


def O4(niz, f):
    indikatori = 1
    ulaz = f
    ulaz = ulaz.replace('\r','')
    infile = open(ulaz, 'r')
    outfile = open(putanja_t + 'temp', 'w')
    reader = csv.reader(infile, delimiter="\t")
    x = list(reader)
    for ii in range (len(x)):
        for jj in range(len(x[ii])):
            if jj == len(x[ii]) - 1:
                continue
            if ii <= indikatori:
                if ii == 1 and is_number(x[ii][jj]) and float(x[ii][jj])< -99999:
                    print ('N/A', '\t', file = outfile, end = '')
                else:
                    print( x[ii][jj], '\t',file = outfile, end = '')
            else:
                if jj >= 1:
                    if (niz[jj - 1] >= 1 and ii < len(x) - 1 and (float(x[ii][jj])< -99999 and float(x[ii - 1][jj]) >= 0 and float(x[ii + 1][jj]) >= 0)):
                        
                        print( 0.5 * (float(x[ii - 1][jj]) + float(x[ii + 1][jj])), '\t',file = outfile, end = '')
                    else:
                        if niz[jj - 1] >= 2 and ii < len(x) - 2 and float(x[ii][jj])< -99999 and float(x[ii - 1][jj]) >= 0 and float(x[ii + 1][jj])< -99999 and float(x[ii + 2][jj]) >= 0:
                            
                            print (0.5 * (float(x[ii - 1][jj]) + float(x[ii + 2][jj])), '\t',file = outfile, end = '')
                        else:
                            if (niz[jj - 1] >= 3 and ii < len(x) - 3 and float(x[ii][jj])< -99999 and float(x[ii - 1][jj]) >= 0 and float(x[ii + 1][jj])< -99999 and float(x[ii + 2][jj])< -99999 and float(x[ii + 3][jj]) >= 0):
                                
                                print ( 0.5 * (float(x[ii - 1][jj]) + float(x[ii + 3][jj])), '\t',file = outfile, end = '')
                            else:
                                if is_number(x[ii][jj]) and float(x[ii][jj])< -99999:
                                    print ('N/A', '\t',file = outfile, end = '')
                                else:
                                    print (x[ii][jj], '\t',file = outfile, end = '')
                else:
                    if is_number(x[ii][jj]) and float(x[ii][jj])< -99999:
                        print ('N/A', '\t',file = outfile, end = '')
                    else:
                        print (x[ii][jj], '\t',file = outfile, end = '')

        print ( '', file =outfile)
    outfile.close()
    infile.close()
    call(["move", putanja_t + 'temp',  f], shell=True)
    return

def O5(f1, f2, indeksi):
    
    if len(indeksi) == 0:
        return
    indikatori = 0
    ulaz = f1
    ulaz2 = f2
    ulaz = ulaz.replace('\r','')
    ulaz2 = ulaz2.replace('\r','')
    infile = open(ulaz, 'r')
    infile2 = open(ulaz2, 'r')
    outfile = open(putanja_t + "temp", 'w', newline='')
    outfile2 = open(putanja_t + "temp2", 'w', newline='')
    reader = csv.reader(infile, delimiter="\t")
    reader2 = csv.reader(infile2, delimiter="\t")
    x = list(reader)
    y = list(reader2)
    
    for ii in range (len(x)):
        for jj in range(len(x[ii])):
            if jj == len(x[ii]) - 1:
                continue

            if ii <= indikatori:
                if jj > 0 and indeksi[jj - 1][0] == -2:
                    continue
                print(x[ii][jj], '\t', end = '', file = outfile)
            else:
                if jj >= 1:
                    if indeksi[jj - 1][0] == -2:
                        continue
                    if indeksi[jj - 1][0]< 0:
                        print(0, '\t', end = '', file = outfile)
                    else:
                        if float(x[ii][jj]) != 0:
                            print(x[ii][jj], '\t', end = '', file = outfile)
                        else:
                            if float(y[ii][jj])< 0:
                                if ii > 25:
                                    x[ii][jj] = (float(x[ii - 25][jj]) + float(x[ii - 24][jj]) + float(x[ii - 23][jj]) + 3 * float(x[ii - 1][jj])) / 6.0 
                                    print((float(x[ii - 25][jj]) + float(x[ii - 24][jj]) + float(x[ii - 23][jj]) + 3 * float(x[ii - 1][jj])) / 6.0, '\t', end = '', file = outfile)
                                else:
                                    if ii >= 25:
                                        x[ii][jj] = x[ii - 24][jj]
                                        print(x[ii - 24][jj], '\t', end = '', file = outfile)
                                    else:
                                        if is_number(x[ii - 1][jj]):
                                            x[ii][jj] = x[ii - 1][jj]
                                            print(x[ii - 1][jj], '\t', end = '', file = outfile)
                                        else:
                                            print(x[ii][jj], '\t', end = '', file = outfile)
                                        
                            else:
                                if ii > 1 and float(x[ii - 1][jj]) > 0 and float(y[ii - 1][jj]) > 0:
                                    x[ii][jj] = float(y[ii][jj]) + (float(x[ii - 1][jj]) - float(y[ii - 1][jj])) / float(y[ii - 1][jj]) * float(y[ii][jj])
                                    print(float(y[ii][jj]) + (float(x[ii - 1][jj]) - float(y[ii - 1][jj])) / float(y[ii - 1][jj]) * float(y[ii][jj]), '\t', end = '', file = outfile)
                                else:
                                    if ii < len(x) - 1 and float(x[ii + 1][jj]) > 0 and float(y[ii + 1][jj]) > 0:
                                        x[ii][jj] = float(y[ii][jj]) + (float(x[ii + 1][jj]) - float(y[ii + 1][jj])) / float(y[ii + 1][jj]) * float(y[ii][jj])
                                        print(float(y[ii][jj]) + (float(x[ii + 1][jj]) - float(y[ii + 1][jj])) / float(y[ii + 1][jj]) * float(y[ii][jj]), '\t', end = '', file = outfile)
                                    else:
                                        x[ii][jj] = y[ii][jj]
                                        print(y[ii][jj], '\t', end = '', file = outfile)
                else:
                    if is_number(x[ii][jj]) and float(x[ii][jj])< -99999:
                        print('N/A', '\t', end = '', file = outfile)
                    else:
                        print(x[ii][jj], '\t', end = '', file = outfile)
            if jj == len(y[ii]) - 1:
                continue

            if ii <= indikatori:
                if jj> 0 and indeksi[jj - 1][1] == -2:
                    continue
                print(y[ii][jj], '\t', end = '', file = outfile2)
            else:
                if jj >= 1:
                    if indeksi[jj - 1][1] == -2:
                        continue
                    if indeksi[jj - 1][1]< 0:
                        print(0, '\t', end = '', file = outfile2)
                    else:
                        if float(y[ii][jj]) != 0:
                            print(y[ii][jj], '\t', end = '', file = outfile2)
                        else:
                            if float(x[ii][jj])< -99999:
                                if ii > 25:
                                    y[ii][jj] = (float(y[ii - 25][jj]) + float(y[ii - 24][jj]) + float(y[ii - 23][jj]) + 3 * float(y[ii - 1][jj])) / 6.0 
                                    print((float(y[ii - 25][jj]) + float(y[ii - 24][jj]) + float(y[ii - 23][jj]) + 3 * float(y[ii - 1][jj])) / 6.0, '\t', end = '', file = outfile2)
                                else:
                                    if ii >= 25:
                                        y[ii][jj] = y[ii - 24][jj]
                                        print(y[ii - 24][jj], '\t', end = '', file = outfile2)
                                    else:
                                        if is_number(y[ii - 1][jj]):
                                            y[ii][jj] = y[ii - 1][jj]
                                            print(y[ii - 1][jj], '\t', end = '', file = outfile2)
                                        else:
                                            print(y[ii][jj], '\t', end = '', file = outfile2)
                                        
                            else:
                                if ii > 1 and float(y[ii - 1][jj]) > 0 and float(x[ii - 1][jj]) > 0:
                                    y[ii][jj] = float(x[ii][jj]) + (float(y[ii - 1][jj]) - float(x[ii - 1][jj])) / float(x[ii - 1][jj]) * float(x[ii][jj])
                                    print(float(x[ii][jj]) + (float(y[ii - 1][jj]) - float(x[ii - 1][jj])) / float(x[ii - 1][jj]) * float(x[ii][jj]), '\t', end = '', file = outfile2)
                                else:
                                    if ii < len(y) - 1 and float(y[ii + 1][jj]) > 0 and float(x[ii + 1][jj]) > 0:
                                        y[ii][jj] = float(x[ii][jj]) + (float(y[ii + 1][jj]) - float(x[ii + 1][jj])) / float(x[ii + 1][jj]) * float(x[ii][jj])
                                        print(float(x[ii][jj]) + (float(y[ii + 1][jj]) - float(x[ii + 1][jj])) / float(x[ii + 1][jj]) * float(x[ii][jj]), '\t', end = '', file = outfile2)
                                    else:
                                        y[ii][jj] = x[ii][jj]
                                        print(x[ii][jj], '\t', end = '', file = outfile2)
                else:
                    if is_number(y[ii][jj]) and float(y[ii][jj])< 0:
                        print('N/A', '\t', end = '', file = outfile2)
                    else:
                        print(y[ii][jj], '\t', end = '', file = outfile2)
        print( '', file = outfile)
        print( '', file = outfile2)
            
             
                    
                    
                    

            
    
            #if indeksi[ii]
            #if float(y[ii][indeksi[jj - 1][1]]) != 0:
                                       
                            
                        
        
    outfile.close()
    infile.close()
    outfile2.close()
    infile2.close()
    shutil.move(putanja_t + 'temp',  f1)
    shutil.move(putanja_t + 'temp2',  f2)
    return


#skidanje()
    
"""
try:
    brisi_sve_csv(putanja_dl)
    skidanje()
    brisi_sve_csv(putanja_dl)
    if os.path.exists(putanja_t + 'TEMPLATE'):
        shutil.rmtree(putanja_t + 'TEMPLATE')
    os.mkdir(putanja_t + 'TEMPLATE')
    source = putanja_t + ''
    dest1 = putanja_t + 'TEMPLATE\\'

    files = os.listdir(source)

    for f in files:
        shutil.move(source+f, dest1)
except Exception as e:
    logf = open(putanja_o + "LOAD-1-1 ASUS.log", "w", newline='')
    print(str(e), file = logf)
    logf.close()
    time.sleep(10)
    sys.exit()
sys.exit()"""