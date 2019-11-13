import csv


class Distributivo:

    def __init__(self, row: list):
        self.raw = row
        self.carrera = row[0]
        self.cedula = row[1]
        self.nombres = row[2]
        self.codigo = row[3]
        self.materia = row[4]
        self.grupo = row[5]

    def __str__(self):
        return ' '.join(self.raw)


def leer_archivo(archivo, no_primera=True):
    lst = []
    with open(archivo, newline='\n') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        if no_primera:
            next(spamreader, None)
        for row in spamreader:
            lst.append(Distributivo(row))
    return lst


if __name__ == "__main__":
    archivo_distributivo = 'data/distributivo.csv'
    distributivo = leer_archivo(archivo_distributivo)
    print(distributivo)
