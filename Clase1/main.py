numeros = [1, 2, 3, 4, 5]

#Eventos que se le pueden aplicar a una lista
#append: Agrega un elemento al final de la lista
numeros.append(6)
print("Después de append:", numeros)    
#Output: Después de append: [1, 2, 3, 4, 5, 6]  
#insert: Agrega un elemento en una posición específica
numeros.insert(0, 0)
print("Después de insert:", numeros)    
#Output: Después de insert: [0, 1, 2, 3, 4, 5, 6]  
#remove: Elimina la primera aparición de un elemento
numeros.remove(3)
print("Después de remove:", numeros)    
#Output: Después de remove: [0, 1, 2, 4, 5, 6]  
#pop: Elimina y devuelve el último elemento de la lista
ultimo = numeros.pop()
print("Después de pop:", numeros, "Elemento eliminado:", ultimo)    
#Output: Después de pop: [0, 1, 2, 4, 5] Elemento eliminado: 6  
#clear: Elimina todos los elementos de la lista
numeros.clear()
print("Después de clear:", numeros)    
#Output: Después de clear: []  
#sort: Ordena los elementos de la lista
numeros = [3, 1, 4, 2]
numeros.sort()
print("Después de sort:", numeros)    
#Output: Después de sort: [1, 2, 3, 4]  
#reverse: Invierte el orden de los elementos en la lista
numeros.reverse()
print("Después de reverse:", numeros)    
#Output: Después de reverse: [4, 3, 2, 1]  
#index: Devuelve el índice de la primera aparición de un elemento
indice = numeros.index(3)
print("Índice de 3:", indice)    
#Output: Índice de 3: 1  
#count: Cuenta cuántas veces aparece un elemento en la lista
conteo = numeros.count(2)
print("Conteo de 2:", conteo)    
#Output: Conteo de 2: 1  
#extend: Agrega los elementos de otra lista al final de la lista actual
numeros.extend([5, 6, 7])
print("Después de extend:", numeros)    
#Output: Después de extend: [4, 3, 2, 1, 5, 6, 7]           