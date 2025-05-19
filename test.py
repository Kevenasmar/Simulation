from Univers_Officiel import Univers
from Barre2D import Barre
from vector3D import Vector3D as V3D
from Forces import *
import matplotlib.pyplot as plt



if __name__ == "__main__":
    theta2_tab = []
    U = Univers(game=True)

    # Particule fixe : centre de rotation
    p1 = Particule(fix=True, p0 = V3D(30,30,0))
    p2 = Particule(fix=True, p0 = V3D(60,30,0))
    p3 = Particule(fix=False, p0 = V3D(65,30,0))
    U.addEntity(p1)
    U.addEntity(p2)
    U.addEntity(p3)
    
    b1 = Barre(mass = 1, p0 = V3D(35,30,0),t0 = 0, long = 10)
    U.addEntity(b1)

    # Forces
    gravity = Gravity()
    pivot = Pivot(b1,p1,-1,k=1000, c= 100)
    link = Link(p2,p3)
    U.addGenerators(gravity, pivot, link)

    U.simulateRealTime()

    theta2_tab = link.theta()

    time = np.linspace(0, len(theta2_tab) * U.step, len(theta2_tab))

    plt.figure()
    plt.plot(time, theta2_tab, label="Angle between p2 and p3")
    plt.xlabel("Time (s)")
    plt.ylabel("Angle (rad)")
    plt.title("θ₂(t) between p2 and p3")
    plt.grid()
    plt.legend()
    plt.show()

        

    # U.plot()