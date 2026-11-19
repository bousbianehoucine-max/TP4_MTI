#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from tkinter import Tk, Label, Button, END, W, E, Text


class model_file:
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


class view_tk:                               # NEW
    def __init__(self, model):
        master = Tk()
        self.master = master
        self.model = model
        master.title("Directory")

        self.output_label = Label(master, text="Output")

        self.label = Label(master, text="Input:")
        self.entry = Text(master, height=1, width=50)
        self.label_firstname = Label(master, text="First Name:")
        self.entry_firstname = Text(master, height=1, width=50)
        self.label_tel = Label(master, text="Tel:")
        self.entry_tel = Text(master, height=1, width=50)
        self.output = Text(master, height=10, width=50)
        self.search_button = Button(master, text="Search",
                                    command=lambda: self.update("search"))
        self.add_button = Button(master, text="Add",
                                 command=lambda: self.update("add"))
        self.all_button = Button(master, text="Get All",
                                 command=lambda: self.update("get_all"))

        # LAYOUT
        self.label.grid(row=0, column=0, sticky=W)
        self.label_firstname.grid(row=0, column=1, sticky=W)
        self.label_tel.grid(row=0, column=2, sticky=W)
        # input familyname
        self.entry.grid(row=1, column=0, columnspan=10, sticky=W+E)
        # firstname et tel
        self.entry_firstname.grid(row=1, column=1, columnspan=10, sticky=W+E)
        self.entry_tel.grid(row=1, column=2, columnspan=2, sticky=W+E)
        # command
        self.search_button.grid(row=2, column=0)
        self.add_button.grid(row=2, column=1)
        self.all_button.grid(row=2, column=2)
        # Output
        self.output_label.grid(row=3, column=0, sticky=E)
        self.output.grid(row=4, column=0, columnspan=5, sticky=W+E)

    def update(self, method):
        familyname = self.entry.get("1.0", END).strip()
        firstname = self.entry_firstname.get("1.0", END)
        tel = self.entry_tel.get("1.0", END)
        # clean ends of words
        familyname = familyname.strip()
        firstname = firstname.strip()
        tel = tel.strip()
        if method == "search":
            result = self.search(familyname)
        elif method == "add":
            result = self.add(familyname, firstname, tel)
        elif method == "get_all":
            result = self.get_all()
        else:  # reset
            print("method", method)
            result = familyname
        self.output.insert(END, str(result))

    def add(self, familyname, firstname, tel):
        self.model.add(familyname, firstname, tel)
        return self.model.get_all()

    def search(self, familyname):
        result = self.model.search(familyname)
        if result:
            return result
        else:
            return "'%s' not found" % familyname

    def get_all(self):
        return self.model.get_all()

    def run(self,):
        self.master.mainloop()


def controller3():
    data_model = model_file()
    my_viewer = view_tk(data_model)
    my_viewer.run()  # launch GUI


if __name__ == '__main__':
    controller3()