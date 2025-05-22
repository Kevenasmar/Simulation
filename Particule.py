from vector3D import Vector3D as V3D
from math import pi, atan2

class Particule(object):
    
    def __init__(self, mass=1, p0=V3D(), v0=V3D(), a0=V3D(), fix=False, name="paf", color='red'):
        self.mass = mass                     # Masse de la particule (en kg)
        self.position = [p0]                 # Liste des positions successives
        self.speed = [v0]                    # Liste des vitesses successives
        self.acceleration = [a0]             # Liste des accélérations successives
        self.name = name                     # Nom de la particule (affichage/debug)
        self.color = color                   # Couleur utilisée pour l'affichage
        self.forces = V3D()                  # Force résultante appliquée (initialement nulle)
        self.fix = fix                       # Booléen : True si la particule est fixe

    def __str__(self):
        msg = 'Particule ('+str(self.mass)+', '+str(self.position[-1])+', '+str(self.speed[-1])+', '+str(self.acceleration[-1])+', "'+self.name+'", "'+str(self.color)+'" )'
        return msg

    def __repr__(self):
        return str(self)

    def applyForce(self, *args):
        # Ajoute les forces externes à la force résultante
        for f in args:
            self.forces += f

    def simulate(self, step):
        # Applique un pas de simulation via le PFD
        self.pfd(step)
        
    def pfd(self, step):
        # Applique le Principe Fondamental de la Dynamique pour calculer a, v, p
        
        if not(self.fix):  # Si la particule est mobile
            a = self.forces * (1/self.mass)                     # Accélération = F / m
            v = self.speed[-1] + a * step                       # Vitesse = v + a*dt
        else:  # Si la particule est fixe
            a = V3D()
            v = V3D()

        # Position = p + v*dt + 0.5*a*dt²
        p = self.position[-1] + 0.5 * a * step**2 + self.speed[-1] * step

        # Enregistrement des nouvelles valeurs
        self.acceleration.append(a)
        self.speed.append(v)
        self.position.append(p)

        # Réinitialisation des forces (prêtes pour le prochain cycle)
        self.forces = V3D()

    def plot(self):
        # Trace la trajectoire de la particule avec matplotlib
        from pylab import plot
        X = []
        Y = []
        for p in self.position:
            X.append(p.x)
            Y.append(p.y)
    
        return plot(X, Y, color=self.color, label=self.name) + plot(X[-1], Y[-1], 'o', color=self.color)    

    def getPosition(self):
        # Retourne la dernière position connue
        return self.position[-1]
    
    def getSpeed(self):
        # Retourne la dernière vitesse connue
        return self.speed[-1]
    
    def gameDraw(self, scale, screen):
        import pygame
        
        # Conversion coordonnées physiques -> écran
        X = int(scale * self.getPosition().x)
        Y = int(scale * self.getPosition().y)
        
        VX = int(scale * self.getSpeed().x)
        VY = int(scale * self.getSpeed().y) 
        size = 3
        
        # Gestion de la couleur (supporte RGB normalisé ou nom)
        if type(self.color) is tuple:
            color = (self.color[0]*255, self.color[1]*255, self.color[2]*255)
        else:
            color = self.color
            
        # Dessin du point et du vecteur vitesse
        pygame.draw.circle(screen, color, (X, Y), size * 2)
        pygame.draw.line(screen, color, (X, Y), (X + VX, Y + VY), size)

