from datetime import datetime

from ProjectCode.Domain.MarketObjects.StoreObjects.LogicComponents.LogicComp import LogicComp


class RulePurchaseComp(LogicComp):
    """
            rule_type := "alcohol_restriction" | to be added
            product := product_id | -1 for non-specific product rule
            category := category name | "" for non specific category rule
            user_field := age | logged in status | etc..
            operator := ">=" | "<=" | "=="
            quantity := quantity of a product | total price
    """

    def __init__(self, rule_type, product, category, user_field, operator, quantity):
        super().__init__("")
        self.rule_types = {"amount_of_product": True, "alcohol_restriction": True, "basket_total_price": True,
                      "day_of_the_week": True, "amount_of_category": True,  "username_restrictions":True}
        self.rule_type = self.__validateRuleType(rule_type)
        self.product_id = product
        self.category = category
        self.user_field = user_field
        self.operator = operator
        self.quantity = quantity


    def checkIfSatisfy(self, product, basket, total_price, user=None):
        if self.rule_type == "amount_of_product":
            return self.productAmount(basket)
        elif self.rule_type == "basket_total_price":
            return self.compareWithOperator(total_price)
        elif self.rule_type == "amount_of_category":
            return self.amountOfCategory(basket)
        elif self.rule_type == "alcohol_restriction":
            return True
        elif self.rule_type == "username_restrictions":
            return self.usernameRestriction(user)
        elif self.rule_type == "day_of_the_week":
            return self.dayOfTheWeek()
        raise Exception("No such rule type exists")


    def usernameRestriction(self, user):
        if self.user_field == user:
            raise Exception(f"{user} is not allowed to purchase")
        return True

    def amountOfCategory(self,basket):
        amount = 0
        for product_id, product_tuple in basket.items():
            cur_product, cur_quantity = product_tuple[0], product_tuple[1]
            if self.category in cur_product.get_categories():
                amount += cur_quantity
        if self.compareWithOperator(amount):
            return True
        return False

    def productAmount(self, basket):
        for product_id, product_tuple in basket.items():
            if int(product_id) == self.product_id and not self.compareWithOperator(product_tuple[1]):
                return False
        return True

    def dayOfTheWeek(self):
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        current_day = datetime.now().weekday()
        if days_of_week[current_day] == self.user_field:
            return True
        return False


    def alcoholRestriction(self, age):
        if self.user_field == "age":
            return self.compareWithOperator(age)

    def compareWithOperator(self, arg):
        if self.operator == ">=":
            return arg >= self.quantity
        elif self.operator == "<=":
            return arg <= self.quantity
        elif self.operator == "==":
            return arg == self.quantity
        else:
            raise Exception("No such operator exists")


    def __validateRuleType(self, rule_type):
        if self.rule_types.get(rule_type):
            return rule_type
        else:
            raise Exception("No such rule type exists")
