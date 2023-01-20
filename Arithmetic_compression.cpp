#include <iostream>
#include <fstream>
#include <unordered_map>
#include <set>
#include <array>
#include <string>
#include <bitset>

using namespace std;

struct comp {
    template<typename T>
    bool operator()(const T &l, const T &r) const
    {
        if (l.second != r.second) {
            return l.second > r.second;
        }
 
        return l.first > r.first;
    }
};

void BitsPlusFollow(int bit, int& bits_to_follow, string& all_bits) {
	if (bit == 1) {
		all_bits += '1';
	}
	else {
		all_bits += '0';
	}
	for (; bits_to_follow > 0; bits_to_follow--) {
		if (bit == 0) {
			all_bits += '1';
		}
		else {
			all_bits += '0';
		}
	}
}

// Кодируем
void compressor(string text, set<pair<char, int>, comp> set, ofstream& file_coded) {
	unordered_map <char, int> ch;	// Первый и второй столбцы таблицы
	unordered_map <int, int> freq_;	// Первый и третий столбцы таблицы
	unordered_map <int, int> b;	// Первый и четвёртый столбцы таблицы
	unordered_map <int, array<int, 2>> boarders;

	bitset<8> code_bit;
	string str, all_bits = "";
	freq_[0] = 0;
	b[0] = 0;
	
	int flag = 0, l = 0, j = 1;
	for (auto pair: set) {
    	ch[pair.first] = j;
		freq_[j] = pair.second;
		b[j++] = l + pair.second;
    	l += pair.second;
	}
    	int i = 0, delitel = b[j-1];
	boarders[0].at(0) = 0;
	boarders[0].at(1) = 65535;
	int First_qtr = (boarders[0].at(1) + 1) / 4;
	int Half = First_qtr * 2;
	int Third_qtr = First_qtr * 3;
	int bits_to_follow = 0;
    	for (char index: text) {
		j = ch[index];
		i++;
		boarders[i].at(0) = boarders[i-1].at(0) + b[j-1] * (boarders[i-1].at(1) - boarders[i-1].at(0) + 1) / delitel;
		boarders[i].at(1) = boarders[i-1].at(0) + b[j] * (boarders[i-1].at(1) - boarders[i-1].at(0) + 1) / delitel - 1;
		for (;;) {
			if (boarders[i].at(1) < Half) {
				BitsPlusFollow(0, bits_to_follow, all_bits);
			}
			else if (boarders[i].at(0) >= Half) {
				BitsPlusFollow(1, bits_to_follow, all_bits);
				boarders[i].at(0) -= Half;
				boarders[i].at(1) -= Half;
			}
			else if (boarders[i].at(0) >= First_qtr && boarders[i].at(1) < Third_qtr) {
				bits_to_follow++;
				boarders[i].at(0) -= First_qtr;
				boarders[i].at(1) -= First_qtr;
			}
			else {
				break;
			}
			boarders[i].at(0) += boarders[i].at(0);
			boarders[i].at(1) += boarders[i].at(1) + 1;
		}
	}
	for (char ch: all_bits) {
		flag++;
		code_bit <<= 1;
		if (flag % 8 == 0) {
			if (ch == '1') {
				code_bit.set(0);
			}
			str += char(code_bit.to_ulong());
			code_bit.reset();
			flag = 0;
		}
		else if (ch == '1') {
				code_bit.set(0);
		}
	}
	flag = 8 - flag;
	if (flag % 8 != 0) {
		for (int i = 0; i < flag; i++) {
			code_bit <<= 1;
		}
	}
	else {
		flag = 0;
	}
	bitset<8> code_flag(flag);
	file_coded << char(code_flag.to_ulong()) << "\n" << str << char(code_bit.to_ulong());
}

// Декодируем
void decompressor(string path) {
	ofstream file_out("out_text.txt");
	ifstream file_coded(path);
	
	unordered_map <int, char> ch;	// Первый и второй столбцы таблицы
	unordered_map <int, int> freq_;	// Первый и третий столбцы таблицы
	unordered_map <int, int> b;	// Первый и четвёртый столбцы таблицы
	unordered_map <int, array<int, 2>> boarders;

	unordered_map <char, int> alphabet;

	int text_power, power;
	char chrct = ' ';
	string code, buffer;
	
	getline(file_coded, buffer);
	text_power = stoi(buffer);
	
	getline(file_coded, buffer);
	if (buffer != "") {
		bitset<8> bit_power(buffer[0]);
		power = (int)(bit_power.to_ulong());
	}
	else {
		power = 10;
	}
	
	// Заполняем map данными из файла-алфавита
	for (int ind = 0; ind < power; ind++) {
		code = "";
		getline(file_coded, buffer);
		bool flag = true;
		for (auto i: buffer) {
			if (flag) {
				chrct = i;
				flag = false;
			}
			else if (!flag && i != ' ') {
				code += i;
			}
		}
		// Обработка символа новой строки (\n)
		if (code == "") {
			chrct = '\n';
			getline(file_coded, buffer);
			for (auto i: buffer) {
				if (i != ' ') {
					code += i;
				}
			}
		}
		if (code != "") {
			alphabet[chrct] = stoi(code);
		}
	}
	set<pair<char, int>, comp> set(alphabet.begin(), alphabet.end());

	getline(file_coded, buffer);
	char last_ch = buffer[0];
	
	ch[0] = NULL;
	freq_[0] = 0;
	b[0] = 0;
	
	int l = 0, j = 1;
	// Заполнение таблицы
	for (auto pair: set) {
    		ch[j] = pair.first;
		freq_[j] = pair.second;
		b[j++] = l + pair.second;
    		l += pair.second;
	}
	
    	int i = 0, delitel = b[j-1];
	boarders[0].at(0) = 0;
	boarders[0].at(1) = 65535;
	int First_qtr = (boarders[0].at(1) + 1) / 4;
	int Half = First_qtr * 2;
	int Third_qtr = First_qtr * 3;

	int value, freq, text_index;
	bitset<16> bit_value;

	getline(file_coded, buffer);
	bitset<8> bit_flag(buffer[0]);
	int flag = (int)(bit_flag.to_ulong());
	
	string text = "";
	while (!file_coded.eof()) {
		getline(file_coded, buffer);
		for (char j: buffer) {
			bitset<8> tmp(j);
			for (int ind = 7; ind >= 0; ind--) {
				if (tmp.test(ind)) {
					text += '1';
				}
				else {
					text += '0';
				}
			}
		}
		bitset<8> tmp('\n');
		for (int ind = 7; ind >= 0; ind--) {
				if (tmp.test(ind)) {
					text += '1';
				}
				else {
					text += '0';
				}
			}
	}
	for (int ind = 7 + flag; ind >= 0; ind--) {
		text.pop_back();
	}
	// Считывание бит первого числа
	for (text_index = 0; text_index < 16; text_index++) {
		if (text[text_index] == '1') {
			bit_value.set(15-text_index);
		}
	}
	value = (int)(bit_value.to_ulong());
    	for (int i = 1; i < text_power; i++) {
		freq = ((value - boarders[i-1].at(0) + 1) * delitel - 1) / (boarders[i-1].at(1) - boarders[i-1].at(0) + 1);
		for (j = 1; b[j] <= freq; j++);	// Поиск символа
		boarders[i].at(0) = boarders[i-1].at(0) + b[j-1] * (boarders[i-1].at(1) - boarders[i-1].at(0) + 1) / delitel;
		boarders[i].at(1) = boarders[i-1].at(0) + b[j] * (boarders[i-1].at(1) - boarders[i-1].at(0) + 1) / delitel - 1;
		// Обрабатываем варианты переполнения
		for (;;) {
			if (boarders[i].at(1) < Half) {;}	// Ничего
			else if (boarders[i].at(0) >= Half) {
				boarders[i].at(0) -= Half;
				boarders[i].at(1) -= Half;
				value -= Half;
			}
			else if ((boarders[i].at(0) >= First_qtr) && (boarders[i].at(1) < Third_qtr)) {
				boarders[i].at(0) -= First_qtr;
				boarders[i].at(1) -= First_qtr;
				value -= First_qtr;
			}
			else {
				break;
			}
			boarders[i].at(0) += boarders[i].at(0);
			boarders[i].at(1) += boarders[i].at(1) + 1;
			bit_value = bitset<16>(value);
			if (text[text_index] == '1') {
				bit_value <<= 1;
				bit_value.set(0);
			}
			else {
				bit_value <<= 1;
			}
			text_index++;
			value = (int)(bit_value.to_ulong());
		}
		file_out << ch[j];
	}
	file_out << last_ch;
	file_out.close();
}

void Alphabet(string text) {
	ofstream file_coded("encoded_text.txt");	// Открываем файл для записи
	// map для сохранения частоты символов
	unordered_map <char, int> freq;
	unordered_map <char, int> alphabet;

	int text_power = 0;
	
	// Подсчитываем частоту символов (циклом ranged-based for)
	for (char ch: text) {
		text_power++;
		freq[ch]++;
		alphabet[ch] = freq[ch];
	}
	
	file_coded << to_string(text_power) << "\n";
	
	int power = 0;
	string str;
	
	set<pair<char, int>, comp> set(alphabet.begin(), alphabet.end());
	for (auto const &pair: set) {
		power++;
        	str += pair.first;
		str += ' ';
		str += to_string(pair.second);
		str += "\n";
    	}
	bitset<8> bit_power(power);
	file_coded << (char)(bit_power.to_ulong()) << "\n" << str;

	file_coded << text[text.length()-1] << "\n";
	
	compressor(text, set, file_coded);
	cout << "\nFile was succesfully encoded.\n";

	file_coded.close();	// Закрываем файл
}

int main() {
	string text, tmp, path, act;
	// Запрашиваем путь к файлу (сам файл, если он находится в одной директории с исполняемой программой)
	cout << "Please, enter the path to the file: ";
	cin >> path;
	ifstream file_in(path);	// Открываем файл для чтения
	// Проверяем, существует ли файл/открыт ли к нему доступ
	if(!file_in) {
		cout << "\nThe file does not exist or access to it is denied. Please, try again.\n";
		return 0;
	}
	// Запрашиваем действие, которое необходимо выполнить
	cout << "\nYou will not be able to decode the file without its primary encoding!\n\nEnter 1 if you want to encode file, enter 2 in other way: ";
	cin >> act;
	// Проверяем, корректно ли введён индекс действия
	if (act != "1" && act != "2") {
		cout << "\nAn incorrect value was entered. Please, try again.\n";
		return 0;
	}
	// Выполняем кодирование (если поступил соотв. запрос)
	if (act == "1") {
		// Пока не достигли конца файла, построчно считываем данные
		while (!file_in.eof()) {
			getline(file_in, tmp);	// Т.к. функция getline() считывает до символа конца строки,
			text += tmp + '\n';	// Не включая их, дополняем текст этим элементом
		};
		file_in.close();	// Закрываем файл
		text.pop_back();	// Исключаем лишний символ конца строки (\n)
		Alphabet(text);
	}
	// Выполняем декодирование
	else if (act == "2") {	
		// Выполняем декодирование текста
		decompressor(path);
		cout << "\nFile was succesfully decoded.\n";
	}
  return 0;
}