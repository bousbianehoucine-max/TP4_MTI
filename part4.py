#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

class model_file:                            # NEW
    """ Data Model class"""
    def __init__(self):
        self.directory = []
        try:
            myfile = open("directory.txt")
        except:
            print("Can't open DataFile")
            sys.exit()
        lines = myfile.readlines()
        for line in lines:
            line = line.strip('\n')
            fields = line.split('\t')
            person = {}
            person["familyname"] = fields[0]
            person["firstname"] = fields[1]
            person["tel"] = fields[2]
            self.directory.append(person)
        myfile.close()

    def __del__(self,):
        """ Destructor of the Model class,
        It is called at the end of the program
        to reload the data in the file """
        try:
            myfile = open("directory.txt", "w")
        except:
            print("Can't open DataFile")
            sys.exit()
        for person in self.directory:
            line = "\t".join([person['familyname'],
                              person['firstname'],
                              person['tel'],
                              ])
            line += "\n"
            myfile.write(line)
        myfile.close()

    # same methods as the "model" class
    def search(self, name):
        persons = []
        for persn in self.directory:
            if persn["familyname"] == name:
                persons.append(persn)
        return persons

    def get_all(self):
        persons = []
        for persn in self.directory:
            persons.append(persn)
        return persons

    def add(self, name, firstname, tel):
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

    def input_add(self,):
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
        self.data_model = model_file()       # Q2: model_file بدل model
        self.viewer = view()

    def search(self):
        """ search a name """
        name = self.viewer.input()
        persons = self.data_model.search(name)
        self.viewer.output(persons)

    def get_all(self):
        persons = self.data_model.get_all()
        self.viewer.output(persons)

    def add(self):
        """ Add a new name """
        name, firstname, tel = self.viewer.input_add()
        self.data_model.add(name, firstname, tel)
        persons = self.data_model.get_all()
        self.viewer.output(persons)


if __name__ == '__main__':
    contro = controller()
    contro.search()
    contro.add()