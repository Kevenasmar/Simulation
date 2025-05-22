from vector3D import Vector3D as V3D
from MoteurCC import MoteurCC
from Forces import *
from matplotlib import pyplot as plt
from Univers_Officiel import Univers

if __name__ == '__main__':

    # === Paramètres physiques du moteur CC ===
    R = 1.0       # Résistance [Ω]
    L = 0.001     # Inductance [H] (négligée)
    k_c = 0.01    # Constante de couple [Nm/A]
    k_e = 0.01    # Constante de FEM [V/rad/s]
    J = 0.01      # Inertie propre du moteur [kg·m²]
    f = 0.1       # Frottement visqueux [Nms/rad]
    P = V3D(50, 50, 0)  # Position du moteur dans l’espace 2D

    # === Liste des tensions continues à tester (de 20V à 220V par pas de 20) ===
    tensions = list(range(20, 221, 20))

    # === Listes de stockage des résultats pour chaque tension ===
    distances = []  # Distance finale entre moteur et particule
    omegas = []     # Vitesse de rotation finale du moteur

    # === Boucle de simulation pour chaque tension ===
    for U in tensions:
        # Nouveau monde simulé pour cette tension
        monUnivers = Univers(game=False)

        # Création des entités : une particule et un moteur CC
        particule = Particule(p0=V3D(40, 50, 0))  # Position initiale à gauche du moteur
        moteur = MoteurCC(R, L, k_c, k_e, J, f, p=P)
        moteur.setVoltage(U)  # Application de la tension U

        # Ajout au monde simulé
        monUnivers.addEntity(particule)
        monUnivers.addEntity(moteur)

        # === Générateurs de forces ===
        force_moteur = ForceMoteur(moteur, particule)                   # Force tangentielle liée au couple moteur
        force_ressort = SpringDamperMoteur(moteur, particule, k=50, c=1)  # Liaison élastique entre le moteur et la particule
        monUnivers.addGenerators(force_moteur, force_ressort)

        # === Simulation pendant 60 secondes temps simulé ===
        monUnivers.simulateFor(60)

        # === Récupération des résultats à la fin de la simulation ===
        distance = (particule.getPosition() - moteur.p).mod()  # Norme de la distance finale
        distances.append(distance)

        omegas.append(moteur.getSpeed())  # Vitesse de rotation finale

    # === Affichage du graphe final ===
    plt.figure()
    plt.plot(omegas, distances, 'o-', color='blue')
    plt.xlabel("Vitesse de rotation Ω (rad/s)")
    plt.ylabel("Distance finale d (unités)")
    plt.title("Distance finale entre le moteur et la particule en fonction de la vitesse")
    plt.grid(True)
    plt.show()
