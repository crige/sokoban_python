##!../bin/python
#env....conda python=3.13.1

import sys
import pygame
import string
import queue
import random

pygame.init()

def start_game():
    """游戏开始界面，用于选择关卡"""
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption('推箱子 - 选择关卡')
    selected_level = 1
    max_level = 11  # 最大关卡数
    clock = pygame.time.Clock()
    
    while True:
        screen.fill((255, 226, 191))
        
        # 使用正确的中文字体名称
        try:
            font = pygame.font.SysFont('microsoft yahei', 36)
            start_font = pygame.font.SysFont('microsoft yahei', 24)
        except:
            font = pygame.font.Font(None, 36)
            start_font = pygame.font.Font(None, 24)
        
        # 显示游戏开始提示
        start_text = start_font.render('游戏即将开始.......', True, (0, 0, 0))
        start_text_rect = start_text.get_rect(center=(200, 20))
        screen.blit(start_text, start_text_rect)
            
        # 显示标题
        title = font.render('推箱子', True, (0, 0, 0))
        screen.blit(title, (150, 50))
        
        # 显示当前选择的关卡
        level_text = font.render(f'第 {selected_level} 关', True, (0, 0, 0))
        screen.blit(level_text, (150, 120))
        
        # 显示操作提示
        hint_font = pygame.font.SysFont('microsoft yahei', 24)
        hint = hint_font.render('使用↑↓选择关卡，回车确认', True, (100, 100, 100))
        screen.blit(hint, (80, 200))
        
        # 添加撤销/重做提示
        undo_hint = hint_font.render('按下Z键撤销，Y键重做', True, (100, 100, 100))
        screen.blit(undo_hint, (120, 230))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_level = max(1, selected_level - 1)
                elif event.key == pygame.K_DOWN:
                    selected_level = min(max_level, selected_level + 1)
                elif event.key == pygame.K_RETURN:
                    return selected_level
                    
        pygame.display.flip()
        clock.tick(60)

class Game:
    """推箱子游戏的主要逻辑类"""
    '''Sokoban_solver_1中的符号定义如下:
    const convertToDataType = (sign) => {
    switch (sign) {
    case ' ': return 'floor'
    case '#': return 'wall'
    case 'B': return 'block'
    case '.': return 'target'
    case '&': return 'player'
    case 'X': return 'target-block'
    case '%': return 'target-player'
    '''
    def is_valid_value(self,char):
        """检查地图中的字符是否有效
        ' ' - 地板
        '#' - 墙
        '@' - 人物在地板上 不支持,用的是 &
        '.' - 目标点
        '*' - 箱子在目标点上 不支持,用的是 X
        '$' - 箱子 不支持,用的是 B
        '+' - 人物在目标点上 不支持,用的是 %
        """
        if ( char == ' ' or #floor
            char == '#' or #wall
            char == '@' or #worker on floor
            char == '.' or #dock
            char == '*' or #box on dock
            char == '$' or #box
            char == '+' ): #worker on dock
            return True
        else:
            return False

    def __init__(self,filename,level):
        self.queue = queue.LifoQueue()
        self.history = []
        self.current_step = -1
        self.matrix = []
        if level < 1:
            print("ERROR: Level " + str(level) + " is out of range")
            sys.exit(1)
        else:
            try:
                file = open(filename,'r')
                level_found = False
                for line in file:
                    if not level_found:
                        if line.strip().startswith("Level "+str(level)):
                            level_found = True
                    else:
                        line = line.rstrip()
                        if line and not line.strip().startswith("Level"):
                            row = []
                            for c in line:
                                if c != '\n':
                                    row.append(c)
                            if row:
                                self.matrix.append(row)
                        elif line.strip().startswith("Level") or not line.strip():
                            break
                if not level_found:
                    print(f"未找到关卡 {level}")
                file.close()
            except Exception as e:
                print(f"读取文件时出错: {str(e)}")
                sys.exit(1)

    def load_size(self):
        """计算游戏窗口大小，每个方块是32x32像素"""
        x = 0
        y = len(self.matrix)
        for row in self.matrix:
            if len(row) > x:
                x = len(row)
        return (x * 32, y * 32)

    def get_matrix(self):
        return self.matrix

    def print_matrix(self):
        for row in self.matrix:
            for char in row:
                sys.stdout.write(char)
                sys.stdout.flush()
            sys.stdout.write('\n')

    def get_content(self,x,y):
        return self.matrix[y][x]

    def set_content(self,x,y,content):
        if self.is_valid_value(content):
            self.matrix[y][x] = content
        else:
            print("ERROR: Value '"+content+"' to be added is not valid")

    def worker(self):
        """查找人物的位置，返回(x, y, 当前位置的字符)"""
        x = 0
        y = 0
        for row in self.matrix:
            for pos in row:
                if pos == '@' or pos == '+':
                    return (x, y, pos)
                else:
                    x = x + 1
            y = y + 1
            x = 0

    def can_move(self,x,y):
        """检查人物是否可以移动到指定位置"""
        next_pos = self.get_content(self.worker()[0]+x,self.worker()[1]+y)
        return next_pos in [' ', '.']  # 可以移动到空地或目标点

    def next(self,x,y):
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y)

    def can_push(self,x,y):
        """检查是否可以推动箱子"""
        next_pos = self.next(x,y)
        next_next_pos = self.next(x+x,y+y)
        return (next_pos in ['$', '*'] and  # 当前位置是箱子
                next_next_pos in [' ', '.'])  # 箱子的下一个位置是空地或目标点

    def is_completed(self):
        for row in self.matrix:
            for cell in row:
                if cell == '$':
                    return False
        return True

    def move_box(self,x,y,a,b):
        """移动箱子
        参数:
        x,y - 箱子当前位置
        a,b - 移动方向
        """
        current_box = self.get_content(x,y)
        future_box = self.get_content(x+a,y+b)
        moved = False  # 标记是否移动了箱子
        
        if current_box == '$' and future_box == ' ':
            self.set_content(x+a,y+b,'$')
            self.set_content(x,y,' ')
            moved = True
        elif current_box == '$' and future_box == '.':
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,' ')
            moved = True
        elif current_box == '*' and future_box == ' ':
            self.set_content(x+a,y+b,'$')
            self.set_content(x,y,'.')
            moved = True
        elif current_box == '*' and future_box == '.':
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,'.')
            moved = True
        
        return moved

    def unmove(self):
        """撤销上一步移动"""
        if not self.queue.empty():
            movement = self.queue.get()
            if movement[2]:
                current = self.worker()
                self.move(movement[0] * -1,movement[1] * -1, False)
                self.move_box(current[0]+movement[0],current[1]+movement[1],movement[0] * -1,movement[1] * -1)
            else:
                self.move(movement[0] * -1,movement[1] * -1, False)

    def save_state(self):
        """保存当前状态到历史记录"""
        # 深拷贝当前矩阵状态
        current_state = []
        for row in self.matrix:
            current_state.append(row[:])
            
        # 如果当前不在最新状态,需要删除当前步之后的所有历史
        if self.current_step < len(self.history) - 1:
            self.history = self.history[:self.current_step + 1]
            
        self.history.append(current_state)
        self.current_step += 1
        
    def undo(self):
        """撤销到上一步"""
        if self.current_step > 0:
            self.current_step -= 1
            self.matrix = self.history[self.current_step]
            
    def redo(self):
        """重做下一步"""
        if self.current_step < len(self.history) - 1:
            self.current_step += 1 
            self.matrix = self.history[self.current_step]
            
    def move(self,x,y,save):
        """移动人物或推箱子"""
        if self.can_move(x,y):  # 如果可以移动
            if save:
                self.save_state()  # 移动前保存状态
            current = self.worker()
            future = self.next(x,y)
            if current[2] == '@' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],' ')
            elif current[2] == '@' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],' ')
            elif current[2] == '+' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],'.')
            elif current[2] == '+' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],'.')
        elif self.can_push(x,y):  # 如果可以推箱子
            if save:
                self.save_state()  # 移动前保存状态
            current = self.worker()
            future = self.next(x,y)
            future_box = self.next(x+x,y+y)
            
            # 推箱子的逻辑
            if future in ['$', '*']:  # 如果下一个位置是箱子
                moved = self.move_box(current[0]+x,current[1]+y,x,y)
                if moved:
                    # 移动人物
                    if current[2] == '@':
                        self.set_content(current[0],current[1],' ')
                        self.set_content(current[0]+x,current[1]+y,'@' if future_box == ' ' else '+')
                    else:  # current[2] == '+'
                        self.set_content(current[0],current[1],'.')
                        self.set_content(current[0]+x,current[1]+y,'@' if future_box == ' ' else '+')

    def handle_input(self, event):
        """处理用户输入"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.move(0, -1, True)
            elif event.key == pygame.K_DOWN:
                self.move(0, 1, True)
            elif event.key == pygame.K_LEFT:
                self.move(-1, 0, True)
            elif event.key == pygame.K_RIGHT:
                self.move(1, 0, True)
            elif event.key == pygame.K_z:  # 撤销
                self.undo()
            elif event.key == pygame.K_y:  # 重做
                self.redo()
            elif event.key == pygame.K_q:
                sys.exit(0)

    def handle_level_completion(self):
        """处理关卡完成后的逻辑"""
        pygame.time.wait(800)  # 等待查看最终状态
        display_fireworks(screen)  # 显示烟花效果
        self.show_completion_message()  # 显示完成信息
        self.prompt_next_level()  # 提示进入下一关

    def show_completion_message(self):
        """显示关卡完成信息"""
        # 可以添加更丰富的完成信息显示
        pass

    def prompt_next_level(self):
        """提示进入下一关"""
        # 添加进入下一关的提示和选择
        pass

class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 1
        self.color = (random.randint(50,255), random.randint(50,255), random.randint(50,255))
        self.lifetime = 30  # 烟花持续时间

    def update(self):
        self.size += 1
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

def print_game(matrix,screen):
    """根据地图矩阵绘制游戏画面"""
    screen.fill(background)
    x = 0
    y = 0
    for row in matrix:
        for char in row:
            if char == ' ': #floor
                screen.blit(floor,(x,y))
            elif char == '#': #wall
                screen.blit(wall,(x,y))
            elif char == '@': #worker on floor
                screen.blit(worker,(x,y))
            elif char == '.': #dock
                screen.blit(docker,(x,y))
            elif char == '*': #box on dock
                screen.blit(box_docked,(x,y))
            elif char == '$': #box
                screen.blit(box,(x,y))
            elif char == '+': #worker on dock
                screen.blit(worker_docked,(x,y))
            x = x + 32
        x = 0
        y = y + 32


def get_key():
  while 1:
    event = pygame.event.poll()
    if event.type == pygame.KEYDOWN:
      return event.key
    else:
      pass

def display_box(screen, message):
    """在屏幕中央显示消息框
    "Print a message in a box in the middle of the screen"
    """
    fontobject = pygame.font.SysFont(None, 18)
    pygame.draw.rect(screen, (0,0,0),
                     ((screen.get_width() / 2) - 100,
                      (screen.get_height() / 2) - 10,
                      200,20), 0)
    pygame.draw.rect(screen, (255,255,255),
                     ((screen.get_width() / 2) - 102,
                      (screen.get_height() / 2) - 12,
                      204,24), 1)
    if len(message) != 0:
        screen.blit(fontobject.render(message, 1, (255,255,255)),
                    ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    pygame.display.flip()

def display_end(screen):
    """显示关卡完成消息"""
    message = "Level Completed"
    fontobject = pygame.font.SysFont(None, 18)
    pygame.draw.rect(screen, (0,0,0),
                   ((screen.get_width() / 2) - 100,
                    (screen.get_height() / 2) - 10,
                    200,20), 0)
    pygame.draw.rect(screen, (255,255,255),
                   ((screen.get_width() / 2) - 102,
                    (screen.get_height() / 2) - 12,
                    204,24), 1)
    screen.blit(fontobject.render(message, 1, (255,255,255)),
                ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
    pygame.display.flip()


def ask(screen, question):
  "ask(screen, question) -> answer"
  pygame.font.init()
  current_string = []
  display_box(screen, question + ": " + ''.join(current_string))
  while 1:
    inkey = get_key()
    if inkey == pygame.K_BACKSPACE:
      current_string = current_string[0:-1]
    elif inkey == pygame.K_RETURN:
      break
    elif inkey == pygame.K_MINUS:
      current_string.append("_")
    elif inkey <= 127:
      current_string.append(chr(inkey))
    display_box(screen, question + ": " + string.join(current_string,""))
  return string.join(current_string,"")

def load_resources():
    """加载游戏资源"""
    resources = {
        'wall': pygame.image.load('images/wall.png'),
        'floor': pygame.image.load('images/floor.png'),
        'box': pygame.image.load('images/box.png'),
        'box_docked': pygame.image.load('images/box_docked.png'),
        'worker': pygame.image.load('images/worker.png'),
        'worker_docked': pygame.image.load('images/worker_dock.png'),
        'docker': pygame.image.load('images/dock.png')
    }
    return resources

wall = pygame.image.load('images/wall.png')
floor = pygame.image.load('images/floor.png')
box = pygame.image.load('images/box.png')
box_docked = pygame.image.load('images/box_docked.png')
worker = pygame.image.load('images/worker.png')
worker_docked = pygame.image.load('images/worker_dock.png')
docker = pygame.image.load('images/dock.png')
background = 255, 226, 191
pygame.init()
try:
    level = int(start_game())  # 只调用一次 start_game()
except ValueError:
    print("ERROR: Invalid Level")
    sys.exit(2)

try:
    game = Game('levels_solver.txt', level)
    print("已正确打开文件")
except:
    print("ERROR: 无法打开文件")
    sys.exit(1)

size = game.load_size()
screen = pygame.display.set_mode(size)

def display_fireworks(screen):
    """显示烟花效果"""
    fireworks = []
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    
    # 在屏幕不同位置创建多个烟花
    for _ in range(5):
        x = random.randint(0, screen.get_width())
        y = random.randint(0, screen.get_height())
        fireworks.append(Firework(x, y))
    
    # 烟花动画持续2秒
    while pygame.time.get_ticks() - start_time < 2000:
        screen.fill(background)
        print_game(game.get_matrix(), screen)  # 保持显示游戏画面
        
        # 更新和绘制所有烟花
        for firework in fireworks[:]:
            if firework.update():
                firework.draw(screen)
            else:
                fireworks.remove(firework)
                if len(fireworks) < 5:  # 保持烟花数量
                    x = random.randint(0, screen.get_width())
                    y = random.randint(0, screen.get_height())
                    fireworks.append(Firework(x, y))
        
        pygame.display.flip()
        clock.tick(60)

# 主游戏循环
while 1:
    # 先绘制当前状态
    print_game(game.get_matrix(),screen)
    pygame.display.update()
    
    # 处理输入和移动
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            sys.exit(0)
        elif event.type == pygame.KEYDOWN:
            game.handle_input(event)
            
            # 移动后立即更新显示
            print_game(game.get_matrix(),screen)
            pygame.display.update()
            
            # 检查是否完成
            if game.is_completed():
                game.handle_level_completion()
                level = start_game()    # 返回到开始画面
                game = Game('levels_solver.txt', level)
                size = game.load_size()
                screen = pygame.display.set_mode(size)
