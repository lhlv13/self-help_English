# -*- coding: utf-8 -*-
"""
Created on Sat Oct 29 16:46:40 2022

@author: Yuyi
@email: taichiyuyi@gmail.com
"""
import pygame
import pandas as pd
import time
import random
import copy
import numpy as np
import os 

if not os.path.isdir("./temp"):
    os.mkdir("./temp")

if not os.path.isdir("./backup"):
    os.mkdir("./backup")


class WordsData():
    """  """
    def __init__(self,  cfg_path="./set.cfg"):
        self.__config = {}       ## 配置
        self.__path = {}         ## 設置過的路徑
        self.dataframe = None  ## 儲存原始csv數據
        self.box = None        ## 儲存以box分類之數據
        self.chapter = None    ## 儲存以章節分類之數據
        self.__initSetting(cfg_path)
        pass
    
    
    def __initSetting(self, cfg_path):
        """ 
        
        """
        ## 讀取設定檔
        self.__path["cfg_path"] = cfg_path
        self.__config = self.set_cfg(cfg_path)
        # print(self.__config)
        ## 讀取 xlsx 檔
        temp_elsx = pd.read_excel(self.__config["file_path"])
        # print(temp_elsx)
        ## 另存一份正在使用的csv (根據以往經驗 直接操作xlsx 很容易會檔案損壞)
        csv_path = "./temp/all_words.csv"
        temp_elsx.to_csv(csv_path,encoding="utf_8_sig", index=False)
        
        ## 讀取剛剛另存的 csv
        df, box, chapter = self.read_csv(csv_path)      
        # print(len(chapter["第1組"]))
        self.dataframe = df
        self.box = box         ##  [0:[], 1:[], 2:[], 3:[], 4:[]] 
        self.chapter = chapter ##  ["第0章" : [], ... ]
        
    def getConfig(self):
        return self.__config 
    
    def getPath(self):
        return self.__path 
    
    def set_cfg(self, cfg_path):
        ''' 
            讀取 cfg 檔案並配置參數
            path, font_name, WIDTH, HEIGHT, other_language_size, chinese_size
        '''
        parameters = {}
        with open(cfg_path,"r") as obj:
            datas = obj.readlines()
        for i in range(len(datas)):
            if(datas[i][0]=="\n"):
                continue
            key_value= datas[i].strip().split("=")
            key = key_value[0].strip()
            value = key_value[1].strip()
            parameters[key] = eval(value) if value.isdigit() else value
            
        return parameters
           
    
    def read_csv(self, path):
        box = {}
        count = 1
        title = f"第{count}章"
        chapter = {title:[]}
        for i in range(5):
            box[i] = []
        df = pd.read_csv(path).fillna(0).to_numpy()[:,:7]
        for i in range(len(df)):
            if not str(df[i][0]).isdigit():
                count += 1
                title = f"第{count}章"
                chapter[title] = []
                continue
            box[int(df[i][-1])].append(copy.deepcopy(df[i]))
            chapter[title].append(copy.deepcopy(df[i]))
            
        return df, box, chapter  
    
    def save_excel(self, file_path, df):
        df = pd.DataFrame(df)
        df.columns = ["Index", "Words", "CH", "Part", "Correct", "Error", "Box"]
        df.to_excel(file_path,encoding="utf_8_sig", index=False)


class WordsInterface(WordsData):
    """ """
    def __init__(self, WIDTH=800, HEIGHT=600, screen_title="Box", font_name="arial"):
        super(WordsInterface, self).__init__("./set.cfg")
        self.__config = self.getConfig()
        
        pygame.init()
        pygame.display.set_caption(self.__config["screen_title"])
        
        self.WIDTH = int(self.__config["width"])
        self.HEIGHT = int(self.__config["height"])
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_name = self.__config["font_name"]  ## 字形
        
        ##
        self.__words = None
        self.__box_i = None
        self.__index = None
        self.__isShow = False
        self.__count = 1
        self.__box_counts = []  ## 紀錄每個箱子的數量，用以控制機率
        
        for i in range(len(self.box)):
            self.__box_counts.append(len(self.box[i]))
        
    
    
    def draw_text(self, text, size, x=None, y=None, color=(255, 0, 0)):
        x = self.WIDTH/2 if x==None else x
        y = self.HEIGHT/2 if y==None else y
        
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        
        self.screen.blit(text_surface, text_rect)
        
        
    def draw_text_left_up(self, text, size, x=None, y=None, color=(255, 0, 0)):
        x = self.WIDTH/2 if x==None else x
        y = self.HEIGHT/2 if y==None else y
        
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.x = x
        text_rect.y = y
        
        self.screen.blit(text_surface, text_rect)
    
    def setGrid(self, grid=12):
        x, y = self.WIDTH, self.HEIGHT
        size = x if x < y else y
        x = x // (grid + 1)
        y = y // (grid + 1)
        font_size = size // 10
        return x, y, font_size
    
    def getNum(self, key_pressed):
        if key_pressed[pygame.K_0] or key_pressed[pygame.K_KP0]:
            return "0"
        elif key_pressed[pygame.K_1] or key_pressed[pygame.K_KP1]:
            return "1"
        elif key_pressed[pygame.K_2] or key_pressed[pygame.K_KP2]:
            return "2"
        elif key_pressed[pygame.K_3] or key_pressed[pygame.K_KP3]:
            return "3"
        elif key_pressed[pygame.K_4] or key_pressed[pygame.K_KP4]:
            return "4"
        elif key_pressed[pygame.K_5] or key_pressed[pygame.K_KP5]:
            return "5"
        elif key_pressed[pygame.K_6] or key_pressed[pygame.K_KP6]:
            return "6"
        elif key_pressed[pygame.K_7] or key_pressed[pygame.K_KP7]:
            return "7"
        elif key_pressed[pygame.K_8] or key_pressed[pygame.K_KP8]:
            return "8"
        elif key_pressed[pygame.K_9] or key_pressed[pygame.K_KP9]:
            return "9"
        elif key_pressed[pygame.K_BACKSPACE]:
            return "BACKSPACE"
        else:
            return None
    
    
    def showInfo(self, correct, error, box, number):
        x, y, size = self.setGrid(grid = 12)
        self.draw_text(f"correct : {correct:>.0f}", 30, x=120, y=self.HEIGHT-70, color=(240,240,0))
        self.draw_text(f"error : {error:>.0f}", 30, x=self.WIDTH-120, y=self.HEIGHT-70, color=(240,240,0))
        self.draw_text_left_up(f"Box : {box+1:>.0f}", 30, x=20, y=10, color=(240,240,0)) ## 1~5
        self.draw_text_left_up(f"Number : {number:>.0f}", 30, x=20, y=50, color=(240,240,0))
        pass
    
    def showPracticeInfo(self, word_num):
        x, y, size = self.setGrid(grid = 12)
        self.draw_text_left_up(f"The Remaining Amount: {word_num}", size=30, x=x, y=y*11, color=(240,240,0))
    
    def showMain(self, word):
        x, y, _ = self.setGrid(grid = 12)
        en, ch, part = word[1], word[2], word[3]
        self.draw_text(en, size=self.__config["other_language_size"], x=self.WIDTH//2, y=y*5, color=(240,240,0))
        if self.__isShow:
            self.draw_text(f"{ch} ({part})", size=self.__config["chinese_size"], x=self.WIDTH//2, y=y*9, color=(240,240,0))
            
        pass
    
    
    def save(self):
        self.save_excel(self.__config["file_path"], self.dataframe)
        self.save_excel("./backup/all_words.xlsx", self.dataframe)
    
    def __movePreviousBox(self):
        if self.__box_i == 0:
            return 
        
        ## 修改csv檔
        index = self.findIndex(self.box[self.__box_i][self.__index][0])
        if index:
            self.dataframe[index][5] += 1
            self.dataframe[index][6] -= 1
        ## 修凱箱子內容
        self.box[self.__box_i][self.__index][5] += 1
        self.box[self.__box_i][self.__index][6] -= 1
          
        ## 移動箱子
        word = copy.deepcopy(self.box[self.__box_i][self.__index])
        self.box[self.__box_i].pop(self.__index)
        self.box[self.__box_i - 1].append(word)
        self.__box_counts[self.__box_i] -= 1
        self.__box_counts[self.__box_i - 1] += 1
        
            
    
    def __moveNextBox(self):
        if self.__box_i == 4:
            return
        ## 修改csv檔 
        index = self.findIndex(self.box[self.__box_i][self.__index][0])
        if index:
            self.dataframe[index][4] += 1
            self.dataframe[index][6] += 1
        
        ## 修改箱子內容
        self.box[self.__box_i][self.__index][4] += 1
        self.box[self.__box_i][self.__index][6] += 1
        
        
        ## 移動箱子
        word = copy.deepcopy(self.box[self.__box_i][self.__index])
        self.box[self.__box_i].pop(self.__index)
        self.box[self.__box_i + 1].append(word)
        self.__box_counts[self.__box_i] -= 1
        self.__box_counts[self.__box_i + 1] += 1
    
    def findIndex(self, num):
        size = len(self.dataframe)
        for i in range(size):
            if self.dataframe[i][0] == num:
                return i
        return None
    
    def __menuMode(self, key_pressed):
        """ """
        ## 顯示
        x, y, size = self.setGrid(grid = 3)
        self.draw_text("章節練習模式 (C)", size=size, x=x*2, y=y, color=(255, 255, 255))
        self.draw_text("箱子練習模式 (B)", size=size, x=x*2, y=y*2, color=(255, 255, 255))
        self.draw_text("遺忘曲線模式 (F)", size=size, x=x*2, y=y*3, color=(255, 255, 255))
        
        if key_pressed[pygame.K_c]:
            return "chapter"
        elif key_pressed[pygame.K_b]:
            return "box"
        elif key_pressed[pygame.K_f]:
            return "fc"  ## 遺忘曲線模式
        else:
            return "menu"
    
    
    
    
    def __chapterMode(self, key_pressed, is_init, CH, time_list):
        if is_init:
            x, y, size = self.setGrid(grid = 3)
            num = self.getNum(key_pressed)
            if num:
                ## 防止彈跳
                time_list[1] = time.time()
                if (time_list[1] - time_list[0]) > 0.5 :
                    if num == "BACKSPACE": ## 刪除
                        CH = CH[:-1]
                    else: 
                        CH += num 
                    time_list[0] = time.time()
                
            self.draw_text("請輸入練習章節 : ", size=size, x=x*2, y=y, color=(255, 255, 255))
            self.draw_text(f">> {CH}", size=size, x=x*2, y=y*2, color=(255, 255, 255))
            if key_pressed[pygame.K_RETURN]:  ## 離開
                try:
                    self.__words = copy.deepcopy(self.chapter[f"第{CH}章"])
                    self.__index = random.randint(0, len(self.__words)-1)
                    self.__isShow = False
                    is_init = False
                except:
                    CH = ""
                    
        
                    
        else:
            if len(self.__words) == 0 or key_pressed[pygame.K_m]:
                is_init = True
                CH = ""
                return "menu", is_init, CH, time_list
            
            word = self.__words[self.__index]
            self.showMain(word)      ## 顯示英文
            self.showPracticeInfo(len(self.__words))
            if key_pressed[pygame.K_SPACE]: ## 顯示中文
                self.__isShow = True
            
            if self.__isShow:
                if key_pressed[pygame.K_d]:
                    self.__index = random.randint(0, len(self.__words)-1)
                    self.__isShow = False
                elif key_pressed[pygame.K_a]:
                    self.__words.pop(self.__index)
                    if len(self.__words) > 0:
                        self.__index = random.randint(0, len(self.__words)-1)
                    self.__isShow = False
                
        return "chapter", is_init, CH, time_list
    
    def __boxMode(self, key_pressed, is_init, BOX, time_list):
        if is_init:
            x, y, size = self.setGrid(grid = 3)
            num = self.getNum(key_pressed)
            if num:
                ## 防止彈跳
                time_list[1] = time.time()
                if (time_list[1] - time_list[0]) > 0.5 :
                    if num == "BACKSPACE": ## 刪除
                        BOX = BOX[:-1]
                    else: 
                        BOX += num 
                    time_list[0] = time.time()
            
            self.draw_text("請輸入 Box Number : ", size=size, x=x*2, y=y, color=(255, 255, 255))
            self.draw_text(f">> {BOX}", size=size, x=x*2, y=y*2, color=(255, 255, 255))
            if key_pressed[pygame.K_RETURN]:  ## 離開
                try:
                    self.__words = copy.deepcopy(self.box[eval(BOX)-1])
                    self.__index = random.randint(0, len(self.__words)-1)
                    self.__isShow = False
                    is_init = False
                except:
                    BOX = ""
                    
        
                    
        else:
            if len(self.__words) == 0 or key_pressed[pygame.K_m]:
                is_init = True
                BOX = ""
                return "menu", is_init, BOX, time_list
            
            word = self.__words[self.__index]
            self.showMain(word)      ## 顯示英文
            self.showPracticeInfo(len(self.__words))
            if key_pressed[pygame.K_SPACE]: ## 顯示中文
                self.__isShow = True
            
            if self.__isShow:
                if key_pressed[pygame.K_d]:
                    self.__index = random.randint(0, len(self.__words)-1)
                    self.__isShow = False
                elif key_pressed[pygame.K_a]:
                    self.__words.pop(self.__index)
                    if len(self.__words) > 0:
                        self.__index = random.randint(0, len(self.__words)-1)
                    self.__isShow = False
                    
                
        return "box", is_init, BOX, time_list
    
    def probability(self):
        """ self.__box_counts : 箱子內的個數"""
        total = sum(self.__box_counts[1:])
        if total < 100:
            return np.random.choice(np.array([0,1,2,3,4]), p=np.array([0.85, 0.05, 0.05, 0.03, 0.02]))
            
        
        else:
            return np.random.choice(np.array([0,1,2,3,4]), p=np.array([0.3, 0.25, 0.2, 0.15, 0.1]))
        
    
    def __forgetCurve(self, key_pressed, is_init):
        if is_init:
            while True:
                self.__box_i = self.probability()
                size = len(self.box[self.__box_i])
                if size == 0:
                    continue
                self.__index = random.randint(0, size-1)
                break
            is_init = False
        
        else:
            if key_pressed[pygame.K_m]:
                self.save()
                self.__count = 0
                return "menu", True
            word = self.box[self.__box_i][self.__index]
            en, ch, part, correct, error, bx =\
                word[1], word[2], word[3], word[4], word[5], word[6]
            self.showInfo(correct=correct, error=error, box=bx, number=self.__count)
            self.showMain(word)
            if key_pressed[pygame.K_SPACE]:
                self.__isShow = True
            
            if self.__isShow:
                if key_pressed[pygame.K_d]:  ## 答錯 移動到前一個箱子
                    self.__movePreviousBox()
                    is_init = True
                    self.__isShow = False
                    self.__count += 1 ## 計算目前回答單字量
                elif key_pressed[pygame.K_a]: ## 答對 
                    self.__moveNextBox()
                    is_init = True
                    self.__isShow = False
                    self.__count += 1 ## 計算目前回答單字量
        
            
        return "fc",  is_init   
    
    
    
    
    def run(self, FPS=30, other_language_size=90, chinese_size=60):
        is_running = True
        is_init = True
        choose = None
        CH = ""
        BOX = ""
        mode = "menu"
        time_list = [0, 0]
        time_list[0] = time.time()
        while is_running:
            self.clock.tick(FPS)
            ## 鍵盤
            key_pressed = pygame.key.get_pressed()
                
            for event in pygame.event.get(): ## 離開遊戲
                if event.type == pygame.QUIT:
                    if mode == "fc":
                        self.save()
                    is_running = False
                    
            
            
            ## 模式
            if mode == "menu":
                self.screen.fill(pygame.Color("black"))
                mode = self.__menuMode(key_pressed)
            
            elif mode == "chapter":
                self.screen.fill(pygame.Color("black"))
                mode, is_init, CH, time_list = self.__chapterMode(key_pressed, is_init, CH, time_list)
            
            elif mode == "box":
                self.screen.fill(pygame.Color("black"))
                mode, is_init, BOX, time_list = self.__boxMode(key_pressed, is_init, BOX, time_list)
            
            elif mode == "fc":
                self.screen.fill(pygame.Color("black"))
                mode, is_init = self.__forgetCurve(key_pressed, is_init)
                pass
            
            pygame.display.update()
        pygame.quit()        
        pass

def main():
    game = WordsInterface().run()
    pass


if __name__ == "__main__":
    main()