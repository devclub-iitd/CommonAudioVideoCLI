import tkinter
import subprocess
from tkinter import filedialog, messagebox
import os
import pyqrcode


def clip_filename_with_extension(filename):
    """ clips long file names """

    clipped = filename[filename.rfind('/')+1:]
    if(len(clipped) > 15):
        clipped = clipped[:6] + '...' + clipped[clipped.rfind('.')-4:]
    return clipped


def select_vid_file():
    """ Presents file dialog box to select .mp4/.mkv files """

    global curr_dir
    # print(curr_dir)
    global vid_filename

    filename = filedialog.askopenfilename(
        initialdir=curr_dir, title="Select Video File",
        filetypes=[("Video", ".mp4 .mkv")]
    )
    if(filename.endswith('.mp4') or filename.endswith(".mkv")):
        vid_filename = filename
        video_btn["text"] = clip_filename_with_extension(vid_filename)
    else:
        if(len(vid_filename) > 0):
            pass
        else:
            video_btn["text"] = 'Choose File'


def select_sub_file():
    """ Presents file dialog box to select .srt files """

    global curr_dir
    global sub_filename

    filename = filedialog.askopenfilename(
        initialdir=curr_dir, title="Select Subtitle File",
        filetypes=[("Subtitle", ".srt")]
    )
    if(filename.endswith('.srt')):
        sub_filename = filename
        sub_btn["text"] = clip_filename_with_extension(sub_filename)
    else:
        if(len(sub_filename) > 0):
            pass
        else:
            sub_btn["text"] = 'Choose File'


def change_sub_state():
    """ Enable/Disable subtitle file """

    state = allow_sub.get()
    if(state):
        sub_btn["state"] = tkinter.NORMAL
    else:
        sub_btn["state"] = tkinter.DISABLED


def run_checks_before_play():
    """ File selection checks before calling CLI """

    global vid_filename, sub_filename
    if(
        not(vid_filename.endswith(".mp4"))
        and not(vid_filename.endswith(".mkv"))
    ):
        return 1
    if(allow_sub.get() and not(sub_filename.endswith(".srt"))):
        return 2
    return 0


def generate_qr():
    """ Generates QR code for room link """

    global link
    global photo, qrImage, myQr
    print(link)
    top = tkinter.Toplevel()
    top.title('QR Code')
    qr_lbl = tkinter.Label(top)
    myQr = pyqrcode.create(link)
    qrImage = myQr.xbm(scale=6)
    photo = tkinter.BitmapImage(data=qrImage)
    qr_lbl.config(image=photo, state=tkinter.NORMAL)
    qr_lbl.pack()


def copy_link():
    """ Copies room link to clipboard """

    global link
    root.clipboard_append(link)
    copy_link_btn["text"] = "Link Copied!"


def retrieve_link(bash_command):
    """ Gets room link retrieved from the CLI """

    import tkinter
    global link
    global curr_dir
    print(curr_dir)
    subprocess.Popen(bash_command)
    while(not os.path.exists(curr_dir + '/invite_link.txt')):
        root.after(2000)
    f = open('invite_link.txt', 'r')
    link = f.readline()
    print(link)
    f.close()
    os.remove('invite_link.txt')
    tkinter.messagebox.showinfo(
        'Success',
        'Room Creation Successful! Share the link or scan the QR to join!'
    )
    success_lbl.config(
        text='Share this link and enjoy: ' + link, state=tkinter.NORMAL
    )
    success_lbl.config(font=("Courier", 14))
    success_lbl.grid(row=7, column=0, columnspan=6)
    copy_link_btn.config(state=tkinter.NORMAL)
    copy_link_btn.grid(row=8, column=0, columnspan=3, sticky=tkinter.E)
    qr_gen_btn["state"] = tkinter.NORMAL
    qr_gen_btn.grid(row=8, column=3, columnspan=3, sticky=tkinter.W)


def play():
    """ Gathers widget configurations to create CLI command """

    global curr_dir, vid_filename, sub_filename
    err_status = run_checks_before_play()
    if(err_status == 0):
        bash_command = []
        bash_command.append('python3')
        bash_command.append(curr_dir + 'cli/main.py')
        bash_command.append('-f')
        bash_command.append(vid_filename)
        if(allow_sub.get()):
            bash_command.append('-s')
            bash_command.append(sub_filename)

        if(not server.get()):
            bash_command.append('--web')

        bash_command.append('--audio-quality')
        quality = audio_quality.get()
        if(quality == 0):
            bash_command.append('low')
        elif(quality == 1):
            bash_command.append('medium')
        elif(quality == 2):
            bash_command.append('high')
        '''
        if(show_qr.get()):
            bash_command.append('--qr')
        '''
        if(host_control.get()):
            bash_command.append('--control')
        print(bash_command)
        for widget in root.winfo_children():
            widget["state"] = tkinter.DISABLED
        retrieve_link(bash_command)

    elif(err_status == 1):
        tkinter.messagebox.showerror("ERROR", "No video file chosen")
    elif(err_status == 2):
        tkinter.messagebox.showerror("ERROR", "No subtitle file chosen")
    else:
        tkinter.messagebox.showerror("ERROR", "An error occurred")


def on_closing():
    """ Confirms session closing """

    if messagebox.askokcancel(
        "Quit", "Closing this window will stop this session." +
        "Are you sure you want to quit?"
    ):
        root.destroy()


if __name__ == '__main__':
    global curr_dir
    curr_dir = __file__
    curr_dir = curr_dir[:curr_dir.rfind('gui/main.py')]
    curr_dir = subprocess.run(
        'pwd', capture_output=True, text=True
        ).stdout.strip() + '/' + curr_dir

    # Create root window
    root = tkinter.Tk()
    root.title('Common Audio Video GUI')

    # Remove previously created links
    if(os.path.exists('invite_link.txt')):
        os.remove('invite_link.txt')

    # Place welcome label
    wlcm_lbl = tkinter.Label(
        root, text='Welcome to Common Audio Video Host GUI!'
    )

    wlcm_lbl.grid(row=0, column=0, columnspan=5)

    # Video File Selection
    global vid_filename
    vid_filename = ''
    video_btn = tkinter.Button(
        root, text='Select Video File', command=select_vid_file
    )

    video_btn.grid(row=1, column=0, columnspan=5)

    # Subtitle File Check
    allow_sub = tkinter.IntVar()
    check_sub = tkinter.Checkbutton(
        root, text="Add subtitles:", command=change_sub_state,
        variable=allow_sub, onvalue=1, offvalue=0
        )
    check_sub.deselect()

    check_sub.grid(row=2, column=0, columnspan=2, sticky=tkinter.E)

    # Subtitle File Selection
    global sub_filename
    sub_filename = ''
    sub_btn = tkinter.Button(
        root, text='Choose File',
        command=select_sub_file, state=tkinter.DISABLED
    )

    sub_btn.grid(row=2, column=2, columnspan=3, sticky=tkinter.W)

    # Server Selection
    server = tkinter.IntVar()
    server.set(0)
    radio_server_web = tkinter.Radiobutton(
        root, text="Web", variable=server, value=0
    )
    radio_server_local = tkinter.Radiobutton(
        root, text="Local", variable=server, value=1
    )

    tkinter.Label(root, text='Server: ').grid(row=3, column=0, columnspan=2)
    radio_server_web.grid(row=3, column=2)
    radio_server_local.grid(row=3, column=3)

    # Audio Quality Selection
    audio_quality = tkinter.IntVar()
    audio_quality.set(1)

    radio_quality_low = tkinter.Radiobutton(
        root, text="Low", variable=audio_quality, value=0
    )
    radio_quality_medium = tkinter.Radiobutton(
        root, text="Medium", variable=audio_quality, value=1
    )
    radio_quality_high = tkinter.Radiobutton(
        root, text="High", variable=audio_quality, value=2
    )

    quality_lbl = tkinter.Label(root, text='Audio Quality: ')
    quality_lbl.grid(row=4, column=0, columnspan=2)
    radio_quality_low.grid(row=4, column=2)
    radio_quality_medium.grid(row=4, column=3)
    radio_quality_high.grid(row=4, column=4)

    # Control
    host_control = tkinter.IntVar()
    check_control = tkinter.Checkbutton(
        root, text="Only host can control", variable=host_control,
        onvalue=1, offvalue=0
    )
    check_control.deselect()

    check_control.grid(row=5, column=0, columnspan=5)

    '''
    # Show QR
    show_qr = tkinter.IntVar()
    check_qr = tkinter.Checkbutton(
        root, text="Show QR", variable=show_qr, onvalue=1, offvalue=0
    )
    check_qr.select()

    check_qr.grid(row=5, column=3, columnspan=2)
    '''

    # Play Button
    play_btn = tkinter.Button(root, text="PLAY!", command=play)

    play_btn.grid(row=6, column=0, columnspan=5)

    # Post room creation options
    success_lbl = tkinter.Label(root)
    copy_link_btn = tkinter.Button(root, text="Copy Link", command=copy_link)
    qr_gen_btn = tkinter.Button(root, text="Generate QR", command=generate_qr)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
