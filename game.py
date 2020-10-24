import pygame as pg
import pygame.mixer
import threading
import math
import time

Thread = threading.Thread
Event = threading.Event

pg.init()

#screen = pg.display.set_mode((900, 600))
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
WINDOW_SIZE = (900, 600)

FONT = pg.font.Font(None, 32)
color = (225, 225, 225)
blue = (0, 0, 128)
white = (255, 255, 255)
green = (0, 255, 0)
red = (255, 0, 0)
black = (0, 0, 0)
yellow = ((255,255,0))
speed = [2, 0]

class MyThread(Thread):
    def __init__(self, event, func, seconds=1.0):
        Thread.__init__(self)
        self.stopped = event
        self.func = func
        self.seconds = seconds
    def run(self):
        while not self.stopped.wait(self.seconds):
            self.func()
    

class InputBox:

    """
    x => x position,
    y the y position 
    w width of the input
    h height of the input
    text the text on the input box
    """
    def __init__(self, x, y, w, h, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    self.text = ''
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode # text = ""; enter r key text = "r"; enter a text="ra"
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+20))
        # Blit the rect.
        pg.draw.rect(screen, self.color, self.rect, 2)

class Button():
    def __init__(self, color, x,y,width,height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self,win,outline=None):
        #Call this method to draw the button on the screen
        if outline:
            pg.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pg.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.text != '':
            font = pg.font.SysFont('comicsans', 20)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))
    def setText(self, text):
        self.text = text

    def setColor(self, color):
        self.color = color

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False
    def deepCopy(self):
        return Button(self.color, self.x, self.y, self.width, self.height)

class Line():
    def __init__(self, x, y, w_h, is_w):
        self.x = x
        self.y = y
        self.w_h = w_h
        self.is_w = is_w
    
    def isParallel(self, line):
        return self.is_w == line.is_w

    def isCrossed(self, line):
        verticalLine = None
        horizontalLine = None

        if self.isParallel(line):
            return False


        if not self.is_w:
            verticalLine = self
            horizontalLine = line
        else:
            horizontalLine = self
            verticalLine = line
        
        if verticalLine.x > horizontalLine.x and verticalLine.x < horizontalLine.x + horizontalLine.w_h and verticalLine.y < horizontalLine.y and verticalLine.y + verticalLine.w_h > horizontalLine.y:
            return True
        return False
    def toString(self):
        return "x: " + str(self.x) + " y: " + str(self.y) + " w_h: " + str(self.w_h) + " is_w: " + str(self.is_w)

class Text():
    def __init__(self, fontName, fontSize, text, pos, textColor):
        self.textColor = textColor
        self.font = pg.font.Font(fontName, fontSize)
        self.text = self.font.render(text, True,  textColor, color)
        self.textRect = self.text.get_rect()
        self.textRect.center = pos
    def draw(self, screen):
        screen.blit(self.text, self.textRect)
    def setText(self, text):
        self.text = self.font.render(text, True,  self.textColor, color)

class Bullet():
    def __init__(self, pos, angle):
        self.isFinished = False
        self.width = 5
        self.height = 10
        self.pos = pos
        self.angle = angle
        self.bulletBut = Button(black, self.pos[0], self.pos[1], self.width, self.height, '')
    def shoot(self, screen):
        if not self.isFinished:
            self.bulletBut.draw(screen, black)
    def move(self, speed):
        # 0 up, 90 left, 180 down, 270 right
        if self.angle == 0:
            self.pos[1] = self.pos[1] - speed
        elif self.angle == 180:
            self.pos[1] = self.pos[1] + speed
        elif self.angle == 90:
            self.pos[0] = self.pos[0] - speed
        else:
            self.pos[0] = self.pos[0] + speed
        self.bulletBut = Button(black, self.pos[0], self.pos[1], self.width, self.height, '')
        
class BulletManager():
    def __init__(self, screen):
        self.bullets = []
        self.screen = screen
    def addBullet(self, bullet):
        self.bullets.append(bullet)
    def display(self, speed):
        for bullet in self.bullets: # 200, 100, 500, 480
            if (bullet.pos[0] < 200 or bullet.pos[0] > 700 or bullet.pos[1] < 100 or bullet.pos[1] > 580) and not bullet.isFinished:
                bullet.isFinished = True
            if not bullet.isFinished:
                bullet.move(speed)
                bullet.shoot(self.screen)
    

class Window:
    def __init__(self, nextW, wType, size=WINDOW_SIZE):
        self.next = nextW
        self.type = wType
        self.screen = pg.display.set_mode(size)

    def getDataFromFile(self, username, dataFile):
        f = open(dataFile, 'r')
        for line in f:
            data = line.rstrip("\n").split(",")
            if data[0] == username:
                return data[1]
        return 0
    
    def updateData(self, username, data, dataFile):
        f = open(dataFile, 'r')
        lines = []
        for line in f:
            lines.append(line)
        f.close()
        print(lines)
        g = open(dataFile, 'w')

        isNewUser = True
        for l in lines:
            lineData = l.rstrip("\n").split(",")
            print(lineData, lineData[0] == username)
            if lineData[0] == username:
                isNewUser = False
                g.write(username+','+str(data)+"\n")
            else:
                g.write(l)
        if isNewUser:
            g.write(username+','+str(data)+"\n")
        g.close()
    def addScores(self, username, scores):
        f = open('scores.csv', 'r')
        lines = []
        isScore = True
        for line in f:
            print(isScore)
            data = line.rstrip("\n").split(",")
            print(data)
            if int(scores) > int(data[1]) and isScore:
                isScore = False
                lines.append(username+','+str(scores)+"\n")
            lines.append(line)
        
        if isScore and len(lines) < 10:
            lines.append(username+','+str(scores)+"\n")
        
        f.close()

        g = open('scores.csv', 'w')

        lineLength = 10

        if len(lines) < 10:
            lineLength = len(lines)
        
        for i in range(lineLength):
            g.write(lines[i])
        g.close()







class InstructionWindow(Window):
    def __init__(self):
        Window.__init__(self, '', 'instruct')
        self.font  = pg.font.Font('freesansbold.ttf', 17)
        self.next_button = Button(green, 750, 500, 100, 20, "NEXT")
        self.back_button = Button(green, 400, 500, 100, 20, "BACK")
        
        self.slides = ['images/slide1.welcome.jpeg', 'images/slide2.controller.jpeg', 'images/slide3.robotmovement.jpeg', 'images/slide4.rotation.jpeg', 'images/slide5.keyboardrotation.jpeg', 'images/slide6.happyracing.jpeg']
        self.slidesText = [slide1Text, slide2Text, slide3Text, slide4Text, slide5Text, slide6Text]
        self.slidePos = 0
    def display(self):
        self.screen.fill(color)
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                if (event.pos[0] >= 750 and event.pos[0] <= event.pos[0] <= 850 and event.pos[1] >= 500 and event.pos[1] <= 520): #checkinmg if the user clicks the next button
                    if self.slidePos == 4:
                        self.next_button.setText('QUIT')
                        self.next_button.setColor(red)
                    if self.slidePos >= 5: # Checking if it is the last slide
                        self.next = 'menu'
                    else:
                        self.slidePos = self.slidePos + 1
                    
                if (event.pos[0] >= 400 and event.pos[0] <= event.pos[0] <= 500 and event.pos[1] >= 500 and event.pos[1] <= 520): #checkinmg if the user clicks the back button
                    if self.slidePos > 0:
                        self.slidePos = self.slidePos - 1
                    if self.next_button.text == 'QUIT':
                        self.next_button.setText('NEXT')
                        self.next_button.setColor(green)
                    
            if event.type == pg.QUIT:
                pg.quit()
        #self.ballrect = self.image.get_rect()
        self.next_button.draw(self.screen, black)
        self.back_button.draw(self.screen, black)
        self.slidesText[self.slidePos](self.screen)

        #ballrect.center = (0, 0)
        image = pg.image.load(self.slides[self.slidePos])
        image = pg.transform.scale(image, (350, 600))

        ballrect = image.get_rect()
        self.screen.blit(image, ballrect)
        pg.display.flip()

class MainMenuWindow(Window):
    def __init__(self, username):
        Window.__init__(self, '', 'menu')
        self.coins = int(self.getDataFromFile(username, 'coins.csv'))
        self.ammo = int(self.getDataFromFile(username, 'ammo.csv'))
        self.font  = pg.font.Font('freesansbold.ttf', 17)
        self.solo_button = Button(green, 100, 200, 200, 40, "SOLO MODE")
        self.compete_button = Button(green, 100, 300, 200, 40, "COMPETE MODE")
        self.username_text = Text('freesansbold.ttf', 17, username, (100, 60), black)
        self.leader_board = Text('freesansbold.ttf', 24, 'LEADER BOARD', (650, 200), black)

        self.coins_text = Text('freesansbold.ttf', 17, 'COINS: ' + str(self.coins), (220, 60), black)
        self.ammo_text = Text('freesansbold.ttf', 17, 'AMMO: ' + str(self.ammo), (330, 60), black)

        self.shop_button = Button(green, 550, 50, 100, 50, "SHOP")
        self.i_button = Button(green, 660, 50, 100, 50, "I")
        self.sound_button = Button(green, 770, 50, 100, 50, "SOUND")
        pg.mixer.init()
        pg.mixer.music.load('gamesound.ogg')
        self.mCounter = 0
        
    def getScores(self):
        f = open('scores.csv', 'r')
        lines = []
        for line in f:
            data = line.rstrip("\n").split(",")
            lines.append(data)
        f.close()
        return lines

    def display(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                if (event.pos[0] >= 100 and event.pos[0]  <= 300 and event.pos[1] >= 200 and event.pos[1] <= 240): #checkinmg if the user clicks the back button
                    self.next = 'solo'
                elif (event.pos[0] >= 100 and event.pos[0]  <= 300 and event.pos[1] >= 300 and event.pos[1] <= 340): #checkinmg if the user clicks the back button
                    self.next = 'compete'
                elif (event.pos[0] >= 550 and event.pos[0]  <= 650 and event.pos[1] >= 50 and event.pos[1] <= 100):
                    self.next = 'shop'
                # on click of the sound button
                elif (event.pos[0] >= 770 and event.pos[0]  <= 870 and event.pos[1] >= 50 and event.pos[1] <= 100):
                    if self.mCounter == 0:
                        pg.mixer.music.play(-1)
                    elif self.mCounter%2 == 1:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                    self.mCounter+=1

                elif (event.pos[0] >= 660 and event.pos[0]  <= 760 and event.pos[1] >= 50 and event.pos[1] <= 100):
                    self.next = "instruct"
            if event.type == pg.QUIT:
                pg.quit()

        self.screen.fill(color)
        self.compete_button.draw(self.screen, (0,0,0))
        self.solo_button.draw(self.screen, (0,0,0))
        self.shop_button.draw(self.screen, (0,0,0))
        self.username_text.draw(self.screen)
        self.coins_text.draw(self.screen)
        self.ammo_text.draw(self.screen)
        self.i_button.draw(self.screen, (0,0,0))
        self.sound_button.draw(self.screen, (0,0,0))
        self.leader_board.draw(self.screen)
        yValue = 230
        for score in self.getScores():
            Text('freesansbold.ttf', 17, score[0] + ': ' + score[1], (650, yValue), black).draw(self.screen)
            yValue+=25
        
        pg.display.flip()
        #pg.display.update()

class LoginWindow(Window):
    def __init__(self):
        Window.__init__(self, '', 'login')
        self.fail = False
        self.input_box1 = InputBox(350, 200, 200, 50) 
        self.input_box2 = InputBox(350, 300, 200, 50)

        self.input_boxes = [self.input_box1, self.input_box2]
        self.button = Button(green, 350, 400, 200, 50, "ENTER")

        self.title = Text('freesansbold.ttf', 32, 'ROBOT RACE', (450, 50), black) # Username label 
        self.username_text = Text('freesansbold.ttf', 22, 'Enter Username', (450, 200), black) # Username label  
        self.password_text = Text('freesansbold.ttf', 22, 'Enter Password', (450, 300), black) # Password label
        self.error_text = Text('freesansbold.ttf', 22, 'Invalid username or password', (450, 100), red) # error message
    def display(self):
        self.screen.fill(color)
        for event in pg.event.get(): 
                if event.type == pg.MOUSEBUTTONDOWN:
                    if (event.pos[0] >= 350 and event.pos[0] <= event.pos[0] <= 550 and event.pos[1] >= 400 and event.pos[1] <= 450): #checkinmg if the user clicks the button
                        f = open("user.csv", "r")
                        count =  0
                        skipFirstLine = 0
                        for line in f:
                            if skipFirstLine != 0:
                                data = line.rstrip("\n").split(",")
                                if data[0] == self.input_box1.text and data[1] == self.input_box2.text:
                                    count+=1
                                    break
                            skipFirstLine+=1
                        f.close()
                        if count == 0:
                            self.fail = True
                        else:
                            data = self.getDataFromFile(self.input_box1.text, 'last_login.csv')
                            if int(data) == 0:
                                self.next = 'instruct'
                                self.updateData(self.input_box1.text, 1, 'last_login.csv')
                            else:
                                self.next = 'menu'
                            
                if event.type == pg.QUIT:
                    done = True
                for box in self.input_boxes:
                    box.handle_event(event)
        for box in self.input_boxes:
            box.update()
            
        if self.fail:
            self.error_text.draw(self.screen)

        for box in self.input_boxes:
            box.draw(self.screen)
        self.button.draw(self.screen, (0, 0, 0))
        self.title.draw(self.screen)
        self.username_text.draw(self.screen)
        self.password_text.draw(self.screen)
        pg.display.flip() # It makes all the components will have drawn on the windows appears

class SoloModeWindow(Window):                                
    def __init__(self, username, modeType):
        Window.__init__(self, '', modeType)
        self.username = username
        self.numCoins = int(self.getDataFromFile(username, 'coins.csv'))
        self.numAmmo = int(self.getDataFromFile(username, 'ammo.csv'))
        self.timer = Text('freesansbold.ttf', 22, '', (450, 50), black)
        self.countDown = 3
        self.counter = Text('freesansbold.ttf', 22, str(self.countDown), (600, 50), red)
        self.player = Text('freesansbold.ttf', 17, username, (80, 100), black)
        self.scoresCount = 0
        self.score = Text('freesansbold.ttf', 17, 'SCORES: 0', (80, 250), black)
        self.coins = Text('freesansbold.ttf', 17, 'COINS: ' + str(self.numCoins), (80, 350), black)
        self.ammo = Text('freesansbold.ttf', 17, 'AMMO: ' + str(self.numAmmo), (80, 150), black)
        self.button = Button(yellow, 720, 25, 150, 50, "PAUSE")
        self.maze_space = Button(color, 200, 100, 500, 480, '')
        self.end_space = Button(color, 200, 100, 20, 30)
        self.displayAmmo = False

        self.obstacles1CurrentPos = [200, 350]
        self.obstacles1 = Button(black, self.obstacles1CurrentPos[0], self.obstacles1CurrentPos[1], 15, 20)

        self.maze_line1 = Button(black, 300, 170, 100, 2, '')
        self.maze_line2 = Button(black, 500, 100, 2, 72, '')
        self.maze_line3 = Button(black, 200, 242, 80, 2, '')
        self.maze_line4 = Button(black, 280, 242, 2, 80, '')
        self.maze_line5 = Button(black, 380, 240, 120, 2, '')

        self.maze_line6 = Button(black, 590, 172, 2, 78, '')
        self.maze_line7 = Button(black, 200, 400, 70, 2, '')
        self.maze_line8 = Button(black, 380, 400, 120, 2, '')

        self.maze_line9 = Button(black, 380, 320, 2, 80, '')
        self.maze_line10 = Button(black, 600, 320, 2, 80, '')

        self.maze_line11 = Button(black, 600, 400, 100, 2, '')

        self.maze_line12 = Button(black, 280, 508, 2, 72, '')
        self.maze_line13 = Button(black, 380, 508, 120, 2, '')
        self.maze_line14 = Button(black, 600, 508, 2, 72, '')
        self.maze_line15 = Button(black, 500, 322, 2, 80, '')


        # Third maze extra
        self.maze_line16 = Button(black, 400, 100, 2, 72, '')
        self.maze_line17 = Button(black, 300, 100, 2, 72, '')
        
        self.angle = 0 # 0 up, 90 left, 180 down, 270 right
        self.image = pg.image.load("images/robotproto.png")
        self.image = pg.transform.scale(self.image, (40, 40))
        self.image = pg.transform.rotate(self.image, self.angle)
        self.speed = int(self.getDataFromFile(username, 'current_speed.csv'))
        self.move_pos = [-1 * self.speed, 0]
        self.ballrect = self.image.get_rect()
        self.ballrect.center = (670, 565)
        self.timeCounter = 45
        self.flag = True
        self.stopFlag = Event()
        self.lasKeyPressed = ''
        self.level = 1
        self.currentPos = [655, 560]

        #self.currentPos = [295, 485]
        self.imageWidth = 28
        self.imageHeight = 16
        self.numCounter = 0
        self.robotBut = Button(black, self.currentPos[0], self.currentPos[1], self.imageWidth, self.imageHeight, '')
        self.isPause =  False
        self.exit = Button(red, 360, 280, 100, 40, 'EXIT')

        self.gameOverText = Text('freesansbold.ttf', 22, 'GAME OVER', (450, 200), red)
        self.resume = Button(yellow, 500, 280, 100, 40, 'RESUME')
        self.restart = Button(green, 440, 280, 50, 20, 'RESTART')
        self.isGameOver = False
        self.startTimer()

        self.bulletManager = BulletManager(self.screen)

        # Obstacles level
        self.obstacles1CurrentPos = [200, 350]
        self.obstacles1 = Button(black, self.obstacles1CurrentPos[0], self.obstacles1CurrentPos[1], 15, 20)

        self.obstacles2CurrentPos = [420, 100]
        self.obstacles2 = Button(black, self.obstacles2CurrentPos[0], self.obstacles2CurrentPos[1], 15, 20)

        self.obstacles3CurrentPos = [470, 580]
        self.obstacles3 = Button(black, self.obstacles3CurrentPos[0], self.obstacles3CurrentPos[1], 15, 20)

        self.obstacles4CurrentPos = [700, 350]
        self.obstacles4 = Button(black, self.obstacles4CurrentPos[0], self.obstacles4CurrentPos[1], 15, 20)

        # Variables for checking if obstacles has been shot
        self.isObstacle1BeenShotInCurrentLevel = False
        self.isObstacle2BeenShotInCurrentLevel = False
        self.isObstacle3BeenShotInCurrentLevel = False
        self.isObstacle4BeenShotInCurrentLevel = False

    def obstacleMovement(self):
        stopFlag = Event()
        thread = MyThread(stopFlag, self.moveObstacle, 0.05)
        thread.start()

    def moveForward(self):
        if self.level >= 3 and self.hasHitAnObstacle():
            self.isGameOver = True
        self.isCompleted()
        initialCurrentPos = [self.currentPos[0], self.currentPos[1]] #
        moveVal = [0, 0] #movement value initial
        if self.angle == 0:
            self.currentPos[1]  = self.currentPos[1] - self.speed #currentPos = [x, y]
            moveVal = [0, -1 * self.speed]
        elif self.angle == 180:
            self.currentPos[1] = self.currentPos[1] + self.speed
            moveVal = [0, 1 * self.speed]
        elif self.angle == 270:
            self.currentPos[0] = self.currentPos[0] + self.speed
            moveVal = [1 * self.speed, 0]
        elif self.angle == 90:
            self.currentPos[0] = self.currentPos[0] - self.speed
            moveVal = [-1 * self.speed, 0]
        if not self.hasHitAnyWalls():
            return moveVal
        else:
            self.currentPos = initialCurrentPos
            return [0, 0]
    
    def simulateMove(self, simulatedCurrentPos, direction):
        angle = self.angle

        if direction == 'LEFT':
            angle = (self.angle - 90)%360
        elif direction ==  'RIGHT':
            angle = (self.angle + 90)%360

        if angle == 0:
            simulatedCurrentPos[1]  = simulatedCurrentPos[1] - self.speed #currentPos = [x, y]
            return [0, -1 * self.speed]
        elif angle == 180:
            simulatedCurrentPos[1] = simulatedCurrentPos[1] + self.speed
            return [0, 1 * self.speed]
        elif angle == 270:
            simulatedCurrentPos[0] = simulatedCurrentPos[0] + self.speed
            return [1 * self.speed, 0]
        elif angle == 90:
            simulatedCurrentPos[0] = simulatedCurrentPos[0] - self.speed
            return [-1 * self.speed, 0]
    def simulateMoveBackward(self, simulatedCurrentPos, direction):
        angle = self.angle

        if direction == 'LEFT':
            angle = (self.angle - 90)%360
        elif direction ==  'RIGHT':
            angle = (self.angle + 90)%360

        
        if angle == 0:
            simulatedCurrentPos[1]  = simulatedCurrentPos[1] + self.speed #currentPos = [x, y])
            return [0,  self.speed]
        elif angle == 180:
            simulatedCurrentPos[1] = simulatedCurrentPos[1] - self.speed
            return [0, -1 * self.speed]
        elif angle == 270:
            simulatedCurrentPos[0] = simulatedCurrentPos[0] - self.speed
            return [-1 * self.speed, 0]
        elif angle == 90:
            simulatedCurrentPos[0] = simulatedCurrentPos[0] + self.speed
            return [self.speed, 0]
    
    def distanceFromEnd(self, pos):
        opp = pos[0] - 200 
        adj = pos[1] - 100

        return math.sqrt(opp*opp + adj*adj)
        
    def moveBackward(self):
        if self.level >= 3 and self.hasHitAnObstacle():
            self.isGameOver = True
        self.isCompleted()
        moveVal = [0, 0]
        initialCurrentPos = [self.currentPos[0], self.currentPos[1]]
        if self.angle == 0:
            self.currentPos[1] = self.currentPos[1] + self.speed
            moveVal = [0, 1 * self.speed]
        if self.angle == 180:
            self.currentPos[1] = self.currentPos[1] - self.speed
            moveVal = [0, -1 * self.speed]
        if self.angle == 270:
            self.currentPos[0] = self.currentPos[0] - self.speed
            moveVal = [-1 * self.speed, 0]
        if self.angle == 90:
            self.currentPos[0] = self.currentPos[0] + self.speed
            moveVal = [self.speed, 0]

        if not self.hasHitAnyWalls():
            return moveVal
        
        self.currentPos = initialCurrentPos
        return [0, 0]

    def generateLines(self, rect):
        lines = []
        l1 = Line(rect.x, rect.y, rect.width, True)
        lines.append(l1)
        lines.append(Line(rect.x, rect.y+rect.height, rect.width, True))
        lines.append(Line(rect.x, rect.y, rect.height, False))
        lines.append(Line(rect.x+rect.width, rect.y, rect.height, False))
        return lines

    def hasHitWall(self, wall, robot=None):
        if not robot:
            if self.angle == 0 or self.angle == 180:
                robotBut = Button(color, self.currentPos[0], self.currentPos[1], self.imageWidth, self.imageHeight)
            else:
                robotBut = Button(color, self.currentPos[0] + 8, self.currentPos[1] - 8,  self.imageHeight, self.imageWidth)
            self.robotBut = robotBut
        else:
            robotBut = robot
        
        robotLines = self.generateLines(robotBut)
        wallLines = self.generateLines(wall)

        cross = False
        for i in robotLines:
            for j in wallLines:
                if i.isCrossed(j):
                    return True
        return False
        

    # This method checks if a player or computer has completed a maze
    def isCompleted(self):
        if self.hasHitWall(self.end_space):
            self.timeCounter = 45
            self.numCoins +=1
            self.scoresCount +=1
            self.updateData(self.username, self.numCoins, 'coins.csv')
            self.level +=1
            self.ballrect.center = (670, 565)
            self.currentPos = [655, 560]

            self.isObstacle1BeenShotInCurrentLevel = False
            self.isObstacle2BeenShotInCurrentLevel = False
            self.isObstacle3BeenShotInCurrentLevel = False
            self.isObstacle4BeenShotInCurrentLevel = False
            return True
        return False
    
    """
    This checks if an item which can be something that we can shoot, basically
    a compete robot or an obstcles.

    itemType let's know the kind of item we are checking, either a compete robot
    or an obstacle. if itemType is 1(one) it obstacles 0(zero) for compete robot
    """
    def collidesWithBullets(self, item):
        for bullet in self.bulletManager.bullets:
            if not bullet.isFinished:
                if self.hasHitWall(bullet.bulletBut, item):
                    bullet.isFinished = True
                    return True
        return False

    def checkObstaclesCollisionWithBullets(self):
        counter = 0
        for obstacle in [self.obstacles1, self.obstacles2, self.obstacles3, self.obstacles4]:
            if self.collidesWithBullets(obstacle):
                if counter == 0:
                    self.isObstacle1BeenShotInCurrentLevel =  True
                    self.obstacles1CurrentPos = [200, 350]
                elif counter == 1:
                    self.isObstacle2BeenShotInCurrentLevel =  True
                    self.obstacles2CurrentPos = [420, 100]
                elif counter == 2:
                    self.isObstacle3BeenShotInCurrentLevel =  True
                    self.obstacles3CurrentPos = [470, 580]
                elif counter == 3:
                    self.isObstacle4BeenShotInCurrentLevel =  True
                    self.obstacles4CurrentPos = [700, 350]
        counter+=1

        
    def display(self):
        self.screen.fill(color)
        keys = pg.key.get_pressed()

        if keys[pg.K_q] and keys[pg.K_p] and not self.isPause and not self.isGameOver and self.countDown == 0:
            self.ballrect = self.ballrect.move(self.moveForward()) # 5 > 6

        if keys[pg.K_a] and keys[pg.K_l] and not self.isPause and not self.isGameOver and self.countDown == 0:
            self.ballrect = self.ballrect.move(self.moveBackward())

        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                # Onclick for the pause button
                if event.pos[0] >= 720 and  event.pos[0] <= 870 and event.pos[1] >= 25 and event.pos[1] <= 75:
                    if self.isPause:
                        self.button.setText("PAUSE")
                    else:
                        self.button.setText("RESUME")
                    self.isPause = not self.isPause

                # Onclick for the exit button
                if event.pos[0] >= 360 and  event.pos[0] <= 420 and event.pos[1] >= 280 and event.pos[1] <= 320: #360, 280, 60, 40
                    self.next = 'menu'
                
                # Onclick for resume or restart
                if event.pos[0] >= 500 and  event.pos[0] <= 600 and event.pos[1] >= 280 and event.pos[1] <= 320:
                    if self.isGameOver:
                        self.__init__(self.username, 'solo')
                    else:
                        self.isPause = False
                        self.button.setText('PAUSE')
                
                #500, 280, 100, 40
            if event.type == pg.QUIT:
                done = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_w and not self.isPause and not self.isGameOver and self.countDown == 0:
                    initialAngle = self.angle
                    self.angle = (self.angle+90)%360
                    if not self.hasHitAnyWalls():
                        self.image = pg.transform.rotate(self.image, 90)
                    else:
                        self.angle = initialAngle
                    
                if event.key == pg.K_o and not self.isPause and not self.isGameOver and self.countDown == 0:
                    initialAngle = self.angle
                    self.angle = (self.angle - 90)%360
                    if not self.hasHitAnyWalls():
                        self.image = pg.transform.rotate(self.image, -90)
                    else:
                        self.angle = initialAngle
                if event.key == pg.K_SPACE and not self.isPause and not self.isGameOver and self.countDown == 0 and self.numAmmo > 0:
                    self.bulletManager.addBullet(Bullet([self.currentPos[0], self.currentPos[1]], self.angle))
                    self.numAmmo -=1
                    self.updateData(self.username, self.numAmmo, 'ammo.csv')
                
                    
        # Updates the second maze by updating some of the maze walls
        if self.level > 1:
            # level 2
            self.maze_line13 = Button(black, 280, 508, 320, 2, '')
            self.maze_line9 = Button(black, 380, 240, 2, 160, '')
            self.maze_line15 = Button(black, 500, 242, 2, 160, '')

        self.timer.draw(self.screen)
        self.player.draw(self.screen)
        self.counter.setText(str(self.countDown))
        self.counter.draw(self.screen)
        self.score.draw(self.screen)
        self.coins.draw(self.screen)
        self.ammo.setText("AMMO: "+str(self.numAmmo))
        self.ammo.draw(self.screen)
        
        self.button.draw(self.screen, black)
        self.maze_space.draw(self.screen, black)
        self.maze_line1.draw(self.screen, black)
        self.maze_line2.draw(self.screen, black)
        self.maze_line3.draw(self.screen, black)
        self.maze_line4.draw(self.screen, black)
        self.maze_line5.draw(self.screen, black)
        self.maze_line6.draw(self.screen, black)
        self.maze_line7.draw(self.screen, black)
        self.maze_line8.draw(self.screen, black)
        self.maze_line9.draw(self.screen, black)
        self.maze_line10.draw(self.screen, black)
        self.maze_line11.draw(self.screen, black)
        self.maze_line12.draw(self.screen, black)
        self.maze_line13.draw(self.screen, black)
        self.maze_line14.draw(self.screen, black)
        self.maze_line15.draw(self.screen, black)
        if self.level > 2:
            self.maze_line17.draw(self.screen, black)
            self.maze_line16.draw(self.screen, black)
        
        self.end_space.draw(self.screen, black)
        self.coins.setText('COINS: ' + str(self.numCoins))
        self.score.setText('SCORES: ' + str(self.scoresCount))

        if self.level >= 3 and not self.isObstacle1BeenShotInCurrentLevel:
            self.obstacles1.draw(self.screen, black)
        
        if self.level >= 4 and not self.isObstacle2BeenShotInCurrentLevel:
            self.obstacles2.draw(self.screen, black) # up
        
        if self.level >= 5 and not self.isObstacle3BeenShotInCurrentLevel:
            self.obstacles3.draw(self.screen, black) # down

        if self.level >= 6 and not self.isObstacle4BeenShotInCurrentLevel:
            self.obstacles4.draw(self.screen, black) # right

        if self.isGameOver:
            self.gameOverText.draw(self.screen)
            self.exit.draw(self.screen, red)
            self.resume.setText('RESTART')
            self.resume.draw(self.screen, yellow)
        if self.isPause:
            self.exit.draw(self.screen, red)
            self.resume.draw(self.screen, yellow)
        self.robotBut.draw(self.screen, black)
        self.bulletManager.display(self.speed + (self.level*2))
       
        self.screen.blit(self.image, self.ballrect) 
        pg.display.flip()
    def startTimer(self):
        self.stopFlag = Event()
        thread = MyThread(self.stopFlag, self.updateTimer) # creates a path
        thread.start()
    def stopTimer(self):
        self.stopFlag.set()
    
    def moveObstacle(self):
        if self.isGameOver:
            self.stopTimer()
            return
        self.checkObstaclesCollisionWithBullets()
        if self.hasHitAnObstacle() and self.level >= 3:
            self.addScores(self.username, self.scoresCount)
            self.isGameOver = True
        if not self.isPause and not self.isGameOver:
            if self.obstacles1CurrentPos[0] > 700:
                self.obstacles1CurrentPos[0] = 200
            if self.obstacles2CurrentPos[1] > 580:
                 self.obstacles2CurrentPos[1] = 100
            if self.obstacles3CurrentPos[1] < 100:
                self.obstacles3CurrentPos[1] = 580
            if self.obstacles4CurrentPos[0] < 200:
                self.obstacles4CurrentPos[0] = 700

            self.obstacles1CurrentPos[0] = self.obstacles1CurrentPos[0] + self.speed + (self.level*2)
            self.obstacles2CurrentPos[1] = self.obstacles2CurrentPos[1] + self.speed + (self.level*2)
            self.obstacles3CurrentPos[1] = self.obstacles3CurrentPos[1] - self.speed + (self.level*2)
            self.obstacles4CurrentPos[0] = self.obstacles4CurrentPos[0] - self.speed + (self.level*2)
            self.obstacles1 = Button(black, self.obstacles1CurrentPos[0], self.obstacles1CurrentPos[1], 15, 20)
            self.obstacles2 = Button(black, self.obstacles2CurrentPos[0], self.obstacles2CurrentPos[1], 15, 20)
            self.obstacles3 = Button(black, self.obstacles3CurrentPos[0], self.obstacles3CurrentPos[1], 15, 20)
            self.obstacles4 = Button(black, self.obstacles4CurrentPos[0], self.obstacles4CurrentPos[1], 15, 20)
    
    def updateTimer(self):
        if not self.isPause and not self.isGameOver:
            self.timer.setText(str(self.timeCounter))
            self.timer.draw(self.screen)
            pg.display.flip()
            if self.isGameOver:
                self.stopTimer()
            if self.timeCounter == 0:
                self.stopTimer()
                self.addScores(self.username, self.scoresCount)
                self.isGameOver = True
            if self.countDown == 0:
                self.timeCounter -=1
            else:
                #
                self.countDown -=1
            
    
    def hasHitAnObstacle(self, robot=None):
        #compete
        if not robot:
            #computer => compete mode
            return self.hasHitWall(self.obstacles1, self.robotBut) or (self.hasHitWall(self.obstacles2, self.robotBut) and self.level > 3) \
            or (self.hasHitWall(self.obstacles3, self.robotBut) and self.level > 4) or (self.hasHitWall(self.obstacles4, self.robotBut) and self.level > 5)
    
        else:
            # player
            return self.hasHitWall(self.obstacles1, robot) or (self.hasHitWall(self.obstacles2, robot) and self.level > 3) \
            or (self.hasHitWall(self.obstacles3, robot) and self.level > 4) or (self.hasHitWall(self.obstacles4, robot) and self.level > 5)
    
    def hasHitAnyWalls(self, robot=None):
        walls = [self.maze_line1, self.maze_line2, self.maze_line3, self.maze_line4, self.maze_line5, self.maze_line6,
        self.maze_line7, self.maze_line8, self.maze_line9, self.maze_line10, self.maze_line11, self.maze_line12,
        self.maze_line13, self.maze_line14, self.maze_line15, self.maze_space]


        for wall in walls:
           if self.hasHitWall(wall, robot):
               return True
        return False




class CompeteModeWindow(SoloModeWindow):                         
    def __init__(self, username, modeType):
        SoloModeWindow.__init__(self, username, modeType)
        self.COMPUTER_WON = 1
        self.PLAYER_WON = 2

        self.computerScore = 0
        self.playerScore = 0
        self.computer = Text('freesansbold.ttf', 17, 'Computer', (780, 100), black)
        self.who_won = 0
        self.computerWonText = Text('freesansbold.ttf', 23, 'Computer Won', (450, 200), red)
        self.playerWonText = Text('freesansbold.ttf', 23, 'You Won', (450, 200), black)
        self.computer_score = Text('freesansbold.ttf', 17, 'SCORES: 0', (780, 250), black)
        self.playerCurrentPos = [615, 560]
        self.playerRobot = Button(black, self.playerCurrentPos[0], self.playerCurrentPos[1], self.imageWidth, self.imageHeight, '')
        self.playerAngle = 0
        self.playerImage = pg.image.load("images/robotproto.png")
        self.playerImage = pg.transform.scale(self.playerImage, (40, 40))
        self.playerImage = pg.transform.rotate(self.playerImage, self.angle)
        self.playerBallrect = self.playerImage.get_rect()
        self.playerBallrect.center = (630, 565)
        self.isComputerHitByABullet = False

    def display(self):
        self.screen.fill(color)
        keys = pg.key.get_pressed()
        if keys[pg.K_q] and keys[pg.K_p] and not self.isPause and not self.isGameOver and self.countDown == 0:
            self.playerBallrect = self.playerBallrect.move(self.movePlayerForward())

        if keys[pg.K_a] and keys[pg.K_l] and not self.isPause and not self.isGameOver and self.countDown == 0:
            self.playerBallrect = self.playerBallrect.move(self.movePlayerBackward())

        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            
            if event.type == pg.MOUSEBUTTONDOWN: #720, 25, 150, 50
                if event.pos[0] >= 720 and  event.pos[0] <= 870 and event.pos[1] >= 25 and event.pos[1] <= 75:
                    if self.isPause:
                        self.button.setText("PAUSE")
                    else:
                        self.button.setText("RESUME")
                    self.isPause = not self.isPause
                
                if event.pos[0] >= 360 and  event.pos[0] <= 420 and event.pos[1] >= 280 and event.pos[1] <= 320: #360, 280, 60, 40
                    self.next = 'menu'

                # Onclick for resume or restart
                if event.pos[0] >= 500 and  event.pos[0] <= 600 and event.pos[1] >= 280 and event.pos[1] <= 320:
                    if self.isGameOver:
                        self.__init__('Pythagoras', 'solo')
                    else:
                        self.isPause = False
                        self.button.setText('PAUSE')
            
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_w and not self.isPause and not self.isGameOver and self.countDown == 0:
                    initialAngle = self.angle
                    self.playerAngle = (self.playerAngle+90)%360
                    if not self.hasHitAnyWalls():
                        self.playerImage = pg.transform.rotate(self.playerImage, 90)
                    else:
                        self.playerAngle = initialAngle
                    
                if event.key == pg.K_o and not self.isPause and not self.isGameOver and self.countDown == 0:
                    initialAngle = self.playerAngle
                    self.playerAngle= (self.playerAngle - 90)%360
                    if not self.hasHitAnyWalls():
                        self.playerImage = pg.transform.rotate(self.playerImage, -90)
                    else:
                        self.playerAngle = initialAngle

                if event.key == pg.K_SPACE and not self.isPause and not self.isGameOver and self.countDown == 0 and self.numAmmo > 0:
                    self.bulletManager.addBullet(Bullet([self.playerCurrentPos[0], self.playerCurrentPos[1]], self.playerAngle))
                    self.numAmmo -=1
                    self.updateData(self.username, self.numAmmo, 'ammo.csv')

        self.timer.draw(self.screen)
        self.player.draw(self.screen)
        self.counter.setText(str(self.countDown))
        self.counter.draw(self.screen)
        self.score.draw(self.screen)
        self.coins.draw(self.screen)
        self.ammo.draw(self.screen)
        self.computer.draw(self.screen)
        self.computer_score.draw(self.screen)

        self.button.draw(self.screen, black)
        self.maze_space.draw(self.screen, black)
        self.maze_line1.draw(self.screen, black)
        self.maze_line2.draw(self.screen, black)
        self.maze_line3.draw(self.screen, black)
        self.maze_line4.draw(self.screen, black)
        self.maze_line5.draw(self.screen, black)
        self.maze_line6.draw(self.screen, black)
        self.maze_line7.draw(self.screen, black)
        self.maze_line8.draw(self.screen, black)
        self.maze_line9.draw(self.screen, black)
        self.maze_line10.draw(self.screen, black)
        self.maze_line11.draw(self.screen, black)
        self.maze_line12.draw(self.screen, black)
        self.maze_line13.draw(self.screen, black)
        self.maze_line14.draw(self.screen, black)
        self.maze_line15.draw(self.screen, black)
        self.end_space.draw(self.screen, black)
        self.coins.setText('COINS: ' + str(self.numCoins))
        self.computer_score.setText('SCORE: ' + str(self.computerScore))
        self.score.setText('SCORE: ' + str(self.playerScore))
        self.robotBut.draw(self.screen, black)
        self.playerRobot.draw(self.screen, black)
        self.counterStop = 0
        if self.level >= 3:
            self.obstacles1.draw(self.screen, black)

        if self.isGameOver:
            self.exit.draw(self.screen, red)
            self.resume.setText('RESTART')
            self.resume.draw(self.screen, yellow)
            if self.who_won == self.COMPUTER_WON:
                self.computerWonText.draw(self.screen)
            else:
                self.playerWonText.draw(self.screen)

        if self.isPause:
            self.exit.draw(self.screen, red)
            self.resume.draw(self.screen, yellow)
        if not self.isComputerHitByABullet:
            self.screen.blit(self.image, self.ballrect)
            self.screen.blit(self.playerImage, self.playerBallrect)
        self.bulletManager.display(self.speed)
        pg.display.flip()

    def isCompleted(self):
        isComputerCompleted = self.hasHitWall(self.end_space, self.robotBut)
        isPlayerCompleted = self.hasHitWall(self.end_space, self.playerRobot)

        if isComputerCompleted or isPlayerCompleted and not self.isGameOver:
            print("======>>>>>>>>>>>>>>>> Compete isComplete", self.isGameOver)
            if isComputerCompleted:
                self.computerScore +=1
                if self.computerScore == 3:
                    self.isGameOver = True
                    self.who_won = self.COMPUTER_WON
            if isPlayerCompleted:
                print(self.playerScore, 'Player score')
                self.playerScore +=1
                self.numCoins +=1
                self.updateData(self.username, self.numCoins, 'coins.csv')
                if self.playerScore == 3:
                    self.isGameOver = True
                    self.who_won = self.PLAYER_WON
            self.timeCounter = 45
            self.level +=1
            self.speed +=2
            self.ballrect.center = (670, 565)
            self.playerBallrect.center = (630, 565)
            self.currentPos = [655, 560]
            self.playerCurrentPos = [615, 560]
            self.isObstacle1BeenShotInCurrentLevel = False
            self.isObstacle2BeenShotInCurrentLevel = False
            self.isObstacle3BeenShotInCurrentLevel = False
            self.isObstacle4BeenShotInCurrentLevel = False
            self.isComputerHitByABullet = False
            return True
        return False
    def getMaxMovement(self):
        return 100//self.speed

    def movePlayerForward(self):
        if self.level >= 3 and self.hasHitAnObstacle(self.playerRobot):
            self.isGameOver = True
        self.isCompleted()
        initialCurrentPos = [self.playerCurrentPos[0], self.playerCurrentPos[1]] #
        moveVal = [0, 0] #movement value initial
        if self.playerAngle == 0:
            self.playerCurrentPos[1]  = self.playerCurrentPos[1] - self.speed #playerCurrentPos = [x, y]
            moveVal = [0, -1 * self.speed]
        elif self.playerAngle == 180:
            self.playerCurrentPos[1] = self.playerCurrentPos[1] + self.speed
            moveVal = [0, 1 * self.speed]
        elif self.playerAngle == 270:
            self.playerCurrentPos[0] = self.playerCurrentPos[0] + self.speed
            moveVal = [1 * self.speed, 0]
        elif self.playerAngle == 90:
            self.playerCurrentPos[0] = self.playerCurrentPos[0] - self.speed
            moveVal = [-1 * self.speed, 0]
        
        if self.playerAngle == 0 or self.playerAngle == 180:
            self.playerRobot = Button(black, self.playerCurrentPos[0], self.playerCurrentPos[1], self.imageWidth, self.imageHeight, '')
        else:
            self.playerRobot = Button(black, self.playerCurrentPos[0] + 8, self.playerCurrentPos[1] - 8, self.imageHeight, self.imageWidth, '')
        if not self.hasHitAnyWalls(self.playerRobot):
            return moveVal
        else:
            self.playerCurrentPos = initialCurrentPos
            return [0, 0]

    def movePlayerBackward(self):
        if self.level >= 3 and self.hasHitAnObstacle(self.playerRobot):
            self.isGameOver = True
        self.isCompleted()
        moveVal = [0, 0]
        initialCurrentPos = [self.playerCurrentPos[0], self.playerCurrentPos[1]]
        if self.playerAngle == 0:
            self.playerCurrentPos[1] = self.playerCurrentPos[1] + self.speed
            moveVal = [0, 1 * self.speed]
        if self.playerAngle == 180:
            self.playerCurrentPos[1] = self.playerCurrentPos[1] - self.speed
            moveVal = [0, -1 * self.speed]
        if self.playerAngle == 270:
            self.playerCurrentPos[0] = self.playerCurrentPos[0] - self.speed
            moveVal = [-1 * self.speed, 0]
        if self.playerAngle == 90:
            self.playerCurrentPos[0] = self.playerCurrentPos[0] + self.speed
            moveVal = [self.speed, 0]

        if self.playerAngle == 0 or self.playerAngle == 180:
            self.playerRobot = Button(black, self.playerCurrentPos[0], self.playerCurrentPos[1], self.imageWidth, self.imageHeight, '')
        else:
            self.playerRobot = Button(black, self.playerCurrentPos[0] + 8, self.playerCurrentPos[1] - 8, self.imageHeight, self.imageWidth, '')
        if not self.hasHitAnyWalls(self.playerRobot):
            return moveVal
        
        self.playerCurrentPos = initialCurrentPos
        return [0, 0]
    def computerPlayer(self):
        self.stopFlag = Event()
        thread = MyThread(self.stopFlag, self.selectMove, 0.05)
        thread.start()

    def selectMove(self):
        allDir = ['LEFT', 'RIGHT', 'FORWARD']
        possibleDir = []
        for direc in allDir:
            if self.angle == 90 and direc == 'LEFT' :
                canM = self.canMove('LEFT', self.currentPos) # return a set (Boolean, distance)
                if canM[0]:
                    possibleDir.append({'direc': 'LEFT', 'distance': canM[1]})
            elif self.angle == 0 and direc == 'RIGHT':
                canM = self.canMove('RIGHT', self.currentPos)
                if canM[0]:
                    possibleDir.append({'direc': 'RIGHT', 'distance': canM[1]})
            if direc == 'FORWARD':
                canM = self.canMove('FORWARD', self.currentPos)
                if canM[0]:
                    possibleDir.append({'direc': 'FORWARD', 'distance': canM[1]})
        direc = {}
        maxDistance = -1
        for d in possibleDir: # [{direct: 'L', 'distance': 300}, {direct: 'R', 'distance': 400}]
            if d['distance'] > maxDistance:
                direc = d #{direct: 'R', 'distance': 400}
                maxDistance = d['distance'] #300
        if self.collidesWithBullets(self.robotBut):
            self.isComputerHitByABullet = True
        if direc['direc'] == 'LEFT':
            initialAngle = self.angle
            self.angle = (self.angle - 90)%360
            if not self.hasHitAnyWalls() and not self.isPause and not self.isGameOver and self.countDown == 0:
                self.image = pg.transform.rotate(self.image, -90)
            else:
                self.angle = initialAngle
        elif direc['direc'] == 'RIGHT':
            initialAngle = self.angle 
            self.angle = (self.angle+90)%360
            if not self.hasHitAnyWalls() and not self.isPause and not self.isGameOver and self.countDown == 0:
                self.image = pg.transform.rotate(self.image, 90)
            else:
                self.angle = initialAngle
        else:
            if not self.isPause and not self.isGameOver and self.countDown == 0:
                self.ballrect = self.ballrect.move(self.moveForward())

        

    def canMove(self, direction, currentPos):
        simulatedCurrentPos = [currentPos[0], currentPos[1]]
        distance = 0
        
        if direction == 'FORWARD':
            distance = self.distanceFromEnd(simulatedCurrentPos)
            maxMovement = 2
            simulatedRobot = Button(color,  simulatedCurrentPos[0],  simulatedCurrentPos[1], self.imageWidth, self.imageHeight)
        else:
            distance = self.distanceFromEnd([simulatedCurrentPos[0] + 8,  simulatedCurrentPos[1] - 8])
            maxMovement = self.getMaxMovement()
            simulatedRobot = Button(color,  simulatedCurrentPos[0] + 8,  simulatedCurrentPos[1] - 8,  self.imageHeight, self.imageWidth)
    
        if self.hasHitAnyWalls(simulatedRobot):
            return (False, distance)
        for i in range(maxMovement):
            self.simulateMove(simulatedCurrentPos, direction)
            if direction == 'FORWARD':
                simulatedRobot = Button(color,  simulatedCurrentPos[0],  simulatedCurrentPos[1], self.imageWidth, self.imageHeight)
            else:
                simulatedRobot = Button(color,  simulatedCurrentPos[0] + 8,  simulatedCurrentPos[1] - 8,  self.imageHeight, self.imageWidth)
            if self.hasHitAnyWalls(simulatedRobot) or self.isTrapped(simulatedCurrentPos, direction):
                return (False, distance)
        return (True, distance)
    def competeObstacleMovement(self):
        stopFlag = Event()
        thread = MyThread(stopFlag, self.competeMoveObstacle, 0.05)
        thread.start()
    
    def competeMoveObstacle(self):
        if self.hasHitAnObstacle(self.playerRobot) and self.level >= 3:
            self.who_won = self.COMPUTER_WON
            self.addScores(self.username, self.scoresCount)
            self.isGameOver = True

        if self.hasHitAnObstacle() and self.level >= 3:
            self.who_won = self.PLAYER_WON
            self.addScores(self.username, self.scoresCount)
            self.isGameOver = True

        if not self.isPause and not self.isGameOver:
            if self.obstacles1CurrentPos[0] > 700:
                self.obstacles1CurrentPos[0] = 200
            if self.obstacles2CurrentPos[1] > 580:
                 self.obstacles2CurrentPos[1] = 100
            if self.obstacles3CurrentPos[1] < 100:
                self.obstacles3CurrentPos[1] = 580
            if self.obstacles4CurrentPos[0] < 200:
                self.obstacles4CurrentPos[0] = 700
            
            self.obstacles1CurrentPos[0] = self.obstacles1CurrentPos[0] + self.speed
            self.obstacles2CurrentPos[1] = self.obstacles2CurrentPos[1] + self.speed
            self.obstacles3CurrentPos[1] = self.obstacles3CurrentPos[1] - self.speed
            self.obstacles4CurrentPos[0] = self.obstacles4CurrentPos[0] - self.speed
            self.obstacles1 = Button(black, self.obstacles1CurrentPos[0], self.obstacles1CurrentPos[1], 15, 20)
            self.obstacles2 = Button(black, self.obstacles2CurrentPos[0], self.obstacles2CurrentPos[1], 15, 20)
            self.obstacles3 = Button(black, self.obstacles3CurrentPos[0], self.obstacles3CurrentPos[1], 15, 20)
            self.obstacles4 = Button(black, self.obstacles4CurrentPos[0], self.obstacles4CurrentPos[1], 15, 20)

    def isTrapped(self, pos, direction):
        simulatedCurrentPos = [pos[0], pos[1]]
        direct2 = ''

        #We want to check if the robot is close to the destination
        if pos[1] < 242:
            return False
        
        if self.angle == 90 and direction == 'FORWARD':
            direct2 = 'RIGHT'
        
        if self.angle == 0 and direction == 'LEFT':
            direct2 = 'RIGHT'
        
        if direct2 == '':
            return False

        for i in range(self.getMaxMovement()):
            self.simulateMove(simulatedCurrentPos, direction)
            if direction == 'FORWARD':
                simulatedRobot = Button(color,  simulatedCurrentPos[0],  simulatedCurrentPos[1], self.imageWidth, self.imageHeight)
            else:
                simulatedRobot = Button(color,  simulatedCurrentPos[0] + 8,  simulatedCurrentPos[1] - 8,  self.imageHeight, self.imageWidth)
            if self.hasHitAnyWalls(simulatedRobot):
                self.simulateMoveBackward(simulatedCurrentPos, direction)
                if direction == 'FORWARD':
                    simulatedRobot = Button(color,  simulatedCurrentPos[0],  simulatedCurrentPos[1], self.imageWidth, self.imageHeight)
                else:
                    simulatedRobot = Button(color,  simulatedCurrentPos[0] + 8,  simulatedCurrentPos[1] - 8,  self.imageHeight, self.imageWidth)
                for j in range(self.getMaxMovement()):
                    self.simulateMove(simulatedCurrentPos, direct2)
                    if direction == 'FORWARD':
                        simulatedRobot = Button(color,  simulatedCurrentPos[0],  simulatedCurrentPos[1], self.imageWidth, self.imageHeight)
                    else:
                        simulatedRobot = Button(color,  simulatedCurrentPos[0] + 8,  simulatedCurrentPos[1] - 8,  self.imageHeight, self.imageWidth)
                    if self.hasHitAnyWalls(simulatedRobot):
                        return True
        return False


class ShopWindow(Window):
    def __init__(self, username):
        Window.__init__(self, '', 'shop')
        self.username = username
        self.coins = int(self.getDataFromFile(username, 'coins.csv'))
        self.speedLevel = int(self.getDataFromFile(username, 'speed.csv'))
        self.ammo = int(self.getDataFromFile(username, 'ammo.csv'))
        self.coinsText = Text('freesansbold.ttf', 17, 'COINS: ' + str(self.coins), (100, 60), black)
        self.ammoDisplay = Text('freesansbold.ttf', 17, 'AMMO: ' + str(self.ammo), (100, 100), black)
        self.ammoText = Text('freesansbold.ttf', 17, '10 AMMO ', (100, 350), black)
        self.quitButton = Button(color, 700, 50, 100, 40, "QUIT")

        self.purchase = Button(color, 50, 250, 150, 40, "PURCHASE")
        self.purchaseAmmo = Button(color, 100, 400, 200, 40, "PURCHASE")
        self.info = Button(color, 200, 320, 100, 40, "INFO")
        self.pmwChart = Button(color, 400, 100, 400, 300, "PMW SIGNAL CHART")
        self.bigInfo = Text('freesansbold.ttf', 17, 'This chart describes how fast your robot moves.', (590, 420), black)
        self.bigInfo2 = Text('freesansbold.ttf', 17, 'At the moment, the chart shows a slow speed.', (590, 460), black)

        self.image = pg.image.load("images/uparrow.png")
        self.speedSlides = ["images/slow_speed.JPG", "images/mid_speed.JPG", "images/top_speed.JPG"]

        self.image = pg.transform.scale(self.image, (40, 70))
        self.image2 = pg.transform.scale(self.image, (40, 70))

        self.image = pg.transform.rotate(self.image, 180)
        self.ballrect = self.image.get_rect()
        self.ballrect2 = self.image.get_rect()

        self.ballrect.center = (80, 200)
        self.ballrect2.center = (145, 200)
        self.slidePos = 0
    
    def display(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN: #720, 25, 150, 50

                # on click for the down arrow 
                if event.pos[0] >= 60 and event.pos[0] <= 100 and event.pos[1] >= 170 and event.pos[1] <= 240:
                    if self.slidePos > 0:
                        self.slidePos -=1
                    if self.slidePos == 0:
                        self.bigInfo2.setText('At the moment, the chart shows a slow speed.')
                    elif self.slidePos == 1:
                        self.bigInfo2.setText('At the moment, the chart shows a medium speed.')
                    else:
                        self.bigInfo2.setText('At the moment, the chart shows a fast speed.')
                    self.setCurrentSpeed(self.slidePos)
                if event.pos[0] >= 125 and event.pos[0] <= 165 and event.pos[1] >= 170 and event.pos[1] <= 240:
                    if self.slidePos < 2:
                        self.slidePos +=1

                    if self.slidePos == 0:
                        self.bigInfo2.setText('At the moment, the chart shows a slow speed.')
                    elif self.slidePos == 1:
                        self.bigInfo2.setText('At the moment, the chart shows a medium speed.')
                    else:
                        self.bigInfo2.setText('At the moment, the chart shows a fast speed.')
                    self.setCurrentSpeed(self.slidePos)
                #on click for quit button
                if event.pos[0] >= 700 and event.pos[0] <= 800 and event.pos[1] >= 50 and event.pos[1] <= 90:
                    self.next = 'menu'

                #on click on speed purchased
                if event.pos[0] >= 50 and event.pos[0] <= 200 and event.pos[1] >= 250 and event.pos[1] <= 290:
                    if self.slidePos == 1 and self.coins >= 15 and self.speedLevel == 1:
                        self.coins -=15
                        self.speedLevel +=1
                    elif self.slidePos == 2 and self.coins >= 20 and self.speedLevel < 3:
                        self.speedLevel +=1
                        self.coins -=20
                    self.updateData(self.username, self.speedLevel, 'speed.csv')
                    self.updateData(self.username, self.coins, 'coins.csv')
                    
    
                #on click on ammo purchased
                if event.pos[0] >= 100 and event.pos[0] <= 300 and event.pos[1] >= 400 and event.pos[1] <= 490 and self.coins >= 15:
                    self.coins-=15
                    self.ammo+=10
                    self.updateData(self.username, self.ammo, 'ammo.csv')
                    self.updateData(self.username, self.coins, 'coins.csv')
                

        
        self.screen.fill(color)
        self.quitButton.draw(self.screen, (0,0,0))
        self.purchase.draw(self.screen, (0,0,0))
        self.purchaseAmmo.draw(self.screen, black)
        self.coinsText.setText("COINS: " + str(self.coins))
        self.coinsText.draw(self.screen)
        self.info.draw(self.screen, black)
        self.ammoDisplay.setText('AMMO: ' + str(self.ammo))
        self.ammoText.draw(self.screen)
        self.ammoDisplay.draw(self.screen)
        self.pmwChart.draw(self.screen, black)
        self.bigInfo.draw(self.screen)
        self.bigInfo2.draw(self.screen)
        self.screen.blit(self.image, self.ballrect)
        self.screen.blit(self.image2, self.ballrect2)

        image = pg.image.load(self.speedSlides[self.slidePos])
        image = pg.transform.scale(image, (400, 300))

        ballrect = image.get_rect()
        ballrect.center = (600, 250)
        self.screen.blit(image, ballrect)
        pg.display.flip()
    def setCurrentSpeed(self, pos):
        if pos == 1 and self.speedLevel > 0:
            self.updateData(self.username, 6, 'current_speed.csv')
        elif pos == 2 and self.speedLevel > 1:
            self.updateData(self.username, 8, 'current_speed.csv')
        else:
            self.updateData(self.username, 4, 'current_speed.csv')


class WindowManager():
    def __init__(self):
        self.username = ''
        self.currentWindow = LoginWindow()
        self.coin = 0
    def setCurrentWindow(self):
        if self.currentWindow.next == 'menu':
            if self.currentWindow.type == 'login':
                self.username = self.currentWindow.input_box1.text
            self.currentWindow = MainMenuWindow(self.username)
        elif self.currentWindow.next == 'instruct':
            if self.currentWindow.type == 'login':
                self.username = self.currentWindow.input_box1.text
            self.currentWindow = InstructionWindow()
        elif self.currentWindow.next == 'solo':
            self.currentWindow = SoloModeWindow(self.username, 'solo')
            self.currentWindow.obstacleMovement()
        elif self.currentWindow.next == 'compete':
            self.currentWindow = CompeteModeWindow(self.username, 'compete')
            self.currentWindow.computerPlayer()
            self.currentWindow.competeObstacleMovement()
        elif self.currentWindow.next == 'shop':
            self.currentWindow = ShopWindow(self.username)

    def setCoin(self, coin):
        self.coin = coin
    def setUsername(self, username):
        self.username = username

done = False

def main():
    clock = pg.time.Clock()
    count = 0
    w = WindowManager() # init window manager class current window is LoginWindow
    #currentWindow = CompeteModeWindow('pythagoras', 'compete')
    #currentWindow.computerPlayer()
    #currentWindow.obstacleMovement()
    while not done:
        w.currentWindow.display()
        #currentWindow.display()
        w.setCurrentWindow() #
        clock.tick(30)
        count+=1

def slide1Text(screen):
    # text = Text()
    font  = pg.font.Font('freesansbold.ttf', 17)
    text = font.render("Welcome to Robot Race! The game where you learn",
     True,  black, color)
    textRect = text.get_rect()
    textRect.center = (600, 50)

    text1 = font.render("about robot movement through competing with classmates.",
     True,  black, color) 
    textRect1 = text.get_rect()
    textRect1.center = (600, 80)

    text2 = font.render("Technology (and particularly robotics) can seem like a",
     True,  black, color) 
    textRect2 = text.get_rect()
    textRect2.center = (600, 120)

    text3 = font.render("complex, unreachable subject, so we want you to take baby",
     True,  black, color) 
    textRect3 = text.get_rect()
    textRect3.center = (600, 150)

    text4 = font.render("steps towards STEM (science, technology, engineering",
     True,  black, color)
    textRect4 = text.get_rect()
    textRect4.center = (600, 180)

    text5 = font.render(" and maths) by providing you with a fun, interactive",
     True,  black, color) 
    textRect5 = text.get_rect()
    textRect5.center = (600, 210)

    text6 = font.render("game that gives you a taste of robotics.",
     True,  black, color) 
    textRect6 = text.get_rect()
    textRect6.center = (600, 240)

    screen.blit(text, textRect)
    screen.blit(text1, textRect1)
    screen.blit(text2, textRect2)
    screen.blit(text3, textRect3)
    screen.blit(text4, textRect4)
    screen.blit(text5, textRect5)
    screen.blit(text6, textRect6)

def slide2Text(screen):
    font  = pg.font.Font('freesansbold.ttf', 17)
    text = font.render("First, we need to establish the difference between robot",
     True,  black, color) 
    textRect = text.get_rect()
    textRect.center = (600, 50)

    text1 = font.render("movement and in real life and in this game.",
     True,  black, color) 
    textRect1 = text.get_rect()
    textRect1.center = (600, 80)

    text2 = font.render("Here is a controller which you could use to control a robot.",
     True,  black, color) 
    textRect2 = text.get_rect()
    textRect2.center = (600, 120)

    screen.blit(text, textRect)
    screen.blit(text1, textRect1)
    screen.blit(text2, textRect2)

def slide3Text(screen):
    font  = pg.font.Font('freesansbold.ttf', 17)
    text = font.render("If we move both thumb sticks forwards, the robot moves.",
     True,  black, color) 
    textRect = text.get_rect()
    textRect.center = (600, 50)

    text1 = font.render("forwards too. We will use the keyboard letters",
     True,  black, color) 
    textRect1 = text.get_rect()
    textRect1.center = (600, 80)

    text2 = font.render("Q and P as our forward moving thumb sticks.",
     True,  black, color) 
    textRect2 = text.get_rect()
    textRect2.center = (600, 120)

    text3 = font.render("If we move both thumb sticks backwards, the robot ",
     True,  black, color) 
    textRect3 = text.get_rect()
    textRect3.center = (600, 150)

    text4 = font.render("moves backwards too. We will use the keyboard letters",
     True,  black, color)
    textRect4 = text.get_rect()
    textRect4.center = (600, 180)

    text5 = font.render("A and L as our backward moving thumb sticks.",
     True,  black, color) 
    textRect5 = text.get_rect()
    textRect5.center = (600, 210)

    screen.blit(text, textRect)
    screen.blit(text1, textRect1)
    screen.blit(text2, textRect2)
    screen.blit(text3, textRect3)
    screen.blit(text4, textRect4)
    screen.blit(text5, textRect5)

def slide4Text(screen):
    font  = pg.font.Font('freesansbold.ttf', 17)
    text = font.render("Here comes the tricky part: rotation.",
     True,  black, color) 
    textRect = text.get_rect()
    textRect.center = (600 - 10, 50)

    text1 = font.render("Sometimes, robots rotate with their wheel as a pivot.",
     True,  black, color) 
    textRect1 = text.get_rect()
    textRect1.center = (600 - 10, 80)

    text2 = font.render("Other times, robots may be able to rotate from their",
     True,  black, color) 
    textRect2 = text.get_rect()
    textRect2.center = (600 - 10, 120)

    text3 = font.render("centre  this is how the robot will move in our game.",
     True,  black, color)
    textRect3 = text.get_rect()
    textRect3.center = (600 - 10, 150)

    screen.blit(text, textRect)
    screen.blit(text1, textRect1)
    screen.blit(text2, textRect2)
    screen.blit(text3, textRect3)

def slide5Text(screen):
    font  = pg.font.Font('freesansbold.ttf', 17)
    text = font.render("In Robot Race, clockwise rotation will happen by ",
     True,  black, color) 
    textRect = text.get_rect()
    textRect.center = (600, 50)

    text1 = font.render("pressing Q and L together. Anticlockwise rotation will",
     True,  black, color) 
    textRect1 = text.get_rect()
    textRect1.center = (600, 80)

    text2 = font.render("happen by pressing A and P together.",
     True,  black, color) 
    textRect2 = text.get_rect()
    textRect2.center = (600, 120)
    

    screen.blit(text, textRect)
    screen.blit(text1, textRect1)
    screen.blit(text2, textRect2)

def slide6Text(screen):
    font  = pg.font.Font('freesansbold.ttf', 17)
    text = font.render("Using these controls, try and finish as many mazes",
     True,  black, color) 
    textRect = text.get_rect()
    textRect.center = (600, 50)

    text1 = font.render("as you can before the time runs out! The top 5",
     True,  black, color) 
    textRect1 = text.get_rect()
    textRect1.center = (600, 80)

    text2 = font.render("scores of the Solo Mode will be displayed in the",
     True,  black, color) 
    textRect2 = text.get_rect()
    textRect2.center = (600, 120)

    text3 = font.render("leader board. Happy Racing!",
     True,  black, color) 
    textRect3 = text.get_rect()
    textRect3.center = (600, 150)

    screen.blit(text, textRect)
    screen.blit(text1, textRect1)
    screen.blit(text2, textRect2)
    screen.blit(text3, textRect3)


if __name__ == '__main__':
    main()
    pg.quit()
