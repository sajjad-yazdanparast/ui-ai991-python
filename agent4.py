import random
import time
import threading
from base import BaseAgent, TurnData, Action


class State:
    def __init__(self, x, y, parent=None, action=None):
        self.x = x
        self.y = y
        self.parent = parent
        self.action = action
        if parent:
            self.path_length = self.parent.path_length + 1
        else:
            self.path_length = 0
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'x: {self.x}, y:{self.y}, action: {self.action}'


class Agent(BaseAgent):

    def __init__(self):
        BaseAgent.__init__(self)
        self.path = []
        self.threads = []
        self.last_Action = None
        self.mode_start_position = None
        print(f"MY NAME: {self.name}")
        print(f"PLAYER COUNT: {self.agent_count}")
        print(f"GRID SIZE: {self.grid_size}")
        print(f"MAX TURNS: {self.max_turns}")
        print(f"DECISION TIME LIMIT: {self.decision_time_limit}")



    def do_turn(self, turn_data: TurnData) -> Action:
        pass 

if __name__ == '__main__':
    winner = Agent().play()
    print("WINNER: " + winner)
