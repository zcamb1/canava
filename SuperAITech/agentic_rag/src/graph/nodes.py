from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field, asdict
@dataclass
class Node:
    uid: str
    label: str = field(init=False)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any])-> "Node":
        return cls(**data)

@dataclass
class Document(Node):
    title: str
    path: str
    label: str = field(init=False, default="Document")

@dataclass
class Chunk(Node):
    text: str
    embed: str
    label: str = field(init=False, default="Chunk")

@dataclass
class Highlight(Node):
    text: str
    embed: str
    label: str = field(init=False, default="Highlight")

@dataclass
class Role(Node):
    title: str
    conditions: List[str]
    label: str = field(init=False, default="Role")

@dataclass
class Pic(Node):
    knox_id: str
    label: str = field(init=False, default="Pic")
    desc: List[str]
    phone: str
    full_name:str
    location: str
    

@dataclass
class Time(Node):
    create_at: str
    efficient_time: str
    label: str = field(init=False, default="Time")