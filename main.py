#создание словаря для с подсчитанными символами
def symbols_counter(bytes):
    dict_sym = {}
    for i in range(len(bytes)):
        dict_sym[chr(bytes[i])] = dict_sym.get(chr(bytes[i]), 0) + 1
    return dict(sorted(dict_sym.items(), key=lambda item: item[1], reverse=False))

#класс создать объект с честотой и символом
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

#упорядочивает буквы 
def sort_leafs(dict_chars):
	arr = []
	for i in dict_chars:
		arr.append(Vertex(dict_chars[i], i))
	arr.sort()
	return arr

#чтение файла в байтах
def openbytes(myfile):
	f = open(myfile, 'rb')
	return f.read()

#супер функция которая сжимает
def compress(myfile):
	bytes = openbytes(myfile)
	dict_sym = symbols_counter(bytes)
	print("dict_sym: ", dict_sym)
	vertex_arr = sort_leafs(dict_sym)
	#print("vertex_arr: ", vertex_arr)
	tree = tree_gen(vertex_arr)
	#print("tree: ", tree)
	huffman = huf_func(tree)
	print(huffman)
	#text = encrypt(text, huffman)

#суперская функция которая потом разожмёт
def decompress(myfile):
	hex = openbytes(myfile)
	print(f"{hex} decompressed")

	#прочитать дерево 
	#прочитать текст по дереву
	#записать в файл

#main
if __name__ == '__main__':
	print("[c]ompress/[d]ecompress?")
	arg1 = "c" #input()
	print("input file")
	arg2 = "Text.txt" #input()
	if (arg1 == "c"):
		compress(arg2)
	elif (arg1 == "d"):
		decompress(arg2)
	else:
		print("error!")