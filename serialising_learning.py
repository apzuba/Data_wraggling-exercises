#-------------WAY 1 Pickle/ DAT-------------

import pickle


#1 Create the binary file
phonebook = {
    'James': 935739753,
    'Marie': 37523795,
    'Julie_hot': 93859382,
    'Amelie': 35353232
}

#creates the file
out_file = open('phonebook.dat','wb')
pickle.dump(phonebook, out_file)
out_file.close()


#2 open binary files
in_file = open('phonebook.dat', 'rb')
phonebook2 = pickle.load(in_file)
in_file.close()
print(phonebook2)




#-------------WAY 2 JSON-------------
#I don't really get the point of this one, since we're not writing into a file here.
import json
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int

p = Person(name='John', age = 48)

#method 1 - Manaul Way

# jsonified_p = f'{{"name" : {p.name}, "age" : {p.age} }}'
# print(jsonified_p)

#method 2 - Using an Encoder Function
def encoder_person(person):
    if isinstance(person, Person):
        return {'name': person.name, 'age': person.age}

    raise TypeError(f'Object {person} is not of type Person')


jsonified_p = json.dumps(p, default=encoder_person, indent=4)
print()
print(jsonified_p)


# method 3 - Using an Encoder Class

class PersonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(person, Person):
            return {'name': person.name, 'age': person.age}

        return super().default(o)

jsonified_p = json.dumps(p, cls=PersonEncoder, indent=4)
print()
print(jsonified_p)

