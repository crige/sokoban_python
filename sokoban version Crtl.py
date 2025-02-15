import json

class GameState:
    def __init__(self):
        self.history = []  # 用于存储历史状态
        self.current_step = -1  # 当前步骤索引

    def save_state(self, matrix):
        """保存当前状态到历史记录"""
        # 深拷贝当前矩阵状态
        current_state = [row[:] for row in matrix]
        
        # 如果当前不在最新状态,需要删除当前步之后的所有历史
        if self.current_step < len(self.history) - 1:
            self.history = self.history[:self.current_step + 1]
        
        self.history.append(current_state)
        self.current_step += 1

    def undo(self):
        """撤销到上一步"""
        if self.current_step > 0:
            self.current_step -= 1
            return self.history[self.current_step]
        return None  # 没有可撤销的状态

    def redo(self):
        """重做下一步"""
        if self.current_step < len(self.history) - 1:
            self.current_step += 1
            return self.history[self.current_step]
        return None  # 没有可重做的状态

    def save_to_file(self, filename):
        """将当前历史状态保存到文件"""
        with open(filename, 'w') as f:
            json.dump(self.history, f)

    def load_from_file(self, filename):
        """从文件加载历史状态"""
        with open(filename, 'r') as f:
            self.history = json.load(f)
            self.current_step = len(self.history) - 1  # 设置为最后一步

# 示例用法
if __name__ == "__main__":
    game_state = GameState()
    
    # 假设这是游戏的初始状态
    initial_matrix = [
        ['#', '#', '#', '#'],
        ['#', ' ', 'B', '#'],
        ['#', '@', ' ', '#'],
        ['#', '#', '#', '#']
    ]
    
    # 保存初始状态
    game_state.save_state(initial_matrix)
    
    # 模拟一些操作
    new_matrix = [
        ['#', '#', '#', '#'],
        ['#', ' ', ' ', '#'],
        ['#', '@', 'B', '#'],
        ['#', '#', '#', '#']
    ]
    game_state.save_state(new_matrix)
    
    # 撤销操作
    previous_state = game_state.undo()
    print("撤销后的状态:", previous_state)
    
    # 保存到文件
    game_state.save_to_file('game_state.json')
    
    # 从文件加载状态
    game_state.load_from_file('game_state.json')
    print("从文件加载的状态:", game_state.history)
