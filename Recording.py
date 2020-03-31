import pyaudio
import tkinter as tk
import wave
import threading
import os

class Application():
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 2
    fs = 44100


    def __init__(self, master, topicsname):
        self.topicsname = topicsname
        self.sentence = []
        self.url = None
        self.current_sentence = -1
        self.isRecording = False
        self.file_output = None


        # Tạo nút Record/ Stop/ Chuyển câu
        self.frame = tk.Frame(main)
        self.butrecord = tk.Button(self.frame, text = 'Record', command = self.startRecord)
        self.butstop = tk.Button(self.frame, text = 'Stop', command = self.stopRecord)
        self.butnext = tk.Button(self.frame, text='Câu tiếp theo', command=self.nextSentence)
        self.butrecord.grid(row = 0, column = 0)
        self.butstop.grid(row = 1, column = 0, pady = 5)
        self.butnext.grid(row=2, column=0, pady=5)



        self.label1 = tk.Label(main, text = '\nChọn chủ đề, sau đó nhấn Record và đọc diễn cảm. Nhấn Stop khi đọc hết câu.')
        self.label2 = tk.Label(main,text = 'Đọc diễn cảm câu sau đây:')
        self.sentenceLabel = tk.Label(main,text = '', wraplength = 500)
        self.status = tk.Label(main, text = '')
        self.warning = tk.Label(main, text = '')


        #Tạo nút chọn chủ đề
        self.topic = tk.StringVar(main)
        self.topic.set('Chọn chủ đề')
        self.popupMenu = tk.OptionMenu(main, self.topic, *topicsname)
        self.topic.trace('w', self.TopicChange)

        #Packing
        self.label1.pack()
        self.popupMenu.pack()
        self.label2.pack()
        self.sentenceLabel.pack()
        self.frame.pack()
        self.status.pack()
        self.warning.pack()


    def startRecord(self):
        topicsname = self.topic.get()
        if topicsname == 'Chọn chủ đề':
            self.warning['text'] = 'Chọn chủ đề trước khi nhấn Record!'
            #self.warning['text'] = ''
            return
        self.p = pyaudio.PyAudio()
        self.frame = []
        self.isRecording = True
        self.stream = self.p.open(format = self.sample_format, channels = self.channels, rate = self.fs, frames_per_buffer = self.chunk, input = True)
        self.status['text'] = 'Đang ghi'
        while self.isRecording:
            data = self.stream.read(self.chunk)
            self.frame.append(data)
            main.update()
        self.stream.close()



    def stopRecord(self):
        if self.isRecording == False:
            return
        self.isRecording = False
        self.status['text'] = 'Hoàn tất ghi'
        self.warning['text'] = ''

        topicsname = self.topic.get()

        wf = wave.open('/'.join(['Output', topicsname, str(self.current_sentence) + '.wav']), 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frame))
        wf.close()

        #Điền dữ liệu vào file "Output.txt":


    def nextSentence(self):
        topicsname = self.topic.get()
        if topicsname == 'Chọn chủ đề':
            return
        if self.current_sentence >= len(self.sentence) -1:
            self.status['text'] = 'Hết!'
            self.file_output.close()
            return

        if self.isRecording:
            self.warning['text'] = 'Đang ghi! Nhấn Stop để dừng lại trước khi chuyển sang câu tiếp theo'
            return
        #Điền dữ liệu vào file "Output.txt"
        self.file_output.write(str(self.current_sentence) + '.wav\n')
        self.file_output.write(self.sentence[self.current_sentence])

        #Next câu
        self.current_sentence += 1
        self.status['text'] = ''
        self.sentenceLabel['text'] = self.sentence[self.current_sentence]


    def  TopicChange(self, *args):
        topicsname = self.topic.get()
        file = open("/".join(['Data', topicsname, 'data.txt']), 'r', encoding='utf-8')
        self.url = file.readline()
        self.sentence = file.readlines()
        self.current_sentence = -1
        file.close()
        #print(self.url + '\n')

        output_folder = "/".join(["Output", topicsname])
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        self.file_output = open('/'.join(['Output',topicsname, 'Output.txt']), 'w', encoding='utf-8')

        self.file_output.write(self.url)
        #self.file_output.close()
        self.current_sentence = 0
        self.sentenceLabel['text'] = self.sentence[self.current_sentence]
        self.warning['text'] = ''

#Danh sách các chủ đề
topicsname = []
for (paths, dirs, files) in os.walk('Data/.'):
    for dirname in dirs:
        topicsname.append(dirname)

main = tk.Tk()
main.title('Recorder')
main.geometry('800x300')
app = Application(main, topicsname)
main.mainloop()