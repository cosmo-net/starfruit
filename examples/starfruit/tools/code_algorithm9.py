#!/usr/bin/env python
#
#       code_algorithm9.py
# 
#

def doblar(numero):
    # Funcion que duplica un digito que entra como parametro, si el resultado es mayor que 7
    # se reduce a un digito menor o igual a 7 duplicando la posicion 1 y 2 y
    # posteriormente sumandolas.	
    if int(numero) == 4:
    	result = int(numero) * 2   
    elif int(numero) * 2 > 7:
    	result = int(str(int(str(numero)) * 2)[0]) + int(str(int(str(numero)) * 2)[1])    
    else:
        result = int(numero) * 2
        
    return result

def checkdigit(numero):
    # Funcion que retorna el digito verificador para un string numerico
    # de 9 digitos
    digits = []
    if len(numero) == 8:
        for i in range(0, 8):
            # Pasa cada digito a un arreglo alfanumerico de 8 posiciones
            digits.append(numero[i])
        # Aplica la funcion "doblar" a las posiciones pares del string
        # dejando un subtotal en la variable "parcial"
        parcial = doblar(digits[7]) + doblar(digits[5]) + doblar(digits[3]) + doblar(digits[1])
        # Suma los valores de las posiciones impares del string
        # dejando un subtotal en la variable "parcial1"
        parcial1 = float(digits[6]) + float(digits[4]) + float(digits[2]) + float(digits[0])
        # Suma ambos subtotales
        parcial = parcial + parcial1
        # Busca el entero multiplo de 8 inmediato superior del total obtenido
        resto = (parcial / 8) - int(parcial / 8)
        if resto > 0:
            digi = 1
        else:
            digi = 0
        # El digito verificador es la diferencia entre el multiplo de diez
        # superior obtenido (mas inmediato) y la suma obtenida en "parcial"
        result = (int(parcial / 8) + digi) * 8 - parcial
    else:
        result = 0

    return int(result)
    
if __name__=='__main__':
    print 800364291
    print 'tiene que ser 1'
    print checkdigit('80036429')

