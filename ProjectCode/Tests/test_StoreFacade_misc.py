import json
import unittest
from datetime import datetime
from unittest import TestCase

from ProjectCode.Domain.ExternalServices.MessageController import MessageController
from ProjectCode.Domain.ExternalServices.PaymetService import PaymentService
from ProjectCode.Domain.ExternalServices.SupplyService import SupplyService
from ProjectCode.Domain.ExternalServices.TransactionHistory import TransactionHistory
from ProjectCode.Domain.ExternalServices.TransactionObjects.StoreTransaction import StoreTransaction
from ProjectCode.Domain.ExternalServices.TransactionObjects.UserTransaction import UserTransaction
from ProjectCode.Domain.MarketObjects.Basket import Basket
from ProjectCode.Domain.MarketObjects.Bid import Bid
from ProjectCode.Domain.MarketObjects.Cart import Cart

from ProjectCode.Domain.MarketObjects.Store import Store
from ProjectCode.Domain.MarketObjects.StoreObjects.DiscountPolicy import DiscountPolicy
from ProjectCode.Domain.MarketObjects.StoreObjects.LogicComponents.LogicComp import LogicComp
from ProjectCode.Domain.MarketObjects.StoreObjects.Product import Product
from ProjectCode.Domain.MarketObjects.UserObjects.Admin import Admin
from ProjectCode.Domain.MarketObjects.UserObjects.Guest import Guest
from ProjectCode.Domain.StoreFacade import StoreFacade
from ProjectCode.Domain.Helpers.TypedDict import TypedDict
from ProjectCode.Domain.MarketObjects.Access import Access
from ProjectCode.Domain.MarketObjects.UserObjects.Member import Member


class TestStoreFacade(TestCase):

    def setUp(self):
        send_notification_lambda = lambda self, receiver_id, notification_id, type, subject: True
        config = "../../default_config.json"
        with open(config, 'r') as f:
            config_data: dict = json.load(f)

        self.store_facade = StoreFacade(config_data, send_notification_call=send_notification_lambda)

        #self.store_facade = StoreFacadDe({})
        self.store_facade.admins["Ari"] = Admin("Ari", "password123", "ari@gmail.com")
        self.store_facade.admins["Rubin"] = Admin("Rubin", "password123", "rubin@gmail.com")
        self.store_facade.register("Feliks", "password456", "feliks@gmail.com")
        self.store_facade.register("Amiel", "password789", "amiel@gmail.com")
        self.store_facade.register("YuvalMelamed", "PussyDestroyer69", "fuck@gmail.com")
        self.store_facade.loginAsGuest()
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.createStore("Feliks", "AriExpress")
        self.my_store: Store = self.store_facade.stores.get("AriExpress")
        self.store_facade.addNewProductToStore("Feliks", "AriExpress", "paper", 10, 500, "paper")
        #self.store_facade.addNewProductToStore("Feliks", "AriExpress", "headphones", 10, 500, "paper")
        self.item_paper: Product = self.my_store.getProductById(1, "Feliks")
        self.store_facade.logOut("Feliks")
        self.store_facade.onlineGuests.clear()
        self.store_facade.nextEntranceID = 0


    def test_nominations(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.nominateStoreOwner("Feliks","Amiel","AriExpress")
        self.store_facade.logInAsMember("Amiel","password789")
        self.store_facade.nominateStoreOwner("Feliks", "YuvalMelamed","AriExpress")
        self.store_facade.removeAccess("Feliks","Amiel","AriExpress")

    def test_nominationAgreements_success(self):
        self.store_facade.register("Sup", "password789", "ari@gmail.com")
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.nominateStoreOwner("Feliks","Amiel","AriExpress")
        self.store_facade.nominateStoreOwner("Feliks","Sup","AriExpress")
        self.store_facade.logInAsMember("Amiel","password789")
        self.store_facade.logInAsMember("Sup","password789")
        self.store_facade.nominateStoreOwner("Amiel", "YuvalMelamed","AriExpress")
        request = self.store_facade.rejectStoreOwnerNomination("Feliks","YuvalMelamed","AriExpress")
        print("hi")
        # self.store_facade.approveStoreOwnerNomination("Sup","YuvalMelamed","AriExpress")



    def test_simple_dis(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        oreo = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 500, "Milk")
        self.store_facade.addDiscount("AriExpress","Feliks","Simple",60,"Product",2)
        self.store_facade.addToBasket("Feliks", "AriExpress",2,1)

    def test_discount_conditioned_basket_total_price(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        headphones = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "headphones", 10, 500, "paper")
        rule2 = {'rule_type': 'basket_total_price', 'product_id': '', 'operator': '>=', 'quantity': '100', 'category': '', 'child': {}}
        #rule =  {'rule_type': 'basket_total_price', 'product_id': '', 'operator': '>=', 'quantity': '100', 'category': '', 'child': {'logic_type': 'AND', 'rule': {'rule_type': 'amount_of_category', 'product_id': '', 'operator': '<=', 'quantity': '5', 'category': 'fruit', 'child': {}}}}
        self.store_facade.addDiscount("AriExpress","Feliks","Conditioned",60,"Product",2,
                                      rule2)
        self.store_facade.addToBasket("Feliks", "AriExpress",2,1)
        print(self.store_facade.getBasket("Feliks", "AriExpress").toJson())
        #print(self.store_facade.getBasket("Feliks", "AriExpress").products.get())


    # __getAdmin
    def test_getAdmin_success(self):
        admin: Admin = self.store_facade.getAdmin("Ari")
        self.assertTrue(admin.user_name == "Ari" and admin.email == "ari@gmail.com")
        admin2: Admin = self.store_facade.getAdmin("Rubin")
        self.assertTrue(admin2.user_name == "Rubin" and admin2.email == "rubin@gmail.com")

    def test_getAdmin_fail(self):
        with self.assertRaises(Exception):
            admin: Admin = self.store_facade.getAdmin("Felix")
            self.assertTrue(admin.user_name == "Felix" and admin.email == "felix@gmail.com")

    # __getOnlineMemberOnly
    def test_getOnlineMemberOnly_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        member: Member = self.store_facade.getOnlineMemberOnly("Feliks")
        self.assertTrue(member.user_name == "Feliks" and member.email == "feliks@gmail.com")

    def test_getOnlineMemberOnly_fail(self):
        with self.assertRaises(Exception):
            member: Member = self.store_facade.getOnlineMemberOnly("Feliks")
            self.assertTrue(member.user_name == "Feliks" and member.email == "feliks@gmail.com")

    # __getUserOrMember
    def test_getUserOrMember_getUser_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        member: Member = self.store_facade.getUserOrMember("Feliks")
        self.assertTrue(member.user_name == "Feliks" and member.email == "feliks@gmail.com")

    def test_getUserOrMember_getGuest_success(self):
        self.store_facade.loginAsGuest()
        guest: Guest = self.store_facade.getUserOrMember(0)
        self.assertTrue(guest.get_entrance_id() == "0")

    def test_getUserOrMember_getGuest_fail(self):
        with self.assertRaises(Exception):
            guest: Guest = self.store_facade.getUserOrMember(5)

    def test_getUserOrMember_getMember_fail(self):
        with self.assertRaises(Exception):
            self.store_facade.logInAsMember("Feliks", "password456")
            member: Member = self.store_facade.getUserOrMember("someone")

    # addAdmin
    def test_addAdmin_success(self):
        self.store_facade.addAdmin("Ari", "yoav", "password789", "yoav@gmail.com")
        self.assertTrue(self.store_facade.admins.keys().__contains__("yoav"))

    def test_addAdmin_userNotAdmin_fail(self):
        with self.assertRaises(Exception):
            self.store_facade.addAdmin("Felix", "yoav", "password789", "yoav@gmail.com")
        self.assertTrue(not self.store_facade.admins.keys().__contains__("yoav"))

    def test_addAdmin_newAdminAlreadyAdmin_fail(self):
        with self.assertRaises(Exception):
            self.store_facade.addAdmin("Ari", "Rubin", "password789", "yoav@gmail.com")

    def test_addAdmin_weakPassword_fail(self):
        with self.assertRaises(Exception):
            self.store_facade.addAdmin("Ari", "Rubin", "pass", "yoav@gmail.com")

    def test_addAdmin_selfAddToAdmin_fail(self):
        with self.assertRaises(Exception):
            self.store_facade.addAdmin("Ari", "Ari", "pass", "yoav@gmail.com")





    # addDiscount
    def test_addSimpleDiscount_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 5, 1, "cookies")
        discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Simple", percent=10, level="Product",
                                             level_name=oreo.get_product_id())
        added_discount = self.my_store.getDiscount(1)
        self.assertEqual(discount, added_discount)

    def test_addConditionedDiscountBasketPriceUpdated_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 10, "cookies")
        rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(),
                "operator": ">=", "quantity": 1, "category": "", "child": {}}
        discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Conditioned", percent=10, level="Product",
                                             level_name=oreo.get_product_id(), rule=rule)
        added_discount = self.my_store.getDiscount(1)
        self.store_facade.addToBasket("Feliks", "AriExpress", oreo.get_product_id(), 8)


    def test_addSimpleDiscount_userNotLoggedIn_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 5, 1, "cookies")
        self.store_facade.logOut("Feliks")
        with self.assertRaises(Exception):
            discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Simple", percent=10, level="Product",
                                                 level_name=oreo.get_product_id())
        try:
            added_discount = self.my_store.getDiscount(1)
        except Exception as e:
            self.assertEqual(e.args[0], "No such discount exists")

    def test_addSimpleDiscount_storeNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 5, 1, "cookies")
        with self.assertRaises(Exception):
            discount = self.store_facade.addDiscount("some_store", "Feliks", "Simple", percent=10, level="Product",
                                                     level_name=oreo.get_product_id())
        try:
            added_discount = self.my_store.getDiscount(1)
        except Exception as e:
            self.assertEqual(e.args[0], "No such discount exists")

    def test_addSimpleDiscount_userWithoutPermission_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 5, 1, "cookies")
        with self.assertRaises(Exception):
            discount = self.store_facade.addDiscount("AriExpress", "Amiel", "Simple", percent=10, level="Product",
                                                     level_name=oreo.get_product_id())
        try:
            added_discount = self.my_store.getDiscount(1)
        except Exception as e:
            self.assertEqual(e.args[0], "No such discount exists")

    def test_addSimpleDiscount_productNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        with self.assertRaises(Exception):
            discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Simple", percent=10, level="Product",
                                                     level_name=2)
        try:
            added_discount = self.my_store.getDiscount(1)
        except Exception as e:
            self.assertEqual(e.args[0], "No such discount exists")
        self.assertFalse(self.my_store.get_products().__contains__(2))
    def test_addSimpleDiscount_productAlreadyInSimpleDiscount_Success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 5, 1, "cookies")
        discount1 = self.store_facade.addDiscount("AriExpress", "Feliks", "Simple", percent=10, level="Product",
                                                  level_name=1)
        discount2 = self.store_facade.addDiscount("AriExpress", "Feliks", "Simple", percent=20, level="Product",
                                                  level_name=1)
        discount_policy: DiscountPolicy = self.my_store.get_discount_policy()
        total_discount = discount_policy.calculateOverallDiscountsForSimple()
        self.assertTrue(total_discount == 30)
        # todo: ask amiel

    def test_addSimpleDiscount_invalidDiscountType_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 5, 1, "cookies")
        with self.assertRaises(Exception):
            discount = self.store_facade.addDiscount("AriExpress", "Feliks", "lol", percent=10, level="Product",
                                                     level_name=1)
        try:
            added_discount = self.my_store.getDiscount(1)
        except Exception as e:
            self.assertEqual(e.args[0], "No such discount exists")


    def test_addDiscount_invalidDiscountPercentage_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 5, 1, "cookies")
        with self.assertRaises(Exception):
            discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Simple", percent=101, level="Product",
                                                     level_name=1)
        with self.assertRaises(Exception):
            discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Simple", percent=0, level="Product",
                                                     level_name=1)
        try:
            added_discount = self.my_store.getDiscount(1)
        except Exception as e:
            self.assertEqual(e.args[0], "No such discount exists")

    # Condition Discounts
    def test_calculateConditionedDiscount_byCategory_OR_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 5, 1, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks","AriExpress", "cariot", 10, 10, "Milk")
        sub_rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(),
                        "operator":">=", "quantity": 1,"category": "", "child": {}}
        rule = {"rule_type": "amount_of_product", "product_id": cariot.get_product_id(),
                     "operator": ">=", "quantity": 1,"category": "", "child": {"logic_type": "OR", "rule": sub_rule}}
        discount = self.my_store.addDiscount("Feliks", "Conditioned", percent=10, level="Product",
                                               level_name=self.item_paper.get_product_id(), rule=rule)
        product_dict = {cariot.get_product_id(): (cariot,2), oreo.get_product_id(): (oreo,2)}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(self.item_paper, product_dict, 0)
        self.assertEqual(450, price_after_discount_1)

    def test_calculateConditionedDiscount_byCategory_OR_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 5, 10, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks","AriExpress", "cariot", 10, 10, "Milk")
        sub_rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(),
                        "operator":">=", "quantity": 5,"category": "", "child": {}}
        rule = {"rule_type": "amount_of_product", "product_id": cariot.get_product_id(),
                     "operator": ">=", "quantity": 5,"category": "", "child": {"logic_type": "OR", "rule": sub_rule}}
        discount = self.my_store.addDiscount("Feliks", "Conditioned", percent=10, level="Product",
                                               level_name=self.item_paper.get_product_id(), rule=rule)
        product_dict = {cariot.get_product_id(): (cariot,2), oreo.get_product_id(): (oreo,2)}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(self.item_paper, product_dict, 0)
        self.assertEqual(500, price_after_discount_1)
    def test_calculateConditionedDiscount_byCategory_userNotLoggedIn_Fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 5, 1, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks","AriExpress", "cariot", 10, 10, "Milk")
        sub_rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(),
                        "operator":">=", "quantity": 1,"category": "", "child": {}}
        rule = {"rule_type": "amount_of_product", "product_id": cariot.get_product_id(),
                     "operator": ">=", "quantity": 1,"category": "", "child": {"logic_type": "OR", "rule": sub_rule}}
        self.store_facade.logOut("Feliks")
        with self.assertRaises(Exception):
            discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Conditioned", percent=10, level="Product",
                                               level_name=self.item_paper.get_product_id(), rule=rule)
        product_dict = {cariot.get_product_id(): 2, oreo.get_product_id(): 2}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(self.item_paper, product_dict, 0)
        self.assertEqual(500, price_after_discount_1)


    def test_calculateConditionedDiscount_byCategory_storeDoesNotExist_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 5, 1, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "cariot", 10, 10, "Milk")
        sub_rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(),
                    "operator": ">=", "quantity": 1, "category": "", "child": {}}
        rule = {"rule_type": "amount_of_product", "product_id": cariot.get_product_id(),
                "operator": ">=", "quantity": 1, "category": "", "child": {"logic_type": "OR", "rule": sub_rule}}
        with self.assertRaises(Exception):
            discount = self.store_facade.addDiscount("SomeStore", "Feliks", "Conditioned", percent=10, level="Product",
                                                     level_name=self.item_paper.get_product_id(), rule=rule)
        product_dict = {cariot.get_product_id(): 2, oreo.get_product_id(): 2}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(self.item_paper, product_dict, 0)
        self.assertEqual(500, price_after_discount_1)



    def test_calculateConditionedDiscount_byCategory_XOR_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 1, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "cariot", 10, 10, "Milk")
        sub_rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(),
                    "operator": ">=", "quantity": 5, "category": "", "child": {}}
        rule = {"rule_type": "amount_of_product", "product_id": cariot.get_product_id(),
                "operator": ">=", "quantity": 5, "category": "", "child": {"logic_type": "XOR", "rule": sub_rule}}

        discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Conditioned", percent=10, level="Product",
                                                     level_name=self.item_paper.get_product_id(), rule=rule)
        product_dict = {cariot.get_product_id(): (cariot,2), oreo.get_product_id(): (oreo,7)}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(self.item_paper, product_dict, 0)
        self.assertEqual(450, price_after_discount_1)

    def test_calculateConditionedDiscount_byCategory_XOR_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 1, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "cariot", 10, 10, "Milk")
        sub_rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(),
                    "operator": ">=", "quantity": 5, "category": "", "child": {}}
        rule = {"rule_type": "amount_of_product", "product_id": cariot.get_product_id(),
                "operator": ">=", "quantity": 5, "category": "", "child": {"logic_type": "XOR", "rule": sub_rule}}

        discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Conditioned", percent=10, level="Product",
                                                     level_name=self.item_paper.get_product_id(), rule=rule)
        product_dict = {cariot.get_product_id(): (cariot,7), oreo.get_product_id(): (oreo,7)}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(self.item_paper, product_dict, 0)
        self.assertEqual(500, price_after_discount_1)

    def test_calculateConditionedDiscount_byCategory_XOR_fail2(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 1, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "cariot", 10, 10, "Milk")
        sub_rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(),
                    "operator": ">=", "quantity": 5, "category": "", "child": {}}
        rule = {"rule_type": "amount_of_product", "product_id": cariot.get_product_id(),
                "operator": ">=", "quantity": 5, "category": "", "child": {"logic_type": "XOR", "rule": sub_rule}}

        discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Conditioned", percent=10, level="Product",
                                                     level_name=self.item_paper.get_product_id(), rule=rule)
        product_dict = {cariot.get_product_id(): (cariot,0), oreo.get_product_id(): (oreo,0)}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(self.item_paper, product_dict, 0)
        self.assertEqual(500, price_after_discount_1)

    def test_calculateConditionedDiscount_byCategory_AND_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 1, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "cariot", 10, 10, "Milk")
        sub_rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(),
                    "operator": ">=", "quantity": 5, "category": "", "child": {}}
        rule = {"rule_type": "amount_of_product", "product_id": cariot.get_product_id(),
                "operator": ">=", "quantity": 5, "category": "", "child": {"logic_type": "AND", "rule": sub_rule}}

        discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Conditioned", percent=10, level="Product",
                                                     level_name=self.item_paper.get_product_id(), rule=rule)
        product_dict = {cariot.get_product_id(): (cariot,8), oreo.get_product_id(): (oreo,7)}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(self.item_paper, product_dict, 0)
        self.assertEqual(450, price_after_discount_1)

    def test_calculateConditionedDiscount_byCategory_AND_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 1, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "cariot", 10, 10, "Milk")
        sub_rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(),
                    "operator": ">=", "quantity": 5, "category": "", "child": {}}
        rule = {"rule_type": "amount_of_product", "product_id": cariot.get_product_id(),
                "operator": ">=", "quantity": 5, "category": "", "child": {"logic_type": "AND", "rule": sub_rule}}

        discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Conditioned", percent=10, level="Product",
                                                     level_name=self.item_paper.get_product_id(), rule=rule)
        product_dict = {cariot.get_product_id(): (cariot, 8), oreo.get_product_id(): (oreo, 4)}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(self.item_paper, product_dict, 0)
        self.assertEqual(500, price_after_discount_1)

    def test_calculateAddDiscountWithSimpleDiscount_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 1, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "cariot", 10, 10, "Milk")
        discounts = {"1": {"discount_type": "Simple", "percent": 20, "level": "Category", "level_name": "Milk"},
                     "2": {"discount_type": "Simple", "percent": 10, "level": "Product", "level_name": cariot.get_product_id()}}
        discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Add", discounts=discounts)
        product_dict = {cariot.get_product_id(): (cariot,8)}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(cariot, product_dict, 0)
        self.assertTrue(price_after_discount_1 == 7)

    def test_calculateMaxDiscountWithSimpleDiscount_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 1, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "cariot", 10, 10, "Milk")
        discounts = {"1": {"discount_type": "Simple", "percent": 20, "level": "Category", "level_name": "Milk"},
                     "2": {"discount_type": "Simple", "percent": 10, "level": "Product", "level_name": cariot.get_product_id()}}
        discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Max", discounts=discounts)
        product_dict = {cariot.get_product_id(): (cariot,8)}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(cariot, product_dict, 0)
        self.assertTrue(price_after_discount_1 == 8)

    def test_calculateAddDiscountWithThreeSimpleDiscount_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 1, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "cariot", 10, 10, "Milk")
        discounts = {"1": {"discount_type": "Simple", "percent": 20, "level": "Category", "level_name": "Milk"},
                     "2": {"discount_type": "Simple", "percent": 10, "level": "Product", "level_name": cariot.get_product_id()},
                     "3": {"discount_type": "Simple", "percent": 20, "level": "Store", "level_name": ""}}
        discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Add", discounts=discounts)
        product_dict = {cariot.get_product_id(): (cariot,8)}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(cariot, product_dict, 0)
        self.assertTrue(price_after_discount_1 == 5)

    def test_calculateMaxDiscountWithConditionedDiscount_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 1, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "cariot", 10, 10, "Milk")
        rule = {"rule_type": "amount_of_product", "product_id": cariot.get_product_id(),
                "operator": ">=", "quantity": 5, "category": "", "child": {}}

        discounts = {"1": {"discount_type": "Conditioned", "percent": 20, "level": "Product", "level_name": cariot.get_product_id(), "rule": rule},
                     "2": {"discount_type": "Simple", "percent": 10, "level": "Product", "level_name": cariot.get_product_id()}}

        discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Max", discounts=discounts)
        product_dict = {cariot.get_product_id(): (cariot,8)}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(cariot, product_dict, 0)
        self.assertTrue(price_after_discount_1 == 8)

    def test_PurchaseCartWithDiscounts_byCategory_success(self):
        transaction_history = TransactionHistory()
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 10, "cookies")
        cariot: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "cariot", 10, 10, "Milk")
        sub_rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(),
                    "operator": ">=", "quantity": 5, "category": "", "child": {}}
        rule = {"rule_type": "amount_of_product", "product_id": cariot.get_product_id(),
                "operator": ">=", "quantity": 5, "category": "", "child": {"logic_type": "AND", "rule": sub_rule}}
        discount = self.store_facade.addDiscount("AriExpress", "Feliks", "Conditioned", percent=10, level="Product",
                                                 level_name=self.item_paper.get_product_id(), rule=rule)

        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel" , "AriExpress", 1, 1)
        self.store_facade.addToBasket("Amiel", "AriExpress", 2, 10)
        self.store_facade.addToBasket("Amiel", "AriExpress", 3, 10)
        self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel saad", "555", "123456789",
                                       "some_address", "be'er sheva", "Israel", "1234567")
        user_transaction_list: list = transaction_history.get_User_Transactions("Amiel")
        user_transaction: UserTransaction = user_transaction_list[0]
        self.assertEqual(650, user_transaction.get_overall_price())

    # addNewProductToStore
    def test_addNewProductToStore_success(self):
        # before
        self.store_facade.logInAsMember("Feliks", "password456")
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)
        # after
        self.store_facade.addNewProductToStore("Feliks", "AriExpress", "shoes", 10, 500, "shoes")
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 2)
        new_product: Product = self.my_store.getProductById(2, "Feliks")
        self.assertTrue(new_product.get_name() == "shoes")

    def test_addNewProductToStore_userNotLoggedIn_fail(self):
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)
        with self.assertRaises(Exception):
            self.store_facade.addNewProductToStore("Feliks", "AriExpress", "shoes", 10, 500, "shoes")
        # checks if the store products list hasn't changed
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)

    def test_addNewProductToStore_storeNotExists_fail(self):
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)
        with self.assertRaises(Exception):
            self.store_facade.addNewProductToStore("Feliks", "Some_Store", "shoes", 10, 500, "shoes")

    def test_addNewProductToStore_userWithoutPermission_fail(self):
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)
        self.store_facade.logInAsMember("Amiel", "password789")
        with self.assertRaises(Exception):
            # Amiel is trying to add a product to a store he doesn't own or manage
            self.store_facade.addNewProductToStore("Amiel", "AriExpress", "shoes", 10, 500, "shoes")
        # checks if the store products list hasn't changed
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)

    def test_addNewProductToStore_invalidPrice_0_fail(self):
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            # Amiel is trying to add a product to a store he doesn't own or manage
            self.store_facade.addNewProductToStore("Amiel", "AriExpress", "shoes", 10, 0, "shoes")
        # checks if the store products list hasn't changed
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)

    def test_addNewProductToStore_invalidPrice_negativePrice_fail(self):
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            # Amiel is trying to add a product to a store he doesn't own or manage
            self.store_facade.addNewProductToStore("Amiel", "AriExpress", "shoes", 10, -1, "shoes")
        # checks if the store products list hasn't changed
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)

    def test_addNewProductToStore_invalidQuantity_0_fail(self):
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            # zero price
            self.store_facade.addNewProductToStore("Amiel", "AriExpress", "shoes", 0, 500, "shoes")
        # checks if the store products list hasn't changed
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)

    def test_addNewProductToStore_invalidQuantity_negativeQuantity_fail(self):
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            # negative price
            self.store_facade.addNewProductToStore("Amiel", "AriExpress", "shoes", -1, 500, "shoes")
        # checks if the store products list hasn't changed
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)

    def test_addNewProductToStore_invalidCategory_fail(self):
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            # empty category
            self.store_facade.addNewProductToStore("Amiel", "AriExpress", "shoes", -1, 500, "")
        # checks if the store products list hasn't changed
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)

    def test_addNewProductToStore_invalidName_fail(self):
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            # empty name
            self.store_facade.addNewProductToStore("Amiel", "AriExpress", "", -1, 500, "shoes")
        # checks if the store products list hasn't changed
        self.assertTrue(len(self.my_store.getProducts("Feliks").values()) == 1)

    # addPermissions

    def test_modifyPermissions(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.nominateStoreOwner("Feliks", "Amiel", "AriExpress")
        self.store_facade.removePermissions( "AriExpress", "Feliks", "Amiel", "Bid")
        self.store_facade.removePermissions( "AriExpress", "Feliks", "Amiel", "ProductChange")
        self.assertTrue(self.my_store.get_accesses().get("Amiel").hasRole("Owner"))

    def test_Owner_success(self):
        member_to_nominate: Member = self.store_facade.members.get("Amiel")
        # before
        self.assertTrue(not member_to_nominate.accesses.keys().__contains__("AriExpress"))
        # after
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.nominateStoreOwner("Feliks", "Amiel", "AriExpress")
        self.assertTrue(member_to_nominate.accesses.keys().__contains__("AriExpress"))
        access: Access = member_to_nominate.get_accesses().get("AriExpress")
        self.assertTrue(access.get_nominated_by_username() == "Feliks")
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Amiel"))
        self.assertTrue(access.hasRole("Owner"))

    def test_nominateManager_success(self):
        member_to_nominate: Member = self.store_facade.members.get("Amiel")
        # before
        self.assertTrue(not member_to_nominate.accesses.keys().__contains__("AriExpress"))
        # after
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.nominateStoreManager("Feliks", "Amiel", "AriExpress")
        self.assertTrue(member_to_nominate.accesses.keys().__contains__("AriExpress"))
        access: Access = member_to_nominate.get_accesses().get("AriExpress")
        self.assertTrue(access.get_nominated_by_username() == "Feliks")
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Amiel"))
        self.assertTrue(access.hasRole("Manager"))

    def test_nominate_nomineeNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            self.store_facade.nominateStoreOwner("Feliks", "some_random_guy", "AriExpress")
        self.assertFalse(len(self.my_store.get_accesses().values()) == 2)
        self.assertTrue(len(self.my_store.get_accesses().values()) == 1)

    def test_nominate_storeNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            self.store_facade.nominateStoreOwner("Feliks", "Amiel", "some_store")
        self.assertFalse(self.store_facade.stores.keys().__contains__("some_store"))

    def test_nominate_userWithoutPermission_Ownertry_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        with self.assertRaises(Exception):
            self.store_facade.nominateStoreOwner("Amiel", "YuvalMelamed", "AriExpress")
        self.assertFalse(len(self.my_store.get_accesses().values()) == 2)
        self.assertTrue(len(self.my_store.get_accesses().values()) == 1)
        yuval: Member = self.store_facade.members.get("YuvalMelamed")
        self.assertFalse(yuval.get_accesses().keys().__contains__("AriExpress"))

    def test_nominate_userWithoutPermission_Managertry_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        with self.assertRaises(Exception):
            self.store_facade.nominateStoreManager("Amiel", "YuvalMelamed", "AriExpress")
        self.assertFalse(len(self.my_store.get_accesses().values()) == 2)
        self.assertTrue(len(self.my_store.get_accesses().values()) == 1)
        yuval: Member = self.store_facade.members.get("YuvalMelamed")
        self.assertFalse(yuval.get_accesses().keys().__contains__("AriExpress"))

    def test_nominate_nomineeAlreadyHasBeenNominated_fail(self):
        member_to_nominate: Member = self.store_facade.members.get("Amiel")
        # before
        self.assertTrue(not member_to_nominate.accesses.keys().__contains__("AriExpress"))
        # after
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.nominateStoreOwner("Feliks", "Amiel", "AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.nominateStoreOwner("Feliks", "Amiel", "AriExpress")
        self.assertTrue(member_to_nominate.accesses.keys().__contains__("AriExpress"))
        access: Access = member_to_nominate.get_accesses().get("AriExpress")
        self.assertTrue(access.get_nominated_by_username() == "Feliks")
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Amiel"))
        self.assertTrue(access.hasRole("Owner"))

    # addPurchasePolicy

    def test_addPurchasePolicy_userNotLoggedIn_fail(self):
        pass

    def test_addPurchasePolicy_storeNotExists_fail(self):
        pass

    def test_addPurchasePolicy_userWithoutPermission_fail(self):
        pass

    def test_addPurchasePolicy_invalidPolicy_fail(self):
        pass

    # addToBasket
    def test_addToBasket_success(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        amiel: Member = self.store_facade.members.get("Amiel")
        self.assertTrue(amiel.cart.baskets.keys().__contains__("AriExpress"))
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        self.assertTrue(len(basket.products.values()) == 1)
        self.assertTrue(basket.products.keys().__contains__(1))
        product_tuple: tuple = basket.products.get(1)
        self.assertTrue(product_tuple[0] == self.item_paper)
        self.assertTrue(product_tuple[1] == 5)
        self.assertTrue(product_tuple[2] == 500)

    def test_addToBasket_fromMultipleStores_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.createStore("Feliks", "FeliksExpress")
        my_store2: Store = self.store_facade.stores.get("FeliksExpress")
        self.store_facade.addNewProductToStore("Feliks", "FeliksExpress", "shoes", 10, 500, "shoes")
        item_shoes: Product = my_store2.getProductById(1, "Feliks")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        self.store_facade.addToBasket("Amiel", "FeliksExpress", 1, 5)
        amiel: Member = self.store_facade.members.get("Amiel")
        self.assertTrue(amiel.cart.baskets.keys().__contains__("AriExpress"))
        self.assertTrue(amiel.cart.baskets.keys().__contains__("FeliksExpress"))
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        basket2: Basket = amiel.cart.baskets.get("FeliksExpress")
        self.assertTrue(basket.products.keys().__contains__(1))
        self.assertTrue(basket2.products.keys().__contains__(1))
        product_tuple: tuple = basket.products.get(1)
        product_tuple2: tuple = basket2.products.get(1)
        self.assertTrue(product_tuple[0] == self.item_paper)
        self.assertTrue(product_tuple[1] == 5)
        self.assertTrue(product_tuple[2] == 500)
        self.assertTrue(product_tuple2[0] == item_shoes)
        self.assertTrue(product_tuple2[1] == 5)
        self.assertTrue(product_tuple2[2] == 500)

    def test_addToBasket_userNotLoggedIn_fail(self):
        with self.assertRaises(Exception):
            self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        amiel: Member = self.store_facade.members.get("Amiel")
        self.assertFalse(amiel.cart.baskets.keys().__contains__("AriExpress"))

    def test_addToBasket_storeNotExists_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        with self.assertRaises(Exception):
            self.store_facade.addToBasket("Amiel", "some_store", 1, 5)
        amiel: Member = self.store_facade.members.get("Amiel")
        self.assertFalse(amiel.cart.baskets.keys().__contains__("some_store"))

    def test_addToBasket_productNotExists_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        with self.assertRaises(Exception):
            self.store_facade.addToBasket("Amiel", "AriExpress", 2, 5)
        amiel: Member = self.store_facade.members.get("Amiel")
        self.assertFalse(amiel.cart.baskets.keys().__contains__("AriExpress"))

    def test_addToBasket_invalidQuantity_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        with self.assertRaises(Exception):
            self.store_facade.addToBasket("Amiel", "AriExpress", 1, -1)
        amiel: Member = self.store_facade.members.get("Amiel")
        self.assertFalse(amiel.cart.baskets.keys().__contains__("AriExpress"))

    def test_addToBasket_productNotInStock_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        with self.assertRaises(Exception):
            self.store_facade.addToBasket("Amiel", "AriExpress", 1, 11)
        amiel: Member = self.store_facade.members.get("Amiel")
        self.assertFalse(amiel.cart.baskets.keys().__contains__("AriExpress"))



    # closeStore
    def test_closeStore_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        Feliks_Messages_count_before = MessageController().get_notifications("Feliks").__len__()
        self.store_facade.closeStore("Feliks", "AriExpress")
        self.assertFalse(self.store_facade.getStores()["AriExpress"].active)
        Feliks_Messages_count_after = MessageController().get_notifications("Feliks").__len__()
        self.assertEqual(Feliks_Messages_count_before + 1, Feliks_Messages_count_after, "Feliks should be notified")
        self.assertFalse(self.store_facade.getStores()["AriExpress"].active)

    def test_closeStore_userNotLoggedIn_fail(self):
        with self.assertRaises(Exception):
            self.store_facade.closeStore("Feliks", "AriExpress")
            # check if store is still active
        self.assertTrue(self.my_store.active)

    def test_closeStore_storeNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            self.store_facade.closeStore("Feliks", "some_store")
            # check if store is still active
        self.assertTrue(self.my_store.active)

    def test_closeStore_userWithoutAccessToStore_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        with self.assertRaises(Exception):
            self.store_facade.closeStore("Amiel", "some_store")
            # check if store is still active
        self.assertTrue(self.my_store.active)

    def test_closeStore_userWithAccessToStoreAsOwner_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.nominateStoreOwner("Feliks", "Amiel", "AriExpress")
        self.store_facade.logInAsMember("Amiel", "password789")
        with self.assertRaises(Exception):
            self.store_facade.closeStore("Amiel", "some_store")
            # check if store is still active
        self.assertTrue(self.my_store.active)

    def test_closeStore_userWithAccessToStoreAsManager_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.nominateStoreManager("Feliks", "Amiel", "AriExpress")
        self.store_facade.logInAsMember("Amiel", "password789")
        with self.assertRaises(Exception):
            self.store_facade.closeStore("Amiel", "some_store")
            # check if store is still active
        self.assertTrue(self.my_store.active)

    def test_closeStore_storeAlreadyClosed_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.closeStore("Feliks", "AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.closeStore("Feliks", "AriExpress")
            # check if store is still active
        self.my_store = self.store_facade.stores.get("AriExpress")
        self.assertFalse(self.my_store.active)

    # closeStoreAsAdmin
    def test_closeStoreAsAdmin_success(self):
        self.store_facade.logInAsAdmin("Ari", "password123")
        self.store_facade.closeStoreAsAdmin("Ari", "AriExpress")
        self.my_store = self.store_facade.getStores()["AriExpress"]
        self.assertTrue(self.my_store.closed_by_admin)
        self.assertFalse(self.my_store.active)

    def test_closeStoreAsAdmin_userNotLoggedIn_fail(self):
        with self.assertRaises(Exception):
            self.store_facade.closeStoreAsAdmin("Ari", "AriExpress")
        self.assertFalse(self.my_store.closed_by_admin)
        self.assertTrue(self.my_store.active)

    def test_closeStoreAsAdmin_storeNotExists_fail(self):
        self.store_facade.logInAsAdmin("Ari", "password123")
        with self.assertRaises(Exception):
            self.store_facade.closeStoreAsAdmin("Ari", "some_store")
        self.assertFalse(self.my_store.closed_by_admin)
        self.assertTrue(self.my_store.active)

    def test_closeStoreAsAdmin_userNotAdmin_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            self.store_facade.closeStoreAsAdmin("Feliks", "AriExpress")
        self.assertFalse(self.my_store.closed_by_admin)
        self.assertTrue(self.my_store.active)

    def test_closeStoreAsAdmin_storeAlreadyClosed_fail(self):
        self.store_facade.logInAsAdmin("Ari", "password123")
        self.store_facade.closeStoreAsAdmin("Ari", "AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.closeStoreAsAdmin("Ari", "AriExpress")
        self.my_store = self.store_facade.getStores()["AriExpress"]
        self.assertTrue(self.my_store.closed_by_admin)
        self.assertFalse(self.my_store.active)

    # editBasketQuantity
    def test_editBasketQuantity_member_success(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        product_tuple: tuple = basket.products.get(1)
        self.assertTrue(product_tuple[1] == 5)
        self.store_facade.editBasketQuantity("Amiel", "AriExpress", 1, 8)
        product_tuple2: tuple = basket.products.get(1)
        self.assertTrue(product_tuple2[1] == 8)

    def test_editBasketQuantity_guest_success(self):
        self.store_facade.loginAsGuest()
        guest: Guest = self.store_facade.onlineGuests.get("0")
        self.store_facade.addToBasket("0", "AriExpress", 1, 5)
        basket: Basket = guest.cart.baskets.get("AriExpress")
        product_tuple: tuple = basket.products.get(1)
        self.assertTrue(product_tuple[1] == 5)
        self.store_facade.editBasketQuantity("0", "AriExpress", 1, 8)
        product_tuple2: tuple = basket.products.get(1)
        self.assertTrue(product_tuple2[1] == 8)

    def test_editBasketQuantity_userNotLoggedIn_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        product_tuple: tuple = basket.products.get(1)
        self.assertTrue(product_tuple[1] == 5)
        self.store_facade.logOut("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.editBasketQuantity("Amiel", "AriExpress", 1, 8)
        product_tuple2: tuple = basket.products.get(1)
        self.assertFalse(product_tuple2[1] == 8)
        self.assertTrue(product_tuple2[1] == 5)

    def test_editBasketQuantity_storeNotExists_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        product_tuple: tuple = basket.products.get(1)
        self.assertTrue(product_tuple[1] == 5)
        with self.assertRaises(Exception):
            self.store_facade.editBasketQuantity("Amiel", "some_store", 1, 8)
        product_tuple2: tuple = basket.products.get(1)
        self.assertFalse(product_tuple2[1] == 8)
        self.assertTrue(product_tuple2[1] == 5)

    def test_editBasketQuantity_productNotExists_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        product_tuple: tuple = basket.products.get(1)
        self.assertTrue(product_tuple[1] == 5)
        with self.assertRaises(Exception):
            self.store_facade.editBasketQuantity("Amiel", "AriExpress", 2, 8)
        product_tuple2: tuple = basket.products.get(1)
        self.assertFalse(product_tuple2[1] == 8)
        self.assertTrue(product_tuple2[1] == 5)


    def test_editBasketQuantity_invalidQuantity_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        product_tuple: tuple = basket.products.get(1)
        self.assertTrue(product_tuple[1] == 5)
        with self.assertRaises(Exception):
            self.store_facade.editBasketQuantity("Amiel", "AriExpress", 1, -5)
        product_tuple2: tuple = basket.products.get(1)
        self.assertFalse(product_tuple2[1] == 8)
        self.assertTrue(product_tuple2[1] == 5)

    def test_editBasketQuantity_productNotInBasket_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        with self.assertRaises(Exception):
            self.store_facade.editBasketQuantity("Amiel", "AriExpress", 1, 8)
        self.assertTrue(not amiel.cart.baskets.keys().__contains__("AriExpress"))

    # editProductOfStore
    def test_editProductOfStore_changeQuantityAndPrice_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        product: Product = self.my_store.getProductById(1, "Feliks")
        # before
        self.assertTrue(product.quantity == 10)
        self.assertTrue(product.price == 500)
        self.store_facade.editProductOfStore("Feliks", "AriExpress", 1, quantity=4, price=25)
        self.store_facade.editProductOfStore("Feliks", "AriExpress", 1, quantity=4 , price=25)
        # after
        edited_product: Product = self.my_store.getProductById(1, "Feliks")
        self.assertTrue(edited_product.quantity == 4)
        self.assertTrue(edited_product.price == 25)

    def test_editProductOfStore_userNotLoggedIn_fail(self):
        product: Product = self.my_store.getProductById(1, "Feliks")
        # before
        self.assertTrue(product.quantity == 10)
        self.assertTrue(product.price == 500)
        with self.assertRaises(Exception):
            self.store_facade.editProductOfStore("Feliks", "AriExpress", 1, quantity=4, price=25)
        # after
        self.assertTrue(product.quantity == 10)
        self.assertTrue(product.price == 500)

    def test_editProductOfStore_storeNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        product: Product = self.my_store.getProductById(1, "Feliks")
        self.assertTrue(product.quantity == 10)
        self.assertTrue(product.price == 500)
        with self.assertRaises(Exception):
            self.store_facade.editProductOfStore("Feliks", "some_store", 1, quantity=4, price=25)
        self.assertTrue(product.quantity == 10)
        self.assertTrue(product.price == 500)

    def test_editProductOfStore_userWithoutPermission_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        product: Product = self.my_store.getProductById(1, "Feliks")
        self.assertTrue(product.quantity == 10)
        self.assertTrue(product.price == 500)
        with self.assertRaises(Exception):
            self.store_facade.editProductOfStore("Amiel", "AriExpress", 1, quantity=4, price=25)
        self.assertTrue(product.quantity == 10)
        self.assertTrue(product.price == 500)

    def test_editProductOfStore_productNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        product: Product = self.my_store.getProductById(1, "Feliks")
        self.assertTrue(product.quantity == 10)
        self.assertTrue(product.price == 500)
        with self.assertRaises(Exception):
            self.store_facade.editProductOfStore("Feliks", "AriExpress", 2, quantity=4, price=25)
        self.assertTrue(product.quantity == 10)
        self.assertTrue(product.price == 500)

    def test_editProductOfStore_invalidQuantity_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        product: Product = self.my_store.getProductById(1, "Feliks")
        self.assertTrue(product.quantity == 10)
        with self.assertRaises(Exception):
            self.store_facade.editProductOfStore("Feliks", "AriExpress", 1, quantity=-4)
        self.assertTrue(product.quantity == 10)

    def test_editProductOfStore_invalidPrice_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        product: Product = self.my_store.getProductById(1, "Feliks")
        self.assertTrue(product.price == 500)
        with self.assertRaises(Exception):
            self.store_facade.editProductOfStore("Feliks", "AriExpress", 1, price=-5)
        self.assertTrue(product.price == 500)

    def test_editProductOfStore_invalidCategory_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        product: Product = self.my_store.getProductById(1, "Feliks")
        self.assertTrue(product.name == "paper")
        with self.assertRaises(Exception):
            self.store_facade.editProductOfStore("Feliks", "AriExpress", 1, category="")
        self.assertTrue(product.name == "paper")

    def test_editProductOfStore_invalidName_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        product: Product = self.my_store.getProductById(1, "Feliks")
        self.assertTrue(product.name == "paper")
        with self.assertRaises(Exception):
            self.store_facade.editProductOfStore("Feliks", "AriExpress", 1, name="")
        self.assertTrue(product.name == "paper")

    def test_editProductOfStore_productInSomeBasket_success(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        product_in_basket: Product = basket.products.get(1)[0]
        product: Product = self.my_store.getProductById(1, "Feliks")
        self.assertTrue(product.price == 500)
        self.store_facade.editProductOfStore("Feliks", "AriExpress", 1, price=1000)
        product: Product = self.my_store.getProductById(1, "Feliks")
        product_in_basket: Product = basket.products.get(1)[0]
        self.assertTrue(product.price == 1000)
        self.assertTrue(product_in_basket.price == 1000)

    def test_addToBasketInTwoStoresAndEdit_success(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("YuvalMelamed", "PussyDestroyer69")
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.createStore("YuvalMelamed","yuval_store")
        oreo: Product = self.store_facade.addNewProductToStore("YuvalMelamed","yuval_store","oreo", 20, 1, "cookies")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        self.store_facade.editBasketQuantity("Amiel", self.my_store.get_store_name(), 1, 8)
        self.store_facade.addToBasket("Amiel", "yuval_store", 1, 5)
        self.store_facade.editBasketQuantity("Amiel", "yuval_store", 1, 15)
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        basket2: Basket = amiel.cart.baskets.get("yuval_store")
        product_from_feliks = basket.products.get(1)
        product_from_yuval = basket.products.get(1)
        print("hi")



    # getAllBidsFromUser TODO:BIDS
    def test_getAllBidsFromUser_success(self):
        pass

    def test_getAllBidsFromUser_userNotLoggedIn_fail(self):
        pass

    def test_getAllBidsFromStore_success(self):
        pass

    def test_getAllBidsFromStore_userNotLoggedIn_fail(self):
        pass

    def test_getStaffPendingForBid_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        pending_list: list = self.store_facade.getStaffPendingForBid("AriExpress", 0)
        self.assertTrue(pending_list.__contains__("Feliks"))
        self.store_facade.approveBid("Feliks", "AriExpress", 0)
        pending_list: list = self.store_facade.getStaffPendingForBid("AriExpress", 0)
        self.assertFalse(pending_list.__contains__("Feliks"))

    def test_getStaffPendingForBid_TwoPeople_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("YuvalMelamed", "PussyDestroyer69")
        self.store_facade.nominateStoreOwner("Feliks", "YuvalMelamed", "AriExpress")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        pending_list: list = self.store_facade.getStaffPendingForBid("AriExpress", 0)
        self.assertTrue(pending_list.__contains__("Feliks"))
        self.assertTrue(pending_list.__contains__("YuvalMelamed"))
        self.store_facade.approveBid("Feliks", "AriExpress", 0)
        pending_list: list = self.store_facade.getStaffPendingForBid("AriExpress", 0)
        self.assertTrue(pending_list.__contains__("YuvalMelamed"))
        self.assertFalse(pending_list.__contains__("Feliks"))
        self.store_facade.approveBid("YuvalMelamed", "AriExpress", 0)
        pending_list: list = self.store_facade.getStaffPendingForBid("AriExpress", 0)
        self.assertFalse(pending_list.__contains__("YuvalMelamed"))
        self.assertFalse(pending_list.__contains__("Feliks"))
    def test_approveBid_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        bid: Bid = self.store_facade.approveBid("Feliks", "AriExpress", 0)
        self.assertTrue(bid.get_left_to_approval() == 0)
        self.assertTrue(bid.get_status() == 1)
        self.assertTrue(basket.get_bids().get(0).get_status() == 1)
    def test_approveBid_userNotLoggedIn_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.approveBid("Feliks", "AriExpress", 0)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(basket.get_bids().get(0).get_status() == 0)

    def test_approveBid_storeNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.approveBid("Feliks", "some_store", 0)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(basket.get_bids().get(0).get_status() == 0)



    def test_approveBid_bidNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.approveBid("Feliks", "AriExpress", 1)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(basket.get_bids().get(0).get_status() == 0)

    # placeBid

    def test_placeBid_success(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        self.assertTrue(len(list(basket.get_bids().values())) == 1)
        self.assertTrue(self.my_store.get_bids().__contains__(0))
        self.assertTrue(self.my_store.get_bids_requests().__contains__("Feliks"))


    def test_placeBid_guestLoggedIn_fail(self):
        self.store_facade.loginAsGuest()
        with self.assertRaises(Exception):
            self.store_facade.placeBid("0", "AriExpress", 2000, 1, 4)
        guest: Guest = self.store_facade.members.get("Amiel")
        with self.assertRaises(Exception):
            basket: Basket = guest.get_Basket("AriExpress")
        self.assertFalse(self.my_store.get_bids().__contains__(0))
        self.assertFalse(self.my_store.get_bids_requests().__contains__("Feliks"))

    def test_placeBid_userNotLoggedIn_fail(self):
        with self.assertRaises(Exception):
            self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        guest: Guest = self.store_facade.members.get("Amiel")
        with self.assertRaises(Exception):
            basket: Basket = guest.get_Basket("AriExpress")
        self.assertFalse(self.my_store.get_bids().__contains__(0))
        self.assertFalse(self.my_store.get_bids_requests().__contains__("Feliks"))

    def test_placeBid_storeNotExists_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        with self.assertRaises(Exception):
            self.store_facade.placeBid("Amiel", "some_store", 2000, 1, 4)
        member: Member = self.store_facade.members.get("Amiel")
        with self.assertRaises(Exception):
            basket: Basket = member.get_Basket("some_store")


    def test_placeBid_storeIsClosed_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.closeStore("Feliks", "AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.placeBid("Amiel", "some_store", 2000, 1, 4)
        member: Member = self.store_facade.members.get("Amiel")
        with self.assertRaises(Exception):
            basket: Basket = member.get_Basket("some_store")
        self.assertFalse(self.my_store.get_bids().__contains__(0))
        self.assertFalse(self.my_store.get_bids_requests().__contains__("Feliks"))

    def test_placeBid_productNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.closeStore("Feliks", "AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.placeBid("Amiel", "AriExpress", 2000, 5, 4)
        member: Member = self.store_facade.members.get("Amiel")
        with self.assertRaises(Exception):
            basket: Basket = member.get_Basket("some_store")
        self.assertFalse(self.my_store.get_bids().__contains__(0))
        self.assertFalse(self.my_store.get_bids_requests().__contains__("Feliks"))


    def test_placeBid_quantityInvalid_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.closeStore("Feliks", "AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 0)
        member: Member = self.store_facade.members.get("Amiel")
        with self.assertRaises(Exception):
            basket: Basket = member.get_Basket("some_store")
        self.assertFalse(self.my_store.get_bids().__contains__(0))
        self.assertFalse(self.my_store.get_bids_requests().__contains__("Feliks"))


    # purchaseConfirmedBid
    def test_purchaseConfirmedBid_success(self):
        transaction_history = TransactionHistory()
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        self.assertTrue(len(list(basket.get_bids().values())) == 1)
        self.assertTrue(self.my_store.get_bids().__contains__(0))
        Amiel_Messages_count_before = MessageController().get_notifications("Amiel").__len__()
        AriExpress_Messages_count_before = MessageController().get_notifications("Feliks").__len__()
        self.assertTrue(self.my_store.get_bids_requests().__contains__("Feliks"))
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        bid: Bid = self.store_facade.approveBid("Feliks", "AriExpress", 0)
        self.assertTrue(bid.get_left_to_approval() == 0)
        self.assertTrue(bid.get_status() == 1)
        self.assertTrue(basket.get_bids().get(0).get_status() == 1)
        self.store_facade.purchaseConfirmedBid(0, "AriExpress", "Amiel", "4580030389763292", "23/12", "Amiel saad",
                                               "456", "313277949","Shimoni", "Beer Sheva", "Israel", "1533732")
        Amiel_Messages_count_after = MessageController().get_notifications("Amiel").__len__()
        AriExpress_Messages_count_after = MessageController().get_notifications("Feliks").__len__()
        self.assertTrue(len(transaction_history.get_User_Transactions("Amiel")) == 1)
        self.assertTrue(len(transaction_history.get_Store_Transactions("AriExpress")) == 1)
        self.assertFalse(basket.get_bids().__contains__(0))
        self.assertFalse(self.my_store.get_bids().__contains__(0))
        self.assertEqual(AriExpress_Messages_count_after, AriExpress_Messages_count_before + 1,
                         "AriExpress should be notified")
        self.assertEqual(Amiel_Messages_count_after, Amiel_Messages_count_before + 1, "Amiel should be notified")
        transaction_history.clearAllHistory()
    def test_purchaseConfirmedBid_userNotLoggedIn_fail(self):
        transaction_history = TransactionHistory()
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        self.assertTrue(len(list(basket.get_bids().values())) == 1)
        self.assertTrue(self.my_store.get_bids().__contains__(0))
        Amiel_Messages_count_before = MessageController().get_notifications("Amiel").__len__()
        AriExpress_Messages_count_before = MessageController().get_notifications("Feliks").__len__()
        # self.assertTrue(self.my_store.get_bids_requests().__contains__("Feliks"))
        # self.assertTrue(bid.get_left_to_approval() == 1)
        # self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        bid: Bid = self.store_facade.approveBid("Feliks", "AriExpress", 0)
        self.assertTrue(bid.get_left_to_approval() == 0)
        self.assertTrue(bid.get_status() == 1)
        self.assertTrue(basket.get_bids().get(0).get_status() == 1)
        # self.store_facade.logOut("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.purchaseConfirmedBid(0, "AriExpress", "Amiel", "4580030389763292", "23/12", "Amiel saad",
                                               "456", "313277949", "Shimoni", "Beer Sheva", "Israel", "1533732")
        Amiel_Messages_count_after = MessageController().get_notifications("Amiel").__len__()
        AriExpress_Messages_count_after = MessageController().get_notifications("Feliks").__len__()
        self.assertTrue(len(transaction_history.get_User_Transactions("Amiel")) == 0)
        self.assertTrue(len(transaction_history.get_Store_Transactions("AriExpress")) == 0)
        self.assertTrue(basket.get_bids().__contains__(0))
        self.assertTrue(self.my_store.get_bids().__contains__(0))
        self.assertNotEquals(AriExpress_Messages_count_after, AriExpress_Messages_count_before + 1,
                         "AriExpress should be notified")
        self.assertNotEquals(Amiel_Messages_count_after, Amiel_Messages_count_before + 1, "Amiel should be notified")



    def test_purchaseConfirmedBid_BidInBasketNotExists_fail(self):
        transaction_history = TransactionHistory()
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        self.assertTrue(len(list(basket.get_bids().values())) == 1)
        self.assertTrue(self.my_store.get_bids().__contains__(0))
        Amiel_Messages_count_before = MessageController().get_notifications("Amiel").__len__()
        AriExpress_Messages_count_before = MessageController().get_notifications("Feliks").__len__()
        self.assertTrue(self.my_store.get_bids_requests().__contains__("Feliks"))
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        bid: Bid = self.store_facade.approveBid("Feliks", "AriExpress", 0)
        self.assertTrue(bid.get_left_to_approval() == 0)
        self.assertTrue(bid.get_status() == 1)
        self.assertTrue(basket.get_bids().get(0).get_status() == 1)
        with self.assertRaises(Exception):
            self.store_facade.purchaseConfirmedBid(1, "AriExpress", "Amiel", "4580030389763292", "23/12", "Amiel saad",
                                                   "456", "313277949", "Shimoni", "Beer Sheva", "Israel", "1533732")
        Amiel_Messages_count_after = MessageController().get_notifications("Amiel").__len__()
        AriExpress_Messages_count_after = MessageController().get_notifications("Feliks").__len__()
        self.assertTrue(len(transaction_history.get_User_Transactions("Amiel")) == 0)
        self.assertTrue(len(transaction_history.get_Store_Transactions("AriExpress")) == 0)
        self.assertTrue(basket.get_bids().__contains__(0))
        self.assertTrue(self.my_store.get_bids().__contains__(0))
        self.assertNotEqual(AriExpress_Messages_count_after, AriExpress_Messages_count_before + 1,
                             "AriExpress should be notified")
        self.assertNotEqual(Amiel_Messages_count_after, Amiel_Messages_count_before + 1, "Amiel should be notified")

    def test_purchaseConfirmedBid_bidNotConfirmed_fail(self):
        transaction_history = TransactionHistory()
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        self.assertTrue(len(list(basket.get_bids().values())) == 1)
        self.assertTrue(self.my_store.get_bids().__contains__(0))
        Amiel_Messages_count_before = MessageController().get_notifications("Amiel").__len__()
        AriExpress_Messages_count_before = MessageController().get_notifications("Feliks").__len__()
        self.assertTrue(self.my_store.get_bids_requests().__contains__("Feliks"))
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(basket.get_bids().get(0).get_status() == 0)
        with self.assertRaises(Exception):
            self.store_facade.purchaseConfirmedBid(0, "AriExpress", "Amiel", "4580030389763292", "23/12", "Amiel saad",
                                                   "456", "313277949", "Shimoni", "Beer Sheva", "Israel", "1533732")
        Amiel_Messages_count_after = MessageController().get_notifications("Amiel").__len__()
        AriExpress_Messages_count_after = MessageController().get_notifications("Feliks").__len__()
        self.assertTrue(len(transaction_history.get_User_Transactions("Amiel")) == 0)
        self.assertTrue(len(transaction_history.get_Store_Transactions("AriExpress")) == 0)
        self.assertTrue(basket.get_bids().__contains__(0))
        self.assertTrue(self.my_store.get_bids().__contains__(0))
        self.assertNotEqual(AriExpress_Messages_count_after, AriExpress_Messages_count_before + 1,
                            "AriExpress should be notified")
        self.assertNotEqual(Amiel_Messages_count_after, Amiel_Messages_count_before + 1, "Amiel should be notified")


    # rejectBid

    def test_rejectBid_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        bid: Bid = self.store_facade.rejectBid("Feliks", "AriExpress", 0)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 2)
        self.assertTrue(basket.get_bids().get(0).get_status() == 2)

    def test_TwoPeopleRejectBid_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("YuvalMelamed", "PussyDestroyer69")
        self.store_facade.nominateStoreOwner("Feliks", "YuvalMelamed", "AriExpress")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 2)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        bid: Bid = self.store_facade.approveBid("YuvalMelamed", "AriExpress", 0)
        self.assertTrue(bid.get_left_to_approval() == 1)
        bid: Bid = self.store_facade.rejectBid("Feliks", "AriExpress", 0)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 2)
        self.assertTrue(basket.get_bids().get(0).get_status() == 2)
    def test_rejectBid_userNotLoggedIn_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.rejectBid("Feliks", "AriExpress", 0)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(basket.get_bids().get(0).get_status() == 0)
    def test_rejectBid_storeNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.rejectBid("Feliks", "some_store", 0)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(basket.get_bids().get(0).get_status() == 0)

    def test_rejectBid_storeIsClosed_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        self.store_facade.closeStore("Feliks", "AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.rejectBid("Feliks", "AriExpress", 0)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(basket.get_bids().get(0).get_status() == 0)

    def test_rejectBid_bidNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.rejectBid("Feliks", "AriExpress", 1)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(basket.get_bids().get(0).get_status() == 0)


    def test_rejectBid_bigAlreadyAccepted_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        bid: Bid = self.store_facade.approveBid("Feliks", "AriExpress", 0)
        with self.assertRaises(Exception):
            self.store_facade.rejectBid("Feliks", "AriExpress", 0)
        self.assertTrue(bid.get_left_to_approval() == 0)
        self.assertTrue(bid.get_status() == 1)
        self.assertTrue(basket.get_bids().get(0).get_status() == 1)

    def test_rejectBid_bidAlreadyRejected_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        bid: Bid = self.store_facade.rejectBid("Feliks", "AriExpress", 0)
        with self.assertRaises(Exception):
            self.store_facade.rejectBid("Feliks", "AriExpress", 0)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 2)
        self.assertTrue(basket.get_bids().get(0).get_status() == 2)

    # sendAlternativeBid

    def test_sendAlternativeBid_success(self):
        transaction_history = TransactionHistory()
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        bid: Bid = self.store_facade.sendAlternativeBid("Feliks", "AriExpress", 0, 2200)
        self.assertTrue(bid.get_status() == 3)
        self.assertTrue(bid.get_offer() == 2200)
        self.store_facade.purchaseConfirmedBid(0, "AriExpress", "Amiel", "4580030389763292", "23/12", "Amiel saad",
                                               "456", "313277949", "Shimoni", "Beer Sheva", "Israel", "1533732")
        list_amiel = transaction_history.get_User_Transactions("Amiel")
        transaction: UserTransaction = list_amiel[0]
        self.assertTrue(transaction.get_overall_price() == 2200)
    def test_sendAlternativeBid_userNotLoggedIn_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        self.store_facade.logOut("Feliks")
        with self.assertRaises(Exception):
            self.store_facade.sendAlternativeBid("Feliks", "AriExpress", 0, 2200)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(bid.get_offer() == 2000)


    def test_sendAlternativeBid_storeNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.sendAlternativeBid("Feliks", "some_store", 0, 2200)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(bid.get_offer() == 2000)

    def test_sendAlternativeBid_storeIsClosed_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        self.store_facade.closeStore("Feliks", "AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.sendAlternativeBid("Feliks", "AriExpress", 0, 2200)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(bid.get_offer() == 2000)

    def test_sendAlternativeBid_bidNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.sendAlternativeBid("Feliks", "AriExpress", 1, 2200)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(bid.get_offer() == 2000)

    def test_sendAlternativeBid_bidAlreadyAccepted_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        bid: Bid = self.store_facade.approveBid("Feliks", "AriExpress", 0)
        with self.assertRaises(Exception):
            self.store_facade.sendAlternativeBid("Feliks", "AriExpress", 0, 2200)
        self.assertTrue(bid.get_status() == 1)
        self.assertTrue(bid.get_offer() == 2000)

    def test_sendAlternativeBid_bidAlreadyRejected_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        bid: Bid = self.store_facade.rejectBid("Feliks", "AriExpress", 0)
        with self.assertRaises(Exception):
            self.store_facade.sendAlternativeBid("Feliks", "AriExpress", 0, 2200)
        self.assertTrue(bid.get_status() == 2)
        self.assertTrue(bid.get_offer() == 2000)

    def test_sendAlternativeBid_alternateBidIsLower_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        bid: Bid = self.store_facade.placeBid("Amiel", "AriExpress", 2000, 1, 4)
        self.assertTrue(bid.get_left_to_approval() == 1)
        self.assertTrue(bid.get_status() == 0)
        member: Member = self.store_facade.members.get("Amiel")
        basket: Basket = member.get_Basket("AriExpress")
        with self.assertRaises(Exception):
            self.store_facade.sendAlternativeBid("Feliks", "AriExpress", 0, 1900)
        self.assertTrue(bid.get_status() == 0)
        self.assertTrue(bid.get_offer() == 2000)

    # getAllOfflineMembers
    def test_getAllOfflineMembers_success(self):
        self.store_facade.logInAsAdmin("Ari", "password123")
        offline_members = self.store_facade.getAllOfflineMembers("Ari")
        self.assertTrue(len(offline_members) == 3)
        self.store_facade.logInAsMember("Feliks", "password456")
        offline_members = self.store_facade.getAllOfflineMembers("Ari")
        self.assertTrue(len(offline_members) == 2)
        self.store_facade.logInAsMember("Amiel", "password789")
        offline_members = self.store_facade.getAllOfflineMembers("Ari")
        self.assertTrue(len(offline_members) == 1)
        self.store_facade.logInAsMember("YuvalMelamed", "PussyDestroyer69")
        offline_members = self.store_facade.getAllOfflineMembers("Ari")
        self.assertTrue(len(offline_members) == 0)
        self.store_facade.logOut("Amiel")
        offline_members = self.store_facade.getAllOfflineMembers("Ari")
        self.assertTrue(len(offline_members) == 1)

    def test_getAllOfflineMembers_userNotLoggedIn_fail(self):
        with self.assertRaises(Exception):
            offline_members = self.store_facade.getAllOfflineMembers("Ari")

    def test_getAllOfflineMembers_userNotAdmin_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            offline_members = self.store_facade.getAllOfflineMembers("Feliks")

    # getAllOnlineMembers
    def test_getAllOnlineMembers_success(self):
        self.store_facade.logInAsAdmin("Ari", "password123")
        online_members = self.store_facade.getAllOnlineMembers("Ari")
        self.assertTrue(len(online_members) == 0)
        self.store_facade.logInAsMember("Feliks", "password456")
        online_members = self.store_facade.getAllOnlineMembers("Ari")
        self.assertTrue(len(online_members) == 1)
        self.store_facade.logInAsMember("Amiel", "password789")
        online_members = self.store_facade.getAllOnlineMembers("Ari")
        self.assertTrue(len(online_members) == 2)
        self.store_facade.logInAsMember("YuvalMelamed", "PussyDestroyer69")
        online_members = self.store_facade.getAllOnlineMembers("Ari")
        self.assertTrue(len(online_members) == 3)
        self.store_facade.logOut("YuvalMelamed")
        online_members = self.store_facade.getAllOnlineMembers("Ari")
        self.assertTrue(len(online_members) == 2)

    def test_getAllOnlineMembers_userNotLoggedIn_fail(self):
        with self.assertRaises(Exception):
            online_members = self.store_facade.getAllOnlineMembers("Ari")

    def test_getAllOnlineMembers_userNotAdmin_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            online_members = self.store_facade.getAllOnlineMembers("Feliks")

    # getBasket
    def test_getBasket_member_success(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        self.assertTrue(amiel.cart.baskets.keys().__contains__(self.my_store.get_store_name()))
        basket: Basket = self.store_facade.getBasket("Amiel", self.my_store.get_store_name())
        self.assertTrue(basket.username == amiel.get_username())
        self.assertTrue(basket.store == self.my_store)

    def test_getBasket_guest_success(self):
        self.store_facade.loginAsGuest()
        guest: Guest = self.store_facade.getUserOrMember(0)
        self.store_facade.addToBasket("0", "AriExpress", 1, 5)
        self.assertTrue(guest.cart.baskets.keys().__contains__(self.my_store.get_store_name()))
        basket: Basket = self.store_facade.getBasket("0", self.my_store.get_store_name())
        self.assertTrue(basket.username == "0")
        self.assertTrue(basket.store == self.my_store)

    def test_getBasket_userNotLoggedIn_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        self.store_facade.logOut("Amiel")
        self.assertTrue(amiel.cart.baskets.keys().__contains__(self.my_store.get_store_name()))
        with self.assertRaises(Exception):
            basket: Basket = self.store_facade.getBasket("Amiel", self.my_store.get_store_name())

    def test_getBasket_storeNotExists_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        self.assertTrue(amiel.cart.baskets.keys().__contains__(self.my_store.get_store_name()))
        with self.assertRaises(Exception):
            basket: Basket = self.store_facade.getBasket("Amiel", "some_store")

    def test_getBasket_basketNotExists_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.assertFalse(amiel.cart.baskets.keys().__contains__(self.my_store.get_store_name()))
        with self.assertRaises(Exception):
            basket: Basket = self.store_facade.getBasket("Amiel", "some_store")

    # getCart
    def test_getCart_member_success(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        cart: Cart = self.store_facade.getCart("Amiel")
        self.assertTrue(cart.username == "Amiel")

    def test_getCart_guest_success(self):
        self.store_facade.loginAsGuest()
        guest: Guest = self.store_facade.getUserOrMember(0)
        cart: Cart = self.store_facade.getCart(0)
        self.assertTrue(cart.username == "0")
        self.assertTrue(len(cart.baskets.keys()) == 0)

    def test_getCart_userNotLoggedIn_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        with self.assertRaises(Exception):
            cart: Cart = self.store_facade.getCart("Amiel")




    def test_addDiscount_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.my_store.addProduct(access, "Oreo", 10, 10, "Milk")
        discount = self.my_store.addDiscount("Feliks", "Simple", percent=10, level="Product",
                                             level_name=oreo.get_product_id())
        added_discount = self.my_store.getDiscount(1)
        self.assertTrue(discount == added_discount)

    def test_addMultipleSimpleDiscount_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.my_store.addProduct(access, "Oreo", 10, 10, "Milk")
        cariot: Product = self.my_store.addProduct(access, "Cariot", 10, 10, "Milk")
        mars: Product = self.my_store.addProduct(access, "Mars", 10, 10, "Milk")
        discount1 = self.my_store.addDiscount("Feliks", "Simple", percent=10, level="Product",
                                             level_name=oreo.get_product_id())
        discount2 = self.my_store.addDiscount("Feliks", "Simple", percent=10, level="Product",
                                             level_name=cariot.get_product_id())
        discount3 = self.my_store.addDiscount("Feliks", "Simple", percent=10, level="Product",
                                             level_name=mars.get_product_id())
        added_discount1 = self.my_store.getDiscount(1)
        added_discount2 = self.my_store.getDiscount(2)
        added_discount3 = self.my_store.getDiscount(3)
        self.assertTrue(discount1 == added_discount1)
        self.assertTrue(discount2 == added_discount2)
        self.assertTrue(discount3 == added_discount3)


    def test_calculateSimpleDiscount_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")

        self.product = self.my_store.addProduct(access, "Oreo", 10, 10, "Milk")
        self.discount = self.my_store.addDiscount("Feliks", "Simple", percent=10, level="Product",
                                               level_name=self.product.get_product_id())
        self.product_dict = {self.product.get_product_id(): 1}
        self.price_after_discount = self.my_store.getProductPriceAfterDiscount(self.product, self.product_dict, 0)
        self.assertEqual(self.price_after_discount, 9)


    def test_calculateConditionedDiscount_byCategory_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.my_store.addProduct(access, "Oreo", 10, 10, "Milk")
        cariot: Product = self.my_store.addProduct(access, "Cariot", 10, 10, "Milk")
        sub_rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(),
                    "operator": ">=", "quantity": 1, "category": "", "child": {}}
        rule = {"rule_type": "amount_of_product", "product_id": cariot.get_product_id(),
                "operator": ">=", "quantity": 1, "category": "", "child": {"logic_type": "OR", "rule": sub_rule}}
        discount = self.my_store.addDiscount("Feliks", "Conditioned", percent=10, level="Product",
                                             level_name=self.item_paper.get_product_id(), rule=rule)
        product_dict = {cariot.get_product_id(): (cariot,2), oreo.get_product_id(): (oreo,2)}
        price_after_discount_1 = self.my_store.getProductPriceAfterDiscount(self.item_paper, product_dict, 0)
        self.assertEqual(450, price_after_discount_1)

    def test_getDiscount_storeNotExists_fail(self):
        pass

    def test_getDiscount_discountNotExists_fail(self):
        pass

    # purchase policy

    def test_addPurchasePolicy_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.my_store.addProduct(access, "Oreo", 10, 10, "Milk")
        rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(), "category":"", "operator": "<=", "user_field": "",
                "quantity": 5, "child": {}}
        policy = self.store_facade.addPurchasePolicy("AriExpress","Feliks", "PurchasePolicy", rule, level="Product", level_name=oreo.get_product_id())
        added_discount = self.my_store.getPolicy(1)
        self.assertEqual(policy, added_discount)


    def test_calculatePurchasePolicy_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.my_store.addProduct(access, "Oreo", 10, 10, "Milk")
        rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(), "category":"", "operator": "<=", "user_field": "",
                "quantity": 5, "child": {}}
        policy = self.my_store.addPurchasePolicy("Feliks", "PurchasePolicy", rule, level="Product", level_name=oreo.get_product_id())
        with self.assertRaises(Exception):
            self.store_facade.addToBasket("Feliks", "AriExpress", oreo.get_product_id(), 8)


    def test_NotRelevantProductPurchasePolicy_succeed(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.my_store.addProduct(access, "Oreo", 10, 10, "Milk")
        rule = {"rule_type": "amount_of_product", "product_id": oreo.get_product_id(), "category":"", "operator": "<=", "user_field": "",
                "quantity": 5, "child": {}}
        policy = self.my_store.addPurchasePolicy("Feliks", "PurchasePolicy", rule, level="Product", level_name=oreo.get_product_id())
        self.store_facade.addToBasket("Feliks", "AriExpress", 1, 8)
        self.assertEqual(self.store_facade.getBasket("Feliks","AriExpress").products.get(self.item_paper.get_product_id())[1], 8)

    def test_DayOfTheWeekPurchasePolicy_succeed(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.my_store.addProduct(access, "Oreo", 10, 10, "Milk")
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        current_day = datetime.now().weekday()
        rule = {"rule_type": "day_of_the_week", "product_id": "", "category": "", "operator": "<=",
                "user_field": days_of_week[current_day],
                "quantity": "", "child": {}}
        policy = self.my_store.addPurchasePolicy("Feliks", "PurchasePolicy", rule, level="Product", level_name=oreo.get_product_id())
        #with self.assertRaises(Exception):
        self.store_facade.addToBasket("Feliks", "AriExpress", oreo.get_product_id(), 8)

    def test_addToBasketFromTwoStores_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.createStore("Feliks", "SomeStore")
        self.store_facade.addNewProductToStore("Feliks", "SomeStore", "Oreo", 10, 10, "Milk")
        self.store_facade.addNewProductToStore("Feliks", "AriExpress", "Cariot", 10, 10, "Korn")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "SomeStore", 1, 8)
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 8)
        basket1 = self.store_facade.getBasket("Amiel", "SomeStore").toJson()
        basket2 = self.store_facade.getBasket("Amiel", "AriExpress").toJson()
        print("wazaaap")


    def test_DayOfTheWeekPurchasePolicy_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.my_store.addProduct(access, "Oreo", 10, 10, "Milk")
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        current_day = datetime.now().weekday()
        rule = {"rule_type": "day_of_the_week", "product_id": "", "category": "", "operator": "<=",
                "user_field": 'Friday',
                "quantity": "", "child": {}}
        policy = self.my_store.addPurchasePolicy("Feliks", "PurchasePolicy", rule, level="Product", level_name=oreo.get_product_id())
        with self.assertRaises(Exception):
            self.store_facade.addToBasket("Feliks", "AriExpress", oreo.get_product_id(), 8)

    def test_OR_PurchasePolicy_succeed(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        feliks: Member = self.store_facade.members.get("Feliks")
        access: Access = feliks.accesses.get("AriExpress")
        oreo: Product = self.my_store.addProduct(access, "Oreo", 10, 10, "Milk")
        rule1 = {"rule_type": "amount_of_product", "product_id": self.item_paper.get_product_id(), "category": "", "operator": "<=", "user_field": "", "quantity": 5, "child": {}}
        rule2 = {"rule_type": "amount_of_category", "product_id": "", "category": "Milk", "operator": "<=", "user_field": "", "quantity": 5, "child": {"logic_type":"OR", "rule":rule1}}
        policy = self.my_store.addPurchasePolicy("Feliks", "PurchasePolicy", rule2, level="Product", level_name=oreo.get_product_id())
        with self.assertRaises(Exception):
            self.store_facade.addToBasket("Feliks", "AriExpress", oreo.get_product_id(), 8)


    # purchaseCart

    def test_purchaseCart_oneSuccessOneFail_notEnoughSupply(self):
        transaction_history = TransactionHistory()

        # before
        transaction_history.insertEmptyListToUser("YuvalMelamed")
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        self.assertTrue(len(transaction_history.user_transactions.get("Amiel")) == 0)
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("YuvalMelamed", "PussyDestroyer69")
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 9)
        self.store_facade.addToBasket("YuvalMelamed", "AriExpress",
                                      1, 9)
        Amiel_Messages_count_before = MessageController().get_notifications("Amiel").__len__()
        AriExpress_Messages_count_before = MessageController().get_notifications("AriExpress").__len__()
        YuvalMelamed_Messages_count_before = MessageController().get_notifications("YuvalMelamed").__len__()
        self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel saad", "555", "123456789",
                                       "some_address", "be'er sheva", "Israel", "1234567")
        # check that message was sent to Amiel and to AriExpress
        amiel_transaction_list: list = transaction_history.get_User_Transactions("Amiel")
        yuval_transaction_list: list = transaction_history.get_Store_Transactions("AriExpress")
        yuval_cart = self.store_facade.getCart("YuvalMelamed")
        with self.assertRaises(Exception):
            self.store_facade.purchaseCart("YuvalMelamed", "4580202046783956", "12/26", "Yuval Melamed", "554",
                                           "008234235",
                                           "some_address", "be'er sheva", "Israel", "1234567")
        amiel_transaction_list: list = transaction_history.get_User_Transactions("Amiel")
        yuval_transaction_list: list = transaction_history.get_User_Transactions("YuvalMelamed")
        ariExpress_transaction_list: list = transaction_history.get_Store_Transactions("AriExpress")
        # transaction did not go through!
        self.assertTrue(len(amiel_transaction_list) == 1)
        self.assertTrue(len(ariExpress_transaction_list) == 1)
        # integrity that the transaction failed for Yuval
        self.assertTrue(len(yuval_transaction_list) == 0)
        self.assertEqual(yuval_cart, self.store_facade.getCart("YuvalMelamed"))
        transaction_history.clearAllHistory()  # why?
        Amiel_Messages_count_after = MessageController().get_notifications("Amiel").__len__()
        AriExpress_Messages_count_after = MessageController().get_notifications("AriExpress").__len__()
        YuvalMelamed_Messages_count_after = MessageController().get_notifications("YuvalMelamed").__len__()
        self.assertEqual(AriExpress_Messages_count_after, AriExpress_Messages_count_before + 1,
                         "AriExpress should be notified")
        self.assertEqual(Amiel_Messages_count_after, Amiel_Messages_count_before + 1, "Amiel should be notified")
        self.assertEqual(YuvalMelamed_Messages_count_after, YuvalMelamed_Messages_count_before,
                         "YuvalMelamed shouldn't be notified")

    def test_purchaseCart_userNotLoggedIn_fail(self):
        transaction_history = TransactionHistory()
        self.store_facade.logInAsMember("Amiel", "password789")
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 3)

        self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel saad", "555", "123456789",
                                       "some_address", "be'er sheva", "Israel", "1234567")
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 3)
        self.store_facade.logOut("Amiel")
        amiel_cart = self.store_facade.getCart("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel saad", "555", "123456789",
                                           "some_address", "be'er sheva", "Israel", "1234567")
            # integrity that the transaction failed for Amiel
        amiel_transaction_list: list = transaction_history.get_User_Transactions("Amiel")
        ariExpress_transaction_list: list = transaction_history.get_Store_Transactions("AriExpress")
        # transaction did not go through!
        self.assertTrue(len(amiel_transaction_list) == 1)
        self.assertTrue(len(ariExpress_transaction_list) == 1)
        self.assertEqual(amiel_cart, self.store_facade.getCart("Amiel"))
        transaction_history.clearAllHistory()

    def test_purchaseCart_cartWithoutBaskets_fail(self):
        transaction_history = TransactionHistory()
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        self.store_facade.logInAsMember("Amiel", "password789")
        amiel_cart = self.store_facade.getCart("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel saad", "555", "123456789",
                                           "some_address", "be'er sheva", "Israel", "1234567")
            # integrity that the transaction failed for Amiel
        amiel_transaction_list: list = transaction_history.get_User_Transactions("Amiel")
        ariExpress_transaction_list: list = transaction_history.get_Store_Transactions("AriExpress")
        # transaction did not go through!
        self.assertTrue(len(amiel_transaction_list) == 0)
        self.assertTrue(len(ariExpress_transaction_list) == 0)
        self.assertEqual(amiel_cart, self.store_facade.getCart("Amiel"))
        transaction_history.clearAllHistory()

    def test_purchaseCart_cardNumberInvalid_fail(self):
        transaction_history = TransactionHistory()
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 3)
        amiel_cart = self.store_facade.getCart("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel saad", "555", "123456789",
                                           "some_address", "be'er sheva", "Israel", "1234567")
            # integrity that the transaction failed for Amiel
        amiel_transaction_list: list = transaction_history.get_User_Transactions("Amiel")
        ariExpress_transaction_list: list = transaction_history.get_Store_Transactions("AriExpress")
        # transaction did not go through!
        self.assertTrue(len(amiel_transaction_list) == 0)
        self.assertTrue(len(ariExpress_transaction_list) == 0)
        self.assertEqual(amiel_cart, self.store_facade.getCart("Amiel"))
        transaction_history.clearAllHistory()

    def test_purchaseCart_cardDateInvalid_fail(self):
        transaction_history = TransactionHistory()
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 3)
        amiel_cart = self.store_facade.getCart("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel saad", "555", "123456789",
                                           "some_address", "be'er sheva", "Israel", "1234567")
            # integrity that the transaction failed for Amiel
        amiel_transaction_list: list = transaction_history.get_User_Transactions("Amiel")
        ariExpress_transaction_list: list = transaction_history.get_Store_Transactions("AriExpress")
        # transaction did not go through!
        self.assertTrue(len(amiel_transaction_list) == 0)
        self.assertTrue(len(ariExpress_transaction_list) == 0)
        self.assertEqual(amiel_cart, self.store_facade.getCart("Amiel"))
        transaction_history.clearAllHistory()

    def test_purchaseCart_cardCcvInvalid_fail(self):
        transaction_history = TransactionHistory()
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 3)
        amiel_cart = self.store_facade.getCart("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel saad", "555", "123456789",
                                           "some_address", "be'er sheva", "Israel", "1234567")
            # integrity that the transaction failed for Amiel
        amiel_transaction_list: list = transaction_history.get_User_Transactions("Amiel")
        ariExpress_transaction_list: list = transaction_history.get_Store_Transactions("AriExpress")
        # transaction did not go through!
        self.assertTrue(len(amiel_transaction_list) == 0)
        self.assertTrue(len(ariExpress_transaction_list) == 0)
        self.assertEqual(amiel_cart, self.store_facade.getCart("Amiel"))
        transaction_history.clearAllHistory()

    def test_purchaseCart_productInBasketOutOfStock_fail(self):
        self.store_facade.loginAsGuest()
        transaction_history = TransactionHistory()
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("YuvalMelamed", "PussyDestroyer69")
        # guest adding to his cart and purchasing
        self.store_facade.addToBasket("YuvalMelamed", "AriExpress",
                                      1, 10)
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 2)
        self.store_facade.purchaseCart("YuvalMelamed", "4580202046783956", "12/26", "Yuval Melamed", "554", "008234235",
                                       "some_address", "be'er sheva", "Israel", "1234567")
        # there isn't enough in stock
        amiel_cart = self.store_facade.getCart("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel saad", "555", "123456789",
                                           "some_address", "be'er sheva", "Israel", "1234567")
            # integrity that the transaction failed for Amiel
        amiel_transaction_list: list = transaction_history.get_User_Transactions("Amiel")
        ariExpress_transaction_list: list = transaction_history.get_Store_Transactions("AriExpress")
        # transaction did not go through!
        self.assertTrue(len(amiel_transaction_list) == 0)
        # the guest bought so there is a transaction in the store
        self.assertTrue(len(ariExpress_transaction_list) == 1)
        self.assertEqual(amiel_cart, self.store_facade.getCart("Amiel"))
        transaction_history.clearAllHistory()

    # getMemberPurchaseHistory
    def test_getMemberPurchaseHistory_member_success(self):
        transaction_history = TransactionHistory()
        transaction_history.insertEmptyListToUser("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        amiel_list: list = self.store_facade.getMemberPurchaseHistory("Amiel", "Amiel")
        # no transactions yet!
        self.assertTrue(len(amiel_list) == 0)
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 2)
        self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel saad", "555", "123456789",
                                       "some_address", "be'er sheva", "Israel", "1234567")
        # the list should be updated to 1 there is a transaction!
        self.assertTrue(len(amiel_list) == 1)

    def test_getMemberPurchaseHistory_calledByAdmin_success(self):
        transaction_history = TransactionHistory()
        transaction_history.insertEmptyListToUser("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsAdmin("Ari", "password123")
        amiel_list: list = self.store_facade.getMemberPurchaseHistory("Ari", "Amiel")
        # no transactions yet!
        self.assertTrue(len(amiel_list) == 0)
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 2)
        self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel saad", "555", "123456789",
                                       "some_address", "be'er sheva", "Israel", "1234567")
        # the list should be updated to 1 there is a transaction!
        self.assertTrue(len(amiel_list) == 1)

    def test_getMemberPurchaseHistory_userNotLoggedIn_fail(self):
        transaction_history = TransactionHistory()
        transaction_history.insertEmptyListToUser("Amiel")
        with self.assertRaises(Exception):
            amiel_list: list = self.store_facade.getMemberPurchaseHistory("Amiel", "Amiel")

    def test_getMemberPurchaseHistory_userNotMember_fail(self):
        transaction_history = TransactionHistory()
        with self.assertRaises(Exception):
            amiel_list: list = self.store_facade.getMemberPurchaseHistory("some_guy", "some_guy")

    # getPermissions
    # TODO: ask amiel
    def test_getPermissions_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.nominateStoreManager("Feliks", "Amiel", "AriExpress")
        permissions = self.store_facade.getPermissions("AriExpress", "Feliks", "Amiel")

    def test_getPermissions_userNotLoggedIn_fail(self):
        pass

    def test_getPermissions_storeNotExists_fail(self):
        pass

    def test_getPermissions_storeIsClosed_fail(self):
        pass

    def test_getPermissions_userNotOwner_fail(self):
        pass

    def test_getPermissions_nominatedNotExists_fail(self):
        pass

    def test_getPermissions_nominatedHasNoPermissions_fail(self):
        # TODO: change to success?
        pass

    # getProduct
    def test_getProduct_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 5, 1, "cookies")
        product: Product = self.store_facade.getProduct("AriExpress", 1, "Feliks")
        self.assertTrue(product == self.item_paper)
        product2: Product = self.store_facade.getProduct("AriExpress", 2, "Feliks")
        self.assertTrue(product2 == oreo)

    def test_getProduct_storeNotExists_fail(self):
        with self.assertRaises(Exception):
            product: Product = self.store_facade.getProduct("some_store", 1)

    def test_getProduct_productNotExists_fail(self):
        with self.assertRaises(Exception):
            product: Product = self.store_facade.getProduct("AriExpress", 3)

    def test_getProduct_storeIsClosed_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        product: Product = self.store_facade.getProduct("AriExpress", 1, "Feliks")
        self.assertTrue(product == self.item_paper)
        self.store_facade.closeStore("Feliks", "AriExpress")
        with self.assertRaises(Exception):
            product: Product = self.store_facade.getProduct("AriExpress", 1, "Amiel")

    # getProductsByStore
    def test_getProductsByStore_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        products_dict = self.store_facade.getProductsByStore("AriExpress", "Feliks")
        self.assertTrue(len(products_dict.keys()) == 1)
        product: Product = list(products_dict.values())[0]
        self.assertTrue(product == self.item_paper)
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 1, "cookies")
        self.assertTrue(len(products_dict.keys()) == 2)
        product: Product = list(products_dict.values())[1]
        self.assertTrue(product == oreo)

    def test_getProductsByStore_storeNotExists_fail(self):
        with self.assertRaises(Exception):
            products_dict = self.store_facade.getProductsByStore("some_store", "Feliks")

    def test_getProductsByStore_storeIsClosed_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.closeStore("Feliks", "AriExpress")
        with self.assertRaises(Exception):
            products_dict = self.store_facade.getProductsByStore("some_store")




    def test_getPurchasePolicy_userNotLoggedIn_fail(self):
        pass

    def test_getPurchasePolicy_storeNotExists_fail(self):
        pass

    def test_getPurchasePolicy_policyNotExists_fail(self):
        pass

    def test_getPurchasePolicy_storeIsClosed_fail(self):
        pass

    # getStaffInfo
    # gets all the staff accesses
    def test_getStaffInfo_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        accesses = self.store_facade.getStaffInfo("Feliks", "AriExpress")
        self.assertTrue(len(list(accesses.keys())) == 1)
        access: Access = accesses.get("Feliks")
        self.assertTrue(access.hasRole("Founder"))
        self.store_facade.nominateStoreOwner("Feliks", "Amiel", "AriExpress")
        self.assertTrue(len(list(accesses.keys())) == 2)
        access: Access = accesses.get("Amiel")
        self.assertTrue(access.hasRole("Owner"))
        self.store_facade.nominateStoreManager("Feliks", "YuvalMelamed", "AriExpress")
        self.assertTrue(len(list(accesses.keys())) == 3)
        access: Access = accesses.get("YuvalMelamed")
        self.assertTrue(access.hasRole("Manager"))

    def test_getStaffInfo_userNotLoggedIn_fail(self):
        with self.assertRaises(Exception):
            # Feliks is not logged in
            accesses = self.store_facade.getStaffInfo("Feliks", "AriExpress")

    def test_getStaffInfo_storeNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            # store does not exist
            accesses = self.store_facade.getStaffInfo("Feliks", "some_store")

    def test_getStaffInfo_storeIsClosed_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.closeStore("Feliks", "AriExpress")
        with self.assertRaises(Exception):
            # store is closed
            accesses = self.store_facade.getStaffInfo("Feliks", "some_store")

    # getStorePurchaseHistory
    def test_getStorePurchaseHistory_success(self):
        transaction_history = TransactionHistory()
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")

        self.store_facade.logInAsMember("Feliks", "password456")
        transaction_history_of_ariexpress = self.store_facade.getStorePurchaseHistory("Feliks", "AriExpress")
        self.assertTrue(len(transaction_history_of_ariexpress) == 0)
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("YuvalMelamed", "PussyDestroyer69")
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 9)
        self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26","Amiel Saad", "555", "123456789",
                                       "some_address", "be'er sheva", "Israel", "1234567")
        transaction_history_of_ariexpress = self.store_facade.getStorePurchaseHistory("Feliks", "AriExpress")
        # integrity
        self.assertTrue(len(transaction_history_of_ariexpress) == 1)
        transaction: StoreTransaction = transaction_history_of_ariexpress[0]
        self.assertTrue(transaction.get_overall_price() == 4500)
        transaction_history.clearAllHistory()

    def test_getUserPurchaseHistory_success(self):
        transaction_history = TransactionHistory()
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("Feliks", "password456")
        transaction_history_of_amiel = self.store_facade.getMemberPurchaseHistory("Amiel", "Amiel")
        self.assertTrue(len(transaction_history_of_amiel) == 0)
        self.store_facade.logInAsMember("YuvalMelamed", "PussyDestroyer69")
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 9)
        self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel Saad", "555", "123456789",
                                       "some_address", "be'er sheva", "Israel", "1234567")
        transaction_history_of_amiel = self.store_facade.getMemberPurchaseHistory("Amiel", "Amiel")
        # integrity
        self.assertTrue(len(transaction_history_of_amiel) == 1)
        transaction: StoreTransaction = transaction_history_of_amiel[0]
        self.assertTrue(transaction.get_overall_price() == 4500)
        transaction_history.clearAllHistory()


    def test_getStorePurchaseHistory_Admin_success(self):
        transaction_history = TransactionHistory()
        transaction_history.insertEmptyListToUser("Amiel")
        transaction_history.insertEmptyListToStore("AriExpress")
        # Ari is an Admin!
        self.store_facade.logInAsMember("Ari", "password123")
        transaction_history_of_ariexpress = self.store_facade.getStorePurchaseHistory("Ari", "AriExpress")
        self.assertTrue(len(transaction_history_of_ariexpress) == 0)
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("YuvalMelamed", "PussyDestroyer69")
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 9)
        self.store_facade.purchaseCart("Amiel", "4580020345672134", "12/26", "Amiel saad", "555", "123456789",
                                       "some_address", "be'er sheva", "Israel", "1234567")
        transaction_history_of_ariexpress = self.store_facade.getStorePurchaseHistory("Ari", "AriExpress")
        self.assertTrue(len(transaction_history_of_ariexpress) == 1)
        transaction: StoreTransaction = transaction_history_of_ariexpress[0]
        self.assertTrue(transaction.get_overall_price() == 4500)
        transaction_history.clearAllHistory()

    def test_getStorePurchaseHistory_userNotLoggedIn_fail(self):
        transaction_history = TransactionHistory()
        transaction_history.insertEmptyListToStore("AriExpress")
        self.store_facade.logInAsMember("Feliks", "password456")
        transaction_history_of_ariexpress = self.store_facade.getStorePurchaseHistory("Feliks", "AriExpress")
        self.assertTrue(len(transaction_history_of_ariexpress) == 0)
        self.store_facade.logOut("Feliks")
        with self.assertRaises(Exception):
            transaction_history_of_ariexpress = self.store_facade.getStorePurchaseHistory("Feliks", "AriExpress")
        transaction_history.clearAllHistory()

    def test_getStorePurchaseHistory_storeNotExists_fail(self):
        transaction_history = TransactionHistory()
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            transaction_history_of_ariexpress = self.store_facade.getStorePurchaseHistory("Feliks", "some_store")
        transaction_history.clearAllHistory()

    # getStores
    def test_getStores_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        stores = self.store_facade.getStores()
        self.assertTrue(len(stores.keys()) == 1)
        # integrity
        self.store_facade.createStore("Feliks", "some_store")
        self.assertTrue(len(stores.keys()) == 2)
        self.assertTrue(stores.keys().__contains__("AriExpress") and stores.keys().__contains__("some_store"))

    # logInAsAdmin
    def test_logInAsAdmin_success(self):
        ari: Admin = self.store_facade.admins.get("Ari")
        self.store_facade.logInAsMember("Ari", "password123")
        self.assertTrue(self.store_facade.admins.get("Ari").get_logged())

    def test_logInAsAdmin_userNotExists_fail(self):
        ari: Admin = self.store_facade.admins.get("Ari")
        with self.assertRaises(Exception):
            self.store_facade.logInAsMember("some_user", "password123")
        # integrity
        self.assertFalse(ari.get_logged())

    def test_logInAsAdmin_userNotAdmin_fail(self):
        ari: Admin = self.store_facade.admins.get("Ari")
        with self.assertRaises(Exception):
            self.store_facade.logInAsAdmin("Feliks", "password456")
        # integrity
        self.assertFalse(ari.get_logged())

    def test_logInAsAdmin_wrongPassword_fail(self):
        ari: Admin = self.store_facade.admins.get("Ari")
        with self.assertRaises(Exception):
            self.store_facade.logInAsMember("Ari", "password12")
        # integrity
        self.assertFalse(ari.get_logged())

    def test_logInAsAdmin_adminAlreadyLoggedIn_fail(self):
        ari: Admin = self.store_facade.admins.get("Ari")
        self.store_facade.logInAsMember("Ari", "password123")
        with self.assertRaises(Exception):
            self.store_facade.logInAsMember("Ari", "password123")
        # integrity
        self.assertTrue(self.store_facade.admins.get("Ari").get_logged())

    # loginAsGuest
    def test_loginAsGuest_success(self):
        guest_dict = self.store_facade.onlineGuests
        self.store_facade.loginAsGuest()
        # integrity
        self.assertTrue(len(list(guest_dict.keys())) == 1)

    # logInAsMember
    def test_logInAsMember_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.assertTrue(self.store_facade.online_members.__contains__("Feliks"))
        # integrity
        self.assertFalse(self.store_facade.online_members.__contains__("Amiel"))

    def test_logInAsMember_userNotExists_fail(self):
        with self.assertRaises(Exception):
            self.store_facade.logInAsMember("some_guy", "password456")
        # integrity
        self.assertFalse(self.store_facade.online_members.__contains__("Feliks"))

    def test_logInAsMember_wrongPassword_fail(self):
        with self.assertRaises(Exception):
            self.store_facade.logInAsMember("Feliks", "passord456")
            # integrity
        self.assertFalse(self.store_facade.online_members.__contains__("Feliks"))

    def test_logInAsMember_memberAlreadyLoggedIn_fail(self):
        with self.assertRaises(Exception):
            self.store_facade.logInAsMember("Feliks", "some_password")
            # integrity
        self.assertFalse(self.store_facade.online_members.__contains__("Feliks"))

    # logInFromGuestToMember
    def test_logInFromGuestToMember_success(self):
        self.store_facade.loginAsGuest()
        # from guest to memeber
        self.store_facade.logInFromGuestToMember(0, "Feliks", "password456")
        # integrity
        self.assertTrue(self.store_facade.online_members.__contains__("Feliks"))
        self.assertFalse(self.store_facade.onlineGuests.__contains__("0"))

    def test_logInFromGuestToMember_userNotExists_fail(self):
        self.store_facade.loginAsGuest()
        # from guest to memeber
        with self.assertRaises(Exception):
            self.store_facade.logInFromGuestToMember(0, "some_guy", "password456")
        # integrity
        self.assertTrue(self.store_facade.onlineGuests.__contains__("0"))

    def test_logInFromGuestToMember_wrongPassword_fail(self):
        self.store_facade.loginAsGuest()
        # from guest to memeber
        with self.assertRaises(Exception):
            self.store_facade.logInFromGuestToMember(0, "Feliks", "password45")
        # integrity
        self.assertTrue(self.store_facade.onlineGuests.__contains__("0"))

    def test_logInFromGuestToMember_memberAlreadyLoggedIn_fail(self):
        self.store_facade.loginAsGuest()
        self.store_facade.logInFromGuestToMember(0, "Feliks", "password456")
        # from guest to memeber
        with self.assertRaises(Exception):
            self.store_facade.logInFromGuestToMember(0, "Feliks", "password456")
        # integrity
        self.assertTrue(self.store_facade.online_members.__contains__("Feliks"))
        self.assertFalse(self.store_facade.onlineGuests.__contains__("0"))

    def test_logInFromGuestToMember_notLoggedAsGuest_fail(self):
        # from guest to memeber
        with self.assertRaises(Exception):
            self.store_facade.logInFromGuestToMember(0, "Feliks", "password456")
        # integrity
        self.assertFalse(self.store_facade.online_members.keys().__contains__("Feliks"))
        self.assertFalse(self.store_facade.onlineGuests.keys().__contains__("0"))

    def test_logInFromGuestToMember_checkIfCartIsSaved_success(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress",
                                      1, 9)
        # returning to guest
        self.store_facade.logOut("Amiel")
        # logging back in
        self.store_facade.logInFromGuestToMember(0, "Amiel", "password789")
        # integrity
        cart: Cart = self.store_facade.getCart("Amiel")
        self.assertTrue(cart.baskets.keys().__contains__("AriExpress"))
        basket: Basket = cart.baskets.get("AriExpress")
        self.assertTrue(basket.products.keys().__contains__(1))

    # logOut
    def test_logOut_success(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        self.assertTrue(self.store_facade.online_members.keys().__contains__("Amiel"))
        self.store_facade.logOut("Amiel")
        self.assertFalse(self.store_facade.online_members.keys().__contains__("Amiel"))
        # integrity
        # back to guest
        self.assertTrue(self.store_facade.onlineGuests.keys().__contains__("0"))

    def test_logOut_userNotLoggedIn_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        self.assertTrue(self.store_facade.online_members.keys().__contains__("Amiel"))
        self.store_facade.logOut("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.logOut("Amiel")
        self.assertFalse(self.store_facade.online_members.keys().__contains__("Amiel"))
        # integrity
        # back to guest
        self.assertTrue(self.store_facade.onlineGuests.keys().__contains__("0"))

    # logOutAsAdmin
    def test_logOutAsAdmin_success(self):
        ari: Admin = self.store_facade.admins.get("Ari")
        self.store_facade.logInAsMember("Ari", "password123")
        self.assertTrue(self.store_facade.admins.get("Ari").get_logged())
        self.store_facade.logOutAsAdmin("Ari")
        self.assertFalse(self.store_facade.admins.get("Ari").get_logged())

    def test_logOutAsAdmin_userNotLoggedIn_fail(self):
        ari: Admin = self.store_facade.admins.get("Ari")
        self.store_facade.logInAsMember("Ari", "password123")
        self.assertTrue(self.store_facade.admins.get("Ari").get_logged())
        self.store_facade.logOutAsAdmin("Ari")
        with self.assertRaises(Exception):
            self.store_facade.logOutAsAdmin("Ari")
        self.assertFalse(self.store_facade.admins.get("Ari").get_logged())

    # openStore
    def test_openStore_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.assertTrue(self.my_store.active)
        Feliks_Messages_count_before = MessageController().get_notifications("Feliks").__len__()
        self.store_facade.closeStore("Feliks", "AriExpress")
        Feliks_Messages_count_after = MessageController().get_notifications("Feliks").__len__()
        self.assertEqual(Feliks_Messages_count_after, Feliks_Messages_count_before + 1, "Feliks should be notified")
        self.my_store = self.store_facade.stores.get("AriExpress")
        self.assertFalse(self.my_store.active)
        self.store_facade.openStore("Feliks", "AriExpress")
        self.my_store = self.store_facade.stores.get("AriExpress")
        # integrity
        self.assertTrue(self.my_store.active)

    def test_openStore_userNotLoggedIn_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.assertTrue(self.my_store.active)
        self.store_facade.closeStore("Feliks", "AriExpress")
        self.my_store = self.store_facade.stores.get("AriExpress")
        self.assertFalse(self.my_store.active)
        Feliks_Messages_count_before = MessageController().get_notifications("Feliks").__len__()
        self.store_facade.logOut("Feliks")
        with self.assertRaises(Exception):
            self.store_facade.openStore("Feliks", "AriExpress")
        # integrity
        self.my_store = self.store_facade.stores.get("AriExpress")
        self.assertFalse(self.my_store.active)
        Feliks_Messages_count_after = MessageController().get_notifications("Feliks").__len__()
        self.assertEqual(Feliks_Messages_count_before, Feliks_Messages_count_after, "Feliks shouldn't be notified")

    def test_openStore_storeNameIsEmpty_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.assertTrue(self.my_store.active)
        self.store_facade.closeStore("Feliks", "AriExpress")
        self.my_store = self.store_facade.stores.get("AriExpress")
        self.assertFalse(self.my_store.active)
        with self.assertRaises(Exception):
            self.store_facade.openStore("Feliks", "")
        # integrity
        self.my_store = self.store_facade.stores.get("AriExpress")
        self.assertFalse(self.my_store.active)

    # participateInLottery


    def test_participateInLottery_success(self):
        pass

    def test_participateInLottery_userNotLoggedIn_fail(self):
        pass

    def test_participateInLottery_storeNotExists_fail(self):
        pass

    def test_participateInLottery_storeIsClosed_fail(self):
        pass

    def test_participateInLottery_userAlreadyParticipated_fail(self):
        pass

    def test_participateInLottery_lotteryNotExists_fail(self):
        pass

    def test_participateInLottery_lotteryIsClosed_fail(self):
        pass

    # placeOfferInAuction
    def test_placeOfferInAuction_success(self):
        pass

    def test_placeOfferInAuction_guestLoggedIn_fail(self):
        # TODO: should it be success? can guest do it?
        pass

    def test_placeOfferInAuction_userNotLoggedIn_fail(self):
        pass

    def test_placeOfferInAuction_storeNotExists_fail(self):
        pass

    def test_placeOfferInAuction_storeIsClosed_fail(self):
        pass

    def test_placeOfferInAuction_auctionNotExists_fail(self):
        pass

    def test_placeOfferInAuction_auctionIsClosed_fail(self):
        pass

    def test_placeOfferInAuction_offerTooLow_fail(self):
        pass

    # productFilterByFeatures

    # TODO: amiel did not implement it yet
    def test_productFilterByFeatures_success(self):
        pass

    def test_productFilterByFeatures_userNotLoggedIn_fail(self):
        # TODO: should it be success?
        pass

    def test_productFilterByFeatures_featureNotExists_fail(self):
        pass

    def test_productFilterByFeatures_featureIsEmpty_fail(self):
        pass

    # productSearchByCategory
    def test_productSearchByCategory_sameStore_success(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("Feliks", "password456")
        oreo = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 500, 5, "cookies")
        kit_kat = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "lit-kat", 500, 5, "cookies")
        self.store_facade.addNewProductToStore("Feliks", "AriExpress", "towel", 500, 5, "shower-items")
        products = self.store_facade.productSearchByCategory("cookies")
        products_list: list = products.get("AriExpress")
        self.assertTrue(products_list.__contains__(oreo))
        self.assertTrue(products_list.__contains__(kit_kat))
        self.assertTrue(len(products_list) == 2)

    def test_productSearchByCategory_diffrentStore_success(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.createStore("Feliks", "AriNotExpress")
        oreo = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 500, 5, "cookies")
        kit_kat = self.store_facade.addNewProductToStore("Feliks", "AriNotExpress", "lit-kat", 500, 5, "cookies")
        self.store_facade.addNewProductToStore("Feliks", "AriExpress", "towel", 500, 5, "shower-items")
        products = self.store_facade.productSearchByCategory("cookies")
        products_list: list = products.get("AriExpress")
        products_list2: list = products.get("AriNotExpress")
        self.assertTrue(products_list.__contains__(oreo))
        self.assertTrue(products_list2.__contains__(kit_kat))
        self.assertTrue(len(products_list) == 1)
        self.assertTrue(len(products_list) == 1)

    def test_productSearchByCategory_categoryNotExists_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.createStore("Feliks", "AriNotExpress")
        oreo = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 500, 5, "cookies")
        kit_kat = self.store_facade.addNewProductToStore("Feliks", "AriNotExpress", "lit-kat", 500, 5, "cookies")
        self.store_facade.addNewProductToStore("Feliks", "AriExpress", "towel", 500, 5, "shower-items")
        products = self.store_facade.productSearchByCategory("milkshake")
        # the category doesn't exists, empty result
        self.assertTrue(len(list(products.keys())) == 0)

    def test_productSearchByCategory_categoryIsEmpty_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.createStore("Feliks", "AriNotExpress")
        oreo = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 500, 5, "cookies")
        kit_kat = self.store_facade.addNewProductToStore("Feliks", "AriNotExpress", "lit-kat", 500, 5, "cookies")
        self.store_facade.addNewProductToStore("Feliks", "AriExpress", "towel", 500, 5, "shower-items")
        with self.assertRaises(Exception):
            products = self.store_facade.productSearchByCategory("")
        # the category doesn't exist, empty result

    # productSearchByName
    def test_productSearchByName_sameStore_success(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("Feliks", "password456")
        oreo = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 500, 5, "cookies")
        oreo2 = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 500, 5, "cookies")
        self.store_facade.addNewProductToStore("Feliks", "AriExpress", "towel", 500, 5, "shower-items")
        products = self.store_facade.productSearchByName("oreo")
        products_list: list = products.get("AriExpress")

        self.assertTrue(len(products_list) == 2)

    def test_productSearchByName_NameNotExists_fail(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.createStore("Feliks", "AriNotExpress")
        oreo = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 500, 5, "cookies")
        kit_kat = self.store_facade.addNewProductToStore("Feliks", "AriNotExpress", "lit-kat", 500, 5, "cookies")
        self.store_facade.addNewProductToStore("Feliks", "AriExpress", "towel", 500, 5, "shower-items")
        products = self.store_facade.productSearchByName("milkshake")
        # the category doesn't exists, empty result
        self.assertTrue(len(list(products.keys())) == 0)

    # purchaseCart
    # Tests with 'invalid' means bad info/empty info/missing info
    # so each test can hold several smaller tests

    # register
    def test_register_success(self):
        self.assertFalse(list(self.store_facade.members.keys()).__contains__("Yoav"))
        member: Member = self.store_facade.register("Yoav", "password123", "yoav@gmail.com")
        self.assertTrue(list(self.store_facade.members.keys()).__contains__("Yoav"))
        self.assertTrue(list(self.store_facade.members.values()).__contains__(member))

    def test_register_usernameAlreadyExists_fail(self):
        self.assertTrue(list(self.store_facade.members.keys()).__contains__("Feliks"))
        with self.assertRaises(Exception):
            member: Member = self.store_facade.register("Feliks", "password123", "yoav@gmail.com")

        self.assertTrue(list(self.store_facade.members.keys()).__contains__("Feliks"))
        member: Member = self.store_facade.members.get("Feliks")
        self.assertTrue(list(self.store_facade.members.values()).__contains__(member))
        self.assertFalse(member.password == "password123")

    def test_register_usernameIsEmpty_fail(self):
        with self.assertRaises(Exception):
            member: Member = self.store_facade.register("", "password123", "yoav@gmail.com")
        self.assertFalse(list(self.store_facade.members.keys()).__contains__(""))

    def test_register_passwordIsEmpty_fail(self):
        with self.assertRaises(Exception):
            member: Member = self.store_facade.register("yoav", "", "yoav@gmail.com")
        self.assertFalse(list(self.store_facade.members.keys()).__contains__(""))

    def test_register_emailIsEmpty_fail(self):
        pass

    def test_register_userAlreadyLoggedIn_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        self.assertTrue(list(self.store_facade.online_members.keys()).__contains__("Feliks"))
        with self.assertRaises(Exception):
            member: Member = self.store_facade.register("Feliks", "password123", "yoav@gmail.com")

        self.assertTrue(list(self.store_facade.members.keys()).__contains__("Feliks"))
        member: Member = self.store_facade.members.get("Feliks")
        self.assertTrue(list(self.store_facade.members.values()).__contains__(member))
        self.assertFalse(member.password == "password123")

    # removeAccess
    def test_removeAccess_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        amiel: Member = self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.nominateStoreManager("Feliks", "Amiel", "AriExpress")
        self.assertTrue(amiel.accesses.keys().__contains__("AriExpress"))
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Amiel"))
        Amiel_Notification_count_before = MessageController().get_notifications("Amiel").__len__()
        self.store_facade.removeAccess("Feliks", "Amiel", "AriExpress")
        # integrity
        self.assertFalse(amiel.accesses.keys().__contains__("AriExpress"))
        self.assertFalse(self.my_store.get_accesses().keys().__contains__("Amiel"))
        Amiel_Notification_count_after = MessageController().get_notifications("Amiel").__len__()
        self.assertEqual(Amiel_Notification_count_before + 1, Amiel_Notification_count_after,
                         "Amiel should get be notified")

    def test_removeAccess_userNotLoggedIn_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        amiel: Member = self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.nominateStoreManager("Feliks", "Amiel", "AriExpress")
        self.store_facade.logOut("Feliks")
        self.assertTrue(amiel.accesses.keys().__contains__("AriExpress"))
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Amiel"))
        with self.assertRaises(Exception):
            self.store_facade.removeAccess("Feliks", "Amiel", "AriExpress")
        # integrity
        self.assertTrue(amiel.accesses.keys().__contains__("AriExpress"))
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Amiel"))

    def test_removeAccess_storeNotExists_fail(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        amiel: Member = self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.nominateStoreManager("Feliks", "Amiel", "AriExpress")
        self.assertTrue(amiel.accesses.keys().__contains__("AriExpress"))
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Amiel"))
        with self.assertRaises(Exception):
            self.store_facade.removeAccess("Feliks", "Amiel", "somestore")
        # integrity
        self.assertTrue(amiel.accesses.keys().__contains__("AriExpress"))
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Amiel"))

    def test_removeAccess_storeIsClosed_Success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        amiel: Member = self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.nominateStoreManager("Feliks", "Amiel", "AriExpress")
        self.my_store.active = False
        self.assertTrue(amiel.accesses.keys().__contains__("AriExpress"))
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Amiel"))
        # with self.assertRaises(Exception):
        self.store_facade.removeAccess("Feliks", "Amiel", "AriExpress")
        # integrity
        self.assertFalse(amiel.accesses.keys().__contains__("AriExpress"))
        self.assertFalse(self.my_store.get_accesses().keys().__contains__("Amiel"))

    def test_removeAccess_requesterIsRequstee_fail(self):
        feliks: Member = self.store_facade.logInAsMember("Feliks", "password456")
        self.assertTrue(feliks.accesses.keys().__contains__("AriExpress"))
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Feliks"))
        with self.assertRaises(Exception):
            self.store_facade.removeAccess("Feliks", "Feliks", "AriExpress")
        # integrity
        self.assertTrue(feliks.accesses.keys().__contains__("AriExpress"))
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Feliks"))

    def test_removeAccess_requesterHasNoPermissions_fail(self):
        feliks: Member = self.store_facade.logInAsMember("Feliks", "password456")
        amiel: Member = self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.nominateStoreManager("Feliks", "Amiel", "AriExpress")
        self.assertTrue(feliks.accesses.keys().__contains__("AriExpress"))
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Feliks"))
        # with self.assertRaises(Exception):
        with self.assertRaises(Exception):
            self.store_facade.removeAccess("Amiel", "Feliks", "AriExpress")
        # integrity
        self.assertTrue(feliks.accesses.keys().__contains__("AriExpress"))
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Feliks"))

    def test_removeAccess_requesteeHasNoAccess_fail(self):
        feliks: Member = self.store_facade.logInAsMember("Feliks", "password456")
        amiel: Member = self.store_facade.logInAsMember("Amiel", "password789")
        self.assertTrue(feliks.accesses.keys().__contains__("AriExpress"))
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Feliks"))
        # with self.assertRaises(Exception):
        with self.assertRaises(Exception):
            self.store_facade.removeAccess("Amiel", "Feliks", "AriExpress")
        # integrity
        self.assertTrue(feliks.accesses.keys().__contains__("AriExpress"))
        self.assertTrue(self.my_store.get_accesses().keys().__contains__("Feliks"))

    # removeFromBasket
    def test_removeFromBasket_success(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("Feliks", "password456")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 1, "cookies")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        self.store_facade.addToBasket("Amiel", "AriExpress", 2, 5)
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        self.assertTrue(basket.products.keys().__contains__(1))
        self.store_facade.removeFromBasket("Amiel", "AriExpress", 1)
        self.assertFalse(basket.products.keys().__contains__(1))
        self.assertTrue(basket.products.keys().__contains__(2))
        self.store_facade.removeFromBasket("Amiel", "AriExpress", 2)
        self.assertFalse(basket.products.keys().__contains__(2))
        self.assertFalse(amiel.cart.baskets.__contains__("AriExpress"))

    def test_removeFromBasket_userNotLoggedIn_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        self.assertTrue(basket.products.keys().__contains__(1))
        self.store_facade.logOut("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.removeFromBasket("Amiel", "AriExpress", 1)
        # integrity :
        self.assertTrue(basket.products.keys().__contains__(1))

    def test_removeFromBasket_basketNotExists_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.assertFalse(amiel.cart.baskets.keys().__contains__("AriExpress"))
        with self.assertRaises(Exception):
            self.store_facade.removeFromBasket("Amiel", "AriExpress", 1)
        # integrity :
        self.assertFalse(amiel.cart.baskets.keys().__contains__("AriExpress"))

    def test_removeFromBasket_productNotExists_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        self.assertTrue(basket.products.keys().__contains__(1))
        self.store_facade.logOut("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.removeFromBasket("Amiel", "AriExpress", 2)
        # integrity :
        self.assertTrue(basket.products.keys().__contains__(1))

    def test_removeFromBasket_productNotInBasket_fail(self):
        amiel: Member = self.store_facade.members.get("Amiel")
        self.store_facade.logInAsMember("Feliks", "password456")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks", "AriExpress", "oreo", 10, 1, "cookies")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.addToBasket("Amiel", "AriExpress", 1, 5)
        basket: Basket = amiel.cart.baskets.get("AriExpress")
        self.assertTrue(basket.products.keys().__contains__(1))
        self.store_facade.logOut("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.removeFromBasket("Amiel", "AriExpress", 2)
        # integrity :
        self.assertTrue(basket.products.keys().__contains__(1))

    # todo: ask amiel
    # removePermissions
    def test_removePermissions_success(self):
        pass

    def test_removePermissions_userNotLoggedIn_fail(self):
        pass

    def test_removePermissions_storeNotExists_fail(self):
        pass

    def test_removePermissions_storeIsClosed_fail(self):
        pass

    def test_removePermissions_requesterHasNoPermissions_fail(self):
        pass

    def test_removePermissions_requesteeHasNoAccess_fail(self):
        pass

    def test_removePermissions_permissionsInvalid_fail(self):
        pass

    # removeProductFromStore
    def test_removeProductFromStore_success(self):
        self.store_facade.logInAsMember("Feliks", "password456")
        # item with id 1
        prods = self.my_store.getProducts("Feliks")
        oreo: Product = self.store_facade.addNewProductToStore("Feliks","AriExpress", "Oreo", 10, 10, "Milk")
        self.assertTrue(prods.keys().__contains__(1))
        self.store_facade.removeProductFromStore("Feliks", "AriExpress", 1)
        self.assertFalse(prods.keys().__contains__(1))

    def test_removeProductFromStore_userNotLoggedIn_fail(self):
        # item with id 1
        self.store_facade.logInAsMember("Feliks", "password456")
        prods = self.my_store.getProducts("Feliks")
        self.assertTrue(prods.keys().__contains__(1))
        self.store_facade.logOut("Feliks")
        with self.assertRaises(Exception):
            self.store_facade.removeProductFromStore("Feliks", "AriExpress", 1)
        self.assertTrue(prods.keys().__contains__(1))

    def test_removeProductFromStore_storeNotExists_fail(self):
        # item with id 1
        self.store_facade.logInAsMember("Feliks", "password456")
        prods = self.my_store.getProducts("Feliks")
        self.assertTrue(prods.keys().__contains__(1))
        with self.assertRaises(Exception):
            self.store_facade.removeProductFromStore("Feliks", "some_store", 1)
        self.assertTrue(prods.keys().__contains__(1))

    def test_removeProductFromStore_storeIsClosed_success(self):
        # item with id 1
        self.store_facade.logInAsMember("Feliks", "password456")
        prods = self.my_store.getProducts("Feliks")
        self.assertTrue(prods.keys().__contains__(1))
        self.store_facade.removeProductFromStore("Feliks", "AriExpress", 1)
        self.assertFalse(prods.keys().__contains__(1))

    def test_removeProductFromStore_productNotExists_fail(self):
        # item with id 2
        self.store_facade.logInAsMember("Feliks", "password456")
        prods = self.my_store.getProducts("Feliks")
        self.assertTrue(prods.keys().__contains__(1))
        with self.assertRaises(Exception):
            self.store_facade.removeProductFromStore("Feliks", "AriExpress", 2)
        self.assertTrue(prods.keys().__contains__(1))

    def test_removeProductFromStore_productWithSpecialPolicies_success(self):
        # TODO: check that product is deleted properly
        pass

    # django_getAllStaffMembersNames(self, storename)
    def test_django_getAllStaffMembersNames_success(self):
        pass

    def test_django_getAllStaffMembersNames_storeNotExists_fail(self):
        pass

    def test_django_getAllStaffMembersNames_storeIsClosed_fail(self):
        pass

    # ==================== Messages =======================#

    # ARI RUBIN ADMIN, FELIKS online store owner ARIEXPRESS AMIEL YUVALMELAMED
    # Tests:
    # TODO Although they are empyu, there are other tests who check the functionality in the using functions.
    def test_sendMessageUsers_receiverLoggedIn_success(self):
        # Test sending a message to a receiver who is logged in
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        Amiel_Messages_count_before = self.store_facade.getAllMessagesReceived("Amiel").__len__()
        Feliks_Messages_count_before = self.store_facade.getAllMessagesReceived("Feliks").__len__()
        Feliks_sentMessages_count_before = self.store_facade.getAllMessagesSent("Feliks").__len__()
        self.store_facade.sendMessageUsers("Feliks", "Amiel", "subject", "content", "creation_date", "file")
        Amiel_Messages_count_after = self.store_facade.getAllMessagesReceived("Amiel").__len__()
        Feliks_Messages_count_after = self.store_facade.getAllMessagesReceived("Feliks").__len__()
        Feliks_sentMessages_count_after = self.store_facade.getAllMessagesSent("Feliks").__len__()
        self.assertEqual(Amiel_Messages_count_before + 1, Amiel_Messages_count_after)
        self.assertEqual(Feliks_Messages_count_before, Feliks_Messages_count_after)
        self.assertEqual(Feliks_sentMessages_count_before + 1, Feliks_sentMessages_count_after)

    def test_sendMessageUsers_deleteMessage_success(self):
        # Test sending a message to a receiver who is logged in
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.sendMessageUsers("Feliks", "Amiel", "subject", "content", "creation_date", "file")
        self.store_facade.deleteMessage("Amiel", 1)


    def test_sendMessageUsers_receiverNotLoggedIn_success(self):
        # Test sending a message to a receiver who is not logged in
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        Amiel_Messages_count_before = self.store_facade.getAllMessagesReceived("Amiel").__len__()
        Feliks_Messages_count_before = self.store_facade.getAllMessagesReceived("Feliks").__len__()
        Feliks_sentMessages_count_before = self.store_facade.getAllMessagesSent("Feliks").__len__()
        self.store_facade.logOut("Amiel")
        self.store_facade.sendMessageUsers("Feliks", "Amiel", "subject", "content", "creation_date", "file")
        self.store_facade.logInAsMember("Amiel", "password789")
        Amiel_Messages_count_after = self.store_facade.getAllMessagesReceived("Amiel").__len__()
        Feliks_Messages_count_after = self.store_facade.getAllMessagesReceived("Feliks").__len__()
        Feliks_sentMessages_count_after = self.store_facade.getAllMessagesSent("Feliks").__len__()
        self.assertEqual(Amiel_Messages_count_before + 1, Amiel_Messages_count_after)
        self.assertEqual(Feliks_Messages_count_before, Feliks_Messages_count_after)
        self.assertEqual(Feliks_sentMessages_count_before + 1, Feliks_sentMessages_count_after)

    def test_sendMessageUsers_requesterNotLoggedIn_fail(self):
        # Test sending a message when the requester is not logged in
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("Feliks", "password456")
        Amiel_Messages_count_before = self.store_facade.getAllMessagesReceived("Amiel").__len__()
        Feliks_sentMessages_count_before = self.store_facade.getAllMessagesSent("Feliks").__len__()
        self.store_facade.logOut("Feliks")
        self.store_facade.logOut("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.sendMessageUsers("Feliks", "Amiel", "subject", "content", "creation_date", "file")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("Feliks", "password456")
        Feliks_sentMessages_count_after = self.store_facade.getAllMessagesSent("Feliks").__len__()
        Amiel_Messages_count_after = self.store_facade.getAllMessagesReceived("Amiel").__len__()
        self.assertEqual(Amiel_Messages_count_before, Amiel_Messages_count_after)
        self.assertEqual(Feliks_sentMessages_count_before, Feliks_sentMessages_count_after)

    def test_sendMessageUsers_receiverNotExists_fail(self):
        # Test sending a message to a receiver who does not exist
        self.store_facade.logInAsMember("Amiel", "password789")
        Amiel_sentMessages_count_before = self.store_facade.getAllMessagesSent("Amiel").__len__()
        self.store_facade.logOut("Amiel")
        with self.assertRaises(Exception):
            self.store_facade.sendMessageUsers("Amiel", "FakeAmiel", "subject", "content", "creation_date", "file")
        self.store_facade.logInAsMember("Amiel", "password789")
        Amiel_sentMessages_count_after = self.store_facade.getAllMessagesSent("Amiel").__len__()
        self.assertEqual(Amiel_sentMessages_count_before, Amiel_sentMessages_count_after)

    def test_sendMultipleMessages_succeed(self):
        # Test sending a message to a receiver who does not exist
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.sendMessageUsers("Amiel", "Feliks", "subject", "content", "creation_date", "file")
        self.store_facade.sendMessageUsers("Amiel", "Feliks", "subject1", "content", "creation_date", "file")
        self.store_facade.sendMessageUsers("Amiel", "YuvalMelamed", "subject2", "content", "creation_date", "file")
        self.store_facade.deleteMessage("Feliks", 1)


    def test_readMessage_messageExists_success(self):
        # Test reading a message that exists in the inbox
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.sendMessageUsers("Feliks", "Amiel", "subject", "content", "creation_date", "file")
        message = self.store_facade.getAllMessagesReceived("Amiel")[-1]
        self.assertEqual(message['status'], 'pending')
        message_id = message["id"]
        self.store_facade.readMessage("Amiel", message_id)
        message = self.store_facade.getAllMessagesReceived("Amiel")[-1]
        self.assertEqual(message['status'], 'read')

    def test_readMessage_messageNotExists_fail(self):
        # Test reading a message that does not exist in the inbox
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            self.store_facade.readMessage("Feliks", "nonexistent_message_id")

    def test_getMessagesSent_validUserId_success(self):
        # Test getting sent messages for a valid user ID
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        Feliks_Messages_count_before = self.store_facade.getAllMessagesSent("Feliks").__len__()
        self.store_facade.sendMessageUsers("Feliks", "Amiel", "subject", "content", "creation_date", "file")
        Feliks_Messages_count_after = self.store_facade.getAllMessagesSent("Feliks").__len__()
        messages = self.store_facade.getAllMessagesSent("Feliks")
        self.assertEqual(Feliks_Messages_count_before + 1, Feliks_Messages_count_after)
        self.assertGreater(len(messages), 0)

    def test_getMessagesSent_invalidUserId_fail(self):
        # Test getting sent messages for an invalid user ID
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            self.store_facade.getAllMessagesSent("InvalidUser")

    def test_getMessagesReceived_validUserId_success(self):
        # Test getting received messages for a valid user ID
        self.store_facade.logInAsMember("Feliks", "password456")
        self.store_facade.logInAsMember("Amiel", "password789")
        Amiel_Messages_count_before = self.store_facade.getAllMessagesReceived("Amiel").__len__()
        self.assertEqual(Amiel_Messages_count_before, 0)
        self.store_facade.sendMessageUsers("Feliks", "Amiel", "subject", "content", "creation_date", "file")
        Amiel_Messages_count_after = self.store_facade.getAllMessagesReceived("Amiel").__len__()
        self.assertEqual(Amiel_Messages_count_before + 1, Amiel_Messages_count_after)

    def test_getMessagesReceived_invalidUserId_fail(self):
        # Test getting received messages for an invalid user ID
        with self.assertRaises(Exception):
            self.store_facade.getAllMessagesReceived("InvalidUser")

    def test_readNotification_notificationExists_success(self):
        self.store_facade.logInAsMember("Amiel", "password789")
        self.store_facade.sendNotificationToUser("Amiel", "header", "notification_content", "creation_date")
        notification = self.store_facade.getAllNotificationsReceived("Amiel")[-1]
        self.assertTrue(notification["status"] == 'pending')
        notification_id = notification["id"]
        self.store_facade.readNotification("Amiel", notification_id)
        notification = self.store_facade.getAllNotificationsReceived("Amiel")[-1]
        self.assertTrue(notification["status"] == 'read')

    def test_readNotification_notificationNotExists_fail(self):
        # Test reading a notification that does not exist in the inbox
        self.store_facade.logInAsMember("Feliks", "password456")
        with self.assertRaises(Exception):
            self.store_facade.readNotification("Feliks", "nonexistent_notification_id")

    def test_getNotifications_validUserId_success(self):
        # Test getting notifications for a valid user ID
        self.store_facade.logInAsMember("Feliks", "password456")
        Feliks_Notifications_count_before = self.store_facade.getAllNotificationsReceived("Feliks").__len__()
        self.store_facade.sendNotificationToUser("Feliks", "header", "notification_content", "creation_date")
        Feliks_Notifications_count_after = self.store_facade.getAllNotificationsReceived("Feliks").__len__()
        self.assertEqual(Feliks_Notifications_count_before + 1, Feliks_Notifications_count_after)

    def test_getNotifications_invalidUserId_fail(self):
        # Test getting notifications for an invalid user ID
        with self.assertRaises(Exception):
            self.store_facade.getAllNotificationsReceived("InvalidUser")

    def test_sendNotificationToUser_receiverLoggedIn_success(self):
        # Test sending a notification to a receiver who is logged in
        self.store_facade.logInAsMember("Feliks", "password456")
        Feliks_Notifications_count_before = self.store_facade.getAllNotificationsReceived("Feliks").__len__()
        self.store_facade.sendNotificationToUser("Feliks", "header", "notification_content", "creation_date")
        Feliks_Notifications_count_after = self.store_facade.getAllNotificationsReceived("Feliks").__len__()
        self.assertEqual(Feliks_Notifications_count_before + 1, Feliks_Notifications_count_after)

    def test_sendNotificationToUser_receiverNotLoggedIn_success(self):
        # Test sending a notification to a receiver who is not logged in
        self.store_facade.logInAsMember("Feliks", "password456")
        Feliks_Notifications_count_before = self.store_facade.getAllNotificationsReceived("Feliks").__len__()
        self.store_facade.logOut("Feliks")
        self.store_facade.sendNotificationToUser("Feliks", "header", "notification_content", "creation_date")
        self.store_facade.logInAsMember("Feliks", "password456")
        Feliks_Notifications_count_after = self.store_facade.getAllNotificationsReceived("Feliks").__len__()
        self.assertEqual(Feliks_Notifications_count_before + 1, Feliks_Notifications_count_after)

    def test_sendNotificationToUser_receiverNotExists_fail(self):
        # Test sending a notification to a receiver who does not exist
        with self.assertRaises(Exception):
            self.store_facade.sendNotificationToUser("Invalid User", "header", "notification_content", "creation_date")

    def test_sendNotificationToStore_receiverLoggedIn_success(self):
        # Test sending a notification to a receiver who is logged in
        self.store_facade.logInAsMember("Feliks", "password456")
        Feliks_Notifications_count_before = self.store_facade.getAllNotificationsReceived("Feliks").__len__()
        self.store_facade.sendNotificationToStore("AriExpress", "header", "notification_content", "creation_date")
        Feliks_Notifications_count_after = self.store_facade.getAllNotificationsReceived("Feliks").__len__()
        self.assertEqual(Feliks_Notifications_count_before + 1, Feliks_Notifications_count_after)

    def test_sendNotificationToStore_receiverNotLoggedIn_success(self):
        # Test sending a notification to a receiver who is not logged in
        self.store_facade.logInAsMember("Feliks", "password456")
        Feliks_Notifications_count_before = self.store_facade.getAllNotificationsReceived("Feliks").__len__()
        self.store_facade.logOut("Feliks")
        self.store_facade.sendNotificationToStore("AriExpress", "header", "notification_content", "creation_date")
        self.store_facade.logInAsMember("Feliks", "password456")
        Feliks_Notifications_count_after = self.store_facade.getAllNotificationsReceived("Feliks").__len__()
        self.assertEqual(Feliks_Notifications_count_before + 1, Feliks_Notifications_count_after)

    def test_sendNotificationToStore_receiverNotExists_fail(self):
        # Test sending a notification to a receiver who does not exist
        with self.assertRaises(Exception):
            self.store_facade.sendNotificationToStore("Invalid Store", "header", "notification_content",
                                                      "creation_date")

    # ----------------------------------------------------------------------------------
    # ----------------------------External Services Tests-------------------------------

    def test_ExternalServicePayment_handshake_success(self):
        payment_service = PaymentService("https://php-server-try.000webhostapp.com/")
        answer = payment_service.perform_handshake()
        self.assertTrue(answer)

    def test_ExternalServicePayment_handshake_fail(self):
        payment_service = PaymentService("https://php-server-try.00p.com/")
        with self.assertRaises(Exception):
            answer = payment_service.perform_handshake()

    def test_ExternalServiceSupply_handshake_success(self):
        supply_service = SupplyService("https://php-server-try.000webhostapp.com/")
        answer = supply_service.perform_handshake()
        self.assertTrue(answer)

    def test_ExternalServiceSupply_handshake_fail(self):
        supply_service = PaymentService("https://php-server-try.00p.com/")
        with self.assertRaises(Exception):
            answer = supply_service.perform_handshake()


    def test_ExternalServicePayment_Pay_success(self):
        payment_service = PaymentService("https://php-server-try.000webhostapp.com/")
        answer = payment_service.perform_handshake()
        transaction_id = payment_service.pay("4580029349543845","3","27","Amiel saad", "555", "123456789")
        self.assertTrue(isinstance(transaction_id, str))

    def test_ExternalServicePayment_Pay_cardnum_fail(self):
        payment_service = PaymentService("https://php-server-try.000webhostapp.com/")
        answer = payment_service.perform_handshake()
        with self.assertRaises(Exception):
            transaction_id = payment_service.pay("4545","3","27","Amiel saad", "555", "123456789")

    def test_ExternalServicePayment_Pay_month_fail(self):
        payment_service = PaymentService("https://php-server-try.000webhostapp.com/")
        answer = payment_service.perform_handshake()
        with self.assertRaises(Exception):
            transaction_id = payment_service.pay("4580029349543845","","27","Amiel saad", "555", "123456789")

    def test_ExternalServicePayment_Pay_year_fail(self):
        payment_service = PaymentService("https://php-server-try.000webhostapp.com/")
        answer = payment_service.perform_handshake()
        with self.assertRaises(Exception):
            transaction_id = payment_service.pay("4580029349543845", "3", "", "Amiel saad", "555", "123456789")

    def test_ExternalServicePayment_Pay_name_fail(self):
        payment_service = PaymentService("https://php-server-try.000webhostapp.com/")
        answer = payment_service.perform_handshake()
        with self.assertRaises(Exception):
            transaction_id = payment_service.pay("4580029349543845","3","27","", "555", "123456789")

    def test_ExternalServicePayment_Pay_cvv_fail(self):
        payment_service = PaymentService("https://php-server-try.000webhostapp.com/")
        answer = payment_service.perform_handshake()
        with self.assertRaises(Exception):
            transaction_id = payment_service.pay("4580029349543845","3","27","Amiel saad", "5", "123456789")

    def test_ExternalServicePayment_Pay_id_fail(self):
        payment_service = PaymentService("https://php-server-try.000webhostapp.com/")
        answer = payment_service.perform_handshake()
        with self.assertRaises(Exception):
            transaction_id = payment_service.pay("4580029349543845","3","27","Amiel saad", "555", "1789")


    def test_ExternalServiceSupply_dispatch_success(self):
        supply_service = SupplyService("https://php-server-try.000webhostapp.com/")
        answer = supply_service.perform_handshake()
        supply_id = supply_service.dispatch_supply("Amiel saad", "shimoni", "Beer sheva", "Israel", "493047")
        self.assertTrue(isinstance(supply_id, str))

    def test_ExternalServiceSupply_dispatch_name_fail(self):
        supply_service = SupplyService("https://php-server-try.000webhostapp.com/")
        answer = supply_service.perform_handshake()
        with self.assertRaises(Exception):
            supply_id = supply_service.dispatch_supply("", "shimoni", "Beer sheva", "Israel", "493047")

    def test_ExternalServiceSupply_dispatch_address_fail(self):
        supply_service = SupplyService("https://php-server-try.000webhostapp.com/")
        answer = supply_service.perform_handshake()
        with self.assertRaises(Exception):
            supply_id = supply_service.dispatch_supply("Amiel saad", "", "Beer sheva", "Israel", "493047")

    def test_ExternalServiceSupply_dispatch_city_fail(self):
        supply_service = SupplyService("https://php-server-try.000webhostapp.com/")
        answer = supply_service.perform_handshake()
        with self.assertRaises(Exception):
            supply_id = supply_service.dispatch_supply("Amiel saad", "shimoni", "", "Israel", "493047")

    def test_ExternalServiceSupply_dispatch_country_fail(self):
        supply_service = SupplyService("https://php-server-try.000webhostapp.com/")
        answer = supply_service.perform_handshake()
        with self.assertRaises(Exception):
            supply_id = supply_service.dispatch_supply("Amiel saad", "shimoni", "Beer sheva", "", "493047")

    def test_ExternalServiceSupply_dispatch_zipCode_fail(self):
        supply_service = SupplyService("https://php-server-try.000webhostapp.com/")
        answer = supply_service.perform_handshake()
        with self.assertRaises(Exception):
            supply_id = supply_service.dispatch_supply("Amiel saad", "shimoni", "Beer sheva", "Israel", "")

    def test_ExternalServicePayment_cancel_success(self):
        payment_service = PaymentService("https://php-server-try.000webhostapp.com/")
        answer = payment_service.perform_handshake()
        self.assertTrue(answer)
        answer = payment_service.cancel_pay(answer)
        self.assertTrue(answer)

    def test_ExternalServicePayment_cancel_fail(self):
        payment_service = PaymentService("https://php-server-try.000webhostapp.com/")
        answer = payment_service.perform_handshake()
        self.assertTrue(answer)
        with self.assertRaises(Exception):
            answer = payment_service.cancel_pay("some_id")

    def test_ExternalServiceSupply_cancel_success(self):
        supply_service = SupplyService("https://php-server-try.000webhostapp.com/")
        answer = supply_service.perform_handshake()
        self.assertTrue(answer)
        answer = supply_service.cancel_supply(answer)
        self.assertTrue(answer)

    def test_ExternalServiceSupply_cancel_fail(self):
        supply_service = SupplyService("https://php-server-try.000webhostapp.com/")
        answer = supply_service.perform_handshake()
        self.assertTrue(answer)
        with self.assertRaises(Exception):
            answer = supply_service.cancel_supply("some_id")


if __name__ == '__main__':
    unittest.main()
