class Vector3D():
    """Classe pour un vecteur 3D (x, y, z)"""
    def __init__(self, x=0, y=0, z=0):
        """Constructeur avec des valeurs par défaut nulles"""
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        """Représentation sous forme de chaîne de caractères du vecteur"""
        return "Vector3D(%g, %g, %g)" % (self.x, self.y, self.z)

    def __repr__(self):
        """Représentation officielle sous forme de chaîne de caractères du vecteur"""
        return "Vector3D(%g, %g, %g)" % (self.x, self.y, self.z)

    def __add__(self, other):
        """Addition de deux vecteurs"""
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __neg__(self):
        """Négation du vecteur"""
        return Vector3D(-self.x, -self.y, -self.z)

    def __sub__(self, other):
        """Soustraction de deux vecteurs"""
        return self + (-other)

    def __mul__(self, other):
        """Produit vectoriel entre deux vecteurs (*) ou multiplication par un scalaire"""
        if type(other) is Vector3D:
            # Produit vectoriel
            X = self.y * other.z - self.z * other.y
            Y = self.z * other.x - self.x * other.z
            Z = self.x * other.y - self.y * other.x
        else:
            # Multiplication par un scalaire
            X = other * self.x
            Y = other * self.y
            Z = other * self.z

        return Vector3D(X, Y, Z)

    def __rmul__(self, other):
        """Multiplication inverse (scalaire * vecteur)"""
        return self * other

    def __pow__(self, other):
        """Produit scalaire entre deux vecteurs (**) ou exponentiation par un scalaire"""
        if type(other) is Vector3D:
            # Produit scalaire
            return (self.x * other.x + self.y * other.y + self.z * other.z)
        else:
            # Exponentiation par un scalaire
            X = other * self.x
            Y = other * self.y
            Z = other * self.z
            return Vector3D(X, Y, Z)

    def __rpow__(self, other):
        """Exponentiation inverse (scalaire ** vecteur)"""
        return self ** other

    def __eq__(self, other):
        """Vérifie si deux vecteurs sont égaux"""
        if not isinstance(other, Vector3D):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def mod(self):
        """Norme (magnitude) du vecteur"""
        return (self ** self) ** .5

    def norm(self):
        """Vecteur normalisé"""
        m = self.mod()
        if m != 0:
            return self * (1 / m)
        else:
            return Vector3D()

    def rotZ(self, theta):
        """Rotation du vecteur autour de l'axe Z d'un angle theta"""
        from numpy import cos, sin

        x = cos(theta) * self.x - sin(theta) * self.y
        y = cos(theta) * self.y + sin(theta) * self.x

        self.x = x
        self.y = y
        return self

    def save(self, nom='vec.dat'):
        """Sauvegarde le vecteur dans un fichier en utilisant pickle"""
        from pickle import dump
        file = open(nom, 'wb')
        dump(self, file)
        file.close()

    def load(self, nom='vec.dat'):
        """Charge le vecteur depuis un fichier en utilisant pickle"""
        from pickle import load
        file = open(nom, 'rb')
        temp = load(file)
        self.x = temp.x
        self.y = temp.y
        self.z = temp.z
        file.close()

    def copy(self):
        """Retourne une copie du vecteur"""
        return Vector3D(self.x, self.y, self.z)


