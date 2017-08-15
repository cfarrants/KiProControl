import threading


ListItems = []

def populatelist():
    with open('threadtest.txt', "r") as f:
        for line in f:
            ListItems.append(line)
    print(ListItems)

populatelist()
