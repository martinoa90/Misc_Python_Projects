from tkinter import Tk, Label, StringVar, Entry, Button, mainloop, ttk, Toplevel
import time
import datetime


def run():
    root = Tk()
    root.geometry('300x300')
    root.title('Take a break!')
    greet = Label(root, text='Rest your eyes, go outside', font=('arial', 16, 'bold')).grid(row=1, columnspan=3)

    def set_timer():
        timer = datetime.datetime.now() + datetime.timedelta(minutes=40)
        print(timer.strftime('%H:%M'))

        if timer != 0:
            root.withdraw()
            getrest(timer)

    def getrest(timer):
        while True:
            time.sleep(10)
            set_time = datetime.datetime.now().strftime('%H:%M')
            # print(set_time)
            # print(timer.strftime('%H:%M'))

            if set_time == timer.strftime('%H:%M'):
                print('Take a rest!')
                root.deiconify()
                break

    button = Button(root, text='OK!', command=set_timer, font=('arial', 16, 'bold')).grid(row=4, column=1)

    mainloop()


if __name__ == '__main__':
    run()
