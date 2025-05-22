from Particule import Particule
from Barre2D import Barre
from vector3D import Vector3D as V3D
import numpy as np

class Force:
    """
    Classe de base représentant une force générique appliquée à un objet de la simulation.
    Cette classe peut être héritée pour créer des forces spécifiques (gravité, ressort, etc.).

    Attributs :
    - force : Vecteur de force appliqué (par défaut nul)
    - name : Nom de la force (utile pour l'identification ou le debug)
    - active : Booléen pour activer ou désactiver dynamiquement la force
    """

    def __init__(self, force=V3D(), name='force', active=True):
        self.force = force         # Force par défaut (vecteur nul)
        self.name = name           # Nom de la force
        self.active = active       # Si False, la force ne sera pas appliquée

    def __str__(self):
        # Représentation lisible de la force pour le debug
        return f"Force ({self.force}, {self.name})"

    def __repr__(self):
        return str(self)

    def setForce(self, entity):
        """
        Applique la force à l'entité si la force est active.
        Ce comportement peut être redéfini dans les classes filles.
        """
        if self.active:
            entity.applyForce(self.force)


class Gravity(Force):
    """
    Force gravitationnelle appliquée à tous les objets soumis à une masse.
    Par défaut, elle agit verticalement (direction -y) avec une intensité de 9.8 m/s².

    Attributs :
    - g : Vecteur gravité (ex : V3D(0, -9.8))
    - name : nom de la force
    - active : booléen activant ou désactivant la force
    """

    def __init__(self, g=V3D(0, -9.8), name='gravity', active=True):
        self.g = g             # Accélération gravitationnelle (m/s²)
        self.name = name       # Nom de la force (utilisé pour debug ou affichage)
        self.active = active   # Si False, la force ne s’applique pas

    def setForce(self, entity):
        """
        Applique la force gravitationnelle à l'entité, selon sa masse :
        - Pour une particule : F = m * g
        - Pour une barre : F = m * g appliquée au centre (point = 0.0)
        """
        if not self.active:
            return

        if isinstance(entity, Particule):
            # Gravité appliquée au centre de masse d’une particule
            entity.applyForce(-self.g * entity.mass)

        elif isinstance(entity, Barre):
            # Gravité appliquée au centre géométrique de la barre (point = 0.0)
            entity.applyForce(-self.g * entity.mass, 0.0)


class ForceSelect(Force):
    """
    Force appliquée uniquement à un ou plusieurs objets spécifiés (souvent des particules).
    Permet de cibler un sous-ensemble précis d'entités dans la simulation.

    Attributs :
    - force : Vecteur de force à appliquer
    - subjects : Liste des objets ciblés par la force
    - name : Nom de la force
    - active : Booléen indiquant si la force est active ou non
    """

    def __init__(self, force=V3D(), subject=None, name='force', active=True):
        self.force = force                            # Vecteur de force à appliquer
        self.name = name                              # Nom de la force
        self.active = active                          # Activation dynamique
        self.subjects = subject if isinstance(subject, list) else [subject]  
        # Si un seul objet est passé, on le met dans une liste pour unifier le traitement

    def setForce(self, particule):
        """
        Applique la force uniquement si :
        - la force est active
        - la particule fait partie de la liste ciblée
        """
        if self.active and particule in self.subjects:
            particule.applyForce(self.force)


class Bounce_y(Force):
    """
    Simule un rebond lorsqu'une particule franchit la limite inférieure (y < 0),
    comme un sol virtuel. Une force de restitution proportionnelle à la vitesse 
    d'impact est appliquée vers le haut.

    Attributs :
    - k : coefficient de restitution (élasticité du rebond)
    - step : pas de temps utilisé dans le calcul de la force (influence la réactivité)
    - name : nom pour affichage ou debug
    - active : booléen pour activer/désactiver la force
    """

    def __init__(self, k=1, step=0.1, name="boing", active=True):
        self.name = name       # Nom de la force (utile pour logs ou debug)
        self.k = k             # Coefficient de rebond (élasticité)
        self.step = step       # Pas de temps utilisé pour évaluer la réaction

    def setForce(self, entity):
        """
        Applique une force de rebond si la particule :
        - est passée sous le sol (y < 0)
        - a une vitesse vers le bas (vitesse.y < 0)
        """
        if isinstance(entity, Particule):
            if entity.getPosition().y < 0 and entity.getSpeed().y < 0:
                # Force appliquée vers le haut pour simuler le rebond
                force_rebond = -2 * (self.k / self.step) * V3D(0, entity.getSpeed().y * entity.mass)
                entity.applyForce(force_rebond)

        
class Bounce_x(Force):
    """
    Simule un rebond lorsqu'une particule franchit le mur de gauche (x < 0),
    en appliquant une force de restitution dirigée vers la droite.

    Attributs :
    - k : coefficient de restitution (élasticité du rebond)
    - step : pas de temps utilisé pour l'intensité de la force
    - name : nom de la force (pour affichage ou debug)
    - active : booléen pour activer ou désactiver dynamiquement la force
    """

    def __init__(self, k=1, step=0.1, name="boing", active=True):
        self.name = name       # Nom de la force
        self.k = k             # Coefficient de rebond (réactivité à l’impact)
        self.step = step       # Pas de temps pour le calcul de la réaction

    def setForce(self, entity):
        """
        Applique une force de rebond uniquement si :
        - la particule dépasse la frontière gauche (x < 0)
        - elle se déplace vers la gauche (vitesse x < 0)
        """
        if isinstance(entity, Particule):
            if entity.getPosition().x < 0 and entity.getSpeed().x < 0:
                # Force de rebond appliquée horizontalement vers la droite
                force_rebond = -2 * (self.k / self.step) * V3D(entity.getSpeed().x * entity.mass)
                entity.applyForce(force_rebond)

        
class SpringDamper(Force):
    """
    Simule une liaison de type ressort-amortisseur entre deux particules.
    La force est proportionnelle à l'allongement du ressort et à la vitesse relative.

    Attributs :
    - P0, P1 : particules reliées
    - k : raideur du ressort (en N/m)
    - c : coefficient d'amortissement (en Ns/m)
    - l0 : longueur à l'équilibre (distance sans contrainte)
    """

    def __init__(self, P0, P1, k=0, c=0, l0=0, active=True, name="spring_and_damper"):
        super().__init__(V3D(), name, active)
        self.k = k             # Constante de raideur
        self.c = c             # Amortissement visqueux
        self.P0 = P0           # Première particule
        self.P1 = P1           # Seconde particule
        self.l0 = l0           # Longueur au repos (sans déformation)

    def setForce(self, entity):
        """
        Applique la force de ressort + amortisseur à la particule concernée (P0 ou P1).

        Le ressort agit selon :
            F = -k * (||P1 - P0|| - l0)
        Et l'amortisseur selon :
            F = -c * projection_vitesse_relative
        """

        if not self.active or entity not in [self.P0, self.P1]:
            return

        # === Direction entre les deux particules
        vec_dir = self.P1.getPosition() - self.P0.getPosition()
        v_n = vec_dir.norm()                    # direction unitaire
        flex = vec_dir.mod() - self.l0          # allongement (déformation scalaire)

        # === Vitesse relative projetée dans la direction du ressort
        vit = self.P1.getSpeed() - self.P0.getSpeed()
        vit_n = vit ** v_n * self.c             # projection scalaire amortie

        # === Force résultante totale
        force = (self.k * flex + vit_n) * v_n   # ressort + amortisseur

        # === Application de la force à la bonne particule
        if entity == self.P0:
            entity.applyForce(force)
        elif entity == self.P1:
            entity.applyForce(-force)

            
class Link(SpringDamper):
    """
    Simule une liaison rigide (ou quasi-rigide) entre deux particules.

    Hérite du comportement d'un ressort-amortisseur avec :
    - grande raideur (k) pour empêcher l'allongement,
    - fort amortissement (c) pour stabiliser rapidement.

    Utile pour simuler une barre fixe ou un lien non extensible.
    """

    def __init__(self, P0, P1, name="link"):
        # Calcul de la distance initiale comme longueur au repos
        l0 = (P0.getPosition() - P1.getPosition()).mod()

        # Initialisation du parent avec une grande rigidité et un fort amortissement
        super().__init__(
            P0, P1,
            k=1000,   # raideur élevée → liaison proche du rigide
            c=100,    # amortissement élevé → stabilisation rapide
            l0=l0,
            active=True,
            name=name
        )


class SpringDamperMoteur(Force):
    """
    Modélise un ressort amorti reliant un moteur (fixe) à une particule.

    - Le moteur est considéré comme un point fixe (attribut `.p`)
    - La force exercée dépend :
        • de la distance actuelle par rapport à la longueur à vide (l0),
        • de la vitesse relative de la particule projetée sur la direction du ressort.

    Paramètres :
        moteur : objet avec un attribut de position .p (type V3D)
        particule : particule soumise à la force
        k : raideur du ressort
        c : coefficient d'amortissement
        l0 : longueur au repos (initialisée automatiquement à la distance initiale)
    """

    def __init__(self, moteur, particule, k=10, c=1, name="spring damper moteur"):
        self.moteur = moteur               # Point fixe (position moteur.p)
        self.particule = particule         # Particule mobile attachée au ressort
        self.k = k                         # Raideur du ressort
        self.c = c                         # Amortissement visqueux
        self.name = name                   # Nom de la force
        # Longueur à l'équilibre mesurée à l'initialisation
        self.l0 = (self.particule.getPosition() - self.moteur.p).mod()

    def setForce(self, p):
        if p != self.particule:
            return  # n'agit que sur la particule concernée

        # Récupération des positions
        pos_m = self.moteur.p
        pos_p = p.getPosition()

        # Vecteur entre moteur et particule
        vec_dir = pos_p - pos_m
        unit = vec_dir.norm()        # direction normalisée
        distance = vec_dir.mod()     # longueur actuelle du ressort

        # Vitesse relative projetée sur la direction du ressort
        v_r = self.particule.getSpeed()
        v_n = v_r ** unit            # composante normale (scalaire)

        # Formule de la force ressort + amortissement
        force = (-self.k * (distance - self.l0) - self.c * v_n) * unit

        # Application à la particule
        self.particule.applyForce(force)


class ForceMoteur(Force):
    """
    Applique à une particule une force tangentielle résultant du couple développé
    par un moteur à courant continu (MoteurCC).

    - La particule est considérée en rotation autour du moteur, situé en position fixe (moteur.x, moteur.y).
    - La force simulée correspond à F = τ / r, appliquée dans la direction tangentielle au rayon.

    Paramètres :
        moteur : instance de MoteurCC (doit exposer .x, .y et .getTorque())
        particule : la particule ciblée par cette force tangentielle
        active : booléen pour activer/désactiver dynamiquement la force
    """

    def __init__(self, moteur, particule, active=True, name="force_moteur"):
        super().__init__(V3D(), name, active)
        self.moteur = moteur            # Moteur fixe
        self.particule = particule      # Particule ciblée par la force tangentielle

    def setForce(self, particule):
        # Appliquer la force uniquement si elle est active et que la particule est celle prévue
        if not self.active or particule != self.particule:
            return

        # Vecteur entre le moteur (fixe) et la particule
        vecteur = particule.getPosition() - V3D(self.moteur.x, self.moteur.y, 0)
        rayon = vecteur.mod()
        if rayon == 0:
            return  # Évite une division par zéro (la particule est "sur" le moteur)

        # Calcul de la direction tangentielle au rayon
        tangente = V3D(-vecteur.y, vecteur.x, 0).norm()

        # Récupération du couple produit par le moteur
        torque = self.moteur.getTorque()

        # Calcul de la force tangentielle F = τ / r
        force_moteur = (torque / rayon) * tangente

        # Application de la force à la particule
        particule.applyForce(force_moteur)


class Pivot(Force):
    """
    Classe représentant une liaison pivot souple entre une barre rigide et un point fixe (une particule).
    La liaison est modélisée comme un ressort amortisseur agissant sur le point spécifié de la barre.
    """

    def __init__(self, barre, point_fix, point=0.0, k=1000, c=25, name="pivot", active=True):
        super().__init__(V3D(), name=name, active=active)

        self.barre = barre             # Barre rigide concernée
        self.point_fix = point_fix     # Particule représentant le point fixe
        self.point = point             # Position normalisée sur la barre [-1, 1]
        self.k = k                     # Constante de raideur (N/m)
        self.c = c                     # Coefficient d’amortissement (kg/s)

        # Calcul de la position initiale du point de la barre
        theta0 = self.barre.getAngle()
        dir_barre = V3D(np.cos(theta0), np.sin(theta0), 0)
        P0 = self.barre.getPosition() + (self.point * self.barre)


class SpringDamperBarre(Force):
    """
    Ressort-amortisseur entre deux barres rigides, appliqué à deux points spécifiques (définis en position normalisée).
    Modélise un lien souple (type ressort) entre deux barres avec amortissement visqueux.
    """

    def __init__(self, B0, point0, B1, point1, k=100, c=10, name="spring_barre", active=True):
        super().__init__(V3D(), name, active)

        self.B0 = B0                  # Première barre
        self.B1 = B1                  # Deuxième barre
        self.p0 = point0              # Position normalisée sur la première barre [-1, 1]
        self.p1 = point1              # Position normalisée sur la deuxième barre [-1, 1]
        self.k = k                    # Raideur du ressort (N/m)
        self.c = c                    # Coefficient d’amortissement (kg/s)
        self.active = active

        # Longueur à vide (distance initiale entre les deux points sur les barres)
        P0 = self._get_global_position(B0, point0)
        P1 = self._get_global_position(B1, point1)
        self.l0 = (P1 - P0).mod()

    def _get_global_position(self, barre, point):
        """
        Calcule la position absolue d'un point donné sur une barre (dans le repère global).
        """
        angle = barre.getAngle()
        dir_barre = V3D(np.cos(angle), np.sin(angle), 0)  # direction de la barre
        return barre.getPosition() + (point * barre.L / 2) * dir_barre

    def _get_global_speed(self, barre, point):
        """
        Calcule la vitesse absolue d'un point donné sur une barre (translation + rotation).
        """
        angle = barre.getAngle()
        omega = barre.getAngularSpeed()
        dir_barre = V3D(np.cos(angle), np.sin(angle), 0)
        r = (point * barre.L / 2) * dir_barre              # vecteur du centre au point
        v_translation = barre.getSpeed()
        v_rotation = V3D(-omega * r.y, omega * r.x, 0)     # rotation autour du centre
        return v_translation + v_rotation

    def setForce(self, entity):
        """
        Applique la force sur l'une ou l'autre des barres selon l'entité concernée.
        """
        if not self.active or entity not in [self.B0, self.B1]:
            return

        # Positions et vitesses des deux extrémités
        P0 = self._get_global_position(self.B0, self.p0)
        P1 = self._get_global_position(self.B1, self.p1)
        V0 = self._get_global_speed(self.B0, self.p0)
        V1 = self._get_global_speed(self.B1, self.p1)

        delta = P1 - P0                     # vecteur entre les deux extrémités
        d = delta.mod()                    # distance actuelle
        if d == 0:
            return                         # évite les divisions par 0

        n = delta.norm()                   # vecteur direction normalisée

        v_rel = (V1 - V0) ** n             # composante normale de la vitesse relative

        # Force totale = ressort + amortisseur
        force = (self.k * (d - self.l0) + self.c * v_rel) * n

        # Application de la force à la bonne extrémité
        if entity == self.B0:
            self.B0.applyForce(force, self.p0)
        elif entity == self.B1:
            self.B1.applyForce(-force, self.p1)


class ForceSelectBarre(Force):
    """
    Force ponctuelle appliquée à une barre à un point donné.
    Elle est désactivée automatiquement après un seul pas de simulation.
    Idéale pour simuler une "pichenette" ou un effet déclenché par l'utilisateur.
    """

    def __init__(self, force=V3D(), barre=None, point=0.0, name='force_select_barre', active=True):
        super().__init__(force, name, active)
        self.barre = barre                  # Barre cible de l'effort
        self.point = point                  # Position sur la barre (normalisée entre -1 et 1)
        self.justActivated = False          # Permet de désactiver automatiquement la force au pas suivant

    def setForce(self, entity):
        """
        Applique la force à la barre spécifiée si elle est active.
        Ne s'exécute que pendant un seul pas de simulation.
        """
        if self.active and entity is self.barre:
            self.barre.applyForce(self.force, self.point)
            self.justActivated = True       # Marque qu'une force a été appliquée

    def postStep(self):
        """
        Appelé après chaque pas de simulation : désactive la force si elle a été utilisée.
        Permet d’éviter qu’elle reste active au pas suivant.
        """
        if self.justActivated:
            self.active = False
            self.justActivated = False


class GlissiereBarreParticule(SpringDamper):
    """
    Modélise une liaison glissière entre une barre et une particule.
    Contraint le mouvement perpendiculairement à un axe donné, 
    en utilisant un ressort-amortisseur virtuel uniquement hors de l'axe.
    """

    def __init__(self, barre: Barre, particule: Particule, axis=V3D(1, 0, 0), k=1000, c=100, name="glissiere_barre_particule"):
        # Longueur initiale entre la barre et la particule (au repos)
        l0 = (barre.getPosition() - particule.getPosition()).mod()

        # Initialise un ressort entre la barre (P0) et la particule (P1)
        super().__init__(barre, particule, k, c, l0, active=True, name=name)

        self.axis = axis.norm()  # Axe de la glissière (normalisé)

    def setForce(self, obj):
        """
        Applique une force de rappel perpendiculaire à l'axe de la glissière
        pour contraindre le mouvement à rester sur l'axe.
        """

        # Calcul du vecteur déplacement entre la barre et la particule
        vec_dir = self.P1.getPosition() - self.P0.getPosition()

        # Supprime la composante le long de l'axe de glissement autorisé
        vec_dir -= (vec_dir ** self.axis) * self.axis

        # Si aucune déviation (déjà sur le rail), ne rien faire
        if vec_dir.mod() < 1e-8:
            return

        # Vecteur normal à l’axe (direction de correction)
        v_n = vec_dir.norm()
        flex = vec_dir.mod() - self.l0  # Élongation hors axe

        # Vitesse relative des deux objets
        vit = self.P1.getSpeed() - self.P0.getSpeed()
        vit_n = (vit ** v_n) * self.c  # Projection selon la direction de correction

        # Force résultante (ressort + amortisseur)
        force = (self.k * flex + vit_n) * v_n

        # Application de la force à l'objet concerné
        if obj == self.P0:
            if isinstance(self.P0, Barre):
                self.P0.applyForce(force, point=0)  # Appliqué au centre de la barre
            else:
                self.P0.applyForce(force)
        elif obj == self.P1:
            if isinstance(self.P1, Barre):
                self.P1.applyForce(-force, point=0)
            else:
                self.P1.applyForce(-force)


class Prism(SpringDamper):
    """
    Implémente une liaison prismatique (glissière) entre deux particules.
    Contraint le mouvement relatif à se faire uniquement selon une certaine direction (axe).

    Hérite de SpringDamper (ressort + amortisseur).
    """

    def __init__(self, P0, P1, axis=V3D(), name="prism"):
        # Longueur à l'équilibre initiale (distance entre les deux particules)
        l0 = (P0.getPosition() - P1.getPosition()).mod()
        
        # Initialisation du ressort avec raideur k=1000 et amortissement c=100
        super().__init__(P0, P1, k=1000, c=100, l0=l0, active=True, name=name)
        
        # Direction de glissement autorisée (doit être normalisée)
        self.axis = axis.norm()

    def setForce(self, particule):
        # === Vecteur de liaison (P1 - P0)
        vec_dir = self.P1.getPosition() - self.P0.getPosition()
        
        # === Supprime la composante le long de l'axe autorisé
        # Ce qui reste est la composante perpendiculaire : c'est ce que l'on "corrige"
        vec_dir -= (vec_dir ** self.axis) * self.axis

        # === Direction normalisée de la force correctrice (perpendiculaire à l'axe)
        v_n = vec_dir.norm()

        # === Allongement par rapport à la longueur à l’équilibre
        flex = vec_dir.mod() - self.l0

        # === Vitesse relative entre les deux particules
        vit = self.P1.getSpeed() - self.P0.getSpeed()
        vit_n = vit ** v_n * self.c

        # === Force de rappel (ressort + amortisseur)
        force = (self.k * flex + vit_n) * v_n

        # === Appliquer la force à la bonne particule
        if particule == self.P0:
            particule.applyForce(force)
        elif particule == self.P1:
            particule.applyForce(-force)
        # Sinon, ne rien faire (force non applicable)


class PivotBarre(Force):
    """
    Simule une liaison de type pivot entre deux barres.
    Elle applique une force de rappel (ressort + amortissement) reliant deux points donnés sur deux barres distinctes.

    Paramètres :
        b1, b2 : objets Barre
        point1, point2 : position relative sur chaque barre (entre -1 et 1)
        k : raideur du ressort
        c : coefficient d'amortissement
        name : nom de la force
        active : permet d'activer/désactiver la force
    """

    def __init__(self, b1, point1, b2, point2, k=1000, c=25, name="pivot", active=True):
        super().__init__(V3D(), name=name, active=active)
        self.b1 = b1        # Première barre
        self.p1 = point1    # Position sur la première barre (normalisée)
        self.b2 = b2        # Deuxième barre
        self.p2 = point2    # Position sur la deuxième barre
        self.k = k          # Raideur du ressort
        self.c = c          # Amortissement

    def setForce(self, obj):
        if not self.active or (obj != self.b1 and obj != self.b2):
            return

        # === Calcul des directions locales de chaque barre ===
        dir1 = V3D(np.cos(self.b1.getAngle()), np.sin(self.b1.getAngle()), 0)
        dir2 = V3D(np.cos(self.b2.getAngle()), np.sin(self.b2.getAngle()), 0)

        # === Calcul des positions globales des deux points de liaison ===
        pos1 = self.b1.getPosition() + (self.p1 * self.b1.L / 2) * dir1
        pos2 = self.b2.getPosition() + (self.p2 * self.b2.L / 2) * dir2

        # === Vecteur de liaison (de la barre 1 à la barre 2) ===
        d = pos2 - pos1

        # === Vitesse absolue des points de liaison ===
        v1 = self.b1.getSpeed() + self.b1.getAngularSpeed() * V3D(-dir1.y, dir1.x, 0) * (self.p1 * self.b1.L / 2)
        v2 = self.b2.getSpeed() + self.b2.getAngularSpeed() * V3D(-dir2.y, dir2.x, 0) * (self.p2 * self.b2.L / 2)

        # === Vitesse relative entre les deux points ===
        dv = v2 - v1

        # === Force de type ressort amortisseur ===
        force = self.k * d + self.c * dv

        # === Application de la force sur la bonne barre ===
        if obj == self.b1:
            self.b1.applyForce(force, self.p1)
        elif obj == self.b2:
            self.b2.applyForce(-force, self.p2)


class ForceCorrecteur(Force):
    """
    Contrôleur PID appliquant une force horizontale à la base mobile
    pour stabiliser un pendule inversé fixé à cette base.

    Paramètres PID : 
    - Kp : proportionnel à l'erreur d'angle (theta)
    - Kd : proportionnel à la vitesse angulaire (dérivée)
    - Ki : intégrale de l'erreur (pour compenser le biais)
    """

    def __init__(self, pendule, base, Kp=1000, Kd=100, Ki=0.0, max_force=2000, name="force_correcteur", active=True):
        super().__init__(V3D(), name=name, active=active)
        self.pendule = pendule            # Barre verticale représentant le pendule
        self.base = base                  # Barre horizontale (base mobile)
        self.Kp = Kp                      # Gain proportionnel
        self.Kd = Kd                      # Gain dérivé
        self.Ki = Ki                      # Gain intégral
        self.max_force = max_force        # Force maximale autorisée
        self.integral_error = 0.0         # Intégrale de l'erreur (initialisée à 0)

    def setForce(self, obj):
        """
        Applique la force de correction sur la base uniquement si active.
        Utilise un correcteur PID basé sur l'orientation et la vitesse angulaire du pendule.
        """
        if not self.active or obj != self.base:
            return  # Ne s’applique que sur la base mobile et si la force est active

        # Lecture de l’état du pendule
        theta = self.pendule.getAngle()              # Angle d’inclinaison (en radian)
        omega = self.pendule.getAngularSpeed()       # Vitesse angulaire (rad/s)

        # Intégrale de l’erreur (limitation anti-windup)
        self.integral_error += theta
        self.integral_error = max(min(self.integral_error, 1), -1)

        # Calcul du PID : fx est la force horizontale à appliquer
        fx = -self.Kp * theta - self.Kd * omega - self.Ki * self.integral_error

        # Saturation de la force (sécurité)
        fx = max(min(fx, self.max_force), -self.max_force)

        # Application de la force horizontale au centre de la base
        self.base.applyForce(V3D(fx, 0, 0), 0)
