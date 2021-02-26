#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
   ICE Gauntlet Map Server
'''
import random
import sys
import os
import json
import Ice
Ice.loadSlice('icegauntlet.ice')
# pylint: disable=E0401
# pylint: disable=C0413
import IceGauntlet

MAPS_FILE = 'maps.json'
PROXY_JUEGO = 'proxy_juego.json'
CURRENT_TOKEN = 'current_token'
ROOM_DATA = 'roomdata'
ROOM = 'room'
DATA = 'data'

class RoomManagerI(IceGauntlet.RoomManager):
    '''RoomManager servant'''
    def __init__(self,authentication):
        self.authentication = authentication
        self._maps_ = {}
        if os.path.exists(MAPS_FILE):
            with open(MAPS_FILE, 'r') as contents:
                self._maps_ = json.load(contents)
                
    def publish(self, token, room_data, current=None):
        '''Metodo para publicar un mapa'''
        if self.authentication.isValid(token):
            room = json.loads(room_data)
            room_name = room[ROOM]
            room_data = room[DATA]
            if not room_name in self._maps_:
                print("EL MAPA SE HA AÑADIDO")
                self._maps_[room_name] = {}
                self._maps_[room_name][CURRENT_TOKEN] = token
                self._maps_[room_name][ROOM_DATA] = room_data
                self.__commit__()
            else:
                raise IceGauntlet.RoomAlreadyExists()
        else:
            raise IceGauntlet.Unauthorized()

    def remove(self, token, room_name, current=None):
        '''Metodo para borrar un mapa'''
        if self.authentication.isValid(token):
            if room_name in self._maps_:
                print("EL MAPA SE HA ELIMINADO")
                if self._maps_[room_name].get(CURRENT_TOKEN, None) == token:
                    del self._maps_[room_name]
                    self.__commit__()
                else:
                    print("TOKEN NO ASOCIADO AL MAPA")
                    raise IceGauntlet.Unauthorized()
            else:
                raise IceGauntlet.RoomNotExists()
        else:
            raise IceGauntlet.Unauthorized()
    def __commit__(self):
        with open(MAPS_FILE, 'w') as contents:
            json.dump(self._maps_, contents, indent=4, sort_keys=True)

class DungeonI(IceGauntlet.Dungeon):
    '''Game servant'''
    def __init__(self):
        self._maps_ = {}
        if os.path.exists(MAPS_FILE):
            with open(MAPS_FILE, 'r') as contents:
                self._maps_ = json.load(contents)

    def getRoom(self, current = None):
        '''Metodo para devolver mapas'''
        room_data = ''
        nombre_mapa = ''
        string_room = ''
        try:
            lista = list(self._maps_.keys())
            nombre_mapa = random.choice(lista)
            room_data = self._maps_[nombre_mapa].get(ROOM_DATA, None)
            string_room = '{"data": ' + str(room_data) + ', "room": "' + nombre_mapa + '"}'
        except:
            print('*** NO HAY MAPAS ***')
            raise IceGauntlet.RoomNotExists()
        return string_room

class Server(Ice.Application):
    '''Servidor de mapas'''
    def run(self,args):
        try:
            proxy = sys.argv[1]
        except ValueError:
            print('Command arguments: {} <proxy>'.format(
                os.path.basename(sys.argv[0]))
            )
            sys.exit(1)
        proxy_comm = self.communicator().stringToProxy(proxy)
        authentication = IceGauntlet.AuthenticationPrx.checkedCast(proxy_comm)
        if not authentication:
            raise RuntimeError('Invalid proxy')
        sirviente_juego = DungeonI()
        sirviente_mapas = RoomManagerI(authentication)
        adapter = self.communicator().createObjectAdapter('ServerAdapter')
        proxy_juego = adapter.addWithUUID(sirviente_juego)
        proxy_mapa = adapter.addWithUUID(sirviente_mapas)
        self.escribir_proxy_juego(proxy_juego)
        print(str(proxy_mapa))
        adapter.activate()
        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()
        
    def escribir_proxy_juego(self, proxy_juego):
        '''Metodo para escribir el proxy de juego'''
        self.proxy = {}
        if os.path.exists(PROXY_JUEGO):
            with open(PROXY_JUEGO, 'r') as contents:
                self.proxy = json.load(contents)
        self.proxy["proxy"] = {}
        self.proxy["proxy"] = str(proxy_juego)
        with open(PROXY_JUEGO, 'w') as contents:
            json.dump(self.proxy, contents, indent=4, sort_keys=True)

if __name__ == '__main__':
    app = Server()
    sys.exit(app.main(sys.argv))
