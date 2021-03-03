

import sys, os, socket, statistics
# from tkinter import*
#
# def id_input():
#
#     def submit():
#         global userID
#         userID = entry1.get()
#         root.quit()
#         root.destroy()
#
#     root=Tk()
#     root.geometry("200x67")
#     mainFrame = Frame(root)
#     mainFrame.pack(fill=X)
#
#     frame1 = Frame(mainFrame)
#     frame1.pack(fill=X)
#     idLabel = Label(frame1)
#     idLabel.configure(text="user ID",width=10)
#     idLabel.pack(side=LEFT)
#     entry1 = Entry(frame1)
#     entry1.pack(side=LEFT)
#
#     frame2 = Frame(mainFrame)
#     frame2.pack(fill=X)
#     button = Button(frame2)
#     button.configure(text="ok",command=submit)
#     button.pack(fill=X)
#
#     root.mainloop()


def fileParsing(something, MAC_list, level_list):
    with open(something) as lines:
        for numberOfLine, line in enumerate(lines):
            if(numberOfLine % 2 == 0):
                # odd lines --> mac addresses
                beginning = line.index(':')
                end = line.index('\n')
                mac = line[beginning + 2:end]
            else:
                # even lines --> dbm levels of each address
                beginning = line.index('-')
                end = line.index('d')
                level = int(line[beginning:end-1])
                if mac not in MAC_list:
                    MAC_list.append(mac)
                    level_list.append(list())
                level_list[MAC_list.index(mac)].append(level)
    lines.close()
    return MAC_list, level_list


def median(some_list):
    median_levels = list()
    for index1 in range(len(some_list)):
        # check if some_list[index1] is empty
        median_levels.append(statistics.median(some_list[index1]))
    return median_levels


x_force = sys.argv[1]
y_force = sys.argv[2]


def stringToSend(MAC_list, level_list, userID):
    splitter = " "  # config.py
    data = sys.argv[1] + splitter + sys.argv[2] + splitter + userID + splitter
    print(data)
    for index in range(len(MAC_list)):
        data += MAC_list[index] + splitter + str(level_list[index]) + splitter
    return data


def send2server(something):  # send one string
    msg = s.recv(1024)
    print(msg.decode("utf-8"))
    s.send(bytes(something, "utf-8"))
    print('Done sending')
    s.close()


# id_input()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 12345
print('Trying to connect to server...')
s.connect((host, port))
print('Connection established')

wifiList_filename = 'wifilist.txt'
MAC_list = list()
level_list = list()
n_force = sys.argv[3]
for i in range(int(n_force)):
    os.system("sudo iwlist wlx88366cff59d0 scan | grep -E 'level|Address' > wifilist.txt")
    MAC_list, level_list = fileParsing(wifiList_filename, MAC_list, level_list)

median_levels = median(level_list)
userID = input("userID: ")
data = stringToSend(MAC_list, median_levels, userID)

send2server(data)

print('Client exits...')
print('Hard-coded values : ', x_force, y_force, n_force)

# data = s.recv(1024)
# closestAPs = pickle.loads(data)
# print(closestAPs)
