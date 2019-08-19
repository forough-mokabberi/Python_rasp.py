
import sys
import serial
import time
import socket
import multiprocessing
import threading
import xml.etree.ElementTree as etree
from threading import Event, Thread
from xml.etree import ElementTree
from xml.dom import minidom
from timeit import default_timer as timer
import select
import os
import zlib
import binascii
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3,GPIO.OUT)
GPIO.setup(5,GPIO.OUT)
# ****************************************************
# *********************  # variables  ****************
# ****************************************************



TCP_IP = '192.168.1.64'
TCP_PORT = 11000
BUFFER_SIZE = 1024
MACHINES = []
Current_Status_Flag = 0
DATA_Ready = 'Deactivate'
List_Flag=0
Receive_Flag = 0
DATA_Ready_Flag=0
Config_Flag=0
Disable_Flag=0
Enable_Flag = 0
ZEROProduction_Flag=0
Serial_Flag=0
RADIO_ERROR_COUNTER = 0
RADIO_ERROR_COUNTER_1 = 0

# ****************************************************
# *********************  create the UART  ************
# ****************************************************

uart = serial.Serial(

    port='/dev/ttyS0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.1
)

print('Communication Management \n')
print("LOADING...")
time.sleep(5)

# ****************************************************
# *******  First communication management  ***********
# ****************************************************
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.bind((TCP_IP, TCP_PORT))
except socket.error as e:
    print('error blid')
    print(e)
    f = open('error_log.txt', 'w')
    f.write("SERVER BIND ERROR ")  # write it to a file called tag_data.xml
    f.close()
    #os.system("sudo reboot")
    sys.stdout.close()

server.listen(5)
print('MACHINE STATUS FIRMWARE 1.0.0 \n')
print('SOCKET WAITING FOR CLIENT \n')

global conn
(conn, addr) = server.accept()
server.settimeout(1)

print('...CONNECTED \n')
ERROR_COMMUNI_COUNTER=0


# ****************************************************
# *******  Timeout communication management  *********
# ****************************************************
def communication_watchdog():

     global WDG_REFLESH

     while(Receive_Flag==1):

         WDG_REFLESH = WDG_REFLESH + 1

         if WDG_REFLESH > 1000:
             print("Timeout communication management error")
             f = open('error_log.txt', 'w')
             f.write("Timeout communication management error ")  # write it to a file called tag_data.xml
             f.close()
             #os.system("sudo reboot")

     return


# ****************************************************
# ***************** First  commonunication  *****#****
# ****************************************************
def First_communication():

    global Current_Status_Flag
    global List_Flag
    global Receive_Flag
    global DATA_Ready
    global MACHINES
    global WDG_REFLESH
    global ERROR_NACK_COUNTER_DATA_RC
    global ERROR_NACK_COUNTER_CONFIG
    global ERROR_NACK_COUNTER_DISABLE
    global ERROR_NACK_COUNTER_ENABLE
    ERROR_FIRST_COMMUNICATION_COUNTER = 0

    while (Current_Status_Flag == 0):

        print(Current_Status_Flag)

        print('Enter First comm')

        ready = select.select([conn], [], [], 5)
        if ready[0]:
          # awaiting for FRST

          data_received = conn.recv(4)

          print('Data RECEVIED = \n')
          print(data_received)

          # process your message
          if data_received == b'FRST':
             print('enter if')
             conn.send(('FRST').encode())
             print('Socket waiting for xml \n')

             time.sleep(1)

             # receive the size of XML file
             ready = select.select([conn], [], [], 5)

             if ready[0]:

                size_xml = conn.recv(6)

                time.sleep(.2)

                try:
                   size = int(size_xml)
                   conn.send(('ACK').encode())
                   time.sleep(1)
                   ready = select.select([conn], [], [], 10)
                   print("wait for XML")
                   if ready[0]:
                       data_received = conn.recv(size)
                       conn.send(('ACK').encode())
                       print('RECEVIED XML')
                       print(data_received)
                       f = open('machine.xml', 'w')
                       f.write((data_received).decode())  # write it to a file called tag_data.xml
                       f.close()
                       prev = 0
                       for eachline in open('machine.xml', 'rb'):
                           prev = zlib.crc32(eachline, prev)
                       print("CRC")
                       print((hex(prev)))

                       ready = select.select([conn], [], [], 5)
                       print("wait for CRC32")
                       if ready[0]:
                           data_received_crc = conn.recv(10)
                           print(data_received_crc)
                           if( (data_received_crc).decode() == str(hex(prev))):
                               time.sleep(.2)
                               data = 'ACK'
                               conn.send(data.encode())
                               print('SEND ACK')
                               print('write XML')
                               print ('END First XML')
                               break
                           else:
                               conn.send(('NACK').encode())
                               f = open('error_log.txt', 'w')
                               f.write("FIRST COMMUNICATION = Does not Received Correct CRC32")  # write it to a file called tag_data.xml
                               f.close()
                               os.system("sudo reboot")
                       else:
                           conn.send(('NACK').encode())
                           f = open('error_log.txt', 'w')
                           f.write("FIRST COMMUNICATION = Does not Received CRC32")  # write it to a file called tag_data.xml
                           f.close()
                           os.system("sudo reboot")
                   else:
                       conn.send(('NACK').encode())
                       f = open('error_log.txt', 'w')
                       f.write("FIRST COMMUNICATION = Does not Received XML")  # write it to a file called tag_data.xml
                       f.close()
                       os.system("sudo reboot")
                except:
                     conn.send(('NACK').encode())
                     #pass  1
                     f = open('error_log.txt', 'w')
                     f.write("FIRST COMMUNICATION = Does not Received correct Size")  # write it to a file called tag_data.xml
                     f.close()
                     os.system("sudo reboot")

             else:
                  #pass    2
                  ERROR_FIRST_COMMUNICATION_COUNTER = ERROR_FIRST_COMMUNICATION_COUNTER + 1
                  print ("ERROR +++++++++")
                  if ERROR_FIRST_COMMUNICATION_COUNTER == 3:
                      f = open('error_log.txt', 'w')
                      f.write("FIRST COMMUNICATION = Does not Received Size")  # write it to a file called tag_data.xml
                      f.close()
                      os.system("sudo reboot")

             # receive the size of STATUS XML file
             ready = select.select([conn], [], [], 5)

             if ready[0]:

                 size_xml = conn.recv(6)

                 time.sleep(.2)

                 try:
                     size = int(size_xml)
                     conn.send(('ACK').encode())
                     time.sleep(1)
                     ready = select.select([conn], [], [], 10)
                     print("wait for SATATUS XML")
                     if ready[0]:
                         data_received = conn.recv(size)
                         conn.send(('ACK').encode())
                         print('RECEVIED STATUS XML')
                         print(data_received)
                         f = open('status.xml', 'w')
                         f.write((data_received).decode())  # write it to a file called tag_data.xml
                         f.close()
                         prev = 0
                         for eachline in open('status.xml', 'rb'):
                             prev = zlib.crc32(eachline, prev)
                         print("STATUS CRC")
                         print((hex(prev)))

                         ready = select.select([conn], [], [], 5)
                         print("wait for STATUS CRC32")
                         if ready[0]:
                             data_received_crc = conn.recv(10)
                             print(data_received_crc)
                             if ((data_received_crc).decode() == str(hex(prev))):
                                 time.sleep(.2)
                                 data = 'ACK'
                                 conn.send(data.encode())
                                 print('SEND ACK')
                                 print('write STATUS XML')
                                 Current_Status_Flag = 1
                                 print(Current_Status_Flag)
                                 DATA_Ready = 'Deactivate'
                                 List_Flag = 1
                                 # Receive_Flag = 1
                                 print ('END STATUS XML')
                                 break
                             else:
                                 conn.send(('NACK').encode())
                                 f = open('error_log.txt', 'w')
                                 f.write(
                                     "FIRST COMMUNICATION = Does not Received Correct STATUS CRC32")  # write it to a file called tag_data.xml
                                 f.close()
                                 os.system("sudo reboot")
                         else:
                             conn.send(('NACK').encode())
                             f = open('error_log.txt', 'w')
                             f.write(
                                 "FIRST COMMUNICATION = Does not Received STATUS CRC32")  # write it to a file called tag_data.xml
                             f.close()
                             os.system("sudo reboot")
                     else:
                         conn.send(('NACK').encode())
                         f = open('error_log.txt', 'w')
                         f.write(
                             "FIRST COMMUNICATION = Does not Received STATUS XML")  # write it to a file called tag_data.xml
                         f.close()
                         os.system("sudo reboot")
                 except:
                     conn.send(('NACK').encode())
                     # pass  1
                     f = open('error_log.txt', 'w')
                     f.write(
                         "FIRST COMMUNICATION = Does not Received correct STATUS XML Size")  # write it to a file called tag_data.xml
                     f.close()
                     os.system("sudo reboot")

             else:
                 # pass    2
                 ERROR_FIRST_COMMUNICATION_COUNTER = ERROR_FIRST_COMMUNICATION_COUNTER + 1
                 print ("ERROR +++++++++")
                 if ERROR_FIRST_COMMUNICATION_COUNTER == 3:
                     f = open('error_log.txt', 'w')
                     f.write(
                         "FIRST COMMUNICATION = Does not Received STATUS XML Size")  # write it to a file called tag_data.xml
                     f.close()
                     os.system("sudo reboot")
        else:
             #pass  3
             f = open('error_log.txt', 'w')
             f.write("FIRST COMMUNICATION = Does not Received FRST")  # write it to a file called tag_data.xml
             f.close()
             os.system("sudo reboot")
    #    time.sleep(3)
    print('Waiting for Data')

    ######## INIT ERROR VARIABLES ##########
    ERROR_NACK_COUNTER_DATA_RC = 0
    ERROR_NACK_COUNTER_CONFIG = 0
    ERROR_NACK_COUNTER_DISABLE = 0
    ERROR_NACK_COUNTER_ENABLE = 0
    WDG_REFLESH = 0
    ########################################
    return

# ****************************************************
# #*****************  Receive_data  ****************
# #****************************************************

def Receive_data():

  global WDG_REFLESH
  global Receive_Flag
  global DATA_Ready_Flag
  global Config_Flag
  global Disable_Flag
  global Enable_Flag
  global ZEROProduction_Flag
  global List_Flag
  global Serial_Flag
  global Serial_Flag2
  global EXCEPT_COUNTER_RECEIVE_DATA
  Receive_Flag = 1

  while (Receive_Flag==1):


        print('Enter Receive_data Function')
        print ("WDG= ")
        print(WDG_REFLESH)
        try:
            data_received = conn.recv(16)
            #time.sleep(0.2)
            print(data_received)

            if (data_received == b'DATA_Ready'):
                WDG_REFLESH = 0
                Serial_Flag = 0
                Data_ready()

            elif data_received == b'Config':
                WDG_REFLESH = 0
                Serial_Flag2 = 0
                Config()

            elif data_received == b'Disable':
               WDG_REFLESH = 0
               Serial_Flag2 = 0
               Receive_Flag = 0
               Disable()

            elif data_received == b'Enable':
               WDG_REFLESH = 0
               Serial_Flag2 = 0
               Receive_Flag = 0
               Enable()


            elif data_received == b'ZEROProduction':
               WDG_REFLESH = 0
               Serial_Flag2 = 0
               Receive_Flag = 0
               Zero_Production_function()

            elif data_received == b'Status':
                WDG_REFLESH = 0
                Serial_Flag2 = 0
                Status_function()

        except:
            pass

        WDG_REFLESH = WDG_REFLESH + 1

        if WDG_REFLESH > 1000:
            print("Timeout communication management error")
            f = open('error_log.txt', 'w')
            f.write("Timeout communication management error ")  # write it to a file called tag_data.xml
            f.close()
            os.system("sudo reboot")


  return

# ****************************************************
# #*****************  Data_ready  ****************
# #****************************************************
def Data_ready():

   global DATA_Ready_Flag
   global DATA_Ready
   global Receive_Flag
   global Serial_Flag
   global ERROR_NACK_COUNTER_DATA_RC
   print("task dr")
   print(DATA_Ready_Flag)
   DATA_Ready_Flag = 1
   Serial_Flag = 0
   print('Enter Data_ready Function')
   # SEND ACTIVE
   conn.send((DATA_Ready).encode())
   print(DATA_Ready)
   print('DATA_Ready sended')

   if (DATA_Ready == 'Activate'):
       Receive_Flag = 0
       start=timer()
       ready = select.select([conn], [], [], 5)
       end=timer()
       print(end-start)
       print("ready: ")
       print(ready)
       if ready[0]:
          # receive ACK OR NACK
          data_received_2 = conn.recv(4)
          print(data_received_2)

          if (data_received_2 == b"ACK"):
             # SEND SIZE
             conn.send("SIZE".encode())
             print('SENDED SIZE')

             ready = select.select([conn], [], [], 5)
             if ready[0]:
                    # RECEIVE ACK SIZE
                     data_received_3 = conn.recv(4)
                     print(data_received_3)

                     if(data_received_3 == b"ACK"):
                         # OPEN XML
                        f = open('machine.xml')
                        F_all = f.read()
                        xml_str = str(F_all)
                         # print(xml_str.encode())
                        Length_XML = len(xml_str)
                        Length_XML_str = str(Length_XML)
                        print(Length_XML_str)
                        conn.send(Length_XML_str.encode())
                        print("send size number")
                        # SEND XML SIZE
                        # WAIT FOR ACK
                        ready = select.select([conn], [], [], 5)
                        if ready[0]:
                            data_received_4 = conn.recv(4)
                            print(data_received_4)
                            if(data_received_4== b"ACK"):
                               time.sleep(0.01)
                               # SEND XML
                               conn.send(xml_str.encode())
                               print("send xml")
                               prev=0
                               for eachline in open('machine.xml','rb'):
                                   prev = zlib.crc32(eachline,prev)
                               print("CRC")
                               print((hex(prev)))
                               conv_prev= (hex(prev)).lower()
#                               conv_prev = 0xfce2134
                               conn.send(conv_prev.encode())
                               print("send crc")

                               ready = select.select([conn], [], [], 6)
                               if ready[0]:
                                   data_received_5 = conn.recv(4)
                                   print(data_received_5)
                                   if(data_received_5 == b"ACK"):

                                      ready = select.select([conn], [], [], 6)

                                      if ready[0]:
                                          data_received_6 = conn.recv(4)
                                          print(data_received_6)
                                          if (data_received_6 == b"ACK"):
                                              DATA_Ready_Flag = 0
                                              ERROR_NACK_COUNTER_DATA_RC = 0
                                          else:
                                              ERROR_NACK_COUNTER_DATA_RC = ERROR_NACK_COUNTER_DATA_RC + 1
                                              print("did not received ACK")
                                              #  ERROR 4
                                              if ERROR_NACK_COUNTER_DATA_RC == 3:
                                                  f = open('error_log.txt', 'w')
                                                  f.write(
                                                      "DATA READ = ERROR 4")  # write it to a file called tag_data.xml
                                                  f.close()
                                                  os.system("sudo reboot")
                                      else:
                                          ERROR_NACK_COUNTER_DATA_RC = ERROR_NACK_COUNTER_DATA_RC + 1
                                          print("did not received ACK")
                                          #  ERROR 4
                                          if ERROR_NACK_COUNTER_DATA_RC == 3:
                                              f = open('error_log.txt', 'w')
                                              f.write("DATA READ = ERROR 4")  # write it to a file called tag_data.xml
                                              f.close()
                                              os.system("sudo reboot")
                                   else:
                                       ERROR_NACK_COUNTER_DATA_RC = ERROR_NACK_COUNTER_DATA_RC + 1
                                       print("did not received ACK")
                                       #  ERROR 4
                                       if ERROR_NACK_COUNTER_DATA_RC == 3:
                                           f = open('error_log.txt', 'w')
                                           f.write("DATA READ = ERROR 4")  # write it to a file called tag_data.xml
                                           f.close()
                                           os.system("sudo reboot")

                            else:
                                ERROR_NACK_COUNTER_DATA_RC = ERROR_NACK_COUNTER_DATA_RC + 1
                                print("did not received ACK")
                                #  ERROR 4
                                if ERROR_NACK_COUNTER_DATA_RC == 3:
                                    f = open('error_log.txt', 'w')
                                    f.write("DATA READ = ERROR 4")  # write it to a file called tag_data.xml
                                    f.close()
                                    os.system("sudo reboot")
                        else:
                            ERROR_NACK_COUNTER_DATA_RC = ERROR_NACK_COUNTER_DATA_RC + 1
                            print("did not received ACK")
                            #  ERROR 4
                            if ERROR_NACK_COUNTER_DATA_RC == 3:
                                f = open('error_log.txt', 'w')
                                f.write("DATA READ = ERROR 4")  # write it to a file called tag_data.xml
                                f.close()
                                os.system("sudo reboot")
                     else:
                         ERROR_NACK_COUNTER_DATA_RC = ERROR_NACK_COUNTER_DATA_RC + 1
                         print("did not received ACK")
                         #  ERROR 4
                         if ERROR_NACK_COUNTER_DATA_RC == 3:
                             f = open('error_log.txt', 'w')
                             f.write("DATA READ = ERROR 4")  # write it to a file called tag_data.xml
                             f.close()
                             os.system("sudo reboot")
             else:
                 ERROR_NACK_COUNTER_DATA_RC = ERROR_NACK_COUNTER_DATA_RC + 1
                 print("did not received ACK")
                 #  ERROR 4
                 if ERROR_NACK_COUNTER_DATA_RC == 3:
                     f = open('error_log.txt', 'w')
                     f.write("DATA READ = ERROR 4")  # write it to a file called tag_data.xml
                     f.close()
                     os.system("sudo reboot")
          else:
              ERROR_NACK_COUNTER_DATA_RC = ERROR_NACK_COUNTER_DATA_RC + 1
              print("did not received ACK")
              #  ERROR 4
              if ERROR_NACK_COUNTER_DATA_RC == 3:
                  f = open('error_log.txt', 'w')
                  f.write("DATA READ = ERROR 4")  # write it to a file called tag_data.xml
                  f.close()
                  os.system("sudo reboot")
       else:
           ERROR_NACK_COUNTER_DATA_RC = ERROR_NACK_COUNTER_DATA_RC + 1
           print("did not received ACK")
           #  ERROR 4
           if ERROR_NACK_COUNTER_DATA_RC == 3:
               f = open('error_log.txt', 'w')
               f.write("DATA READ = ERROR 4")  # write it to a file called tag_data.xml
               f.close()
               os.system("sudo reboot")

   if(DATA_Ready_Flag==1):
      print("enter zero flag")
      DATA_Ready_Flag = 0

   DATA_Ready = 'Deactivate'
   Serial_Flag = 1
   return

# ****************************************************
# #*****************  Config ****************
# #****************************************************
def Config():

      global Config_Flag
      global DATA_Ready
      global Receive_Flag
      global  List_Flag
      global Serial_Flag
      global Serial_Flag2
      global ERROR_NACK_COUNTER_CONFIG
      Config_Flag = 1


      print('Enter Config Function')
      data = 'ACK_config'
      conn.send(data.encode())
      print('ACK_config')
    #      time.sleep(1)
      ready = select.select([conn],[],[],5)
      if ready[0]:
         print('enter try config')
         # receive the size of XML file
         size_xml_new = conn.recv(6)
         try:
             size_new = int(size_xml_new)
             print('size xml config')
             print(size_new)
             data = 'ACK'
             conn.send(data.encode())
             print('SENDED ACK_SIZE')
             time.sleep(0.1)
             ready = select.select([conn], [], [], 6)

             if ready[0]:
                print('dentro config')
                data_received = conn.recv(size_new)
                print(data_received)
                print('New XML RECEIVED')
        #            time.sleep(0.2)
                f = open('machine.xml', 'w')
                f.write(data_received.decode())  # write it to a file called tag_dat
                f.close()
                print('Write new XML')

                prev = 0
                for eachline in open('machine.xml', 'rb'):
                    prev = zlib.crc32(eachline, prev)
                print("CRC")
                print((hex(prev)))

                ready = select.select([conn], [], [], 5)
                if ready[0]:
                    data_received_crc = conn.recv(10)
                    print(data_received_crc)

                    if ((data_received_crc).decode() == str(hex(prev))):
                        data = 'ACK'
                        conn.send(data.encode())
                        print('SENDED ACK Accepted')
                        List_Flag = 1
                        DATA_Ready = 'Deactivate'
                        ERROR_NACK_COUNTER_CONFIG=0
                        Config_Flag = 0
                    else:
                        data = 'NACK'
                        conn.send(data.encode())
                        ERROR_NACK_COUNTER_CONFIG = ERROR_NACK_COUNTER_CONFIG + 1
                        # CONFIGURATION ERROR 1
                        if ERROR_NACK_COUNTER_CONFIG == 3:
                            f = open('error_log.txt', 'w')
                            f.write("CONFIGURATION = ERROR 1")  # write it to a file called tag_data.xml
                            f.close()
                            os.system("sudo reboot")
                else:
                    ERROR_NACK_COUNTER_CONFIG = ERROR_NACK_COUNTER_CONFIG + 1
                    # CONFIGURATION ERROR 1
                    if ERROR_NACK_COUNTER_CONFIG == 3:
                        f = open('error_log.txt', 'w')
                        f.write("CONFIGURATION = ERROR 1")  # write it to a file called tag_data.xml
                        f.close()
                        os.system("sudo reboot")
             else:
                ERROR_NACK_COUNTER_CONFIG = ERROR_NACK_COUNTER_CONFIG + 1
                # CONFIGURATION ERROR 1
                if ERROR_NACK_COUNTER_CONFIG == 3:
                    f = open('error_log.txt', 'w')
                    f.write("CONFIGURATION = ERROR 1")  # write it to a file called tag_data.xml
                    f.close()
                    os.system("sudo reboot")

         except:
            data = 'NACK'
            conn.send(data.encode())
            ERROR_NACK_COUNTER_CONFIG = ERROR_NACK_COUNTER_CONFIG + 1
            # CONFIGURATION ERROR 1
            if ERROR_NACK_COUNTER_CONFIG == 3:
                f = open('error_log.txt', 'w')
                f.write("CONFIGURATION = ERROR 1")  # write it to a file called tag_data.xml
                f.close()
                os.system("sudo reboot")
            pass
      else:
          ERROR_NACK_COUNTER_CONFIG = ERROR_NACK_COUNTER_CONFIG + 1
          # CONFIGURATION ERROR 1
          if ERROR_NACK_COUNTER_CONFIG == 3:
              f = open('error_log.txt', 'w')
              f.write("CONFIGURATION = ERROR 1")  # write it to a file called tag_data.xml
              f.close()
              os.system("sudo reboot")

      if (Config_Flag == 1):

          Config_Flag = 0
      else:
         generate_list()
         DATA_Ready = 'Deactivate'
         Serial_Flag2 = 0

      Receive_Flag = 0
      return

# ****************************************************
# #***************** Disable ****************
# #****************************************************
def Disable():

   global Disable_Flag
   global MACHINES
   global Receive_Flag
   global Serial_Flag
   global DATA_Ready
   global ERROR_NACK_COUNTER_DISABLE
   Disable_Flag = 1

   print('Enter Disable Function')
   data = 'ACK'
   conn.send(data.encode())
   print('SEND ACK1')
  #time.sleep(0.1)
  # receive the size
   Time_out_Disable = 0
   while Time_out_Disable < 3:
         ready = select.select([conn], [], [], 5)
         if ready[0]:
            Disable_SIZE = conn.recv(6)
            # print('Disable vector Size = '+ Diable_SIZE)
            print(Disable_SIZE.decode())
            try:
                Disable_SIZE = int((Disable_SIZE).decode())
                Vector_Disable = []

                for iv in range(Disable_SIZE):
                    ready = select.select([conn], [], [], 5)
                    if ready[0]:
                        Data = conn.recv(3)
                        Vector_Disable.append(Data.decode())
                        print(Data)    #                        print(Vector_Disable)
                    else:
                        f = open('error_log.txt', 'w')
                        f.write("DISABLE = ERROR 1")  # write it to a file called tag_data.xml
                        f.close()
                        os.system("sudo reboot")

                Check_SUM_SUM_Disable = 0
                # Vector_Disable= Vector_Disable.decode()
                print('RECEIVED Disable vector')

                print(Vector_Disable)

                for jd in range((Disable_SIZE) - 1):

                    Check_SUM_SUM_Disable = Check_SUM_SUM_Disable + int(Vector_Disable[jd])

                Value_2_Disable_Checksum = bytearray()
                Value_2_Disable_Checksum[0:2] = (Check_SUM_SUM_Disable).to_bytes(2, byteorder="big")
                Checksum_Disable = 0xFF - (Value_2_Disable_Checksum[1])

                if (Checksum_Disable == int(Vector_Disable[Disable_SIZE - 1])):

                    data = 'ACK'
                    conn.send(data.encode())
                    print('Send ACK')
                    tree = etree.parse('machine.xml')
                    root = tree.getroot()

                    F = 0

                    for nd in range(len(Vector_Disable)):

                        for id in range(len(MACHINES)):

                            if (int(MACHINES[id]) == int(Vector_Disable[nd])):

                                root[id][2].text = 'Disable'
                                F = F + 1
                                print (id)

                                if (F == int(Disable_SIZE - 1)):

                                    Time_out_Disable = 3
                                    tree.write('machine.xml')
                                    Disable_Flag=0
                                    ERROR_NACK_COUNTER_DISABLE = 0
                                    data = 'ACK'
                                    conn.send(data.encode())
                                    print('Send ACK')
                                    break
                                else:
                                    data = 'NACK'
                                    conn.send(data.encode())
                                    Time_out_Disable = Time_out_Disable + 1
                                    ERROR_NACK_COUNTER_DISABLE = ERROR_NACK_COUNTER_DISABLE + 1
                                    # DISABLE ERROR 1
                                    if ERROR_NACK_COUNTER_DISABLE == 3:
                                        f = open('error_log.txt', 'w')
                                        f.write("DISABLE = ERROR 1")  # write it to a file called tag_data.xml
                                        f.close()
                                        os.system("sudo reboot")

                else:
                    Time_out_Disable = Time_out_Disable + 1
                    data = 'NACK'
                    conn.send(data.encode())
                    ERROR_NACK_COUNTER_DISABLE = ERROR_NACK_COUNTER_DISABLE + 1
                    # DISABLE ERROR 1
                    if ERROR_NACK_COUNTER_DISABLE == 3:
                        f = open('error_log.txt', 'w')
                        f.write("DISABLE = ERROR 1")  # write it to a file called tag_data.xml
                        f.close()
                        os.system("sudo reboot")

            except:
                Time_out_Disable = Time_out_Disable + 1
                ERROR_NACK_COUNTER_DISABLE = ERROR_NACK_COUNTER_DISABLE + 1
                # DISABLE ERROR 1
                if ERROR_NACK_COUNTER_DISABLE == 3:
                    f = open('error_log.txt', 'w')
                    f.write("DISABLE = ERROR 1")  # write it to a file called tag_data.xml
                    f.close()
                    os.system("sudo reboot")
                pass
         else:
             Time_out_Disable = Time_out_Disable + 1
             ERROR_NACK_COUNTER_DISABLE = ERROR_NACK_COUNTER_DISABLE + 1
             # DISABLE ERROR 1
             if ERROR_NACK_COUNTER_DISABLE == 3:
                 f = open('error_log.txt', 'w')
                 f.write("DISABLE = ERROR 1")  # write it to a file called tag_data.xml
                 f.close()
                 os.system("sudo reboot")
   if (Disable_Flag== 1):
       Disable_Flag = 0
   DATA_Ready = 'Deactivate'

   return

# ****************************************************
# #***************** Enable ****************
# #****************************************************
def Enable():

    global Enable_Flag
    global MACHINES
    global Receive_Flag
    global Serial_Flag
    global DATA_Ready
    global ERROR_NACK_COUNTER_ENABLE

    Enable_Flag = 1

    print('Enter  Enable Function')
    data = 'ACK'
    conn.send(data.encode())
    print('SEND ACK')
    Time_out_Enable = 0

    while Time_out_Enable < 3:
        ready = select.select([conn], [], [], 5)
        if ready[0]:
           Enable_SIZE = conn.recv(6)
           print(Enable_SIZE.decode())
           try:
            Enable_SIZE = int(Enable_SIZE.decode())
            Vector_Enable = []

            for iv in range(Enable_SIZE):
                ready = select.select([conn], [], [], 5)
                if ready[0]:
                 Data = conn.recv(3)
                 Vector_Enable.append(Data.decode())
                 print(Data)
                else:
                    f = open('error_log.txt', 'w')
                    f.write("ENABLE = ERROR 1")  # write it to a file called tag_data.xml
                    f.close()
                    os.system("sudo reboot")

            Check_SUM_SUM_Enable = 0
            print(Vector_Enable)


            for je in range((Enable_SIZE) - 1):
                Check_SUM_SUM_Enable = Check_SUM_SUM_Enable + int(Vector_Enable[je])

            print(Check_SUM_SUM_Enable)

            Value_2_Enable_Checksum = bytearray()
            Value_2_Enable_Checksum[0:2] = (Check_SUM_SUM_Enable).to_bytes(2, byteorder="big")
            Checksum_Enable = 0xFF - (Value_2_Enable_Checksum[1])

            print(Checksum_Enable)
            print(Vector_Enable[Enable_SIZE - 1])

            if (Checksum_Enable == int(Vector_Enable[Enable_SIZE - 1])):

                data = 'ACK'
                conn.send(data.encode())
                print('SEND2 ACK')

                tree = etree.parse('machine.xml')
                root = tree.getroot()

                Fe = 0

                for ne in range(len(Vector_Enable)):

                    for ie in range(len(MACHINES)):

                        if (int(MACHINES[ie]) == int(Vector_Enable[ne])):
                            root[ie][2].text = 'Enable'
                            Fe = Fe + 1
                            print('Fe')

                if (Fe == int(Enable_SIZE - 1)):

                    Time_out_Enable = 3
                    tree.write('machine.xml')
                    print('Flag')
                    data = 'ACK'
                    conn.send(data.encode())
                    print('Send ACK')
                    Enable_Flag=0
                    ERROR_NACK_COUNTER_ENABLE = 0
                    break

                else:
                    data = 'NACK'
                    conn.send(data.encode())
                    Time_out_Enable = Time_out_Enable + 1
                    print("Error checkcum Enable: ")
                    print(Time_out_Enable)
                    ERROR_NACK_COUNTER_ENABLE = ERROR_NACK_COUNTER_ENABLE + 1
                    # ENABLE ERROR 1
                    if ERROR_NACK_COUNTER_ENABLE == 3:
                        f = open('error_log.txt', 'w')
                        f.write("ENABLE = ERROR 1")  # write it to a file called tag_data.xml
                        f.close()
                        os.system("sudo reboot")

            else:
                Time_out_Enable = Time_out_Enable + 1
                data = 'NACK'
                conn.send(data.encode())
                ERROR_NACK_COUNTER_ENABLE = ERROR_NACK_COUNTER_ENABLE + 1
                # ENABLE ERROR 1
                if ERROR_NACK_COUNTER_ENABLE == 3:
                    f = open('error_log.txt', 'w')
                    f.write("ENABLE = ERROR 1")  # write it to a file called tag_data.xml
                    f.close()
                    os.system("sudo reboot")

           except:
            Time_out_Enable = Time_out_Enable + 1
            ERROR_NACK_COUNTER_ENABLE = ERROR_NACK_COUNTER_ENABLE + 1
            # ENABLE ERROR 1
            if ERROR_NACK_COUNTER_ENABLE == 3:
                f = open('error_log.txt', 'w')
                f.write("ENABLE = ERROR 1")  # write it to a file called tag_data.xml
                f.close()
                os.system("sudo reboot")
            pass
        else:
            Time_out_Enable = Time_out_Enable + 1
            ERROR_NACK_COUNTER_ENABLE = ERROR_NACK_COUNTER_ENABLE + 1
            # ENABLE ERROR 1
            if ERROR_NACK_COUNTER_ENABLE == 3:
                f = open('error_log.txt', 'w')
                f.write("ENABLE = ERROR 1")  # write it to a file called tag_data.xml
                f.close()
                os.system("sudo reboot")

        if (Enable_Flag == 1):
            Enable_Flag = 0
        DATA_Ready = 'Deactivate'
    return

# ****************************************************
# #***************** Zero_Production ****************
# #****************************************************

def Zero_Production_function():

   global Zero_Production
   global ZEROProduction_Flag
   global Receive_Flag
   global Serial_Flag
   global DATA_Ready
   global ERROR_NACK_COUNTER_ZERO_PRODUCTION

   data = 'ACK'
   conn.send(data.encode())
   print('SEND ACK')
   # receive the size
   ZEROProduction_Flag = 1
   print('Enter  zero Function')
   Time_out_Zero_production = 0

   while Time_out_Zero_production < 3:
       ready = select.select([conn], [], [], 5)
       if ready[0]:

          ZERO_Production_SIZE = conn.recv(6)
          print(ZERO_Production_SIZE.decode())
          try:
           ZERO_Production_SIZE2= int(ZERO_Production_SIZE.decode())
           Vector_Zero_Production = []

           for iz in range(ZERO_Production_SIZE2):
               ready = select.select([conn], [], [], 5)
               if ready[0]:
                   Data = conn.recv(3)
                   Vector_Zero_Production.append(Data.decode())
                   print(Data)
               else:
                   f = open('error_log.txt', 'w')
                   f.write("ZERO PRODUCTION = ERROR 1")  # write it to a file called tag_data.xml
                   f.close()
                   os.system("sudo reboot")

           Check_SUM_Zero_Production = 0
           print(Vector_Zero_Production)


           for jz in range((ZERO_Production_SIZE2) - 1):
               Check_SUM_Zero_Production = Check_SUM_Zero_Production + int(Vector_Zero_Production[jz])

           print(Check_SUM_Zero_Production)

           Value_2_Zero_Production_Checksum = bytearray()
           Value_2_Zero_Production_Checksum[0:2] = (Check_SUM_Zero_Production).to_bytes(2, byteorder="big")
           Check_SUM_Zero_Production = 0xFF - (Value_2_Zero_Production_Checksum[1])

           print(Check_SUM_Zero_Production)
           print(Vector_Zero_Production[ZERO_Production_SIZE2 - 1])

           if (Check_SUM_Zero_Production == int(Vector_Zero_Production[ZERO_Production_SIZE2 - 1])):

               print('enter checksum if')
               data = 'ACK'
               conn.send(data.encode())
               print('SEND2 ACK')

               tree = etree.parse('machine.xml')
               root = tree.getroot()

               Fz = 0

               for nz in range(len(Vector_Zero_Production)):

                   for iz in range(len(MACHINES)):

                       if (int(MACHINES[iz]) == int(Vector_Zero_Production[nz])):
                           root[iz][2].text = 'Zero production'
                           Fz = Fz + 1
                           print('Fz')

               if (Fz == int(ZERO_Production_SIZE2 - 1)):

                   Time_out_Zero_production = 3
                   tree.write('machine.xml')
                   print('Flag')
                   ZEROProduction_Flag = 0
                   ERROR_NACK_COUNTER_ZERO_PRODUCTION = 0
                   data = 'ACK'
                   conn.send(data.encode())
                   print('Send ACK')
                   break

               else:
                   data = 'NACK'
                   conn.send(data.encode())
                   Time_out_Zero_production = Time_out_Zero_production + 1
                   ERROR_NACK_COUNTER_ZERO_PRODUCTION = ERROR_NACK_COUNTER_ZERO_PRODUCTION + 1
                   # ZERO PRODUC ERROR 1
                   if ERROR_NACK_COUNTER_ZERO_PRODUCTION == 3:
                       f = open('error_log.txt', 'w')
                       f.write("ZERO PRODUCTION = ERROR 1")  # write it to a file called tag_data.xml
                       f.close()
                       os.system("sudo reboot")


           else:
               data = 'NACK'
               conn.send(data.encode())
               Time_out_Zero_production = Time_out_Zero_production + 1
               ERROR_NACK_COUNTER_ZERO_PRODUCTION = ERROR_NACK_COUNTER_ZERO_PRODUCTION + 1
               # ZERO PRODUC ERROR 1
               if ERROR_NACK_COUNTER_ZERO_PRODUCTION == 3:
                   f = open('error_log.txt', 'w')
                   f.write("ZERO PRODUCTION = ERROR 1")  # write it to a file called tag_data.xml
                   f.close()
                   os.system("sudo reboot")
          except:
              Time_out_Zero_production = Time_out_Zero_production + 1
              ERROR_NACK_COUNTER_ZERO_PRODUCTION = ERROR_NACK_COUNTER_ZERO_PRODUCTION + 1
              # ZERO PRODUC ERROR 1
              if ERROR_NACK_COUNTER_ZERO_PRODUCTION == 3:
                  f = open('error_log.txt', 'w')
                  f.write("ZERO PRODUCTION = ERROR 1")  # write it to a file called tag_data.xml
                  f.close()
                  os.system("sudo reboot")
              pass
       else:
           Time_out_Zero_production = Time_out_Zero_production + 1
           ERROR_NACK_COUNTER_ZERO_PRODUCTION = ERROR_NACK_COUNTER_ZERO_PRODUCTION + 1
           # ZERO PRODUC ERROR 1
           if ERROR_NACK_COUNTER_ZERO_PRODUCTION == 3:
               f = open('error_log.txt', 'w')
               f.write("ZERO PRODUCTION = ERROR 1")  # write it to a file called tag_data.xml
               f.close()
               os.system("sudo reboot")

       if (ZEROProduction_Flag == 1):
           ZEROProduction_Flag = 0

       print('esce')
       DATA_Ready = 'Deactivate'
   return


# ****************************************************
# #*****************  Status ****************
# #****************************************************
def Status_function():

      global Status_Flag
      global DATA_Ready
      global Receive_Flag
      global  List_Flag
      global Serial_Flag
      global Serial_Flag2
      global ERROR_NACK_COUNTER_Status
      Status_Flag = 1


      print('Enter Status Function')
      data = 'ACK_status'
      conn.send(data.encode())
      print('ACK_status')
    #      time.sleep(1)
      ready = select.select([conn],[],[],5)
      if ready[0]:
         print('enter try status')
         # receive the size of XML file
         size_xml_new = conn.recv(6)
         try:
             size_new = int(size_xml_new)
             print('size xml status')
             print(size_new)
             data = 'ACK'
             conn.send(data.encode())
             print('SENDED ACK_SIZE')
             time.sleep(0.1)
             ready = select.select([conn], [], [], 6)

             if ready[0]:
                print('dentro status')
                data_received = conn.recv(size_new)
                print(data_received)
                print('New XML RECEIVED')
        #            time.sleep(0.2)
                f = open('Status.xml', 'w')
                f.write(data_received.decode())  # write it to a file called tag_dat
                f.close()
                print('Write new XML')

                prev = 0
                for eachline in open('Status.xml', 'rb'):
                    prev = zlib.crc32(eachline, prev)
                print("CRC")
                print((hex(prev)))

                ready = select.select([conn], [], [], 5)
                if ready[0]:
                    data_received_crc = conn.recv(10)
                    print(data_received_crc)

                    if ((data_received_crc).decode() == str(hex(prev))):
                        data = 'ACK'
                        conn.send(data.encode())
                        print('SENDED ACK Accepted')
                        DATA_Ready = 'Deactivate'
                        ERROR_NACK_COUNTER_Status=0
                        Status_Flag = 0
                    else:
                        data = 'NACK'
                        conn.send(data.encode())
                        ERROR_NACK_COUNTER_Status = ERROR_NACK_COUNTER_Status + 1
                        # CONFIGURATION ERROR 1
                        if ERROR_NACK_COUNTER_Status == 3:
                            f = open('error_log.txt', 'w')
                            f.write("CONFIGURATION = ERROR 1")  # write it to a file called tag_data.xml
                            f.close()
                            os.system("sudo reboot")
                else:
                    ERROR_NACK_COUNTER_Status = ERROR_NACK_COUNTER_Status + 1
                    # CONFIGURATION ERROR 1
                    if ERROR_NACK_COUNTER_Status == 3:
                        f = open('error_log.txt', 'w')
                        f.write("CONFIGURATION = ERROR 1")  # write it to a file called tag_data.xml
                        f.close()
                        os.system("sudo reboot")
             else:
                ERROR_NACK_COUNTER_Status = ERROR_NACK_COUNTER_Status + 1
                # CONFIGURATION ERROR 1
                if ERROR_NACK_COUNTER_Status == 3:
                    f = open('error_log.txt', 'w')
                    f.write("CONFIGURATION = ERROR 1")  # write it to a file called tag_data.xml
                    f.close()
                    os.system("sudo reboot")

         except:
            data = 'NACK'
            conn.send(data.encode())
            ERROR_NACK_COUNTER_Status = ERROR_NACK_COUNTER_Status + 1
            # CONFIGURATION ERROR 1
            if ERROR_NACK_COUNTER_Status == 3:
                f = open('error_log.txt', 'w')
                f.write("CONFIGURATION = ERROR 1")  # write it to a file called tag_data.xml
                f.close()
                os.system("sudo reboot")
            pass
      else:
          ERROR_NACK_COUNTER_Status = ERROR_NACK_COUNTER_Status + 1
          # CONFIGURATION ERROR 1
          if ERROR_NACK_COUNTER_Status == 3:
              f = open('error_log.txt', 'w')
              f.write("CONFIGURATION = ERROR 1")  # write it to a file called tag_data.xml
              f.close()
              os.system("sudo reboot")

      if (Status_Flag == 1):

          Status_Flag = 0

      DATA_Ready = 'Deactivate'
      Serial_Flag2 = 0

      return


# ****************************************************
# ******************** Generate the list *************
# ****************************************************

def generate_list():

   global List_Flag
   global Serial_Flag2
   global Serial_Flag
   global Receive_Flag
   global MACHINES
   global Disconnect_vector

   MACHINES = []
   Disconnect_vector = []

   print('Enter list generate')
   print(Current_Status_Flag)

   try:
       tree = etree.parse('machine.xml')
       root = tree.getroot()

       for child in root:

           MACHINES.append(child.find('ID_machine').text)
           Disconnect_vector.append(0)

       List_Flag=0
       Serial_Flag = 1
       Serial_Flag2 = 1
       Receive_Flag = 1
   except:
       f = open('error_log.txt', 'w')
       f.write("GENERATE LIST = ERROR 1")  # write it to a file called tag_data.xml
       f.close()
       os.system("sudo reboot")

   return


# ****************************************************
# ******************** Serial  *************
# ****************************************************
def Serial():

   global DATA_Ready
   global MACHINES
   global Serial_Flag
   global Serial_Flag2
   global WDG_REFLESH
   global RADIO_ERROR_COUNTER
   global RADIO_ERROR_COUNTER_1
   global Disconnect_vector
   CMD_ZERO_PRODUCTION = 1
   CMD_CYCLE_TIME   = 0
   CMD_PRODUCTION = 2

   Serial_Flag = 1
   Serial_Flag2 = 1

    #GPIO 2 M0
    #GPIO 3  M1

   try:
       tree = etree.parse('machine.xml')
       root = tree.getroot()
       print('machine.xml.parse')
       tree_status_xml = etree.parse('Status.xml')
       root_status_xml = tree_status_xml.getroot()
       print('Status.xml.parse')

       print('Test Serial')


       for itr in range(len(MACHINES)):

          WDG_REFLESH = 0
          while(Serial_Flag == 0):
            wait = 1
          if(Serial_Flag2 == 0):
            itr = 0
            break

          if not root[itr][2].text == 'Disable':

             msg = bytearray()
             # convert to byte
             value = int(MACHINES[itr])

             msg[0:2] = (value).to_bytes(2, byteorder="big")

             GPIO.output(3, GPIO.HIGH)  # M0
             GPIO.output(5, GPIO.HIGH)  # M1
             time.sleep(0.02)

             sector =int(root[itr][14].text)
             print("sector: ")
             print(str(sector))

             radio = bytearray(b'\xc2\x18\x40')
             radio2= bytearray(b'\xc0\x18\x40')

             radio[1:1] = (value).to_bytes(2, byteorder="big")
             radio[4:1]= (sector).to_bytes(1, byteorder="big")
             radio2[1:1] = (value).to_bytes(2, byteorder="big")
             radio2[4:1] = (sector).to_bytes(1, byteorder="big")

             uart.flushInput()
             uart.write(radio)
             print('prog radio:')
             print(radio)
             time.sleep(0.1)

             try:
                 RX_RADIO = uart.read(6)
                 print ( 'PROG_RADIO:')
                 print (RX_RADIO)
             except:
                 pass
             if not RX_RADIO == radio2:
                print(' RADIO FAULT ')
                RADIO_ERROR_COUNTER = RADIO_ERROR_COUNTER + 1
                print(radio2)
                print(RX_RADIO)
                GPIO.output(3, GPIO.HIGH)  # M0
                GPIO.output(5, GPIO.HIGH)  # M1
                time.sleep(0.02)
                uart.flushInput()
                uart.write(radio)
                time.sleep(0.1)
                try:
                    RX_RADIO = uart.read(6)
                except:
                    pass
                if not RX_RADIO == radio2:
                    print('2 RADIO FAULT ')
                    RADIO_ERROR_COUNTER_1 = RADIO_ERROR_COUNTER_1 + 1
                    print(radio2)
                    print(RX_RADIO)

             GPIO.output(3, GPIO.HIGH)  # M0
             GPIO.output(5, GPIO.LOW)  # M1
             time.sleep(0.02)



             if (root[itr][2].text == 'Zero production'):

                 msg[2:3] = (0).to_bytes(3, byteorder="big")
                 msg[5:1]=(CMD_ZERO_PRODUCTION).to_bytes(1, byteorder="big")
                 root[itr][8].text = str(0)

             else:
                 msg[2:2] = (int(root[itr][7].text)).to_bytes(2, byteorder="big")
                 msg[4:1] = (0).to_bytes(1, byteorder="big")
                 msg[5:1] = (CMD_CYCLE_TIME).to_bytes(1, byteorder="big")


             value_1 = (msg[0] + msg[1] + msg[2] + msg[3] + msg[4] + msg[5])
             value_2 = bytearray()
             value_2[0:2] = (value_1).to_bytes(2, byteorder="big")
             checksum = 0xFF - value_2[1]
             msg[6:1] = (checksum).to_bytes(1, byteorder="big")

             Time_out = 0

             while Time_out < 3:

                   uart.write(msg)
                   uart.flushInput()
                   start = timer()
                   time.sleep(0.30)

                   try:
                       Serial_data = uart.read(9)
                       print(itr)
                       print(msg)
                       print(Serial_data)
                       end = timer()
                       print(end - start)
                       ID_num2 = int(root[itr][1].text)
                       ID_num  = int.from_bytes(Serial_data[0:2], byteorder="big")

                       if( (len(Serial_data)> 8)):
                           if((ID_num == ID_num2)):

                               value1 = Serial_data[0] + Serial_data[1] + Serial_data[2] + Serial_data[3] + Serial_data[4] + \
                                    Serial_data[5] + Serial_data[6] + Serial_data[7]
                               value2 = bytearray()
                               value2[0:2] = ((value1).to_bytes(2, byteorder="big"))
                               checksum = 0xFF - value2[1]

                               if (checksum) == Serial_data[8]:

                                  ID_num = int.from_bytes(Serial_data[0:2], byteorder="big")
                                  Status_num = int.from_bytes(Serial_data[2:3], byteorder="big")
                                  Operator_num = int.from_bytes(Serial_data[3:5], byteorder="big")
                                  Production_num = int.from_bytes(Serial_data[5:8], byteorder="big")
                                  xml_prodiction = int(root[itr][8].text)
                                  print('Production_num:')
                                  print(str(Production_num ))
                                  print('XML_Production_num:')
                                  print(str(xml_prodiction))

                                  if not (root[itr][2].text == 'Zero production'):
                                     if (Production_num < xml_prodiction):

                                         Production_num = xml_prodiction + Production_num
                                         print('error production')
                                         msg[2:3] = (Production_num).to_bytes(3, byteorder="big")
                                         msg[5:1] = (CMD_PRODUCTION).to_bytes(1, byteorder="big")
                                         value_1 = (msg[0] + msg[1] + msg[2] + msg[3] + msg[4] + msg[5])
                                         value_2 = bytearray()
                                         value_2[0:2] = (value_1).to_bytes(2, byteorder="big")
                                         checksum = 0xFF - value_2[1]
                                         msg[6:1] = (checksum).to_bytes(1, byteorder="big")
                                         uart.write(msg)
                                         uart.flushInput()

                                  if (Serial_Flag2 == 1):

                                      if not(root[itr][2].text == 'Zero production'):
                                        root[itr][8].text = str(Production_num)
                                    #load status name in machine xml
                                      for Status_itr in range(len(root_status_xml)):
                                          if(root_status_xml[Status_itr][1] == str(Status_num)):
                                              root[itr][2].text = root_status_xml[Status_itr][0].text


                                      root[itr][10].text = str(Operator_num)

                                      tree.write('machine.xml')
                                      Time_out = 3

                               else:

                                  Time_out = Time_out + 1
                                  if (Time_out == 2):
                                      if (Serial_Flag2 == 1):
                                          root[itr][2].text = 'error checksum'
                                          tree.write('machine.xml')

                           else:
                               Time_out = Time_out + 1
                               if(Time_out==2):
                                  if (Serial_Flag2 == 1):

                                      root[itr][2].text = 'Disconnect'
                                      tree.write('machine.xml')
                       else:
                           Time_out = Time_out + 1
                           if (Time_out == 2):
                               if (Serial_Flag2 == 1):
                                   if(Disconnect_vector[itr]==0):
                                       Disconnect_vector[itr]=1
                                   else:
                                      Disconnect_vector[itr]=0
                                      root[itr][2].text = 'Disconnect'
                                      tree.write('machine.xml')

                   except:
                       end = timer()
                       Time_out = Time_out + 1
                       print(end - start)
                       if (Time_out == 2):
                           if (Serial_Flag2 == 1):
                               root[itr][2].text = 'Disconnect'
                               tree.write('machine.xml')
                       pass
                   #time.sleep(1)

       print('Serial end')
       print(' RADIO FAULT:   ')
       print(RADIO_ERROR_COUNTER)
       print(' 2 RADIO FAULT:   ')
       print(RADIO_ERROR_COUNTER_1)
       print ('')

       if(Serial_Flag2==1):
          DATA_Ready = 'Activate'
       Serial_Flag2 = 1
   except:
       f = open('error_log.txt', 'w')
       f.write("SERIAL = ERROR 1")  # write it to a file called tag_data.xml
       f.close()
       os.system("sudo reboot")
   return




def TheredFunction():


    TH1 = threading.Thread(target= Receive_data)
    TH2 = threading.Thread(target= Serial)


    TH1.daemon = True
    TH2.daemon = True

    TH1.start()
    TH2.start()


    TH1.join()
    TH2.join()



    return


# ****************************************************
# *********************  Main script  ****************
# ****************************************************


if __name__ == "__main__":

   First_communication()
   generate_list()
   while True:

        TheredFunction()
