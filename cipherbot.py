import requests
import random
import time
import json
import os

token = str(os.environ.get('TOKEN'))
url = 'https://api.telegram.org/bot'

class Riddle:
    def __init__(self):
        self.scoreboard = {'Paralitiq': 3, 'alexoal': 2, 'SyksAxxx': 1}
        self.winners = []
        self.reward = 3
        self.status = 'setup'
        self.question = self.getQuestion()
        print(f'Accepted Question:{self.question}')
        self.correctAnswer = self.getAnswer()
        print(f'Accepted Answer:{self.correctAnswer}')
        self.run()
        
    def getQuestion(self):
        bot.sendMessage(228334796, 'Ну, запиливай!')
        while True:
            update = Update(bot.getOneUpdate(bot.offset))
            if update.sender == 'Bpy6na': return update.message_id
                
    def getAnswer(self):
        bot.sendMessage(228334796, 'Теперь ответ')
        while True:
            update = Update(bot.getOneUpdate(bot.offset))
            if update.sender == 'Bpy6na': return update.text

    def run(self):
        bot.forwardMessage(228334796, -1001202697355, self.question)
        bot.sendMessage(-1001202697355, 'Напиши "шифр", и я повторю задание.')
        bot.sendMessage(-1001202697355, 'А ответы отправляй мне в личку!')
        self.status = 'running'
        
    def reduceReward(self, winner):
        
        self.winners.append(winner)
        if winner not in self.scoreboard.keys(): self.scoreboard.update({winner:0})
        print(self.scoreboard)
        self.scoreboard.update({winner:+self.reward})
        print(self.scoreboard)
        self.reward -= 1
        if self.reward == 0: self.close()
        
    def close(self):
        self.status = 'setup'
        bot.sendMessage(-1001202697355, 'Шифр разгадан! Победители:')
        for winner in self.winners: bot.sendMessage(-1001202697355, winner)
        bot.sendMessage(-1001202697355, f'Итоговый зачет:\n{str(self.scoreboard)}')
        self.winners = []

class Update:
    def __init__(self, result):
        self.result = result
        self.message_id = self.result.get('message',{}).get('message_id','')
        self.text = self.result.get('message',{}).get('text','').lower()
        if self.result.get('message',{}).get('new_chat_participant',{}).get('username',''):
            self.newMemberName = self.result.get('message',{}).get('new_chat_participant',{}).get('username','')
        else: self.newMemberName = self.result.get('message',{}).get('new_chat_participant',{}).get('first_name','')
        if self.result.get('message',{}).get('from',{}).get('username',''):
            self.sender = self.result.get('message',{}).get('from',{}).get('username','')
        else: self.sender = self.result.get('message',{}).get('from',{}).get('first_name','')
        self.chatType = self.result.get('message',{}).get('chat',{}).get('type','')
        self.chat_id = self.result.get('message',{}).get('chat',{}).get('id','')
        print(self.result)   
           
class CipherBot:
    def __init__(self, ready, token):
        self.ready = False
        self.token = token
        self.offset = int(self.getInitialOffset())+1
        
    def getEndpoint(self, endpoint):
        self.endpoint = endpoint
        
    def buildSignature(self):
        self.url = url + self.token + self.endpoint
        
    def getInitialOffset(self):
        offset = self.getOneUpdate('None').get('update_id')
        print(f'First update received. Update ID: {offset}')
        return offset    
    
    def getOneUpdate(self, offset):
        updates = None
        print('awaiting update...')
        while not updates:
            time.sleep(1)
            call = requests.get(f'https://api.telegram.org/bot{token}/getUpdates?offset='+str(offset))
            updates = call.json().get('result')
        self.offset = int(updates[-1].get('update_id'))+1
        return updates[-1]
    
    def getUpdates(self):
        call = requests.get(f'https://api.telegram.org/bot{token}/getUpdates?offset='+str(self.offset))
        result = call.json().get('result')
        if result:
            self.offset = int(result[-1].get('update_id'))+1
            return result
        
    def checkForEvents(self, update):
        if update.chat_id == '228334796' and update.text == 'closeRiddle': activeRiddle.close()
        
        if update.chatType == 'private' and update.text == activeRiddle.correctAnswer:
            if update.sender not in activeRiddle.winners: 
                self.sendMessage(update.chat_id, 'Молодей! Победа!')
                activeRiddle.reduceReward(update.sender)
            else: self.sendMessage(update.chat_id, 'Тебе за это задание уже заправили!')
            
        elif update.chatType == 'private': self.sendMessage(update.chat_id, 'Ноуп')
            
        if update.chatType in ('group','supergroup'):
            if update.text == 'шифр' and activeRiddle.status == 'running': activeRiddle.run()
                
        if update.newMemberName:
            self.sendMessage(update.chat_id, f'Привет, {update.newMemberName}')
            if activeRiddle.status == 'running': activeRiddle.run()
            
        
    def sendMessage(self, chatId, text):
        self.getEndpoint('/sendMessage')
        self.buildSignature()
        call = requests.post(self.url, data={'chat_id':chatId,'text':text})
        print(f'Sent to {chatId}: {text}')
        
    def forwardMessage(self, fromChatId, toChatId, messageId):
        self.getEndpoint('/forwardMessage')
        self.buildSignature()
        call = requests.post(self.url, data={'chat_id':toChatId,'from_chat_id':fromChatId, 'message_id':messageId})
        print(f'Forwarded message {messageId} to {toChatId}')

if __name__ == '__main__':
    print(f'Token Initialized: {token}')
    bot = CipherBot(False, token)
    while True:
        activeRiddle = Riddle()
        while activeRiddle.status == 'running':
            try:
                time.sleep(1)
                bot.update = Update(bot.getUpdates()[-1])
                bot.checkForEvents(bot.update)
            except TypeError:
                pass
       
    
