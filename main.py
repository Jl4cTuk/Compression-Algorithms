#создание словаря для с подсчитанными символами
def symbols_counter(bytes):
    dict_sym = {}
    for i in range(len(bytes)):
        dict_sym[chr(bytes[i])] = dict_sym.get(chr(bytes[i]), 0) + 1
    return dict(sorted(dict_sym.items(), key=lambda item: item[1], reverse=False))

#класс
class Vertex:
	def __init__(self, freq, symbol):
		self.freq = freq
		self.symbol = symbol
		
	def __lt__(self, other):
		b = (self.freq <= other.freq)
		return b

#объндиняет буквы в древо
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
	list_of_leafs = sort_leafs(dict_sym)
	
	print(dict_sym)
	print(list_of_leafs)

#суперская функция которая потом разожмёт
def decompress(myfile):
	hex = openbytes(myfile)
	print(f"{hex} decompressed")

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