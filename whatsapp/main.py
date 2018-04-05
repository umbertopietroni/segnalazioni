import urllib.request
import os
import shutil
import pprint
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

import time
import traceback

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re
from datetime import datetime
from datetime import timedelta
import pickle

import sys
sys.path.insert(0, '../dbinterface/')
from classes import *

def getorderedfiles(dirpath):
	a = [s for s in os.listdir(dirpath)
		 if os.path.isfile(os.path.join(dirpath, s))]
	a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)))
	return a

DOWNLOAD_PATH = "/home/umberto/Scaricati/"




def delete_chat(driver,chat_id):
	usersDiv = driver.find_element_by_id("side")
	messageDiv = driver.find_element_by_id("main")
	actionChains = ActionChains(driver)
	contacts = usersDiv.find_elements_by_class_name("_2wP_Y")
	print("inizio delete")
	
	for contact in contacts:
		chatTitle = contact.find_elements_by_class_name("_1wjpf")
		if chatTitle[0].text == chat_id:
			contact.click()
			#actionChains.move_to_element(contact)
			#actionChains.perform()
			msg_menu = contact.find_element_by_class_name("ZR5SB").click()
			usersDiv.find_element_by_xpath('//*[@title="Elimina chat"]').click()
			#driver.implicitly_wait(2)
			wait = WebDriverWait(driver, 10)
			pop_up = wait.until(EC.presence_of_element_located((By.CLASS_NAME, '_1CnF3')))

			#pop_up = driver.find_element_by_class_name("_1CnF3")
			if pop_up:
				pop_up.find_elements_by_class_name("_1WZqU")[1].click()
			

"""metodo per cancellare i messaggi ricevuti. da eseguire dopo aver salvato segnalazione"""


#def delete_message_list(driver):
	##usare quando bot ha cliccato dentro il contatto
	
	#usersDiv = driver.find_element_by_id("side")
	#messageDiv = driver.find_element_by_id("main")
	#actionChains = ActionChains(driver)
	#contacts = usersDiv.find_elements_by_class_name("_2wP_Y")
	#print("inizio delete")
	
	#for contact in contacts:
		#chatTitle = contact.find_elements_by_class_name("_1wjpf")
		#if chatTitle[0].text == "Umberto":
			#contact.click()
			#messageList = messageDiv.find_elements_by_class_name("message-in")
			#for m in messageList:
				#try:
					#delete_msg(driver,m)
				#except:
					#print("Errore Eliminazione")
					
			#messageList = messageDiv.find_elements_by_class_name("message-in")

	#if messageList:
		#delete_message_list(driver)
	
#def delete_msg(driver,m):
	#actionChains = ActionChains(driver)
	#usersDiv = driver.find_element_by_id("side")

	
	#actionChains.move_to_element(m)
	#actionChains.perform()
	#images = m.find_elements_by_tag_name("img")
	#if images:
		#msg_menu = m.find_element_by_class_name("_2R973")
	#else:
		#msg_menu = m.find_elements_by_class_name("_3kN0h")[0]
	#if msg_menu:
		#print("Trovato")
		##msg_menu[0].click()
		#msg_menu.click()
		#usersDiv.find_element_by_xpath('//*[@title="Elimina messaggio"]').click()
		#driver.implicitly_wait(1)
		#pop_up = driver.find_element_by_class_name("_1CnF3")
		#pop_up.find_elements_by_class_name("_1WZqU")[1].click()
		##driver.implicitly_wait(2)
	#else:
		#print("NO")
	
def get_date_from_msg(text):
	date_rex = re.compile('\[(.+?)\]')
	pre_date = date_rex.findall(text)[0]
	h,mi,d,mo,y= [int(s) for s in re.findall(r'\d+', pre_date)]
	date = datetime(y,mo,d,h,mi)
	print(date)
	return date
	
	
"""
   @save_msg
   salvo tutti i messaggi contenuti in messageList. dopo di questo metodo è necessario fare un delete_chat
"""
def save_msg(driver,messageList,chatTitle):
	ts = time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime(time.time())) + "__" + str(time.time())
	msg_dir = "inbox/" +chatTitle+'/'+ts
	try:
		os.makedirs(msg_dir)
	except:
		pass
		
	text = ""
	m= {}
	photo = []
	date = []
	pos = []
	
	for m in messageList:
		images = m.find_elements_by_tag_name("img")
		if images:
			im = images[0]
			pos_class = im.get_attribute("class")
			#is_pop = im.find_elements_by_class_name("_1Qnxi")
			if pos_class == "_1Qnxi":
				print("posizione trovata")
				father = im.find_element_by_xpath('..')
				if father:
					pos = father.get_attribute("href")
					if ("maps" in pos):
						#https://maps.google.com/maps?q=44.7649225%2C10.3085252&z=17&hl=it
						#print(pos)
						lat_rex = re.compile(r'q=(.+?)%2C')
						long_rex = re.compile(r'%2C(.+?)&z=')
						lat = float(lat_rex.findall(pos)[0])
						lon = float(long_rex.findall(pos)[0])
						#print(lat,lon)
						pos = [lat,lon]
						print(pos)
						
				
				
			else:
				src = im.get_attribute("src").replace("blob:", "")
				im.click()
				#mpt = driver.find_elements_by_class_name("media-panel-tools")[0]
				mpt = driver.find_elements_by_class_name("_3Kxus")[0]
				buttons = mpt.find_elements_by_class_name("rAUz7")
				# download
				buttons[3].click()
				# close window
				buttons[4].click()

				# look for last downloaded file
				time.sleep(1)
				downloaded_files = getorderedfiles(DOWNLOAD_PATH)
				downloaded_files.reverse()
				firstfile = downloaded_files.pop(0)

				if firstfile.startswith("WhatsApp"):
					print("Moving file : " + DOWNLOAD_PATH+firstfile)
					downloaded_fname =  firstfile.replace("WhatsApp Image ", "")
					downloaded_fname =  downloaded_fname.replace(" ", "_")
					downloaded_fname =  downloaded_fname.replace(" ", "_")
					downloaded_fname =  downloaded_fname.replace("_at_", "__")
					
					shutil.move(DOWNLOAD_PATH+firstfile, msg_dir + "/%s" % downloaded_fname)
					photo.append( msg_dir + "/%s" % downloaded_fname)
					
					#content = open(filename, 'rb').read()
				
			
			
		else:
			copyableText = m.find_elements_by_class_name("copyable-text")
			#print("copyableText = ", copyableText)
			if copyableText:
				for ct in copyableText[0:1]:
					print("ct = ", ct.text)
				
				#precise timestamp data-pre-plain-text = [16:52, 18/3/2018] Guido Dondi
				pre_text = copyableText[0].get_attribute("data-pre-plain-text")
				date = get_date_from_msg(pre_text)
				#timestamp = m.find_elements_by_class_name("_2f-RV")
				#for ts in timestamp[0:1]:
					#print("ts = ", ts.text)
				 
				text += ct.text +' '
			
	m  = {
	"message_id" : ts,
	"date": date,
	"text": text,
	"user": chatTitle,
	"photo": photo,
	"location": pos,
	}
		
	print(m)
	pprint.pprint(m, open(msg_dir+"/" +'msg.dict', 'w'))
	segnalazione = msg_to_segnalazione(m,msg_dir)
	if segnalazione:
		segnalazione.printIssue()
		with open(msg_dir+"/"+'issue.pickle', 'wb') as output:
			pickle.dump(segnalazione, output, pickle.HIGHEST_PROTOCOL)
	
	
		
def is_timeout(date):
	now = datetime.now()
	delta = timedelta(seconds=60)
	print(now-date)
	
	if now-date>delta:
		print("Tempo scaduto")
		return True
	else:
		print("non ancora")
		return False
		
def msg_to_segnalazione(msg,msg_dir):
	if msg:
		
		msg_id = msg["message_id"]
		user_id = msg["user"]
		
		text = msg.get("text","")
		photo= msg.get("photo",[])
		date = msg.get("date", "")
		pos = msg.get("location",[])
		#text_classification_dict = msg.get("text_category", [])
		
		
		segnalazione = Issue(msg_id)
		segnalazione.setInfo("channel", "whatsapp")
		segnalazione.setInfo("msg_id",msg_id)
		segnalazione.setInfo("text",text)
		segnalazione.setInfo("date",date)
		segnalazione.setInfo("user_id",user_id)
		segnalazione.setInfo("phone_number", user_id)
		if pos:
			segnalazione.setLatitude(pos[0])
			segnalazione.setLongitude(pos[1])
		#segnalazione.setCategory(msg.get("category",""))
		#segnalazione.setClassificationDict(text_classification_dict)
		for p in photo:
			#photo_id = p["file_id"] # dimensione maggiore
			#filename = msg_dir + "/" + photo_id + ".jpg"
			#img_classification_dict = p.get("photo_category",[])
			image = IssueImage(p)
			segnalazione.addImage(image)
		
		return segnalazione
		
	print("ERROR: message not defined")
	
def main(driver, chatHistory, replyQueue, firstRun):		
	
	driver.switch_to_window(driver.window_handles[0])
	
	usersDiv = driver.find_element_by_id("side")
	#messageDiv = driver.find_element_by_id("main")
	actionChains = ActionChains(driver)

	contacts = usersDiv.find_elements_by_class_name("_2wP_Y")
	
	new_messages = []
	received_msgs = []
	
	for contact in contacts:
		chatTitle = contact.find_elements_by_class_name("_1wjpf")
		#print("chatTitle = ", chatTitle[0].text)
		unread = contact.find_elements_by_class_name("unread")
		#forse al posto di unread ci vuole "OUeyt"

		if chatTitle[0].text:
			# click on contact element and read all incoming messages
			ct = ""
			ts = ""
			messageList = []
			
			contact.click()
			driver.implicitly_wait(1.5)

			print("="*100)
			try:
				messageDiv = driver.find_element_by_id("main")
				messageList = messageDiv.find_elements_by_class_name("message-in")
				print("messageList = ", len(messageList))
				
			except:
				print("No message")
			if messageList:
				##cerco ultimo messaggio, testo o foto e calcolo tempo passato
				last_msg = messageList[-1]
				copyableText = last_msg.find_elements_by_class_name("copyable-text")
				if copyableText:
					#precise timestamp -> data-pre-plain-text = [16:52, 18/3/2018] Guido Dondi:
					pre_text = copyableText[0].get_attribute("data-pre-plain-text")
					date = get_date_from_msg(pre_text)
				else:
					time = last_msg.find_element_by_class_name("_3EFt_")
					print(time.text)
					h,mi = [int(s) for s in re.findall(r'\d+', time.text)]
					now = datetime.now()
					date = now.replace(hour=h, minute=mi)
					
				if is_timeout(date):
					
					save_msg(driver,messageList, chatTitle[0].text)
					
					##INVIO MESSAGGIO
					input_box = driver.find_element_by_class_name('_2S1VP')
					input_box.send_keys("Segnalazione Ricevuta, Grazie!")
					driver.find_element_by_xpath('//span[@data-icon="send"]').click()
					
					delete_chat(driver, chatTitle[0].text)
				
				
				

				
				
				"""
				# look for images..
				images = m.find_elements_by_tag_name("img")
				print("Images = ", images)
				for im in images:
					src = im.get_attribute("src").replace("blob:", "")
					#print("im = ", src)
					try:
						os.makedirs(chatTitle[0].text)
					except:
						pass
#					time.sleep(30)
					# right click and save
					#actionChains.context_click(im).perform()
					#print("Keys.ARROW_DOWN = ", Keys.ARROW_DOWN)
					#actionChains.send_keys(Keys.ARROW_DOWN).perform()
					#actionChains.send_keys("l").perform()
					im.click()
					
					# look for save image button
#					driver.switch_to_window(driver.window_handles[0])


					#mpt = driver.find_elements_by_class_name("media-panel-tools")[0]
					mpt = driver.find_elements_by_class_name("_3Kxus")[0]
					buttons = mpt.find_elements_by_class_name("rAUz7")
#					print(buttons)
					# download
					buttons[3].click()
					# close window
					buttons[4].click()

					# look for last downloaded file
					downloaded_files = getorderedfiles(DOWNLOAD_PATH)
					downloaded_files.reverse()
					firstfile = downloaded_files[0]
					
					#print("downloaded_files = ", downloaded_files)
					
					#print(DOWNLOAD_PATH+firstfile)
					#local_filename, headers = urllib.request.urlretrieve(src)
					#print("local_filename = ", local_filename)
					
					if firstfile.startswith("WhatsApp"):
						print("Moving file : " + DOWNLOAD_PATH+firstfile)
						downloaded_fname =  firstfile.replace("WhatsApp Image ", "")
						downloaded_fname =  downloaded_fname.replace(" ", "_")
						downloaded_fname =  downloaded_fname.replace(" ", "_")
						downloaded_fname =  downloaded_fname.replace("_at_", "__")
						shutil.move(DOWNLOAD_PATH+firstfile, chatTitle[0].text + "/%s" % downloaded_fname)
#					
					time.sleep(2)

#					urllib.urlretrieve(src, chatTitle[0].text + "/filename.png")
#					f = urllib.request.urlopen(src)
#					content = f.read()
#					f.close()
#					open(chatTitle[0].text + "/filename.png", "wb").write(content)
					"""
					
				

			
			
			
			
	
	#delete_message_list(driver)
	#delete_chat(driver)
	
		
	



