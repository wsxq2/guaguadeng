"""
刮刮登纸牌游戏 - Card类
表示游戏中的单张牌
"""

class Card:
    """
    表示一张牌
    
    Attributes:
        value (int): 牌的大小值 (1-10)
        suit (str): 牌的花色 ('♠', '♥', '♦', '♣')
    """
    
    SUITS = ['♠', '♥', '♦', '♣']  # 黑桃、红心、方块、梅花
    
    def __init__(self, value, suit):
        """
        初始化一张牌
        
        Args:
            value (int): 牌的大小值 (1-10)
            suit (str): 牌的花色
        """
        if value < 1 or value > 10:
            raise ValueError("牌的值必须在1-10之间")
        if suit not in self.SUITS:
            raise ValueError(f"花色必须是 {self.SUITS} 中的一个")
            
        self.value = value
        self.suit = suit
    
    def __str__(self):
        """返回牌的字符串表示"""
        return f"{self.suit}{self.value}"
    
    def __repr__(self):
        """返回牌的详细表示"""
        return f"Card({self.value}, '{self.suit}')"
    
    def __eq__(self, other):
        """比较两张牌是否相等"""
        if not isinstance(other, Card):
            return False
        return self.value == other.value and self.suit == other.suit
    
    def __lt__(self, other):
        """比较牌的大小，用于排序"""
        if not isinstance(other, Card):
            return NotImplemented
        return self.value < other.value
    
    def __hash__(self):
        """使Card可以作为字典的键"""
        return hash((self.value, self.suit))
    
    @classmethod
    def create_deck(cls):
        """
        创建一副完整的40张牌
        
        Returns:
            list: 包含40张牌的列表
        """
        deck = []
        for suit in cls.SUITS:
            for value in range(1, 11):
                deck.append(cls(value, suit))
        return deck