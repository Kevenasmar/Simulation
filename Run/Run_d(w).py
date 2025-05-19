from Classes.vector3D import Vector3D as V3D
from Classes.MoteurCC import MoteurCC
from Classes.Forces import *
from matplotlib import pyplot as plt
from Classes.Univers_Officiel import Univers


if __name__ == '__main__':

    # Paramètres physiques du moteur
    R = 1.0
    L = 0.001
    k_c = 0.01
    k_e = 0.01
    J = 0.01
    f = 0.1
    P = V3D(50, 50, 0)

    # Liste des tensions à tester
    tensions = list(range(20, 221, 20))

    # Résultats
    distances = []
    omegas = []

    # Boucle sur chaque tension
    for U in tensions:
        # Crée un nouvel univers pour chaque tension
        monUnivers = Univers(game=False)

        # Crée une particule et un moteur
        particule = Particule(p0=V3D(40, 50, 0))
        moteur = MoteurCC(R, L, k_c, k_e, J, f, p=P)
        moteur.setVoltage(U)

        # Ajoute les entités
        monUnivers.addEntity(particule)
        monUnivers.addEntity(moteur)

        # Ajoute les forces
        force_moteur = ForceMoteur(moteur, particule)
        force_ressort = SpringDamperMoteur(moteur, particule, k=50, c=1)
        monUnivers.addGenerators(force_moteur, force_ressort)

        # Simule pendant 10 secondes
        monUnivers.simulateFor(60)

        # Calcule la distance entre le moteur et la particule à la fin
        distance = (particule.getPosition() - moteur.p).mod()
        distances.append(distance)

        # Stocke la vitesse de rotation finale du moteur
        omegas.append(moteur.getSpeed())

    # Affiche le graphe : distance en fonction de la vitesse de rotation
    plt.figure()
    plt.plot(omegas, distances, 'o-', color='blue')
    plt.xlabel("Vitesse de rotation Ω (rad/s)")
    plt.ylabel("Distance finale d (unités)")
    plt.title("Distance vs Vitesse de rotation")
    plt.grid(True)
    plt.show()


        

