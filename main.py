import struct  #для разлиновывания байтов


#класс создать объект с частотой и символом
class Vertex:

	def __init__(self, freq, symbol):
		self.freq = freq
		self.symbol = symbol

	def __lt__(self, other):
		b = (self.freq <= other.freq)
		return b


#класс для дерева
class TreeBuilder:

	def __init__(self, right, left):
		self.freq = right.freq + left.freq
		self.right = right
		self.left = left

	def __lt__(self, other):
		return self.freq <= other.freq


#чтение файла в байтах
def openbytes(myfile):
	f = open(myfile, 'rb')
	return f.read()


#функции сжатия
#создание словаря для с подсчитанными символами
def symbols_counter(bytes):
	dict_sym = {}
	for i in range(len(bytes)):
		dict_sym[chr(bytes[i])] = dict_sym.get(chr(bytes[i]), 0) + 1
	return dict_sym


#упорядочивает буквы
def sort_leafs(dict_chars):
	arr = []
	for i in dict_chars:
		arr.append(Vertex(dict_chars[i], i))
	arr.sort()
	return arr


#распределение vertex объектов
def tree_gen(arr):
	while (len(arr) >= 2):
		left = arr.pop(0)
		right = arr.pop(0)
		node = TreeBuilder(left, right)
		arr.append(node)
		arr.sort()
	root_node = arr[0]
	return root_node


#создёет код хаффмана
def huf_func(root, symbol_code='', huffman_code=dict()):
	if type(root.right) is Vertex:
		huffman_code[root.right.symbol] = symbol_code + '1'
	else:
		huffman_code = huf_func(root.right, symbol_code + '1', huffman_code)
	if type(root.left) is Vertex:
		huffman_code[root.left.symbol] = symbol_code + '0'
	else:
		huffman_code = huf_func(root.left, symbol_code + '0', huffman_code)
	return huffman_code


#создаст текст из хаффмана
def huf_text(bytes, huffman):
	text = ''
	for i in bytes:
		ch = chr(i)
		text += huffman[ch]
	return text


#супер функция из интернета которая чето там сделает мне крутое
def rawbytes(letter):
	outlist = []
	for cp in letter:
		num = ord(cp)
		if num < 256:
			outlist.append(struct.pack('B', num))
		elif num < 65535:
			outlist.append(struct.pack('>H', num))
		else:
			b = (num & 0xFF0000) >> 16
			H = num & 0xFFFF
			outlist.append(struct.pack('>bH', b, H))
	return b''.join(outlist)


#буква и её кол-во
def write_header(filename, dict_sym):
	col_letters = (len(dict_sym.keys()) - 1).to_bytes(1, byteorder='little')
	filename.write(col_letters)
	for letter, code in dict_sym.items():
		filename.write(rawbytes(letter))
		filename.write(code.to_bytes(4, byteorder='little'))


#из инета
def get_byte_array(padded_encoded_text):
	if (len(padded_encoded_text) % 8 != 0):
		print("Encoded text not padded")
		exit(0)

	b = bytearray()
	for i in range(0, len(padded_encoded_text), 8):
		byte = padded_encoded_text[i:i + 8]
		b.append(int(byte, 2))
	return b


#паддинг текста по 8
def pad_encoded_text(encoded_text):
	extra_padding = 8 - len(encoded_text) % 8
	for _ in range(extra_padding):
		encoded_text += "0"

	padded_info = "{0:08b}".format(extra_padding)
	encoded_text = padded_info + encoded_text
	return encoded_text


#дописываем текст
def write_text(file, enc_text):
	enc_text_pad = pad_encoded_text(enc_text)
	out = get_byte_array(enc_text_pad)
	file.write(bytes(out))


#архиватор
def compress(myfile):
	bytes = openbytes(myfile)
	dict_sym = symbols_counter(bytes)
	vertex_arr = sort_leafs(dict_sym)
	tree = tree_gen(vertex_arr)
	huffman = huf_func(tree)
	enc_text = huf_text(bytes, huffman)

	file = f"{myfile}.huf"
	f = open(file, 'wb')
	write_header(f, dict_sym)
	write_text(f, enc_text)
	f.close()
	print("Compressed")


#чтение словаря
def read_header(hex):
	letter = hex[0]+1
	header = hex[1:5*letter + 1]
	dict_sym = dict()
	for i in range(letter):
		dict_sym[chr(header[i*5])] = int.from_bytes(header[i*5+1:i*5+5], byteorder='little')
	return dict_sym

#чтение символов
def read_text(hex):
	letter = hex[0]+1
	enc_text = hex[5*letter + 1:]
	return enc_text

#антиархиватор ну или декомпрессионер
def decompress(myfile):
	hex = openbytes("text.txt.huf")

	dict_sym = read_header(hex)
	enc_text = read_text(hex)
	print(dict_sym)
	print(enc_text.decode("utf-8"))
	
	#print("decompressed")

#main
if __name__ == '__main__':
	#print("[c]ompress/[d]ecompress?")
	arg1 = "d"  #input()
	#print("input file")
	arg2 = "text.txt"  #input()
	if (arg1 == "c"):
		compress(arg2)
	elif (arg1 == "d"):
		decompress(arg2)
	else:
		print("error!")
