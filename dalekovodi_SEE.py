#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 20:49:53 2023

@author: vladimirdjosovic
"""

import pandas as pd
import numpy as np
from selenium import webdriver
import time
import os
from selenium.webdriver.common.keys import Keys
import datetime
import pandas as pd
import zipfile
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
def func(x, a, b):
    return a * x + b


def minimalni_ram(ime, sat):
    year_s = 2022
    year_e = 2022
    month_s = 11
    month_e = 11
    day_s = 18
    day_e = 19
    hour_s = 0
    hour_e = 0
    date1 = "%04d-%02d-%02d %02d:%02d"%(int(year_s), int(month_s), int(day_s), int(hour_s), 0)
    date2 = "%04d-%02d-%02d %02d:%02d"%(int(year_e), int(month_e), int(day_e), int(hour_e), 0)
    datem1 = datetime.datetime.strptime(date1, "%Y-%m-%d %H:%M")
    datem2 = datetime.datetime.strptime(date2, "%Y-%m-%d %H:%M")
    razlika_sati = datem2 - datem1
    razlika_sati = int(razlika_sati.total_seconds() / 3600)
    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.helperApps.alwaysAsk.force", False);
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.manager.showAlertOnComplete", False)
    fp.set_preference('browser.helperApps.neverAsk.saveToDisk','application/zip,application/octet-stream,application/x-zip-compressed,multipart/x-zip,application/x-rar-compressed, application/octet-stream,application/msword,application/vnd.ms-word.document.macroEnabled.12,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/rtf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,application/vnd.ms-word.document.macroEnabled.12,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/xls,application/msword,text/csv,application/vnd.ms-excel.sheet.binary.macroEnabled.12,text/plain,text/csv/xls/xlsb,application/csv,application/download,application/vnd.openxmlformats-officedocument.presentationml.presentation,application/octet-stream')
    fp.set_preference("browser.download.dir", r"C:\Users\User\Downloads")
    browser = webdriver.Firefox(executable_path=r"C:\Users\User\anaconda3\geckodriver.exe", firefox_profile=fp)
    is_loaded = False
    while not is_loaded:
        try:
            browser.get("https://publicationtool.jao.eu/core/preFinalComputation")
            WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div/div[2]/header/button')))
            is_loaded = True
        except Exception as e:
            print (e)
    #i = sat - 3
    #if i < 0:
    #    i += 24
    if sat >= 23:
        datem1 = datem1 -  datetime.timedelta(hours = 24)
    datem = datem1 + datetime.timedelta(hours = sat - 1)
    datem_plus = datem + datetime.timedelta(hours = 1)
    datum_down = "%04d-%02d-%02d %02d:%02d"%(datem.year, datem.month, datem.day, datem.hour, 0)
    datum_down_plus = "%04d-%02d-%02d %02d:%02d"%(datem_plus.year, datem_plus.month, datem_plus.day, datem_plus.hour, 0)
    
    browser.find_element_by_xpath('/html/body/div/div/div[1]/div[1]/div[4]/div/input').click()
    browser.find_element_by_xpath('/html/body/div/div/div[1]/div[1]/div[4]/div/input').send_keys(Keys.DELETE*20,datum_down[:-6],Keys.LEFT*40, Keys.DELETE*5, Keys.ENTER)
    for kk in range(sat - 1):                          
        browser.find_element_by_xpath('/html/body/div/div/div[1]/div[2]/div[3]').click()
    WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/header/button')))
    browser.find_element_by_xpath('/html/body/div/div/div[2]/header/button').click()
    WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/header/div[3]/button[2]')))
    browser.find_element_by_xpath('/html/body/div/div/div[2]/header/div[3]/button[2]').click()
    datum_zip = "%04d-%02d-%02d %02d%02d"%(datem.year, datem.month, datem.day, datem.hour, 0)
    datum_zip_plus = "%04d-%02d-%02d %02d%02d"%(datem_plus.year, datem_plus.month, datem_plus.day, datem_plus.hour, 0)
   
    
    
    
    while not os.path.exists(r"C:\\Users\\User\\Downloads\\PreFinalComputation " + datum_zip + r" - " + datum_zip_plus + r".zip"):
        time.sleep(1)
    for fname in os.listdir(r"C:\\Users\\User\\Downloads\\"):
        if fname.endswith('.part'):
            while os.path.exists(fname):
                time.sleep(1)
    
    time.sleep(5)
    with zipfile.ZipFile(r"C:\\Users\\User\\Downloads\\PreFinalComputation " + datum_zip + r" - " + datum_zip_plus + r".zip", 'r') as zip_ref:
        zip_ref.extractall(r"C:\Users\User\Downloads")
    os.remove(r"C:\\Users\\User\\Downloads\\PreFinalComputation " + datum_zip + r" - " + datum_zip_plus + r".zip")
    
    podaci = pd.read_csv(r"C:\\Users\\User\\Downloads\\PreFinalComputation " + datum_zip + r" - " + datum_zip_plus + r".csv", sep = ";")
    podaci = podaci[podaci['Presolved'] == True]
    os.remove(r"C:\\Users\\User\\Downloads\\PreFinalComputation " + datum_zip + r" - " + datum_zip_plus + r".csv")
    podaci["CneName"] = podaci['CneName'].str.strip()
    podaci = podaci[podaci['CneName'] == ime]
    podaci = podaci.loc[podaci.groupby(['DateTimeUtc', 'CneName']).Ram.idxmin()]
    browser.close()
    if len(podaci['Ram'] > 0):
        mm = min(podaci['Ram'])
        senhr = podaci["Ptdf_DE"] * 100 - podaci["Ptdf_HR"] * 100
        senhu = podaci["Ptdf_DE"] * 100 - podaci["Ptdf_HU"] * 100
        senro = podaci["Ptdf_DE"] * 100 - podaci["Ptdf_RO"] * 100
        sensi = podaci["Ptdf_DE"] * 100 - podaci["Ptdf_SI"] * 100
      
        sen_avg = (np.mean(senhr) + np.mean(senhu) + np.mean(senro) + np.mean(sensi)) / 4.0
        
    else:
        mm = sen_avg = np.nan
    return mm, sen_avg

v = pd.read_excel("JAO_SVE_ZAJEDNO_oktobar.xls")
v["CneName"] = v['CneName'].str.strip()
v['HU-DE'] = v['HU Price'] - v['DE Price']
v['remaining'] = v['Ram'] - (v['Hub_ALBE'] * v['Ptdf_ALBE'] + v['Hub_ALDE'] * v['Ptdf_ALDE'] + v['Hub_AT'] * v['Ptdf_AT'] + v['Hub_BE'] * v['Ptdf_BE'] + v['Hub_CZ'] * v['Ptdf_CZ'] + v['Hub_DE'] * v['Ptdf_DE'] + v['Hub_FR'] * v['Ptdf_FR'] + v['Hub_HR'] * v['Ptdf_HR'] + v['Hub_HU'] * v['Ptdf_HU'] + v['Hub_NL'] * v['Ptdf_NL'] + v['Hub_PL'] * v['Ptdf_PL'] + v['Hub_RO'] * v['Ptdf_RO'] + v['Hub_SI'] * v['Ptdf_SI'] + v['Hub_SK'] * v['Ptdf_SK'])


rrs = np.genfromtxt("dalekovodi.txt", delimiter = ',', usecols = [0], dtype = str, autostrip=True)
koef = pd.DataFrame()
sensi_df = pd.DataFrame()
procena1 = pd.DataFrame()
procena2 = pd.DataFrame()
problem_sens = pd.DataFrame()

sr_x = pd.DataFrame()
sr_y = pd.DataFrame()
nov_sens = pd.DataFrame()
nov_ram = pd.DataFrame()
delta_ram_MW = pd.DataFrame()

koef["Sat"] = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24']
sensi_df["Sat"] = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24']
procena1["Sat"] = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24']
procena2["Sat"] = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24']
problem_sens["Sat"] = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24']


sr_x["Sat"] = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24']
sr_y["Sat"] = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24']
nov_sens["Sat"] = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24']
nov_ram["Sat"] = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24']
delta_ram_MW["Sat"] = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24']


for k in range(len(rrs)):
    dale_satno_koe = np.array([])
    dale_satno_sensi = np.array([])
    dale_satno_procena1 = np.array([])
    dale_satno_procena2 = np.array([])
    
    niz_sr_x = np.array([])
    niz_sr_y = np.array([])
    niz_nov_sens = np.array([])
    niz_nov_ram = np.array([])
    niz_delta_ram_MW = np.array([])
    
    prob = np.array([])
    for j in range(24):
        v1 = v[v["CneName"] == rrs[k]]
        v1 = v1[(v1['HourUTC'] == "H" + str(j + 1))]
        v1 = v1[v1['HU-DE'] >  0]
        v1 = v1[v1['remaining'] < 20]
        v1 = v1.loc[v1.groupby(['DateUTC','HourUTC', 'CneName']).Ram.idxmin()]
        x = v1["Ram"]
        
        y = v1['Y-osa'] = v1["AT net position"] - (v1["Commercial Flow AT>HU  "] - v1["Commercial Flow HU>AT  "] + v1["Commercial Flow AT>SI  "] - v1["Commercial Flow SI>AT  "] + v1["Commercial Flow SK>HU  "] - v1["Commercial Flow HU>SK  "])
        if len(y) < 2:
            dale_satno_koe = np.append(dale_satno_koe, np.nan)
            dale_satno_sensi = np.append(dale_satno_sensi, np.nan)
            dale_satno_procena1 = np.append(dale_satno_procena1, np.nan)
            dale_satno_procena2 = np.append(dale_satno_procena2, np.nan)
            prob = np.append(prob, np.nan)
            
            niz_sr_x = np.append(niz_sr_x, np.nan)
            niz_sr_y = np.append(niz_sr_y, np.nan)
            niz_nov_sens = np.append(niz_nov_sens, np.nan)
            niz_nov_ram = np.append(niz_nov_ram, np.nan)
            niz_delta_ram_MW = np.append(niz_delta_ram_MW, np.nan)
            
            continue
        senhr = v1["Ptdf_DE"] * 100 - v1["Ptdf_HR"] * 100
        senhu = v1["Ptdf_DE"] * 100 - v1["Ptdf_HU"] * 100
        senro = v1["Ptdf_DE"] * 100 - v1["Ptdf_RO"] * 100
        sensi = v1["Ptdf_DE"] * 100 - v1["Ptdf_SI"] * 100
      
        sen_avg = (np.mean(senhr) + np.mean(senhu) + np.mean(senro) + np.mean(sensi)) / 4.0
        
        #plt.scatter(x,y)
        #plt.scatter(np.mean(x), np.mean(y))
        popt, pcov = curve_fit(func, x, y)
        
        if popt[0] > 0:
            popt[0] = 0
        
        
        rr, sen = minimalni_ram(rrs[k], j + 1)
        dale_satno_koe = np.append(dale_satno_koe, popt[0])
        dale_satno_sensi = np.append(dale_satno_sensi, sen_avg)
        niz_sr_x = np.append(niz_sr_x, np.mean(x))
        niz_sr_y = np.append(niz_sr_y, np.mean(y))
            
        if not np.isnan(rr):
            dale_satno_procena1 = np.append(dale_satno_procena1, -(np.mean(x) - rr) * popt[0] + np.mean(y))
            dale_satno_procena2 = np.append(dale_satno_procena2,  -rr / sen * 100.0)
            prob = np.append(prob, -np.mean(x) / sen_avg * 100.0)
            niz_nov_sens = np.append(niz_nov_sens, sen)
            niz_nov_ram = np.append(niz_nov_ram, rr)
            niz_delta_ram_MW = np.append(niz_delta_ram_MW, -np.mean(x) + rr)
        else:    
            dale_satno_procena1 = np.append(dale_satno_procena1, np.nan)
            dale_satno_procena2 = np.append(dale_satno_procena2, np.nan)
            niz_nov_sens = np.append(niz_nov_sens, np.nan)
            niz_nov_ram = np.append(niz_nov_ram, np.nan)
            niz_delta_ram_MW = np.append(niz_delta_ram_MW, np.nan)
            prob = np.append(prob, np.nan)
    
    
    dale_satno_koe = np.roll(dale_satno_koe, 2)
    dale_satno_sensi = np.roll(dale_satno_sensi, 2)
    dale_satno_procena1 = np.roll(dale_satno_procena1, 2)
    dale_satno_procena2 = np.roll(dale_satno_procena2, 2)
    prob = np.roll(prob, 2)
    niz_sr_x = np.roll(niz_sr_x, 2)
    niz_sr_y = np.roll(niz_sr_y, 2)
    niz_nov_sens = np.roll(niz_nov_sens, 2)
    niz_nov_ram = np.roll(niz_nov_ram, 2)
    niz_delta_ram_MW = np.roll(niz_delta_ram_MW, 2)
    
    koef[rrs[k]] = dale_satno_koe
    sensi_df[rrs[k]] = dale_satno_sensi
    procena1[rrs[k]] = dale_satno_procena1
    procena2[rrs[k]] = dale_satno_procena2
    problem_sens[rrs[k]] = prob
    sr_x[rrs[k]] = niz_sr_x
    sr_y[rrs[k]] = niz_sr_y
    nov_sens[rrs[k]] = niz_nov_sens
    nov_ram[rrs[k]] = niz_nov_ram
    delta_ram_MW[rrs[k]] = niz_delta_ram_MW

    
writer = pd.ExcelWriter('JAO-procena_18.11.2022.xls', engine='xlsxwriter',
                        options={'strings_to_numbers': True})

koef.to_excel(writer, index=False, sheet_name="Koeficijenti prave")
sensi_df.to_excel(writer, index=False, sheet_name="Koeficijenti za senzitivnost")
procena1.to_excel(writer, index=False, sheet_name="procena koef prave")
procena2.to_excel(writer, index=False, sheet_name="nova sensitivnost")
problem_sens.to_excel(writer, index=False, sheet_name="istorijska senzitivnost")

sr_x.to_excel(writer, index=False, sheet_name="srednji ram")
sr_y.to_excel(writer, index=False, sheet_name="srednja tacka")
nov_sens.to_excel(writer, index=False, sheet_name="nova sens")
nov_ram.to_excel(writer, index=False, sheet_name="novi ram")
delta_ram_MW.to_excel(writer, index=False, sheet_name="delta ram MW")


writer.save()
