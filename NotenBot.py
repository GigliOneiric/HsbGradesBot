import codecs
import os
import filecmp
import smtplib, ssl
import sys
import hashlib
import csv


from logging import error
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# Credentials HSBHV
username = "xxx"
password = "xxx"

# Credentials Mail
user = "xxx@gmail.com"
pwd = "xxx"
recipient = "xx@outlook.com"
subject = "Neue Note"
body = ""

def textCompare(fl1,fl2):
    file1 = open(fl1, 'r')
    file2 = open(fl2, 'r')
    lines1=file1.readlines()
    lines2=file2.readlines()

    if lines1 == lines2:
        return True 
    else:
        return False

def extract_table(fl, o1):
	html = open(fl).read()
	soup = BeautifulSoup(html)
	tables = soup.find_all("table")
	table = tables[1]

	output_rows = []
	for table_row in table.findAll('tr'):
		columns = table_row.findAll('td')
		output_row = []
		for column in columns:
			output_row.append(column.text)
		output_rows.append(output_row)
		
	with open(o1, 'w') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerows(output_rows)


def send_email(user, pwd, recipient, subject, body):
    import smtplib

    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print("successfully sent the mail")
    except:
        print("failed to send mail")

def check_marks(username, pwd):
	# initialize the Chrome driver
	driver = webdriver.Chrome("chromedriver")
	# head to hsbhv login page
	driver.get("https://iup.hs-bremerhaven.de/qisserver/rds?state=user&type=0")
	# find username/email field and send the username itself to the input field
	driver.find_element_by_id("asdf").send_keys(username)
	# find password input field and insert password as well
	driver.find_element_by_id("fdsa").send_keys(password)
	# click login button
	driver.find_element_by_id("loginForm:login").click()
	# wait the ready state to be complete
	WebDriverWait(driver=driver, timeout=10).until(
		lambda x: x.execute_script("return document.readyState === 'complete'")
	)
	error_message = "Incorrect username or password."
	# get the errors (if there are)
	errors = driver.find_elements_by_class_name("flash-error")
	# print the errors optionally
	# for e in errors:
	#     print(e.text)
	# if we find that error message within errors, then login is failed

	if any(error_message in e.text for e in errors):
		print("[!] Login failed")
	else:
		print("[+] Login successful")


	driver.find_element_by_link_text("Info über angemeldete Prüfungen").click()
	driver.find_element(By.XPATH, "//img[@alt='Symbol für Information']").click(); 

	# write file
	h = driver.page_source
	f = open('working.html', 'wb')
	f.write(h.encode('utf8'))
	f.close()
	
	extract_table('working.html','working.csv');
	extract_table('current.html','current.csv');
	
	same = textCompare('current.csv','working.csv')
	print(same)
	
	if same is False:
		f = open('current.html', 'wb')
		f.write(h.encode('utf8'))
		f.close()
        
        send_email(user, pwd, recipient, subject, body);

	# close the driver
	driver.close()

check_marks(username, pwd);	
	