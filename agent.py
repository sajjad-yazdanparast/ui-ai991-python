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

    @staticmethod
    def find_signs(map, sign):
        return [(i,j) for i in range(len(map)) for j in range(len(map[i])) if map[i][j] == sign ]

    def is_valid_state(self, map, node):
        result = (node.x, node.y)
        if result[0] < 0 or result[1] < 0 or result[0] >= self.grid_size or result[1] >= self.grid_size:
            return False
        if map[result[0]][result[1]] == '*':
            return False
        return True

    def find_target(self, map, mode, current_position):
        if mode == 'find_diamond':
            is_target = lambda node: True if map[node.x][node.y].isdigit() else False
        elif mode == 'find_base': 
            is_target = lambda node: True if map[node.x][node.y] == self.name.lower() else False

        node = State(current_position[0], current_position[1])
        if is_target(node):
            return node

        frontier = [node]
        explored = []

        while True:
            if not frontier:
                return None

            node = frontier.pop(0)
            explored.append(node)

            actions = [
                (0, 1, 'R'),
                (0, -1, 'L'),
                (1, 0, 'D'),
                (-1, 0, 'U'),
            ]

            for action in actions:
                child_node = State(node.x + action[0], node.y + action[1], node, action[2])
                if not self.is_valid_state(map, child_node):
                    continue
                if child_node in explored or child_node in frontier:
                    continue
                if is_target(child_node):
                    print('explored ...')
                    print(len(explored))
                    return child_node
                frontier.append(child_node)

    def fill_path(self, me, turn_data):
        if me.carrying:
            mode = 'find_base'
        else:
            mode = 'find_diamond'
        
        

        start = time.time()
        target_node = self.find_target(turn_data.map, mode, me.position)
        end = time.time()
        print('time spent : ',end - start)

        if not target_node:
            return random.choice(list(Action))

        
        while True:
            if not target_node.action:
                break
            self.path.append(target_node.action)
            target_node = target_node.parent
        

    def do_turn(self, turn_data: TurnData) -> Action:

        for agent in turn_data.agent_data:
            if agent.name == self.name:
                me = agent

        if not any([t.is_alive() for t in self.threads]) and not self.path:
            x = threading.Thread(target=self.fill_path, args=(me, turn_data))
            self.threads.append(x)
            self.mode_start_position = me.position
            x.start()
            if self.decision_time_limit == float('inf'):
                x.join()
            else:
                x.join(0.8 * self.decision_time_limit)
        # elif not self.path:
        #     current_thread = [x for x in self.threads if x.is_alive()][0]
        #     current_thread.join(0.8 * self.decision_time_limit)
        #     print(current_thread.is_alive())
        
        
        # if not self.decision_time_limit == float('inf'):
        #     time.sleep(float(0.5 * self.decision_time_limit))
        
        if not self.path:
            print('timeeeeeeeeeeeeeeeeeeeeee')
            if self.last_Action == Action.RIGHT:
                self.last_Action = Action.LEFT
                print('random left')
                return Action.LEFT
            else:
                self.last_Action = Action.RIGHT
                print('random right')
                return Action.RIGHT

        elif self.mode_start_position:
            print(me.position)
            print(self.mode_start_position)

            if me.position != self.mode_start_position:
                if self.last_Action == Action.RIGHT:
                    self.last_Action = Action.LEFT
                    self.mode_start_position = None
                    return Action.LEFT
                else:
                    self.last_Action = Action.RIGHT
                    self.mode_start_position = None
                    return Action.RIGHT
            else:
                self.mode_start_position = None
        
            

        action_name = self.path.pop()
        
        if action_name == "U":
            return Action.UP
        if action_name == "D":
            return Action.DOWN
        if action_name == "L":
            return Action.LEFT
        if action_name == "R":
            return Action.RIGHT


if __name__ == '__main__':
    winner = Agent().play()
    print("WINNER: " + winner)
