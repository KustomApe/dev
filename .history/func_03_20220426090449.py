from distutils.log import info


def hello_zack():
    persons = ['Zack', 'Eric']
    for person in persons:
        print('Hello ' + person)
        return

def seikyusyo(name, price, info):
    conclusion = name + price + info
    return conclusion