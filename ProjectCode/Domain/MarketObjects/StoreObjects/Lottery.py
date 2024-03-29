from ProjectCode.Domain.Helpers.TypedDict import *
from ProjectCode.Domain.Helpers.JsonSerialize import JsonSerialize


class Lottery:
    def __init__(self, lottery_id, product_id, price, accumulated_price):
        self.__lottery_id = lottery_id
        self.__product_id = product_id
        self.__price = price
        self.__accumulated_price = accumulated_price
        self.__participants = TypedDict(str, int)
        self.__winner = None

    # Getters
    def get_lottery_id(self):
        return self.__lottery_id

    def get_product_id(self):
        return self.__product_id

    def get_price(self):
        return self.__price

    def get_accumulated_price(self):
        return self.__accumulated_price

    def get_participants(self):
        return self.__participants

    # Setters
    def set_lottery_id(self, lottery_id):
        self.__lottery_id = lottery_id

    def set_product_id(self, product_id):
        self.__product_id = product_id

    def set_price(self, price):
        self.__price = price

    def set_accumulated_price(self, accumulated_price):
        self.__accumulated_price = accumulated_price

    def add_participant_share(self, username, share):
        if self.__participants.get(username) is None:
            self.__participants[username] = share
        else:
            self.__participants[username] += share


    def get_winner(self):
        return self.__winner

    def set_winner(self, value):
        self.__winner = value

# =======================JSON=======================#
    def toJson(self):
        return{
            "lottery_id": self.__lottery_id,
            "product_id": self.__product_id,
            "price": self.__price,
            "accumulated_price": self.__accumulated_price,
            "participants": self.__participants,
            "winner": self.__winner
        }