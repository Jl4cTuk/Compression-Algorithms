file = open("Text.txt", "r")
text = file.read()
file.close()
#print(text)
symbols = [0] * 127,[0] * 127
for i in range(127):
	symbols[0][i] = chr(i)
for i in range(len(text)):
	symbols[1][ord(text[i])]+=1

print(symbols)