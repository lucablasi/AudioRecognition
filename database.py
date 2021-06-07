def create_database(path):
    """
    Crea fingerprint database según el contenido en 'path'.
    :param path: ubicación carpeta archivos de audio
    :type path: str
    """

    from os import listdir
    from os.path import isfile, join
    from fingerprint import fingerprint
    import pickle

    # Lista de archivos en carpeta
    files = [f for f in listdir(path) if isfile(join(path, f))]

    # Generar fingerprints de los archivos en path
    prints = []
    i = 1
    print('Processing...')
    for file in files:
        print(str(i) + '/' + str(len(files)))
        filepath = path + '/' + file
        fp = fingerprint(filepath)
        prints.append(fp)
        i += 1

    database = list(zip(files, prints))

    # Guardar variable
    with open('database.pkl', 'wb') as f:
        pickle.dump(database, f)

    print('Database created successfully.')


def update_database(path):
    """
    Actualiza el fingerprint database según el contenido en 'path'.
    Evita procesar archivos ya 'fingerprinted'
    Elimina fingerprints de archivos borrados
    :param path: ubicación carpeta archivos de audio
    :type path: str
    """

    from os import listdir
    from os.path import isfile, join
    from fingerprint import fingerprint
    import pickle

    # Importar database
    with open('database.pkl', 'rb') as f:
        database = pickle.load(f)

    # Lista archivos database:
    files_database = [i[0] for i in database]

    # Lista archivos en carpeta
    files_folder = [f for f in listdir(path) if isfile(join(path, f))]

    # Lista archivos nuevos
    files_new = list(set(files_folder) - set(files_database))

    # Generar fingerprints para los archivos nuevos
    prints_new = []
    i = 1
    print('Processing...')
    for file in files_new:
        print(str(i) + '/' + str(len(files_new)))
        filepath = path + '/' + file
        fp = fingerprint(filepath)
        prints_new.append(fp)
        i += 1

    # Agregar tuples nuevos y eliminar tuples de archivos borrados
    database_new = list(zip(files_new, prints_new))
    database += database_new
    database = [i for i in database if i[0] in files_folder]
    database = sorted(database)     # Sort alfabéticamente

    # Guardar variable
    with open('database.pkl', 'wb') as f:
        pickle.dump(database, f)

    print('Database updated successfully.')
