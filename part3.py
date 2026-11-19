#!/usr/bin/env python
# -*- coding: utf-8 -*-
class model:
    """ data model class"""
    def __init__(self):
        self.directory = [
            {"firstname":'Ahmed', "familyname":'Mahdi', 'tel':'0778787887'},
            {"firstname":'Mohamed', "familyname":'Mahdi','tel':'0778787887'},
            {"firstname":'Mounir', "familyname":'Katibi','tel':'0778787887'},
            {"firstname":'Noui', "familyname":'Brahimi','tel':'0778787887'},
        ]
    def search(self, nom):
        """ lookup for a tel by lastname"""
        persons = []
        for persn in self.directory:
            if persn["familyname"] == nom:
                persons.append(persn)
        return persons

    def get_all(self):
        persons = []
        for persn in self.directory:
            persons.append(persn)
        return persons

    def add(self, name, firstname, tel):     # NEW
        """ Add a person """
        person = {}
        person["familyname"] = name
        person["firstname"] = firstname
        person["tel"] = tel
        self.directory.append(person)


class view:
    def __init__(self,):
        pass
    def input(self,):
        """ retrieve the name to search for"""
        print("Finding a phone")
        print("Give a name")
        name = input()
        return name
    def output(self, persons):
        """ display information from a list of persons"""
        print("List of found names")
        print(" %d found people " % len(persons))
        for pers in persons:
            print(pers["familyname"], pers["firstname"], pers['tel'])

    def input_add(self,):                    # NEW
        """get name to add"""
        print("Add a person")
        print("Give a name")
        name = input()
        print("Give a firstname")
        firstname = input()
        print("Give a tel")
        tel = input()
        return (name, firstname, tel)


class controller:
    def __init__(self,):
        """ controller constrctor"""
        self.data_model = model()
        self.viewer = view()

    def search(self):
        """ search a name """
        name = self.viewer.input()
        persons = self.data_model.search(name)
        self.viewer.output(persons)

    def get_all(self):
        persons = self.data_model.get_all()
        self.viewer.output(persons)

    def add(self):                           # NEW
        """ Add a new name """
        name, firstname, tel = self.viewer.input_add()
        self.data_model.add(name, firstname, tel)
        persons = self.data_model.get_all()
        self.viewer.output(persons)


if __name__ == '__main__':
    contro = controller()

    # Q2: شخص واحد
    contro.add()

    # Q3: بزاف أشخاص
    while True:
        contro.add()
        if input("Add another? (y/n): ") != "y":
            break