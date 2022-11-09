#так как символы кодируются в utf-8, то русские буквы где-то там за тысячу и больше в таблице, поэтому пока только те символы, которые есть в ascii

#функция отсортирует кол-во каждого символа по столбикам
def sort(x):
	for i in range(128):
		for j in range(127):
			if x[1][j]>x[1][j+1]:
				tmp=x[1][j]
				x[1][j]=x[1][j+1]
				x[1][j+1]=tmp

				tmp=x[0][j]
				x[0][j]=x[0][j+1]
				x[0][j+1]=tmp
	return x

#функция удалит символы которые используются ноль раз
def removal(x):
	while x[1][0]==0:
			del x[1][0]
			del x[0][0]
	return x

file = open("Text.txt", "r")
text = file.read()
file.close()
symbols = [[0] * 128,[0] * 128]
for i in range(128):
	symbols[0][i] = chr(i)
	
for i in range(len(text)):
	symbols[1][ord(text[i])]+=1

sort(symbols)
removal(symbols)
print(symbols)