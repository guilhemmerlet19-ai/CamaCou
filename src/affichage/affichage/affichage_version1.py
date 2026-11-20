import threading

import numpy as np
import customtkinter as ctk
from PIL import Image as PILImage

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image


# =============================================================================
# LA CUISINE : le nœud ROS (tourne dans le thread secondaire)
# =============================================================================
class NoeudAffichage(Node):
    def __init__(self):
        super().__init__("affichage")

        # Le passe-plat
        self.derniere_image = None
        self.numero_image = 0               # augmente à chaque nouvelle image
        self.verrou = threading.Lock()

        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT) 
        self.create_subscription(Image, "/sonar/image_cartesian_8_bit",
                                 self.callback_image, qos)

    def callback_image(self, msg):
        # Appelé par ROS (thread cuisine) à chaque image reçue
        with self.verrou:
            self.derniere_image = msg
            self.numero_image += 1


# =============================================================================
# LE SERVEUR : la fenêtre (tourne dans le thread principal)
# =============================================================================
class CamacouApp(ctk.CTk):
    def __init__(self, noeud):
        super().__init__()
        self.noeud = noeud
        self.dernier_numero_affiche = 0

        self.title("Camacou")
        # Plein écran (Échap pour en sortir)
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.grid_columnconfigure(0, weight=1)  # gauche : grandit
        self.grid_columnconfigure(1, weight=0)  # droite : largeur fixe
        self.grid_rowconfigure(0, weight=1)

        # Cadre de gauche : l'image sonar
        self.cadre_gauche = ctk.CTkFrame(self)
        self.cadre_gauche.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.label_image = ctk.CTkLabel(self.cadre_gauche,
                                        text="En attente de l'image sonar…",
                                        font=("Arial", 20))
        self.label_image.place(relx=0.5, rely=0.5, anchor="center")

        # Cadre de droite : le paramétrage de la caméra (étapes suivantes)
        self.cadre_droite = ctk.CTkFrame(self, width=320)
        self.cadre_droite.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.label_droite = ctk.CTkLabel(self.cadre_droite, text="Paramétrage cam",
                                         font=("Arial", 20))
        self.label_droite.place(relx=0.5, rely=0.5, anchor="center")

        # On lance la surveillance du passe-plat
        self.rafraichir_image()

    def rafraichir_image(self):
        # 1) Regarder le passe-plat (rapidement, avec le verrou)
        with self.noeud.verrou:
            msg = self.noeud.derniere_image
            numero = self.noeud.numero_image

        # 2) Nouveau plat ? On le sert
        if msg is not None and numero != self.dernier_numero_affiche:
            self.dernier_numero_affiche = numero

            # Message ROS (octets bruts) -> tableau 2D -> image PIL
            arr = np.frombuffer(msg.data, dtype=np.uint8)
            arr = arr.reshape(msg.height, msg.step)[:, :msg.width]
            img = PILImage.fromarray(arr)

            # Image PIL -> image CustomTkinter -> dans le label
            self.ctk_img = ctk.CTkImage(light_image=img, dark_image=img,
                                        size=(img.width, img.height))
            self.label_image.configure(image=self.ctk_img, text="")

        # 3) Revenir voir dans 33 ms
        self.after(33, self.rafraichir_image)


# =============================================================================
# MAIN : on embauche les deux employés
# =============================================================================
def main():
    rclpy.init()
    noeud = NoeudAffichage()                       # la cuisine

    t = threading.Thread(target=rclpy.spin, args=(noeud,), daemon=True)
    t.start()                                      # le cuisinier commence

    ctk.set_appearance_mode("dark")
    app = CamacouApp(noeud)                        # le serveur
    app.mainloop()                                 # bloque jusqu'à la fermeture

    # Fenêtre fermée : on range
    noeud.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()