import requests
import random
import time
import json
import urllib
import webbrowser
import io
import base64

token = '1017242146:AAEnjzBDXaWFFeg3KSLCTla0SMUGs-O5fOw'
url = 'https://api.telegram.org/bot'
chat_id = '-1001202697355'
bpy6_chat = '228334796'
cipherPts = 1

class Cipher:
    def __init__(self, currentCipher, answer):
        self.currentCipher = currentCipher
        self.answer = answer
        self.winners = []
        self.points = cipherPts
    def run(self):
        bot.forwardMessage(bpy6_chat, chat_id, self.currentCipher)
        bot.sendMessage(chat_id, 'Напиши "шифр", и я повторю задание.')
        bot.sendMessage(chat_id, 'А ответы отправляй мне в личку!')

    def close(self):
        global scoreboard
        (self.currentCipher, self.answer) = ('new','new')
        bot.sendMessage(chat_id, 'Раунд завершен! Победители:')
        for winner in self.winners: bot.sendMessage(chat_id, winner)
        self.winners = []
        bot.sendMessage(chat_id, str(scoreboard))
        self.points = cipherPts    
    
class CipherBot:
    def __init__(self, ready, token):
        self.ready = False
        self.token = token
        file = open('update_id.txt','r')
        self.offset = int(file.readline())
        file.close()
    
    def update(self):
        call = requests.get('https://api.telegram.org/bot1017242146:AAHhJtdAaBXwhgyS2Giqdy37QpFWcTqT9E0/getUpdates?offset='+str(self.offset))
        update = call.json().get('result')
        if update:
            self.offset = int(update[-1].get('update_id'))+1
            file = open('update_id.txt','w')
            file.write(str(self.offset))
            file.close()
        if update: print(update)
        return update
        
    def checkForEvents(self, update):
        global scoreboard
        for event in update:
            print(riddle.answer.encode('utf-8'))      
            if 'text' in event.get('message'):
                if event.get('message').get('text').lower() == 'шифр' and event.get('message').get('from').get('is_bot') == False:
                    bot.forwardMessage(bpy6_chat, chat_id, riddle.currentCipher)
                if event.get('message').get('chat').get('type') == 'private':
                    self.addToScoreboard(event.get('message').get('from').get('username'))
                    attempt = event.get('message').get('text').lower()
                    if str(base64.b64encode(attempt.encode('utf-8'))) == riddle.answer:
                        if event.get('message').get('from').get('username') not in riddle.winners:
                            riddle.winners.append(event.get('message').get('from').get('username'))
                            scoreboard.update({event.get('message').get('from').get('username'):scoreboard.get(event.get('message').get('from').get('username'))+riddle.points})
                            riddle.points -= 1
                            self.sendMessage(self.getChatId(event), 'Молодей! Победа!')
                        else: self.sendMessage(self.getChatId(event), 'Эээ! Тебе за это задание уже заправили!')
                    else: self.sendMessage(self.getChatId(event), 'Ноуп')
                                               
                print(event.get('message').get('from').get('username') + ': ' + event.get('message').get('text'))
                       
            if 'new_chat_participant' in event.get('message'):
                if event.get('message').get('new_chat_participant').get('username'):
                    username = event.get('message').get('new_chat_participant').get('username')
#                    chatid = event.get('message').get('chat').get('id')
                    chatid = '-1001202697355'
                    print(chatid)
                    self.sendMessage(self.getChatId(event), f'Доброе утро, {username}!' ) 
                    bot.sendMessage(chat_id, 'Напиши "шифр", и я повторю задание.')
                    bot.sendMessage(chat_id, 'А ответы отправляй мне в личку!')
    
    def addToScoreboard(self, username):
        global scoreboard
        if username not in scoreboard.keys(): 
            scoreboard.update({username:0})
            print(username+' added to scoreboard')
        else: print(scoreboard)
            
    def getEndpoint(self, endpoint):
        self.endpoint = endpoint
        
    def buildSignature(self):
        self.url = url + self.token + self.endpoint
        
    def getChatId(self, event):
        chatId = str(event.get('message').get('chat').get('id'))
        return chatId
    
    def forwardMessage(self, fromChatId, toChatId, messageId):
        self.getEndpoint('/forwardMessage')
        self.buildSignature()
        call = requests.post(self.url, data={'chat_id':toChatId,'from_chat_id':fromChatId, 'message_id':messageId})
        print(call.text)
        
    def sendAnimation(self, event):
        self.getEndpoint('/sendAnimation')
        self.buildSignature()
        call = requests.post(self.url, data={'chat_id':self.getChatId(event),'animation':self.getKielbasa()})
        print(call.text)
    
    def sendMessage(self, chatId, text):
        self.getEndpoint('/sendMessage')
        self.buildSignature()
        call = requests.post(self.url, data={'chat_id':chatId,'text':text})
        print(call.text)

def getNewCipher(currentCipher, answer):
    if (currentCipher, answer) == ('new','new'):
        bot.sendMessage(bpy6_chat, 'Давай-ка, запили мне новый шифр!')
        received = False
        while not received:
            try:
                time.sleep(1)
                for event in bot.update():
                    if event.get('message').get('chat').get('id') == 228334796: currentCipher = event.get('message').get('message_id')
                    print(currentCipher)
                    received = True
            except TypeError:
                print('wtf try again')
        bot.sendMessage(bpy6_chat, 'Отличненько! Теперь дай ответ')
        received = False
        while not received:
            try:
                time.sleep(1)
                for event in bot.update():
                    if event.get('message').get('chat').get('id') == 228334796: answer_raw = event.get('message').get('text')
                    answer = str(base64.b64encode(answer_raw.encode('utf-8')))
                    print(answer)
                    received = True
            except TypeError:
                print('wtf try again')
        bot.sendMessage(bpy6_chat, 'Ну хорошо, давай врубим это дело!')
    riddle = Cipher(currentCipher, str(answer))
    return riddle

if __name__ == '__main__':
    bot = CipherBot(False, token)
    with open('cipher.txt', 'r') as f:
        currentCipher = f.readline().strip()
        answer = f.readline().strip()
    print(currentCipher, answer)
    riddle = getNewCipher(currentCipher, answer)
    riddle.run()
    
    with open('scoreboard.txt', 'r') as f:
        scoreboard = dict(eval(f.read()))
        print(scoreboard)
    with open('winners.txt', 'r') as f:
        riddle.winners = eval(f.read())
        print(riddle.winners)
    with open('currentpoints.txt', 'r') as f:
        riddle.points = int(f.read())
        print(riddle.points)
    
    while True:
        try:
            time.sleep(1)
            bot.checkForEvents(bot.update())
            if riddle.points == 0: 
                riddle.close()
                break
        except TypeError:
            print('TypeError exception occurred')
        finally:
            with open('scoreboard.txt', 'w') as f:
                f.write(str(scoreboard))
            with open('winners.txt', 'w') as f:
                f.write(str(riddle.winners))
            with open('currentpoints.txt', 'w') as f:
                f.write(str(riddle.points))
            with open('cipher.txt', 'w') as f:
                f.write(str(riddle.currentCipher))
                f.write('\n')
                f.write(str(riddle.answer))
