import re

class Alumno:
    """
    Clase usada para el tratamiento de las notas de los alumnos. Cada uno
    incluye los atributos siguientes:

    numIden:   Número de identificación. Es un número entero que, en caso
               de no indicarse, toma el valor por defecto 'numIden=-1'.
    nombre:    Nombre completo del alumno.
    notas:     Lista de números reales con las distintas notas de cada alumno.
    """

    def __init__(self, nombre, numIden=-1, notas=[]):
        self.numIden = numIden
        self.nombre = nombre
        self.notas = [nota for nota in notas]

    def __add__(self, other):
        """
        Devuelve un nuevo objeto 'Alumno' con una lista de notas ampliada con
        el valor pasado como argumento. De este modo, añadir una nota a un
        Alumno se realiza con la orden 'alumno += nota'.
        """
        return Alumno(self.nombre, self.numIden, self.notas + [other])

    def media(self):
        """
        Devuelve la nota media del alumno.
        """
        return sum(self.notas) / len(self.notas) if self.notas else 0

    def __repr__(self):
        """
        Devuelve la representación 'oficial' del alumno. A partir de copia
        y pega de la cadena obtenida es posible crear un nuevo Alumno idéntico.
        """
        return f'Alumno("{self.nombre}", {self.numIden!r}, {self.notas!r})'

    def __str__(self):
        """
        Devuelve la representación 'bonita' del alumno. Visualiza en tres
        columnas separas por tabulador el número de identificación, el nombre
        completo y la nota media del alumno con un decimal.
        """
        return f'{self.numIden}\t{self.nombre}\t{self.media():.1f}'

    def leeAlumnos(ficAlum):
        """
        Lee un fichero de texto con los datos de los alumnos y devuelve un
        diccionario con clave el nombre del alumno y valor el objeto Alumno
        correspondiente.

        El fichero debe tener en cada línea el número de identificación, el nombre
        completo del alumno (puede tener espacios) y las notas (números reales).

        >>> alumnos = leeAlumnos('alumnos.txt')
        >>> for alumno in alumnos:
        ...     print(alumnos[alumno])
        ...
        171     Blanca Agirrebarrenetse 9.5
        23      Carles Balcells de Lara 4.9
        68      David Garcia Fuster     7.0
        """
        diccionario = {}

        with open(ficAlum, encoding='utf-8') as f:
            for linea in f:
                tokens = re.split(r'[ \t]+', linea.strip())

                if not tokens:
                    continue

                numIden = int(tokens[0])
                for i in range(1, len(tokens)):
                    if re.fullmatch(r'\d+(?:\.\d+)?', tokens[i]):
                        nombre = ' '.join(tokens[1:i])
                        notas = list(map(float, tokens[i:]))
                        break

                alumno = Alumno(nombre, numIden, notas)
                diccionario[nombre] = alumno

        return diccionario

    def normalizaHoras(ficText, ficNorm):
        """
        Normaliza expresiones horarias de un fichero de texto, escribiéndolas en formato HH:MM.

        Las expresiones incorrectas no se modifican.
        """
        
        def formatea(h, m=0):
            return f"{int(h):02}:{int(m):02}"

        def texto_a_hora_min(partes, periodo=None):
            """Convierte texto como '5 y cuarto' a HH:MM ajustando según el periodo"""
            hora = int(partes[0])
            if 'y cuarto' in partes:
                minuto = 15
            elif 'y media' in partes:
                minuto = 30
            elif 'menos cuarto' in partes:
                hora = hora - 1 if hora > 1 else 12
                minuto = 45
            else:
                minuto = 0

            if hora < 1 or hora > 12:
                return None 

            if periodo:
                if periodo == 'de la mañana':
                    if hora == 12:
                        hora = 0
                elif periodo == 'del mediodía':
                    if hora != 12:
                        hora += 12
                elif periodo == 'de la tarde':
                    if 1 <= hora <= 7:
                        hora += 12
                    else:
                        return None
                elif periodo == 'de la noche':
                    if 8 <= hora <= 11:
                        hora = hora % 12
                    elif hora == 12:
                        hora = 0
                    elif 1 <= hora <= 4:
                        hora = hora % 12
                    else:
                        return None
                elif periodo == 'de la madrugada':
                    if 1 <= hora <= 6:
                        hora = hora % 12
                    else:
                        return None
            else:
                hora %= 12 

            return formatea(hora, minuto)

        patrones = [
            (re.compile(r'\b(\d{1,2})h(\d{1,2})m\b'), lambda m: formatea(m[1], m[2]) if 0 <= int(m[1]) <= 23 and 0 <= int(m[2]) <= 59 else m[0]),
            (re.compile(r'\b(\d{1,2})h\b'), lambda m: formatea(m[1], 0) if 0 <= int(m[1]) <= 23 else m[0]),

            (re.compile(r'\b(\d{1,2}):(\d{2})\b'), lambda m: formatea(m[1], m[2]) if 0 <= int(m[1]) <= 23 and 0 <= int(m[2]) <= 59 else m[0]),

            (re.compile(r'\b(\d{1,2}) en punto\b'), lambda m: formatea(m[1], 0) if 0 <= int(m[1]) <= 23 else m[0]),

            (re.compile(r'\b(\d{1,2}) (y cuarto|y media|menos cuarto)? de la (mañana|tarde|noche|madrugada|del mediodía)\b'),
            lambda m: texto_a_hora_min([m[1], m[2]], 'de la ' + m[3]) if m[3] != 'del mediodía' else texto_a_hora_min([m[1], m[2]], m[3])),

            (re.compile(r'\b(\d{1,2}) (y cuarto|y media|menos cuarto)\b'),
            lambda m: texto_a_hora_min([m[1], m[2]])),
        ]

        with open(ficText, encoding='utf-8') as f_in, open(ficNorm, 'w', encoding='utf-8') as f_out:
            for linea in f_in:
                original = linea
                for regex, reemplazo in patrones:
                    def reemplazar(match):
                        grupos = match.groups()
                        texto = match.group(0)
                        try:
                            nuevo = reemplazo((texto, *grupos))
                            return nuevo if nuevo else texto
                        except:
                            return texto  
                    linea = regex.sub(reemplazar, linea)
                f_out.write(linea)
