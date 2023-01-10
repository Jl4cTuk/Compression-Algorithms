from collections import Counter

def compress(file):
	
	filein = open(file, 'r')
	s = filein.read()
	
	dict = {}
	p = []
	list = ""
	for ch, freq in Counter(s).items():
		dict[ch] = freq
		p.append(dict[ch]/len(s))
		list+=ch
	
	#запись
	f = open("enc_aric", 'wb')
	f.write(len(s).to_bytes(4, 'big'))
	f.write(len(dict).to_bytes(2, 'big'))
	for ch in dict:
		f.write(ch.encode())
		f.write(dict[ch].to_bytes(2, 'big'))
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

