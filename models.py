from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Character:
    name: str
    attack: int
    defense: int
    hp: int
    max_hp: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        return cls(
            name=data['name'],
            attack=data['attack'],
            defense=data['defense'],
            hp=data['hp'],
            max_hp=data['hp']
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'attack': self.attack,
            'defense': self.defense,
            'hp': self.hp
        }

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, damage: int) -> int:
        actual_damage = max(1, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def __str__(self) -> str:
        return f"{self.name} - ATK: {self.attack}, DEF: {self.defense}, PV: {self.hp}/{self.max_hp}"


@dataclass
class Monster(Character):
    pass


@dataclass
class Score:
    player_name: str
    waves: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Score':
        return cls(
            player_name=data['player_name'],
            waves=data['waves']
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'player_name': self.player_name,
            'waves': self.waves
        }
