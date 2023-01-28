from collections import Counter

def do_nothing():
    pass
def bit_write(bit, f):    
    global bit_w, bit_l
    bit_w, bit_l = bit_w >> 1, bit_l - 1
    if (bit & 1):
        bit_w |= 0x80
    if bit_l == 0:
        bit_l = 8
        f.write(bit_w.to_bytes(1, "little"))

def bit_read(f):  
    global bit_r, bit_l, bit_extra
    if bit_l == 0:
        bit = f.read(1)
        bit_r = int.from_bytes(bit, "little")
        if bit == b"":
            bit_extra, bit_r = bit_extra + 1, 255
            if bit_extra > 14:
                exit(1)
        bit_l = 8
    t, bit_r, bit_l = bit_r & 1, bit_r >> 1, bit_l - 1
    return t

def bit_plus_follow(bit, bit_follow, f):    
    bit_write(bit, f)
    for i in range(bit_follow):
        bit_write(1 - bit, f)

def compress(file):
    global bit_w, bit_l
    s = open(file, 'rb').read()
    bit_l, bit_w = 8, 0
    occurrences = {}
    symbol_intervals = [0, 1]
    
    for ch, freq in Counter(s).items():
        occurrences[ch] = freq
    occurrences = dict(sorted(occurrences.items(), key = lambda item: item[1], reverse = True))
    
    for i in occurrences:
        symbol_intervals.append(occurrences[i] + symbol_intervals[len(symbol_intervals)-1])

    f = open("enc", 'wb+')
    f.write(len(occurrences).to_bytes(1, "little")) #длина словаря
    for ch, freq in occurrences.items(): #словарь
        f.write(ch.to_bytes(1, "little"))
        f.write(freq.to_bytes(3, "little"))
    txt = open(file, 'r').read()
    boarders = [0, 65535]
    dif = boarders[1] - boarders[0] + 1
    divider = symbol_intervals[-1]
    f_qtr, half, t_qtr, bit_follow = 16384, 32768, 49152, 0
    for ch in txt:
        j = 2 + next(index for index, key in enumerate(occurrences) if key == ord(ch))
        boarders = [boarders[0] + symbol_intervals[j - 1] * dif // divider, boarders[0] + symbol_intervals[j] * dif // divider - 1]
        while True:
            if boarders[1] < half:
                bit_plus_follow(0, bit_follow, f)
                bit_follow=0
            elif boarders[0] >= half:
                bit_plus_follow(1, bit_follow, f)
                bit_follow, boarders = 0, [boarders[0] - half, boarders[1] - half]
            elif boarders[0] >= f_qtr and boarders[1] < t_qtr:
                bit_follow, boarders = bit_follow + 1, [boarders[0] - f_qtr, boarders[1] - f_qtr]
            else:
                break
            boarders = [boarders[0]*2, boarders[1]*2 + 1]
        dif = boarders[1] - boarders[0] + 1

    boarders = [boarders[0] + symbol_intervals[0] * dif // divider, boarders[0] + symbol_intervals[1] * dif // divider - 1]
    while True:
        if boarders[1] < half:
            bit_plus_follow(0, bit_follow, f)
            bit_follow=0
        elif boarders[0] >= half:
            bit_plus_follow(1, bit_follow, f)
            bit_follow, boarders = 0, [boarders[0] - half, boarders[1] - half]
        elif boarders[0] >= f_qtr and boarders[1] < t_qtr:
            bit_follow, boarders = bit_follow + 1, [boarders[0] - f_qtr, boarders[1] - f_qtr]
        else:
            break
        boarders = [boarders[0]*2, boarders[1]*2 + 1]
    bit_follow += 1
    if boarders[0] < f_qtr:
        bit_plus_follow(0, bit_follow, f)
    else:
        bit_plus_follow(1, bit_follow, f)
    f.close()

def decompress(file):
    global bit_r, bit_l, bit_extra
    bit_r = bit_l = bit_extra = value = 0
    occurrences = {}
    symbol_intervals = [0, 1]
    f = open(file, "rb")
    out = open("dec", "wb+")
    dict_len = int.from_bytes(f.read(1), 'little')
    for x in range(dict_len):
        ch, freq = int.from_bytes(f.read(1), 'little'), int.from_bytes(f.read(3), 'little')
        occurrences[ch] = freq
    for i in occurrences:
        symbol_intervals.append(occurrences[i] + symbol_intervals[-1])
    boarders = [0, 65535]
    dif = boarders[1] - boarders[0] + 1
    divider = symbol_intervals[-1]
    f_qtr, half, t_qtr = 16384, 32768, 49152
    lst = list(occurrences.keys())
    for i in range(16):
        bit = bit_read(f)
        value = value*2 + bit
    while True:
        freq, j = ((value - boarders[0] + 1) * divider - 1) // dif, 1
        while symbol_intervals[j] <= freq: #поиск
            j += 1
        boarders = [boarders[0] + symbol_intervals[j - 1] * dif // divider, boarders[0] + symbol_intervals[j] * dif // divider - 1]
        while True:
            if boarders[1] < half:
                do_nothing()
            elif boarders[0] >= half:
                boarders, value = [boarders[0] - half, boarders[1] - half], value - half
            elif boarders[0] >= f_qtr and boarders[1] < t_qtr:
                boarders, value = [boarders[0] - f_qtr, boarders[1] - f_qtr], value - f_qtr
            else:
                break
            boarders = [boarders[0]*2, boarders[1]*2 + 1]
            k = bit_read(f)
            value = value*2 + k
        if j == 1:
            break
        out.write(lst[j - 2].to_bytes(1, "little")) 
        dif = boarders[1] - boarders[0] + 1
    out.close()