import os
import filecmp
import huffman
import arithmetic

def take_file():
	file = input("input file:\n")
	if os.path.exists(file):
		return file
	else:
		exit("file not found")

def main():
	method = input("a/h \n")
	option = input("c/d \n")
	file = take_file()
	
	if method == 'h': #huffman
		if option == 'c':
			huffman.compress(file)
		elif option == 'd':
			huffman.decompress(file)
	
	elif method == 'a': #arithmetic
		if option == 'c':
			arithmetic.compress(file)
		elif option == 'd':
			arithmetic.decompress(file)
	
if __name__ == "__main__":
    main()