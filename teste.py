lista = [(10, 10)]
soma = (1, 0)

resultado = (
    lista[0][0] + soma[0],
    lista[0][1] + soma[1]
)

lista.remove(lista[0])
lista.insert(0, resultado)
print(lista)