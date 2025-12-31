class Console(ScrolledText):
    '''
    Console class for the output window
    '''

    def __init__(self, console, height=25, width=70):
        super().__init__(console, state='disabled', wrap=tkinter.WORD, height=height, width=width)
        #self.scrollarea = ScrolledText(self.console, state='disabled', wrap=tkinter.WORD, height=25, width=70)
        self.grid(column=0)
        self.tag_config('normal', foreground="#000000")
        self.tag_config('success', foreground="#13D60C")
        self.tag_config('error', foreground="#FF0000")
        self.tag_config('warn', foreground="#FFB217")
    
    def clear(self):
        '''
        reset the console to default
        '''

        self.configure(state='normal')
        self.delete('1.0', tkinter.END)
        self.print("--------------------------------------------------------------------",1)
        self.print("Camera Calibrator App\n\nCreated by dan1elw.\nhttps://github.com/dan1elw\nCopyright 2022. Version {}".format(self.VERSIONINDEX),1)
        self.print("--------------------------------------------------------------------\n",1)
        self.print("Time: {}\n".format(time.strftime('%d.%m.%Y , %H:%M Uhr')))
        self.configure(state='disabled')
        self.update()

    def print(self, text, pause=1, format='normal'):
        '''
        function to plot some formatted text into the console.
        '''

        self.configure(state='normal')
        if text[:7] == '[ERROR]':
            self.insert(tkinter.END, text, 'error')
        else:
            self.insert(tkinter.END, text, format)
        self.insert(tkinter.END, '\n')
        self.configure(state='disabled')
        self.yview(tkinter.END)
        self.update()
        
        # waiting a little bit for smoother output
        if pause == 1:
            self.timestopper += 1
            time.sleep(self.timepause)
