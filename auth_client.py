#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Authentication client class"""
import hashlib
import sys
import getpass
import os
import Ice
Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

def convertir_hash (password):
    """Metodo para calcular el hash"""
    hash_object = hashlib.sha256(password.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig

class Client(Ice.Application):
    """Class Client"""
    def run(self,argv):
        try:
            opcion, usuario, proxy = argv[1:]
            proxy_comm = self.communicator().stringToProxy(proxy)
            authentication = IceGauntlet.AuthenticationPrx.checkedCast(proxy_comm)
            if not authentication:
                raise RuntimeError('Invalid proxy')
        except ValueError:
            print('Command arguments: {} <opcion> <user> <proxy>'.format(
                os.path.basename(sys.argv[0]))
            )
            sys.exit(1)
        try:
            if opcion == "-t":
                print('usuario: '+str(usuario))
                password = getpass.getpass('Introduce el password:')
                passw_hash = convertir_hash(password)
                token = authentication.getNewToken(usuario,passw_hash)
                print(token)
            if opcion == "-p":
                while 1:
                    try:
                        nuevo_usuario = int(input('Selecciona tu caso: \n1.Usuario sin'
                        ' contraseña\n2.Usuario con contraseña\n'))
                        if nuevo_usuario == 1:
                            pass_actual_hash = None
                            break
                        if nuevo_usuario == 2 :
                            pass_actual = getpass.getpass("Introduce el password actual: ")
                            pass_actual_hash = convertir_hash(pass_actual)
                            break
                        if nuevo_usuario not in [1,2]:
                            print('Error al seleccionar la opción,'
                            'por favor escriba una opción válida')
                    except ValueError:
                        print('Error al seleccionar la opción, por favor escriba una opción válida')
                n_passw = getpass.getpass("Introduce el password nuevo: ")
                n_passw_hash = convertir_hash(n_passw)
                authentication.changePassword(usuario,pass_actual_hash,n_passw_hash)
                print('*** Cambiaste con exito tu contraseña ***')
            if opcion not in ["-t","-p"]:
                print('Error al seleccionar la opción, por favor escriba una opción válida')
        except ValueError:
            print('Error al seleccionar la opción, por favor escriba una opción válida')
        return 0
if __name__ == '__main__':
    app = Client()
    sys.exit(app.main(sys.argv))
