#!/usr/bin/env python
# coding: utf-8

# In[123]:


import requests
import random
import time
import json


token = ''
url = 'https://api.telegram.org/bot'

class Riddle:
    def __init__(self):
        self.scoreboard = {'Paralitiq': 4, 'alexoal': 4, 'SyksAxxx': 1, 'MedvedevDev': 3, 'Yuris_navigator': 5}
        self.winners = []
        self.reward = 1
        self.status = 'setup'
        self.question = self.getQuestion()
        print(f'Accepted Question: {self.question}')
        self.correctAnswer = self.getAnswer()
        print(f'Accepted Answer: {self.correctAnswer}')
        self.run()
        
    def getQuestion(self):
        bot.sendMessage(228334796, 'Ну, запиливай!')
        while True:
            update = Update(bot.getOneUpdate(bot.offset))
            if update.sender == 'Bpy6na' and update.chatType == 'private': return update.message_id
                
    def getAnswer(self):
        bot.sendMessage(228334796, 'Теперь ответ')
        while True:
            update = Update(bot.getOneUpdate(bot.offset))
            if update.sender == 'Bpy6na' and update.chatType == 'private': return update.text

    def run(self):
        bot.forwardMessage(228334796, -1001459707328, self.question)
        bot.sendMessage(-1001459707328, 'Напиши "шифр", и я повторю задание.')
        bot.sendMessage(-1001459707328, 'А ответы отправляй мне в личку!')
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
        bot.sendMessage(-1001459707328, 'Шифр разгадан! Победители:')
        for winner in self.winners: bot.sendMessage(-1001459707328, winner)
        bot.sendMessage(-1001459707328, f'{self.assembleScoreboard()}')
        self.winners = []

    def assembleScoreboard(self):
        scores = ''
        for key in self.scoreboard.keys(): scores += f'{key}: {str(self.scoreboard.get(key))} \n'
        return scores
        
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
        if self.sender and self.text: print(f'{self.sender}: {self.text}')  
           
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
        if update.chatType == 'private' and update.text == activeRiddle.correctAnswer:
            if update.sender not in activeRiddle.winners: 
                self.sendMessage(update.chat_id, 'Молодей! Победа!')
                activeRiddle.reduceReward(update.sender)
            else: self.sendMessage(update.chat_id, 'Тебе за это задание уже заправили!')
            
        elif update.chatType == 'private': self.sendMessage(update.chat_id, 'Ноуп')
            
        if update.sender == 'Bpy6na':
            if update.text == 'closeriddle': 
                print('Riddle closed by admin')
                activeRiddle.close()
            if update.text == 'editriddle':
                bot.sendMessage(-1001459707328, 'Внимание! Редактируются условия задания...')
                print('Editing riddle by admin request')
                activeRiddle.question = activeRiddle.getQuestion()
                print(f'Accepted Question:{activeRiddle.question}')
                activeRiddle.correctAnswer = activeRiddle.getAnswer()
                print(f'Accepted Answer:{activeRiddle.correctAnswer}')
                activeRiddle.run()
            if update.text == 'showscores':
                bot.sendMessage(update.chat_id, f'{activeRiddle.winners}')
                bot.sendMessage(update.chat_id, f'{activeRiddle.assembleScoreboard()}')
            
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
       
    


# In[ ]:





# In[ ]:



