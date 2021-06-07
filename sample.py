def sample_mic(seconds):
    """
    Graba una señal de audio y realiza su fingerprint
    :param seconds: tiempo de grabacion en segundos
    :return: fingerprint
    """

    import sounddevice as sd
    from scipy.io.wavfile import write
    from fingerprint import fingerprint
    import time

    fs = 44100  # Sample rate
    print('Recording...')
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
    for i in range(1, int(seconds)+1):
        time.sleep(1)
        print(i)
    sd.wait()  # Wait until recording is finished
    print('Recording end.')
    print()
    write('samples/output.wav', fs, myrecording)  # Save as WAV file
    fingerprint_sample = fingerprint('samples/output.wav')
    
    return fingerprint_sample


def sample_file():
    """
    Selecciona un archivo de audio (.wav) y realiza su fingerprint
    :return: fingerprint
    """

    from tkinter import Tk
    from tkinter.filedialog import askopenfilename
    from fingerprint import fingerprint

    Tk().withdraw()
    file = askopenfilename(filetypes=[('audio file', '.wav')])
    fingerprint_sample = fingerprint(file)

    return fingerprint_sample
