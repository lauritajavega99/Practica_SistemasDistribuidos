"""Map Manager client class"""
#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# pylint: disable=W1203
# pylint: disable=W0613

import json
import sys
import os
import Ice
Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

ROOM = 'room'
DATA = 'data'

class Client(Ice.Application):
    """Class Client"""
    def run(self, argv):
        try:
            proxy, token, opcion, fichero = sys.argv[1:]
            proxy_comm = self.communicator().stringToProxy(proxy)
            room_manager = IceGauntlet.RoomManagerPrx.checkedCast(proxy_comm)
            if not room_manager:
                raise RuntimeError('Invalid proxy')
        except ValueError:
            print('Command arguments: {} <proxy> <token> <opcion> <Fichero/Nombre_Mapa>'.format(
                os.path.basename(sys.argv[0]))
            )
            sys.exit(1)
        try:
            if opcion == "-u":
                if os.path.exists("assets/"+fichero+".json"):
                    with open("assets/"+fichero+".json", 'r') as contents:
                        room= json.load(contents)
                    try:
                        room_name = room[ROOM]
                        room_data = room[DATA]
                    except:
                        raise IceGauntlet.WrongRoomFormat()
                    string_room = '{"data": ' + str(room_data) + ', "room": "' + room_name + '"}'
                    room_manager.publish(token, string_room)
                    print("*** SE HA PUBLICADO CON EXITO ***")
                else:
                    print("No se encontró assets/"+fichero+".json, introducelo de nuevo")
            if opcion == "-d":
                room_manager.remove(token, fichero)
                print("*** SE HA ELIMINADO CON EXITO ***")
            if opcion not in ["-u","-d"]:
                print('Error al seleccionar la opción, por favor escriba una opción válida')
        except ValueError:
            print('Error al seleccionar la opción, por favor escriba una opción válida')
        return 0
if __name__ == '__main__':
    app = Client()
    sys.exit(app.main(sys.argv))
    