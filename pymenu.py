import os
from tkinter import ttk, Tk, StringVar
from tkinter import LEFT
from os.path import isfile, splitext, join
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple


Option = namedtuple('Option', ('full_paht', 'name'))


def load_files(path, index):
    files = []
    try:
        entries = os.listdir(path)
    except FileNotFoundError as err:
        return []
    except Exception as another:
        return []
    else:
        for entry in entries:
            if isfile(join(path, entry)):
                __, ext = splitext(entry)
                if ext.lower() in ['.exe', '.bat', 'cmd']:
                    files.append(Option(
                        join(path, entry),
                        entry,
                    ))
        return files


OPTIONS = []


def get_options():
    global OPTIONS
    if OPTIONS:
        return OPTIONS

    path_list = os.getenv('PATH').split(';')
    with ThreadPoolExecutor() as executor:
        results = []
        for index, path in enumerate(path_list):
            resp = executor.submit(load_files, path=path, index=index)
            results.append(resp)
        for res in results:
            for i in res.result():
                OPTIONS.append(i)

    return OPTIONS


def create_option_cmd(option):

    def callback():
        import subprocess
        subprocess.Popen([option.name])

    return callback


def main():

    root = Tk()
    root.title('pymenu')
    root.geometry('1920x30')

    input_value = StringVar()

    frame = None

    def on_input_changed(name, index, mode):
        i = 0

        for widget in frame.winfo_children():
            widget.destroy()

        for option in get_options():
            if option.name.lower().startswith(input_value.get().lower()):
                btn = ttk.Button(frame, text=option.name,
                                 command=create_option_cmd(option))
                btn.pack(side=LEFT)
                i += 1
            if i > 10:
                break

    input_value.trace('w', on_input_changed)

    entry = ttk.Entry(root, textvariable=input_value)
    entry.pack(side=LEFT)

    frame = ttk.Frame(root)

    for option in get_options():
        btn = ttk.Button(frame, text=option.name,
                         command=create_option_cmd(option))
        btn.pack(side=LEFT)

    frame.pack(side=LEFT)

    def enter_clicked(argument):
        for c in frame.winfo_children():
            c.invoke()
            break
        else:
            import subprocess
            subprocess.Popen([entry.get()])

    root.bind('<Return>', func=enter_clicked)
    root.bind('<Escape>', func=lambda e: print('min to tray'))

    root.mainloop()


if __name__ == '__main__':
    main()
