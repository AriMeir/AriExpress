from peewee import *
from ProjectCode.DAL.AdminModel import AdminModel
from ProjectCode.Domain.MarketObjects.UserObjects.Admin import Admin
from ProjectCode.Domain.Repository.Repository import Repository


class AdminRepository(Repository):

    def __init__(self):
        self.model = AdminModel

    def __getitem__(self, user_name):
        return self.get(user_name)


    def __setitem__(self, key, value): #key is meaningless
        try:
            return self.add(value)
        except Exception as e:
            raise Exception("AdminRepository: __setitem__ failed: " + str(e))

    def __delitem__(self, key):
        try:
            return self.remove(key)
        except Exception as e:
            raise Exception("AdminRepository: __delitem__ failed: " + str(e))

    def __contains__(self, key):
        try:
            return self.contains(key)
        except Exception as e:
            raise Exception("AdminRepository: __delitem__ failed: " + str(e))

    def get(self, pk=None):
        try:
            if not pk:
                admin_list = []
                for entry in self.model.select():
                    admin = Admin(entry.user_name, entry.password, entry.email)
                    admin.logged_In = entry.logged_in
                    admin_list.append(admin)
                return admin_list
            else:
                entry = self.model.get(self.model.user_name == pk)
                admin = Admin(entry.user_name, entry.password, entry.email)
                admin.logged_In = entry.logged_in
                return admin
        except Exception as e:
            return None

    def add(self, admin: Admin):
        admin_entry = self.model.get_or_none(self.model.user_name == admin.get_username())
        if admin_entry is not None:
            #update
            admin_entry.password = admin.get_password()
            admin_entry.email = admin.get_email()
            admin_entry.logged_in = admin.get_logged()
            admin_entry.save()
            return admin
        self.model.create(user_name=admin.get_username(), password=admin.get_password(), email=admin.get_email(), logged_in =admin.get_logged())
        return admin

    def remove(self, pk):
        user_entry = AdminModel.get(AdminModel.user_name == pk)
        user_entry.delete_instance()

    def keys(self):
        try:
            return [admin.user_name for admin in AdminModel.select()]
        except Exception as e:
            return []

    def values(self):
        return self.get()

    def contains(self, user_name):
        return user_name in self.keys()
