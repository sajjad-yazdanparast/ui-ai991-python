import abc
import enum
import socket
import struct
import dataclasses
from typing import List

def read_utf(connection: socket.socket):
    length = struct.unpack('>H', connection.recv(2))[0]
    return connection.recv(length).decode('utf-8')


def write_utf(connection: socket.socket, msg: str):
    connection.send(struct.pack('>H', len(msg)))
    connection.send(msg.encode('utf-8'))


class Action(enum.Enum):
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'


@dataclasses.dataclass
class AgentData:
    name: str
    position: tuple
    carrying: int or None
    collected: list
    score: int
    count_required: List[int]


@dataclasses.dataclass
class TurnData:
    turns_left: int
    agent_data: List[AgentData]
    map: list


class BaseAgent(metaclass=abc.ABCMeta):

    def __init__(self):
        self.connection = None
        self.name = None
        self.agent_count = None
        self.grid_size = None
        self.max_turns = None
        self.decision_time_limit = None

    def connect(self):
        self.connection = socket.socket()
        self.connection.connect(('127.0.0.1', 9921))
        self.name = read_utf(self.connection)
        self.agent_count = int(read_utf(self.connection))
        self.grid_size = int(read_utf(self.connection))
        self.max_turns = int(read_utf(self.connection))
        decision_time_limit_str = read_utf(self.connection)
        if decision_time_limit_str == 'None':
            self.decision_time_limit = float('inf')
        else:
            self.decision_time_limit = float(decision_time_limit_str)

    def _read_turn_data(self, first_line: str) -> TurnData:
        turns_left = int(first_line)
        agents = []
        for _ in range(self.agent_count):
            info = read_utf(self.connection).split(" ")
            name = info[0]
            position = tuple(map(int, info[1].split(":")))
            carrying = int(info[2]) if info[2].isdigit() else None
            if info[3] != '-':
                collected = list(map(int, list(info[3])))
            else:
                collected = []
            score = int(info[4])
            reqs = list(map(int, info[5].split(',')))
            # print(reqs)
            data = AgentData(name, position, carrying, collected, score, reqs)
            agents.append(data)
        map_data = []
        for _ in range(self.grid_size):
            map_data.append(list(read_utf(self.connection)))
        return TurnData(turns_left, agents, map_data)

    def play(self) -> str:
        if self.connection is None:
            self.connect()
        while True:
            first_line = read_utf(self.connection)
            if first_line.startswith('WINNER'):
                return first_line.split(" ")[1]
            turn_data = self._read_turn_data(first_line)
            action = self.do_turn(turn_data)
            write_utf(self.connection, action.name)

    @abc.abstractmethod
    def do_turn(self, turn_data: TurnData) -> Action:
        pass