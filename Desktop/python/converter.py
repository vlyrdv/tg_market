from tkinter import *
import math

def convert():
    try:
        result=float(pay.get())*float(eur.get())\
            /float(kzt.get())*float(usdt.get())
    except ValueError as err:
        print(err)
        count.config(text="Ошиблись с ссоде. Используйте точку для нецелых чисел и не вводите буквы")
    else:
        count.config(text=str(result))

root = Tk()

Label(text="Курс USDT-RUB(Тинькофф, покупка):")\
    .grid(row=0, column=0, sticky=W, padx=15, pady=10)
usdt=Entry(width=15)
usdt.grid(row=0, column=1, padx=5, sticky=W)

Label(text="Курс USDT-KZT(Евразийский, продажа):")\
    .grid(row=1, column=0, sticky=W, padx=15, pady=10)
kzt=Entry(width=15)
kzt.grid(row=1, column=1, padx=5, sticky=W )

Label(text="Курс KZT-EUR(Евразийский, покупка):")\
    .grid(row=2, column=0, sticky=W, padx=15, pady=10)
eur=Entry(width=15)
eur.grid(row=2, column=1, padx=5, sticky=W)

Label(text="Сумма покупки(в евро):")\
    .grid(row=3, column=0, sticky=W, padx=15, pady=10)
pay=Entry(width=15)
pay.grid(row=3, column=1)

Label(text="Стоимость(в рублях):")\
    .grid(row=4, column=0, sticky=W, padx=15, pady=10)
count=Label(text="0.0")
count.grid(row=4, column=1, padx=5, sticky=W)

Button(text="Рассчитать", command=convert)\
    .grid(row=5, columnspan=2, sticky=E, padx=5, pady=10)

root.mainloop()
