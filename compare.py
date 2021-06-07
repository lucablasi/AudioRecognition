def compare(samp, threshold_par=4, maxbar_min=50, graph=0):
    """
    Compara el fingerprint del sample contra los fingerprints
    que se encuentran almacenados en database.pkl.
    Decide si existe un match.
    :param samp: fingerprint: Dict{hash: t1}
    :param threshold_par: escalar para umbral de match
    :param maxbar_min: mínimo N de hashes comunes para contar como match
    :param graph:
    :return:
    """

    from time import time
    import pickle
    import numpy as np
    import plotly.graph_objects as go
    import operator
    import pandas as pd

    if samp == 'None':
        print('No sample.')
        return

    # Iniciar contador tiempo
    exec_t0 = time()

    # Importar database
    with open('database.pkl', 'rb') as f:
        database = pickle.load(f)

    # Comparar señal con cada canción en database
    print('Searching for match...')
    for song_data in database:
        # Separar string con nombre de archivo [0] y fp de archivo [1]
        song_name = song_data[0].split('.wav')[0]
        song = song_data[1]

        # Encontrar intersección de hashes para sample y song.
        # Una variable con t1 del sample y otra con t1 de canción.
        samp_match = [(samp[i], i) for i in samp.keys() & song.keys()]
        song_match = [(song[i], i) for i in samp.keys() & song.keys()]

        # Delta temporal y histograma
        dt = [song_match[i][0] - samp_match[i][0] for i in range(len(song_match))]
        hst = np.histogram(dt, bins=100)[0]

        # Encontrar máximo significativo
        maxbar_i, maxbar = max(enumerate(hst), key=operator.itemgetter(1))
        if maxbar >= maxbar_min:
            hst_nomaxbar = np.delete(hst, maxbar_i)  # Para calcular mean() y std() sin el max
            threshold_df = pd.DataFrame(hst_nomaxbar, columns=['H'])
            threshold = threshold_df['H'].mean() + 2 * threshold_df['H'].std()
            threshold = threshold_par * threshold
            if maxbar >= threshold:
                print('Match found.')
                print()
                print('Match: ' + song_name)
                print()
                exec_t1 = time()
                exec_t = round(exec_t1 - exec_t0, 2)
                print('Search time:', exec_t, 's')

                # Graph
                if graph == 1:
                    hst_i = np.histogram(dt, bins=100)[1]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=hst_i, y=hst))
                    fig.update_layout(
                        title='Grabación & canción correcta: Hashes comunes en función de Δt',
                        xaxis_title='Δt',
                        yaxis_title='Número de hashes en común',
                        font=dict(size=18))
                    fig.show()

                return
    print()
    print('No Match.')
    print()
