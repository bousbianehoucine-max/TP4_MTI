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

    def get_all(self):                       # Q3
        persons = []
        for persn in self.directory:
            persons.append(persn)
        return persons


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

    def get_all(self):                       # Q4
        persons = self.data_model.get_all()
        self.viewer.output(persons)


if __name__ == '__main__':
    contro = controller()
    contro.search()
    contro.get_all()