
def symbols_counter(hex):
    dict_sym = {}
    for i in range(len(hex)):
        dict_sym[chr(hex[i])] = dict_sym.get(chr(hex[i]), 0) + 1
    return dict(sorted(dict_sym.items(), key=lambda item: item[1], reverse=False))

def openbytes(myfile):
	f = open(myfile, 'rb')
	return f.read()

def compress(myfile):
	hex = openbytes(myfile)
	dict_sym = symbols_counter(hex)
	print(dict_sym)

def decompress(myfile):
	hex = openbytes(myfile)
	print(f"{hex} decompressed")

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