class casa:

    def __init__(self, color):
        self.color = color
        self.comsumo_de_luz = 0
        self.consumo_de_agua = 0

    def pintar(self, nuevo_color):
        self.color = nuevo_color

    def prender_luz(self, horas):
        self.comsumo_de_luz += horas * 60

    def usar_agua(self, litros):
        self.consumo_de_agua += litros

    def tocar_timbre(self):
        print("Ding Dong!")
        self.comsumo_de_luz += 1  # Consumo de luz por tocar el timbre

mi_casa = casa("rojo")
print(mi_casa.color)  # Salida: rojo

print(mi_casa.consumo_de_agua)
mi_casa.tocar_timbre()  # Salida: Ding Dong!
print("consumo de luz: ",mi_casa.comsumo_de_luz)  # Salida: 1

#herencia 

class Mansion(casa):
    def prender_luz(self):
        self.comsumo_de_luz += 100
    
    def usar_agua(self):
        self.consumo_de_agua += 1000

    def tocar_timbre(self):
        print("Ding Dong! Bienvenido a la mansion")
        self.comsumo_de_luz += 5  # Consumo de luz por tocar el timbre en la mansion

mi_mansion = Mansion("blanco")
print("Mi mansion es de color: ", mi_mansion.color)  # Salida: blanco
mi_mansion.tocar_timbre()  # Salida: Ding Dong! Bienvenido a la mansion
print("consumo de luz en la mansion: ", mi_mansion.comsumo_de_luz)  # Salida: 5
mi_mansion.prender_luz()
print("consumo de luz en la mansion despues de prender luz: ", mi_mansion.comsumo_de_luz)  # Salida: 105
mi_mansion.usar_agua()
print("consumo de agua en la mansion: ", mi_mansion.consumo_de_agua)  # Salida: 1000    
mi_mansion.pintar("azul")
print("Mi mansion ahora es de color: ", mi_mansion.color)  # Salida: azul