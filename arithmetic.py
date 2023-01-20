from collections import Counter
from prettytable import PrettyTable

def BitsPlusFollow(bit, bits_to_follow, all_bits):
    all_bits += str(bit)
    for i in range(bits_to_follow):
        all_bits += str(1-bit)
    bits_to_follow = 0
    return all_bits

def toByte(s):
    return b''.join((int(s[i:i+8][::-1], 2)).to_bytes(1, 'big') for i in range(0, len(s), 8))

def compress(file):
    
    filein = open(file, 'r')
    s = filein.read() #text
    
    symbol_dict = {}
    for ch, freq in Counter(s).items():
        symbol_dict[ch] = freq

    sorted_dict = dict(sorted(symbol_dict.items(), key=lambda item: item[1], reverse=True)) #set

    ch = {}
    freq_ = {}
    b = {}
    boarders = {}

    all_bits = ""
    freq_[0] = 0
    b[0] = 0
    
    l = 0
    j = 1
    for pair, count in sorted_dict.items():
        ch[pair[0]] = j
        freq_[j] = count
        b[j] = l + count
        j += 1
        l += count
    
    i = 0
    delitel = b[j-1]
    boarders[0] = [0, 65535]
    First_qtr = (boarders[0][1] + 1) // 4
    Half = First_qtr * 2
    Third_qtr = First_qtr * 3
    bits_to_follow = 0
    for index in s:
        j = ch[index]
        i += 1
        boarders[i] = [boarders[i-1][0] + b[j-1] * (boarders[i-1][1] - boarders[i-1][0] + 1) // delitel, 
                      boarders[i-1][0] + b[j] * (boarders[i-1][1] - boarders[i-1][0] + 1) // delitel - 1]
        while True:
            if boarders[i][1] < Half:
                all_bits = BitsPlusFollow(0, bits_to_follow, all_bits)
                bits_to_follow = 0
            elif boarders[i][0] >= Half:
                all_bits = BitsPlusFollow(1, bits_to_follow, all_bits)
                bits_to_follow = 0
                boarders[i][0] -= Half
                boarders[i][1] -= Half
            elif boarders[i][0] >= First_qtr and boarders[i][1] < Third_qtr:
                bits_to_follow += 1
                boarders[i][0] -= First_qtr
                boarders[i][1] -= First_qtr
            else:
                break
            boarders[i][0] += boarders[i][0]
            boarders[i][1] += boarders[i][1] + 1


    bitPadd = 8 - len(all_bits)%8
    bitstr = toByte(str(all_bits)[10:-2])
    
    #запись в байтах
    f = open("enc_aric", 'wb')
    f.write(len(s).to_bytes(4, 'big'))
    f.write(len(sorted_dict).to_bytes(2, 'big'))
    for ch in sorted_dict:
        f.write(ch.encode())
        f.write(sorted_dict[ch].to_bytes(2, 'big'))
    f.write(bitPadd.to_bytes(1, 'big'))
    f.write(bitstr)
    f.close()

def decompress(file):

    filein = open(file, 'rb')

    #чтение
    length = int.from_bytes(filein.read(4), 'big') #длина текста
    dictlen = int.from_bytes(filein.read(2), 'big') #кол-во
    dict = {}
    p = []
    list = ""
    for i in range(dictlen):
        a = str(filein.read(1).decode())
        b = int.from_bytes(filein.read(2), 'big')
        dict[a] = b
        p.append(dict[a]/length)
        list+=a

    
    #запись
    f = open("dec_aric", 'wb')
    f.close()


