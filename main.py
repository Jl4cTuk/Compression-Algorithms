import heapq
from collections import Counter, namedtuple
import os
import sys

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
    return ''.join(chr(int(s[i:i+8][::-1], 2)) for i in range(0, len(s), 8))

def toBit(s):
    return ''.join(bin(ord(x))[2:].rjust(8,'0')[::-1] for x in s)

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
	code = makeHufCode(dict)
	encoded = "".join(code[ch] for ch in filein)
	
	dictlen = len(dict)
	huffedText = toByte(encoded)
	bitPadd = 8 - len(encoded)%8

	file = f"{filename}_huf"
	fileout = open(file, "wb")
	
	fileout.write(dictlen.to_bytes(2, 'big')) #запись кол-ва букв
	for i, j in dict.items(): #запись словаря
		fileout.write(i.to_bytes(2, 'big'))
		fileout.write(j.to_bytes(2, 'big'))
	fileout.write(bitPadd.to_bytes(1, 'big')) #запись сколько откусить
	fileout.write(huffedText.encode()) #запись закод. текста
	
	fileout.close()

def decompress(filename):
	filein = open(filename, "rb")
	
	dictlen = int.from_bytes(filein.read(2), 'big') #чтение кол-ва букв
	dict = {}
	for i in range(dictlen): #создание словаря
		a = int.from_bytes(filein.read(2), 'big')
		b = int.from_bytes(filein.read(2), 'big')
		dict[a] = b
	bitPadd = int.from_bytes(filein.read(1), 'big') #сколько откусить
	huffedText = toBit(filein.read().decode())[:-bitPadd] #закод. текст и откусил
	code = makeHufCode(dict) #создание нового хаффманского словаря


	a = huffman_decode(huffedText, code)

	f = f"{filename}_decompr"
	file = open(f, "wb")
	file.write(a)


def fileExist(filename):
	if os.path.exists(filename):
		return True
	else:
		return False


def main_menu():
	print("choose option: [c] or [d]")
	option = input()
	if option == 'c': #compress
		print("file name for compress:")
		filename = input()
		if fileExist(filename):
			compress(filename)
		else:
			sys.exit("File not found")
			
	elif option == 'd': #decompress
		print("file name for decompress:")
		filename = input()
		if fileExist(filename):
			decompress(filename)
		else:
			sys.exit("File not found")
	else:
		print("wrong option")

def main():
	main_menu()
	
if __name__ == "__main__":
	main()