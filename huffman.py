import heapq
from collections import Counter, namedtuple

class Node(namedtuple("Node", ["left", "right"])):
	def walk(self, code, acc):
		self.left.walk(code, acc + "0")
		self.right.walk(code, acc + "1")

class Leaf(namedtuple("Leaf", ["char"])):
	def walk(self, code, acc):
		code[self.char] = acc or "0"

def makeHufCode(dict):
	h = []
	for ch, freq in dict.items():
		h.append((freq, len(h), Leaf(ch)))
	heapq.heapify(h)

	count = len(h)
	while len(h) > 1:
		freq1, _count1, left = heapq.heappop(h)
		freq2, _count2, right = heapq.heappop(h)
		heapq.heappush(h, (freq1 + freq2, count, Node(left, right)))
		count +=1 
	code = {}
	if h:
		[(_freq, _count, root)] = h
		root.walk(code, "") 
	return code

def toByte(s):
    return b''.join((int(s[i:i+8][::-1], 2)).to_bytes(1, 'big') for i in range(0, len(s), 8))

def toBit(s):
    return ''.join(bin(x)[2:].rjust(8,'0')[::-1] for x in s)

def makeDict(s):
	dict = {}
	for ch, freq in Counter(s).items():
		dict[ch] = freq

	return dict

def huffman_decode(en, code):
	pointer = 0
	encoded_str = b''
	while pointer < len(en):
		for ch in code.keys():
			if en.startswith(code[ch], pointer):
				encoded_str += ch.to_bytes(1, 'big')
				pointer += len(code[ch])
			
	return encoded_str

	
def compress(filename):
	s = open(filename, "rb")
	filein = s.read()
	dict = makeDict(filein)
	print(dict)
	code = makeHufCode(dict)
	encoded = "".join(code[ch] for ch in filein)
	
	dictlen = len(dict)
	huffedText = toByte(encoded)
	bitPadd = 8 - len(encoded)%8

	file = "enc_huf"
	fileout = open(file, "wb")

	fileout.write(dictlen.to_bytes(2, 'big')) #запись кол-ва букв
	for i, j in dict.items(): #запись словаря
		fileout.write(i.to_bytes(3, 'big'))
		fileout.write(j.to_bytes(3, 'big'))
	fileout.write(bitPadd.to_bytes(1, 'big')) #запись сколько откусить
	fileout.write(huffedText) #запись закод. текста
	
	fileout.close()

def decompress(filename):
	filein = open(filename, "rb")
	
	dictlen = int.from_bytes(filein.read(2), 'big') #чтение кол-ва букв
	dict = {}
	for i in range(dictlen): #создание словаря
		a = int.from_bytes(filein.read(3), 'big')
		b = int.from_bytes(filein.read(3), 'big')
		dict[a] = b
	bitPadd = int.from_bytes(filein.read(1), 'big') #сколько откусить
	huffedText = toBit(filein.read())[:-bitPadd] #закод. текст и откусил
	code = makeHufCode(dict) #создание нового хаффманского словаря

	a = huffman_decode(huffedText, code)

	f = "dec_huf"
	file = open(f, "wb")
	file.write(a)