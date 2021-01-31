import random
import time
import threading
from base import BaseAgent, TurnData, Action
import copy
import math


class Diamond  :
    GREEN = 0
    BLUE = 1
    RED = 2
    YELLOW = 3
    GRAY = 4


class Agent(BaseAgent):

    def __init__(self):
        BaseAgent.__init__(self)
        self.path = []
        self.threads = []
        self.last_Action = None
        self.mode_start_position = None
        self.base_positions = None
        self.carrying = False
        self.prev_action = set([])
        print(f"MY NAME: {self.name}")
        print(f"PLAYER COUNT: {self.agent_count}")
        print(f"GRID SIZE: {self.grid_size}")
        print(f"MAX TURNS: {self.max_turns}")
        print(f"DECISION TIME LIMIT: {self.decision_time_limit}")


    def find_all_bases(self, agent, map):
        base_positions = [(i,j) for i in range(len(map)) for j in range(len(map[i])) if map[i][j] == agent.name.lower()]
        return base_positions
        # self.base_positions = base_positions

    def manhatan_dist(self, x1, y1, x2,y2) :
        return abs(x1 - x2) + abs(y1- y2)

    def manhatan_dist_to_closest_base(self, x, y, base_positions) :
        return min( [ self.manhatan_dist(x,y,base[0],base[1]) for base in base_positions ] )

    def number_of_close_points_in_zone(self, x, y, zone , distance=3 ) :
        return len(list(map(lambda manhatan_distance : manhatan_distance <= distance ,[self.manhatan_dist(x,y,point[0], point[1]) for point in zone] )))


    def ygy_constraint(self, agent, color) :
        return len(agent.collected) > 2 and color == Diamond.YELLOW and agent.collected[-2] == Diamond.YELLOW and agent.collected[-1] == Diamond.GREEN

    def calculate_diamonds_score(self, agent, turn_data) :
        """
        return a list of list in [x, y, score, color] format
        each inner list corresponds to a specific diamond
        """
        output = [[i,j, 0, eval(turn_data.map[i][j])] for i in range(len(turn_data.map)) for j in range(len(turn_data.map[i])) if turn_data.map[i][j].isdigit()]

        for diamond in output :
            diamond[2] += (diamond[3]**2 +1) # score of color 
            diamond[2] += (agent.collected.count(diamond[3]) * 2)  # number of picked diamonds with color d    
            diamond[2] += ( agent.count_required[diamond[3]] * -1) # ad
            diamond[2] += ( ( agent.count_required[diamond[3]] - agent.collected.count(diamond[3])) *2) # ad - number of picked diamonds with color d   
            base_positions = self.find_all_bases(agent, turn_data.map)
            diamond[2] += (self.manhatan_dist_to_closest_base(diamond[0], diamond[1], base_positions ) * -1) # manhatan distance to closest base  
            diamond[2] += (self.number_of_close_points_in_zone( diamond[0], diamond[1], [(point[0],point[1]) for point in output], 3)*2)
            not_carrying_agents_positions = [other_agent.position for other_agent in turn_data.agent_data if not other_agent.carrying and agent.name != other_agent.name] 
            diamond[2] += (self.number_of_close_points_in_zone(diamond[0], diamond[1], not_carrying_agents_positions ,3)* -20) 
            diamond[2] += 3 if self.ygy_constraint(agent, diamond[3]) else 0
            if diamond[2] <= 0 :
                diamond[2] = 1

        return output

    def is_valid_cell (self, x, y ) :
        return 0 <= x < self.grid_size and  0 <= y < self.grid_size

    def get_neighbors2(self, map, x, y) :
        neighbors = [] 

        if self.is_valid_cell(x-1,y):
            neighbors.append( (x-1, y) )


        if self.is_valid_cell(x,y+1):
            neighbors.append( (x, y+1) )


        if self.is_valid_cell(x+1,y):
            neighbors.append( (x+1, y) )


        if self.is_valid_cell(x,y-1):
            neighbors.append( (x, y-1) )
    
        
        return neighbors 

    def DFS (self, gmap, explored, node, depth) :
        if depth ==0 :
            return 
        children = self.get_neighbors2(gmap, node[0], node[1])
        for child in children :
            if child not in explored :
                explored.append(child)
                self.DFS(gmap,explored,child,depth-1)

        return 
    def wall_calculation2 (self, gmap, x, y, depth=5) :
        at = lambda node : gmap[node[0]][node[1]]
        explored = [(x,y)]
        self.DFS(gmap, explored, (x,y), depth) 
        explored.remove((x,y))
        soorat , makhraj = 0 , 0 
        for node in explored :
            if at(node) =='*' :
                soorat -= 1/ self.manhatan_dist(x,y , node[0], node[1]) or 1 
                # soorat +=1 
            else :
                makhraj += 1 / self.manhatan_dist(x,y , node[0], node[1]) or 1
                # makhraj +=1 
        
        score = soorat / makhraj or 1 
        # print(score)
        # print(f'\tscore for ({x},{y}) = {score}')
        return score


    def cell_score(self, agent, turn_data, x, y) :
        if not self.is_valid_position((x,y),turn_data.map):
            return 0    # for walls 

        # sum =  2*self.wall_calculation2(gmap = turn_data.map,x= x, y=y, depth= math.ceil(self.grid_size /2))
        
        sum = 0

        if agent.carrying :
            cary = agent.carrying
            agent.carrying = None

            base_positions = self.find_all_bases(agent, turn_data.map)

            for base in base_positions :
                score = self.cell_score(agent, turn_data, base[0], base[1]) 
                if score == 0 :
                    score = 1 
                distance = self.manhatan_dist(x, y, base[0], base[1]) 
                sum += score / distance**2 if distance else score

            agent.carrying = cary 
            return sum
        
        diamond_scores = self.calculate_diamonds_score(agent=agent, turn_data=turn_data)
        for score in diamond_scores :
            if self.manhatan_dist(x, y, score[0], score[1]) :
                sum += score[2] / self.manhatan_dist(x, y, score[0], score[1])
            else :
                sum += score[2]
            # sum += score[2] / self.manhatan_dist(x, y, score[0], score[1])**2 if self.manhatan_dist(x, y, score[0], score[1]) else score[2]
        
        return sum 

    def print_map (self, map) :
        for row in map :
            print(row)
        print('')

    def calculate_score_for_agents(self, game_state):
        return [self.cell_score(agent, game_state, agent.position[0], agent.position[1]) for agent in game_state.agent_data]

    def is_valid_position(self, position, map):
        if position[0] < 0 or position[1] < 0 or position[0] >= self.grid_size or position[1] >= self.grid_size:
            return False
        if map[position[0]][position[1]] == '*':
            return False
        return True

    def calculate_state(self, prev_game_state, prev_agent, prev_movement):
        """
        game state : یه چیزی مثل turn data
        agent : یه دونه از عامل ها
        movement: حرکتی که انجام میده مثل right یا left

        returns:
            یه state برمیگردونه. یه جیزی مثل turn data


        """
        actions = {
            'R': (0, 1),
            'L': (0, -1),
            'U': (-1, 0),
            'D': (1, 0),
        }
        agent_index = 0
        game_state = copy.deepcopy(prev_game_state)
        agent = copy.deepcopy(prev_agent)
        movement = copy.deepcopy(prev_movement)
        for i, ag in enumerate(game_state.agent_data):
            if ag.name == agent.name:
                agent_index = i
                break

        # update agent position
        agent.position = (agent.position[0] + actions[movement][0], agent.position[1] + actions[movement][1])
        if not self.is_valid_position(agent.position, game_state.map):
            return None

        agent_position_after_movement = game_state.map[agent.position[0]][agent.position[1]]

        # update carrying and collected
        if str(agent_position_after_movement).isdigit():  # is diamond
            if not agent.carrying:
                agent.carrying = int(agent_position_after_movement)
                game_state.map[agent.position[0]][agent.position[1]] = '.'
        if str(agent_position_after_movement).lower() == str(agent.name).lower():  # is base
            if agent.carrying:
                agent.collected.append(agent.carrying)
                agent.carrying = None

        game_state.agent_data[agent_index] = agent

        return game_state

    def minimax(self, game_state, depth, agents, agent_index):
        # our agent index should be given as agent_index in first function call

        if depth == 0:
            # return next(gen)
            return self.calculate_score_for_agents(game_state)

        max_values = [-10 for i in range(len(agents))]
        print(f'now in ({agents[agent_index].position[0]},{agents[agent_index].position[1]})')
        for movement in ['R', 'L', 'U', 'D']:
            new_state = self.calculate_state(game_state, agents[agent_index], movement)
            if not new_state:
                continue
            values = self.minimax(new_state, depth - 1, agents, (agent_index + 1) % len(agents))

            print(f'> {movement} ==> {values}')
            if max_values[agent_index] < values[agent_index]:
                max_values = values
                self.max_movement = movement
        return max_values


    def do_turn(self, turn_data: TurnData) -> Action:
        my_index = 0
        for i, agent in enumerate(turn_data.agent_data):
            if agent.name == self.name:
                me = agent
                my_index = i
                if not self.base_positions :
                    self.base_positions = self.find_all_bases(me, turn_data.map)
                
        self.carrying = me.carrying

        depth = 4
        self.minimax(turn_data, depth, turn_data.agent_data, my_index)
        actions = {
            'R': Action.RIGHT,
            'L': Action.LEFT,
            'U': Action.UP,
            'D': Action.DOWN,
        }
       


        print(f'selected {self.max_movement}')
        return actions[self.max_movement]
        #
        # # try :
        # up_score = self.cell_score(me, turn_data, me.position[0]-1 , me.position[1])
        # # except Exception as exc :
        # #     up_score = -1
        #
        # # try :
        # down_score = self.cell_score(me, turn_data, me.position[0]+1 , me.position[1])
        # # except Exception as exc :
        #     # down_score = -1
        #
        # # try :
        # left_score = self.cell_score(me, turn_data, me.position[0] , me.position[1]-1)
        # # except Exception as exc :
        #     # left_score = -1
        #
        # # try :
        # right_score = self.cell_score(me, turn_data, me.position[0] , me.position[1]+1)
        # # except Exception as exc :
        # #     right_score = -1
        #
        # max_score = max([up_score,down_score,left_score,right_score])
        # # print(self.cell_score(me, turn_data, me.position[0] , me.position[1]+1))
        # # except Exception as exc :
        # #     print('\n\nERROR\n\n')
        #
        # if max_score == up_score :
        #     print(f'> UP, score={up_score}')
        #     return Action.UP
        #
        # if max_score == down_score :
        #     print(f'> DOWN, score={down_score}')
        #     return Action.DOWN
        #
        # if max_score == left_score :
        #     print(f'> LEFT, score={left_score}')
        #     return Action.LEFT
        #
        # if max_score == right_score :
        #     print(f'> RIGHT, score={right_score}')
        #     return Action.RIGHT

        # return random.choice([Action.UP,Action.DOWN,Action.LEFT,Action.RIGHT,])

if __name__ == '__main__':
    winner = Agent().play()
    print("WINNER: " + winner)

