__version__=="0.0.1"

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

def m21_tempo_MetronomeMark_to_mpy(m21metro:music21.tempo.MetronomeMark)->musicpy.tempo:
    """将musicpy曲速对象转换为music21曲速对象"""
    return musicpy.tempo(m21metro.number)

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
    #如果是part类型，则把m21stream.partName作为musicpy.track的track_name
    return musicpy.track(content=mpychord,start_time=mpyinterval[0],track_name=getattr(m21stream,'partName',None))

def m21_stream_Score_to_mpy(m21score:music21.stream.Score)->musicpy.piece:
    """将music21多轨工程转换为musicpy多轨工程"""
    #print([m21_stream_Stream_to_mpy(m21part) for m21part in m21score.parts])
    return musicpy.build(*[m21_stream_Stream_to_mpy(m21part) for m21part in m21score.parts])
    #TODO:曲速

def m21_to_mpy(m21obj):
    """将music21对象转换为musicpy对象"""
    return {
        music21.pitch.Pitch:m21_pitch_Pitch_to_mpy,
        music21.note.Note:m21_note_Note_to_mpy,
        music21.stream.Stream:m21_stream_Stream_to_mpy,
        music21.stream.Measure:m21_stream_Stream_to_mpy,
        music21.stream.Part:m21_stream_Stream_to_mpy,
        music21.stream.Score:m21_stream_Score_to_mpy,
        }[type(m21obj)](m21obj)

#===================musicpy转music21===================

def mpy_note_to_m21(mpynote:musicpy.note)->music21.note.Note:
    """将musicpy音符转换为music21音符"""
    return music21.note.Note(str(mpynote).title().replace("b","-"),duration=music21.duration.Duration(mpynote.duration*4))

def mpy_chord_to_m21(mpychord:musicpy.chord)->music21.stream.Stream:
    """将musicpy chord转换为music21 stream"""
    m21stream=music21.stream.Stream()
    time=0
    for (note,interval) in zip(mpychord,mpychord.interval):
        m21stream.insert(time,mpy_note_to_m21(note))
        time+=interval*4
    return m21stream.chordify()

def mpy_tempo_to_m21(mpytempo:musicpy.tempo)->music21.tempo.MetronomeMark:
    """将musicpy曲速对象转换为music21曲速对象"""
    return music21.tempo.MetronomeMark(number=mpytempo.bpm)

def mpy_track_to_m21(mpytrack:musicpy.track)->music21.stream.Part:
    """将musicpy track转换为music21 part"""
    m21stream=music21.stream.Part()
    mpychord=mpytrack.content
    time=mpytrack.start_time
    for (note,interval) in zip(mpychord,mpychord.interval):
        m21stream.insert(time,mpy_note_to_m21(note))
        time+=interval*4
    return m21stream

def mpy_piece_to_m21(mpypiece:musicpy.piece)->music21.stream.Score:
    """将musicpy多轨工程转换为music21多轨工程"""
    m21score=music21.stream.Score()
    for tr in mpypiece:
        m21part=mpy_track_to_m21(tr)
        m21score.insert(0,m21part)
    return m21score
    #TODO:曲速

def mpy_to_m21(mpyobj):
    """将musicpy对象转换为music21对象"""
    return {
        musicpy.note:mpy_note_to_m21,
        musicpy.chord:mpy_chord_to_m21,
        musicpy.track:mpy_track_to_m21,
        musicpy.piece:mpy_piece_to_m21,
        musicpy.tempo:mpy_tempo_to_m21,
        }[type(mpyobj)](mpyobj)