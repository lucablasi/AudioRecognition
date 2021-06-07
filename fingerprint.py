def ink(file, wtype='hann', wsize=4410, peak_area=10, amp_min=10):
    """
    Devuelve los picos del espectrograma de la señal.
    :param file: archivo de audio en formato .wav
    :param wtype: tipo de ventana para STFT
    :param wsize: tamaño de ventana para STFT
    :param peak_area: Area a analizar alrededor de un punto
    :param amp_min: Amplitud mínima para picos
    :return: List[Tuples(peak_ti, peak_fi)]
    """

    import numpy as np

    from scipy.signal import stft
    from scipy.io import wavfile

    from scipy.ndimage import generate_binary_structure
    from scipy.ndimage import iterate_structure
    from scipy.ndimage import maximum_filter

    # STFT
    [sr, audio] = wavfile.read(file)
    f, t, a = stft(audio, sr, wtype, wsize)
    # Simple conversión a dB, solo se ve complicado ya que elimina 0s
    # para que no surga un warning.
    a = abs(a)
    a = 10 * np.log10(a, out=np.zeros_like(a), where=(a != 0))

    # Binary structure
    # -------------------- #
    # Genera un nparray binario de 3x3 con la siguente forma:
    #
    #       0 1 0
    #       1 1 1
    #       0 1 0
    #
    # -------------------- #
    struct = generate_binary_structure(2, 1)

    # Struct dilation
    # -------------------- #
    # Dilata o "expande" el struct
    # ej:
    # iterate_structure(struct, 2)
    #
    #   - - - - -       0 0 1 0 0
    #   - 0 1 0 -       0 1 1 1 0
    #   - 1 1 1 -   =>  1 1 1 1 1
    #   - 0 1 0 -       0 1 1 1 0
    #   - - - - -       0 0 1 0 0
    #
    # Esto sirve para decidir el area alrededor de un punto a analizar
    # utilizando la forma definida en generate_binary_structure.
    # Mayor valor de area => menos picos => mayor velocidad procesamiento
    # pero
    # menos picos => posible menor accuracy
    # -------------------- #
    neighborhood = iterate_structure(struct, peak_area)

    # Find local max
    # -------------------- #
    # Busca los máximos locales utilizando la "forma" que creamos
    # con generate_binary_scructure y _iterate_structure como filtro.
    # -------------------- #
    local_max = maximum_filter(a, footprint=neighborhood) == a

    # Peak amplitudes & list peaks
    # -------------------- #
    # Buscamos la amplitud de los picos para descartar
    # por debajo de amp_min
    # -------------------- #
    amps = a[local_max]
    peak_f, peak_t = np.where(local_max)
    amps_filter = np.where(amps > amp_min)

    # Filtrar picos
    peak_t = peak_t[amps_filter]
    peak_f = peak_f[amps_filter]

    fp = list(zip(peak_t, peak_f))
    fp.sort()
    return fp


def hasher(fp, n_pairs=10, min_dt=0, max_dt=200):
    """
    Realiza 'Combinatorial Hashing' de los picos generados en ink()
    :param fp: salida de ink()
    :param n_pairs: numero de pares para cada pico
    :param min_dt: distancia mínima entre picos
    :param max_dt: distancia máxima entre picos
    :return: List[Tuples(t1, hash)]
    """

    import hashlib

    hashes = []
    for i in range(len(fp)):            # Tomamos un pico i
        for j in range(1, n_pairs):     # Tomamos un pico i+j
            if (i + j) < len(fp):       # Nos aseguramos que i+j no se pase de la lista

                t1 = fp[i][0]           # Tomamos los tiempos de ambos picos
                t2 = fp[i + j][0]
                dt = t2 - t1            # Delta t

                f1 = fp[i][1]           # Tomamos las frec. de ambos picos
                f2 = fp[i + j][1]

                # Check delta t entre los dos picos no sea demasiado grande
                if min_dt <= dt <= max_dt:
                    # Combinamos: f1, f2, y dt en un 'hash'
                    h = hashlib.sha1(f"{str(f1)}|{str(f2)}|{str(dt)}".encode('utf-8'))
                    h = h.hexdigest()
                    hashes.append((t1, h))  # Agregar a la nueva lista de hashes
    return hashes


def hash_dict(fp):
    """
    Elimina hashes duplicados y convierte de lista a dict
    :param fp: salida de hasher()
    :return: Dict{hash: t1}
    """

    # Eliminar hashes duplicados
    # ------------------------------ #
    # Eliminar hashes duplicados teóricamente empeora
    # la capacidad de encontrar matches, ya que hay
    # menos tuples (t1, hash).

    # Sin embargo, eliminar duplicados facilita las
    # operaciones ya que garantiza que tod0 match de
    # hashes entre sample y audio original tenga una
    # sola diferencia temporal.

    # En la práctica la pérdida de tuples (t1, hash)
    # es mínima y no tiene un efecto percibible
    # sobre el rendimiendo.
    # ------------------------------ #
    visited = set()
    output = []
    for t, h in fp:
        if h not in visited:
            visited.add(h)
            output.append((t, h))
    output = set(output)

    # Convertir set a dict
    # ------------------------------ #
    # La ventaja del tipo dict es que es más facil y
    # considerablemente más rápido buscar una intersección
    # de los hashes entre dos fingerprints de dos audios
    # separados (sample y database). También facilita
    # retener los t1 correspondientes para cada hash
    # de cada fingerprint.
    # ------------------------------ #
    output = {h: t for t, h in output}
    return output


def fingerprint(file):
    """
    Une las tres funciones necesarias para ir desde un archivo
    de audio a la etapa de comparación.
    :param file:
    :return: fingerprint: Dict{hash: t1}
    """

    fp = ink(file)
    fp = hasher(fp)
    fp = hash_dict(fp)
    return fp
