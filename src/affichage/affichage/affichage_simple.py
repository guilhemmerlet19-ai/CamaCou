import customtkinter as ctk

class CamacouApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Camacou")
        # Taille de la fenêtre : plein écran (Échap pour en sortir)
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        
        # TODO : configurer les colonnes (laquelle grandit ?) et la ligne 0
        self.grid_columnconfigure(0, weight=0)  # règle la colonne n°0 (la première, à gauche)
        self.grid_columnconfigure(1, weight=1)  # règle la colonne n°1 (la deuxième)
        self.grid_rowconfigure(0, weight=1)  
        # Cadre de gauche (largeur fixe) + label au centre
        self.cadre_gauche = ctk.CTkFrame(self, width=1250)
        self.cadre_gauche.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.label_gauche = ctk.CTkLabel(self.cadre_gauche, text="Camacou", font=("Arial", 20))
        self.label_gauche.place(relx=0.5, rely=0.5, anchor="center")

        # TODO : cadre de droite + titre
        self.cadre_droite = ctk.CTkFrame(self, width=1250)
        self.cadre_droite.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.label_droite = ctk.CTkLabel(self.cadre_droite, text="Paramétrage cam", font=("Arial", 20))
        self.label_droite.place(relx=0.5, rely=0.5, anchor="center")

def main():
    ctk.set_appearance_mode("dark")
    app = CamacouApp()
    app.mainloop()

if __name__ == "__main__":
    main()