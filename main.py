import struct
import os

def file_exists(filename):
	filepath = os.path.join(filename)
	return os.path.isfile(filepath)


class Vertex:

	def __init__(self, freq, symbol):
		self.freq = freq
		self.symbol = symbol

	def __lt__(self, other):
		b = (self.freq <= other.freq)
		return b


class TreeBuilder:

	def __init__(self, right, left):
		self.freq = right.freq + left.freq
		self.right = right
		self.left = left

	def __lt__(self, other):
		return self.freq <= other.freq


def openbytes(myfile):
	f = open(myfile, 'rb')
	return f.read()

def symbols_counter(bytes):
	dict_sym = {}
	for i in range(len(bytes)):
		dict_sym[chr(bytes[i])] = dict_sym.get(chr(bytes[i]), 0) + 1
	return dict_sym


def sort_leafs(dict_chars):
	arr = []
	for i in dict_chars:
		arr.append(Vertex(dict_chars[i], i))
	arr.sort()
	return arr


def tree_gen(arr):
	while (len(arr) >= 2):
		left = arr.pop(0)
		right = arr.pop(0)
		node = TreeBuilder(left, right)
		arr.append(node)
		arr.sort()
	root_node = arr[0]
	return root_node


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


def huf_text(bytes, huffman):
	text = ''
	for i in bytes:
		ch = chr(i)
		text += huffman[ch]
	return text


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


def write_symbols(filename, dict_sym):
	col_letters = (len(dict_sym.keys()) - 1).to_bytes(1, byteorder='little')
	filename.write(col_letters)
	for letter, code in dict_sym.items():
		filename.write(rawbytes(letter))
		filename.write(code.to_bytes(4, byteorder='little'))


def get_byte_array(padded_encoded_text):
	if (len(padded_encoded_text) % 8 != 0):
		print("Encoded text not padded")
		exit(0)

	b = bytearray()
	for i in range(0, len(padded_encoded_text), 8):
		byte = padded_encoded_text[i:i + 8]
		b.append(int(byte, 2))
	return b


def pad_encoded_text(encoded_text):
	extra_padding = 8 - len(encoded_text) % 8
	for _ in range(extra_padding):
		encoded_text += "0"

	padded_info = "{0:08b}".format(extra_padding)
	encoded_text = padded_info + encoded_text
	return encoded_text


def write_text(file, enc_text):
	enc_text_pad = pad_encoded_text(enc_text)
	out = get_byte_array(enc_text_pad)
	file.write(bytes(out))


def compress(myfile): #архивировалка
	
	#открыть файл
	bytes = openbytes(myfile)
	
	#создание словаря
	dict_sym = symbols_counter(bytes)
	
	#создаём вершины
	vertex_arr = sort_leafs(dict_sym)
	
	#создание дерева и взятие корня
	tree = tree_gen(vertex_arr)
	
	#создание кодов хаффмана
	huffman = huf_func(tree)
	
	#создание двоичной последовательности текста
	enc_text = huf_text(bytes, huffman)

	#имя файла
	file = f"{myfile}.huf"

	#открыть новый файл
	f = open(file, 'wb')
	
	#запись символа и его количества
	write_symbols(f, dict_sym)
	
	#запись двоичной последовательности в байты
	write_text(f, enc_text)
	
	#закрыть
	f.close()


#чтение словаря
def read_symbols(hex):
	letter = hex[0]+1
	header = hex[1:5*letter + 1]
	dict_sym = dict()
	for i in range(letter):
		dict_sym[chr(header[i*5])] = int.from_bytes(header[i*5+1:i*5+5], byteorder='little')
	return dict_sym

def read_text(input):
	col_letters = input[0]+1
	enc_text_pad = input[5*col_letters + 1:]
	return enc_text_pad

def to_binary(enc_text):
	result = ''
	for i in enc_text:
		bin_byte = bin(i)[2:].rjust(8, '0')
		result += bin_byte
	return result

def remove_padding(padded_text):
	padded_info = padded_text[:8]
	extra_padding = int(padded_info, 2)
	padded_text = padded_text[8:]
	binary_text = padded_text[:-1*extra_padding]
	return binary_text

def huf_to_text(bin_encoded_text, inv_huffman_codes):
	text = ''
	next_code = ''
	for bit in bin_encoded_text:
		next_code += bit
		if (next_code in inv_huffman_codes.keys()):
			text += inv_huffman_codes[next_code]
			next_code = ''
	return text
	
def decompress(myfile): #разархивировалка
	
	#чтение байтов
	hex = openbytes("text.txt.huf")
	
	#создание словаря
	dict_sym = read_symbols(hex)

	#создание вершин
	vertex_arr = sort_leafs(dict_sym)
	
	#создание дерева
	tree = tree_gen(vertex_arr)

	#создание кодов хаффмана
	huffman = huf_func(tree)

	#чтение закодированного текста
	enc_text = read_text(hex)

	#переделывание в бинарьку
	binary = to_binary(enc_text)

	#убирание паддинга
	binary_text = remove_padding(binary)

	#меняем местами код и букву
	#huffman = {v: k for k, v in huffman.items()}
	#print(huffman)

	inv_huffman = {v: k for k, v in huffman.items()}
	#print(inv_huffman)
	
	#ну и всё, расшифровываем текст и GG
	text = huf_to_text(binary_text, inv_huffman)

	#расшифрованный файл
	file = f"{myfile}"[:-4]

	#файл
	f = open(file, 'wb')

	#запись
	f.write(rawbytes(text))
	
	f.close()

if __name__ == '__main__':
	print("[c]ompress/[d]ecompress?")
	arg1 = input()
	
	#проверка параметра
	if not(arg1 == "c" or arg1 == "d"):
		print("wrong parameter")
		exit(1)
		
	print("input file")
	arg2 = input()

	#проверка файла
	if not(file_exists(arg2)):
		print("file not found!")
		exit(1)

	#вызов нужной функции
	if (arg1 == "c"):
		compress(arg2)
	elif (arg1 == "d"):
		decompress(arg2)
			
	