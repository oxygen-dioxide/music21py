import music21
import musicpy

#===================music21转musicpy===================

def m21_pitch_Pitch_to_mpy(m21pitch:music21.pitch.Pitch)->musicpy.note:
    """将music21音高转换为musicpy音符"""
    #musicpy对音名的支持，仅限于无变调符号的7个白键，以及用单个变调符号表示的5个黑键。
    if(m21pitch.name in musicpy.standard):
        if(m21pitch.octave==None):
            #music21音高可以没有八度号，默认为4
            octave=m21pitch.defaultOctave
        else:
            octave=m21pitch.octave
        return musicpy.note(m21pitch.name,octave)
    #如果不支持，则用midi号来转换，只保留实际音高信息
    else:
        return musicpy.note("C",4)+(m21pitch.midi-60)

def m21_note_Note_to_mpy(m21note:music21.note.Note)->musicpy.note:
    """将music21音符转换为musicpy音符"""
    mpynote=m21_pitch_Pitch_to_mpy(m21note.pitch)
    mpynote.duration=m21note.quarterLength/4
    return mpynote

def m21_stream_Stream_to_mpy(m21stream:music21.stream.Stream)->musicpy.track:
    """将music21 Stream转换为musicpy track"""
    #这里使用track而不是chord，因为chord不支持开头休止符的情况
    mpynotes=[]
    mpyinterval=[0]
    for m21obj in m21stream.flatten():
        if(type(m21obj)==music21.note.Note):
            mpynotes.append(m21_note_Note_to_mpy(m21obj))
            mpyinterval.append(m21obj.quarterLength/4)
        elif(type(m21obj)==music21.note.Rest):
            mpyinterval[-1]+=m21obj.quarterLength/4
    mpychord=musicpy.chord(mpynotes,interval=mpyinterval[1:])
    return musicpy.track(content=mpychord,start_time=mpyinterval[0])

def m21_to_mpy(m21obj):
    return {
        music21.pitch.Pitch:m21_pitch_Pitch_to_mpy,
        music21.note.Note:m21_note_Note_to_mpy,
        music21.stream.Stream:m21_stream_Stream_to_mpy,
        }[type(m21obj)](m21obj)

#===================musicpy转music21===================

def mpy_note_to_m21(mpynote:musicpy.note)->music21.note.Note:
    return music21.note.Note(str(mpynote).title().replace("b","-"),duration=music21.duration.Duration(mpynote.duration*4))

def mpy_chord_to_m21(mpychord:musicpy.chord,start_time=0)->music21.stream.Stream:
    m21stream=music21.stream.Stream()
    time=start_time
    for (note,interval) in zip(mpychord,mpychord.interval):
        m21stream.insert(time,mpy_note_to_m21(note))
        time+=interval*4
    return m21stream.chordify()

def mpy_track_to_m21(mpytrack:musicpy.track)->music21.stream.Stream:
    return mpy_chord_to_m21(mpytrack.content,start_time=mpytrack.start_time)

def mpy_to_m21(mpyobj):
    return {
        musicpy.note:mpy_note_to_m21,
        musicpy.chord:mpy_chord_to_m21,
        musicpy.track:mpy_track_to_m21,
        }[type(mpyobj)](mpyobj)