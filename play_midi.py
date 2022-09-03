from mido import Message, MidiFile, MidiTrack
import pygame
 
 
def play_midi(file):
   freq = 44100
   bitsize = -16
   channels = 2
   buffer = 1024
   pygame.mixer.init(freq, bitsize, channels, buffer)
   pygame.mixer.music.set_volume(1)
   clock = pygame.time.Clock()
   try:
       pygame.mixer.music.load(file)
   except:
       import traceback
       print(traceback.format_exc())
   pygame.mixer.music.play()
   while pygame.mixer.music.get_busy():
       clock.tick(30)

def play_note(note, length, track, base_num=0, note_bias=0, delay=0, velocity=1.0, channel=0):
    # meta_time与bpm值有关，但为了适应x studio的使用改为定值
    meta_time = 60 * 32
    # 不同音符升key所升的音不同（如3-4升半音，1-2升全音）
    major_notes = [0, 2, 2, 1, 2, 2, 2, 1]
    base_note = 60
    track.append(
        Message('note_on', note=base_note + note_bias + base_num * 12 + sum(major_notes[0:note]), velocity=round(64 * velocity),
                time=round(delay * meta_time), channel=channel))
    track.append(
        Message('note_off', note=base_note + note_bias + base_num * 12 + sum(major_notes[0:note]), velocity=round(64 * velocity),
                time=round(meta_time * length), channel=channel))

if __name__ == "__main__":
    mid = MidiFile()  # 创建MidiFile对象
    track = MidiTrack()  # 创建音轨
    mid.tracks.append(track)  # 把音轨加到MidiFile对象中
    # bpm = int(input("请输入bpm："))
    
    # 向音轨添加
    #    Message对象（包括program_change、note_on、note_off等）
    #    MetaMessage对象（用以表示MIDI文件的节拍、速度、调式等属性）
    track.append(Message('program_change', program=12, time=0))
    
    monitor = ""
    pitch_list = ["超低音","倍低音","低音","中音","高音","倍高音","超高音"]
    note_symbol_list = ["1/64","1/32","1/16","1/8","1/4","1/2","1/1"]
    note_list = ['0','1','2','3','4','5','6','7'] # 0为空音符,仅占位
    command_list = ["w","a","s","d","q","bk"]  #用于控制音高(w s)、音符长度(a d)、退出程序(q)、回退(bk)
    bias_symbol_list = ['#','b','-','*','.']  #从左向右分别是升半音、降半音、延长一个音、延长半个音、缩短1/2音
    
    pitch_num = 3 #初始为中音
    note_symbol_num = 4 #初始为四分音符

    note_infos = [] #暂时性储存音符，方便删改
    delay = 0 #表示与前一音符的间距
    while monitor != "q":
        pitch = pitch_list[pitch_num]
        note_symbol = note_symbol_list[note_symbol_num]
        note_bias = 0
        length_scale = 1
        wrong_info = "格式错误(见readme)，请重新输入或键入q退出："
        monitor = input(f"({note_symbol}-{pitch})请输入音符：")
        if len(monitor)>4 or len(monitor)==0:
            print(wrong_info)
            continue
        if monitor in command_list:
            if monitor == "w" and pitch_num<len(pitch_list)-1:
                pitch_num += 1
            if monitor == "s" and pitch_num>0:
                pitch_num -= 1
            if monitor == "d" and note_symbol_num<len(note_symbol_list)-1:
                note_symbol_num += 1
            if monitor == "a" and note_symbol_num>0:
                note_symbol_num -= 1
            if monitor == "q":
                break
            if monitor == "bk":
                try:
                    note_infos.pop()
                    print("回到上一步")
                except IndexError:
                    print("上一步为空！")
            continue
        while monitor[0] in bias_symbol_list or monitor[-1] in bias_symbol_list:
            if monitor[0] in bias_symbol_list:
                bias_symbol = monitor[0]
            else:
                bias_symbol = monitor[-1]
            monitor = monitor.replace(bias_symbol,"",1) # 删除该特殊符号(仅一次)，方便下一步提取音符
            if bias_symbol == '#':
                note_bias = 1
            if bias_symbol == 'b':
                note_bias = -1
            if bias_symbol == '-':
                length_scale *= 2
            if bias_symbol == '*':
                length_scale *= 1.5
            if bias_symbol == '.':
                length_scale *= 0.5
        if monitor in note_list:
            note = int(monitor)
            length = pow(0.5,len(note_symbol_list)-1-note_symbol_num)*length_scale
            base_num = pitch_num - 3
            if note == 0:
                delay += length
            else:
                note_infos.append((note,length,track,base_num,note_bias,delay))
                delay = 0
        else:
            print(wrong_info)
    # 将音符信息写入音轨
    for note_info in note_infos:
        note,length,track,base_num,note_bias,delay = note_info
        play_note(note,length,track,base_num,note_bias,delay)
    print("已手动停止！")
    judge = input("是否保存（y/n）？")
    if judge == "y":
        name = input("请输入文件名：")
        mid.save(name+".mid")
        print("已成功保存.")
    judge = input("是否播放（y/n）？")
    if judge == 'y':
        play_midi(name+".mid")