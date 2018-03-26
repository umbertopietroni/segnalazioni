#!/usr/bin/env python
# -*- coding: utf-8 -*
import random
import time
import os
import pprint
import traceback

import telepot
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop

import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

from test_image_classification import predict_image
from classes import *

bad_words = ["fanculo", "vaffa", "vaffanculo", "stronzo", "stronzi", "cazzo", "fottiti", "fottuto", "merda"]


users_category_choice = {}
msg_to_save = {}
state = 0


REPLY_BUTTONS_TEXT = [
						[("Ambiente", "ambiente"), ("Sicurezza-Mobilità", "sicurezza")],
						[("Manutenzione", "manutenzione"), ("Illuminazione", "illuminazione")],
						[("Altro", "altro"),]
					]



def cleanChars(s):
	for ch in """"?!!"£$%&/()ç°§[]{}""":
		try:
			s = s.replace(ch, ' ' + ch + ' ')
		except:
			pass
	return s


def menu_function(text, chat_id):
	response = "Comando non riconosciuto "
	categories = "Clicca per\n"
	categories_test = ""
	category_list = []
	global users_category_choice
	
	for row in REPLY_BUTTONS_TEXT:
		for col in row:
			categories += "/" + col[1] + "  "
			categories_test += "'" + col[0] + "' "
			category_list.append("/"+col[1])
	#categories = ""
	
	#categories e categories_test sono stringhe che uso nel messaggio di inizio
	#category_list è usato per controllare se text è uno delle categorie
	
	if text in ('/start', '/help', '/menu_principale'):
		
		
		response = """Comune di Montecchio Emilia\nServizio per le segnalazioni del cittadino
[Servizio in fase di sperimentazione]


Per effettuare una segnalazione può scrivere più messaggi oppure 
inviare una foto relativa alla segnalazione. 
Quando la segnazione è completa prema sul tasto Invia.

Può anche condividere la sua posizione
per una geolocalizzazione piu' precisa.

Grazie della collaborazione
""" % vars()
	

	bot.sendMessage(chat_id, response, reply_markup=None)
	return 
		
	
	


class UnreadStore(object):
	def __init__(self):
		self._db = {}

	def put(self, msg):
		chat_id = msg['chat']['id']

		if chat_id not in self._db:
			self._db[chat_id] = []

		self._db[chat_id].append(msg)

	# Pull all unread messages of a `chat_id`
	def pull(self, chat_id):
		messages = self._db[chat_id]
		del self._db[chat_id]

		# sort by date
		messages.sort(key=lambda m: m['date'])
		return messages

	# Tells how many unread messages per chat_id
	def unread_per_chat(self):
		return [(k,len(v)) for k,v in self._db.items()]
	def last_msg(self, chat_id):
		if (self._db.get(chat_id,[])):
			return self._db[chat_id][-1]
		
	
"""
@on_callback_query

Uso della callback per gestire i vari passaggi di conferma della segnalazione e della categoria

1. InlineKeyboard per inviare o modificare segnalazione
2. InlineKeyboard dopo il calcolo della categoria per confermarla
3. Se categoria non è corretta si usa altra InlineKeyboard per chiedere direttamente a utente

"""
def on_callback_query(msg):
	
	
	global msg_to_save
	global msg_dir
	
	query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

	chat_id = msg["message"]["chat"]["id"]
	msg_id = telepot.origin_identifier(msg)
	
	#utente invia segnalazione corretta: calcolo della categoria e richiesta di conferma
	#oppure utente invia foto e conferma che segnalazione precedente va associata alla foto
	if (query_data == "save"):
		ts = time.strftime("%Y-%m-%d--%H-%M-%S", time.localtime(time.time())) + "__" + str(time.time())
		msg_dir = "inbox/" + ts
		try:
			os.makedirs(msg_dir)
		except:
			pass
		try:
			X = [msg_to_save[chat_id].get("text","")]
			#response = """Grazie!\nHo ricevuto la sua segnalazione: "%s".\n/menu_principale """ % (X[0])
			
			##CALCOLO CATEGORIA TESTO
			print(X)
			category, categories_prob = predict_text(X)
			msg_to_save[chat_id]["category"] = category
			text_dict = create_dict(categories_prob)
			msg_to_save[chat_id]["text_category"] = text_dict
			
			#CALCOLO CATEGORIA FOTO
			photo_list = msg_to_save[chat_id].get("photo",[])
			if photo_list:
				#msg_to_save[chat_id]["photo_category"] = []
				i = 0
				for photo in photo_list:
					photo_id = photo["file_id"] # dimensione maggiore
					filename = msg_dir + "/" + photo_id + ".jpg"
					bot.download_file(photo_id, filename)
					
					photo_category,photo_prob = predict_image(filename)
					dict_prob = create_dict(photo_prob)
					msg_to_save[chat_id]["photo"][i]["photo_category"] = dict_prob
					i += 1
					
					print (category, photo_category)
			
			
			
			msg_to_save[chat_id]["saved"] = True
			
			keyboard_btns = []
			L = []
			L.append(InlineKeyboardButton(text="Si", callback_data="si"))
			L.append(InlineKeyboardButton(text="No", callback_data="no"))
			keyboard_btns.append(L)
			keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_btns)

			response = """Grazie!\nHo ricevuto la sua segnalazione "%s". Calcolato categoria %s: è corretta?""" % (X[0],category)
			bot.editMessageText(msg_id,response, reply_markup = keyboard)
			
		
		except:
			print (traceback.format_exc())
	
		
		
	#utente sceglie di aggiungere altre informazioni ( non necessario, può semplicemente scrivere altro testo)
	elif (query_data == "add"):
		keyboard_btns = []
		keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_btns)
		text = """Può inserire un altro messaggio o una foto da associare a questa segnalazione""" 
		bot.editMessageText(msg_id,text, reply_markup = keyboard)
	#utente annulla segnalazione
	elif (query_data == "delete"):
		keyboard_btns = []
		keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_btns)
		text = """Segnalazione eliminata. Può scriverne una nuova"""
		msg_to_save[chat_id]["saved"]=True
		bot.editMessageText(msg_id,text, reply_markup = keyboard)
		
	
	#KEYBOARD DI GESTIONE SCELTA CATEGORIA (query_data = ["si","no","altri"]
	#utente conferma che categoria calcolata è corretta: posso salvare la segnalazione
	elif (query_data == "si"):
		keyboard_btns = []
		keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_btns)
		text = """Grazie! La sua segnalazione associata alla categoria %s è stata registrata correttamente. \nPuò inserire una nuova segnalazione""" % msg_to_save[chat_id]["category"]
		bot.editMessageText(msg_id,text, reply_markup = keyboard)
		
		##SALVATAGGIO
		pprint.pprint(msg_to_save[chat_id], open(msg_dir+"/" +'msg.dict', 'w'))
		segnalazione = msg_to_segnalazione(msg_to_save[chat_id],msg_dir)
		segnalazione.printIssue()
		
		
		
	#categoria calcolata per utente è sbagliata: chiedo direttamente quale sia quella corretta
	elif (query_data == "no"):
		keyboard_btns = []
		for row in REPLY_BUTTONS_TEXT:
			L = []
			for col in row:
				L.append(InlineKeyboardButton(text=col[0], callback_data=col[1]))
			keyboard_btns.append(L)
		keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_btns)
		bot.editMessageText(msg_id,'Scegli quale categoria è più corretta', reply_markup = keyboard)
	#tutte gli altri tipi di callback nascono quando utente sceglie categoria corretta. Poi posso salvare la segnalazione
	else:
		keyboard_btns = []
		keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_btns)
		
		text = """Grazie! La sua segnalazione associata alla categoria %s è stata registrata correttamente. \nPuò inserire una nuova segnalazione""" % query_data
		bot.editMessageText(msg_id,text, reply_markup = keyboard)
		msg_to_save[chat_id]["category"] = query_data
		
		#salvataggio
		pprint.pprint(msg_to_save[chat_id], open(msg_dir+"/" +'msg.dict', 'w'))
		segnalazione = msg_to_segnalazione(msg_to_save[chat_id],msg_dir)
		segnalazione.printIssue()
		





	bot.answerCallbackQuery(query_id, text=query_data)

def on_chat_message(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	
	global msg_to_save
	msg["saved"] = False
	print (content_type, chat_type, chat_id, msg["message_id"])
	try:
		
		received_text = cleanChars(msg.get("text", ""))
		bot_name = '@'+bot.getMe()["username"]
		received_text = received_text.replace(bot_name,"")
		
		
		#gestione di messaggi con più foto, prendo ultima foto di messaggio attuale (dimensione più grande)
		#poi va aggiunta in photo_list che poi conterrà solo le foto di dimensioni più grande inviate
		photo = msg.get("photo", [])
		if photo:
			photo = [photo[-1]]
		msg["photo"] = photo
		
		document = msg.get("document", [])
		userinfo = msg["from"]
		
		if msg.get("text", "") and msg.get("text", "")[0] == '/':
			return menu_function(msg.get("text", ""), chat_id)
		last_msg = store.last_msg(chat_id)
		if (last_msg and last_msg["saved"]==False):
			photo_list = last_msg.get("photo",[])
			
			msg["text"] = last_msg.get("text","")+" "+received_text
			msg["photo"] = photo_list + photo
			
				
				
		
		#if document:
			#document_id = document["file_id"]
			#fname = document["file_name"] # dimensione maggiore
			#bot.download_file(document_id, msg_dir + "/" + fname)
			
	
		msg_to_save[chat_id] = msg
		store.put(msg)
		keyboard_btns = []
		L = []
		L.append(InlineKeyboardButton(text="Invia", callback_data="save"))
		L.append(InlineKeyboardButton(text="Aggiungi altro", callback_data="add"))
		L.append(InlineKeyboardButton(text="Annulla", callback_data="delete"))


		keyboard_btns.append(L)
		response = """Grazie %s \nSegnalazione ricevuta: "%s" \nVuole inviare o vuole aggiungere altro (messaggio o foto) ?""" % (str(userinfo["first_name"]),msg.get('text',''))
		bot.sendMessage(chat_id,response, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_btns))
		
		
		


	except:
		bot.sendMessage(chat_id, "Ooops! Qualcosa e' andato storto! Riprova, Grazie!")
		bot.sendSticker(chat_id, "CAADAgADzwUAAmMr4gmeXsfnL_icMwI")
		print (traceback.format_exc())
		
		
def msg_to_segnalazione(msg,msg_dir):
	if msg:
		chat_id = msg["chat"]["id"]
		msg_id = msg["message_id"]
		username = msg["from"]["username"]
		text = msg.get("text","")
		photo= msg.get("photo",[])
		date = msg.get("date", "")
		
		
		segnalazione = Issue(msg_id,username)
		segnalazione.setInfo("text",text)
		segnalazione.setInfo("date",date)
		segnalazione.setCategory(msg.get("category",""))
		if photo:
			photo_id = photo[-1]["file_id"] # dimensione maggiore
			filename = msg_dir + "/" + photo_id + ".jpg"
			image = IssueImage(filename)
			segnalazione.addImage(image)
		
		return segnalazione
		
	print("ERROR: message not defined")
	
def create_dict(class_prob):
	dict_issue = {}
	dict_issue["ambiente"] = class_prob[0]
	dict_issue["illuminazione"] = class_prob[1]
	dict_issue["manutenzione"] = class_prob[2]
	dict_issue["sicurezza"] = class_prob[3]
	return dict_issue


	
	
def predict_text(X):
	with open('nb_classifier.pickle', 'rb') as handle:
		clf = pickle.load(handle)
	with open('nb_vectorizer.pickle', 'rb') as handle:
		vectorizer = pickle.load(handle)

	# transform s into an array with thr trained vectorizer
	v = vectorizer.transform(X).toarray()
	category = clf.predict(v)[0]
	categories = clf.predict_proba(v)[0]
	#print("Predicted class: Ambiente Illuminazione Manutenzione Sicurezza \n", clf.predict_proba(v)[0])
	return category,categories




TOKEN = ''           #Test_Segnalazioni_bot
bot = telepot.Bot(TOKEN)

import sys
#print (sys.argv)

#bot.message_loop(on_chat_message)
store = UnreadStore()
MessageLoop(bot, {'chat': on_chat_message, 'callback_query': on_callback_query}).run_as_thread()

#MessageLoop(bot,on_chat_message).run_as_thread()

print ('REAL TIME MODE: Listening ...')
while 1:
	time.sleep(5)