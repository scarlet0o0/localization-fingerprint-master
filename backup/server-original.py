import socket, pickle, math, copy
# number of APs --> server decides


def findUserLocation(number, userID):
    with open('map_blocks.pkl', 'rb') as f:
        mapBlocks = pickle.load(f)
    # mapBlocks looks something like this:
    # {'0': {'mac address1': 'level1', 'mac address2': 'level2', ...}, '1': {...}, ...}
    euclidian = dict()
    # euclidian should look something like this:
    # {'0': value0, '1': value1, ...}
    current = 0 # for calculating euclidian
    for block in mapBlocks:
        # counter = 0
        # print(block)
        # print("---------------------------------------------------")
        for key in mapBlocks[block]:
            if(len(mapBlocks[block]) == 0):  # temporary --> until mapBlocks is full
                break
            # print(key)
            currentString = 0  # level of specific mac address from the current measurement
            currentBlock = float(mapBlocks[block][key])  # level of specific mac address from the radio map
            # print("current block: " + str(currentBlock))
            if key in stringSplit:  # if mac address in radio map also came up in the current measurement
                # if not --> currentString = 0
                index = stringSplit.index(key)
                currentString = float(stringSplit[index + 1])  # level of specific mac address from the current measurement
                # print("current string: " + str(currentString))
                # counter += 1
            current += ((currentBlock) - (currentString)) ** 2
            #  print("sq:" + str(current))
        if current != 0:  # temporary --> until mapBlocks is full
            current = math.sqrt(current)
            euclidian[block] = current
            # print("sqrt: " + str(euclidian[block]) + " # of APs at block: " + str(len(mapBlocks[block])) + " counter: " + str(counter))
            current = 0
    closestAPs = list()
    closestAPs.append(userID)
    for i in range(int(number)):  # chooses the minimal value and deletes it from the list
        closestAPs.append(min(euclidian, key=euclidian.get))
        euclidian.pop(min(euclidian, key=euclidian.get))
    print(closestAPs)
    return closestAPs


def map():
    with open('map_blocks.pkl', 'rb') as f:
        mapBlocks = pickle.load(f)
    mapBlocks[blockNumber].clear()  # clears all values from radio map at the given block
    for index in range(4, len(stringSplit), 2):
        mapBlocks[blockNumber][stringSplit[index - 1]] = stringSplit[index]
    print(mapBlocks)
    with open('map_blocks.pkl', 'r+b') as f:
        pickle.dump(mapBlocks, f)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 12345
s.bind((host, port))

while True:
    s.listen(5)
    c, addr = s.accept()
    print('Got connection from', addr)
    c.send(bytes("Thank you for connecting", "utf-8"))
    dataString = ""
    while True:
        data = c.recv(1024)
        dataString += str(data.decode("utf-8"))
        if not data:
            break
    c.close()

    stringSplit = dataString.split()  # list --> [1]: # of block, [2]: userID
    # [odd]: ssid, [even]: level
    blockNumber = stringSplit[1]  # we do not use [0] for now
    userID = stringSplit[2]
    numberOfClosestAPs = 1  # server decides...

    if blockNumber == '?':  # if it is "?" #compare it as a string
        print("Find the location mode")
        listOfAPs = findUserLocation(numberOfClosestAPs, userID)
    elif blockNumber.isdigit():
        map()

# end
s.close()
