import io
import socket
import struct
from PIL import Image
import sys

__author__ = "Jin Hui"

class RecAPI(object):

        def __init__(self):
                self.tcp_ip = "192.168.12.4" # Connecting to IP address of MDPGrp12
                self.port = 8000
                self.conn = None
                self.client = None
                self.addr = None
                self.pc_is_connect = False

        def close_pc_socket(self):
                """
                Close socket connections
                """
                if self.conn:
                        self.conn.close()
                        print("Closing server socket")
                if self.client:
                        self.client.close()
                        print("Closing client socket")
                self.pc_is_connect = False

        def pc_is_connected(self):
                """
                Check status of connection to PC
                """
                return self.pc_is_connect

        def init_pc_comm(self):
                """
                Initiate PC connection over TCP
                """
                # Create a TCP/IP socket
                try:
                        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.conn.bind((self.tcp_ip, self.port))
                        self.conn.listen(0)             #Listen for incoming connections
                        print("Listening for incoming connections from RPI...")
                        self.client, self.addr = self.conn.accept()
                        print("Connected! Connection address: ", self.addr)
                        self.pc_is_connect = True
                except Exception as e:  #socket.error:
                        print("Error: ", str(e))
                        print("Try again in a few seconds")


        def write_to_Android(self, message):
                """
                Write message to PC
                """
                try:
                        self.client.sendto(message, self.addr)

                except TypeError:
                        print("Error: Null value cannot be sent")

        def read_coor(self):
                try:
                    coor_data = self.client.recv(1024)
                    if (len(coor_data) < 30 and len(coor_data) > 0):
                        print("Coordinate data: %s" % coor_data)
                        #print("HELLU NEND SUDES")
                        return coor_data
                except Exception as e:
                    print(str(e))
                    print("No data")

        def read_from_RPI(self, filename):
            """
            Read incoming message from RPI
            """
            connection = self.client.makefile('rb')
            print('CHECKPOINT 0')
            try:
                while True:
                    print('CHECKPOINT 1')
                    # Read the length of the image as a 32-bit unsigned int. If the
                    # length is zero, quit the loop
                    image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
                    print('CHECKPOINT 2')

                    if not image_len:
                        # Construct a stream to hold the image data and read the image
                        # data from the connection
                        image_stream = io.BytesIO()
                        print('CHECKPOINT 3')
                        image_stream.write(connection.read(image_len))
                        print('CHECKPOINT 4')
                        # Rewind the stream, open it as an image with PIL and do some
                        # processing on it
                        image_stream.seek(0)
                        print('CHECKPOINT 5')
                        image = Image.open(image_stream)
                        print('CHECKPOINT 6')
                        #print('Image is %dx%d' % image.size)
                        #image.verify()
                        #print('Image is verified')
                        image.save(filename)
                        print('CHECKPOINT 7')

                    print('CHECKPOINT 8')
            except Exception as e:
                print("Error: ", str(e))
                print("Value not read from PC")

if __name__ == "__main__":
        print("main")
        rec = RecAPI()
        rec.init_pc_comm()

        data = rec.read_coor()
        print(data)
        rec.read_from_RPI("test.jpg")
        print("Image is saved")



        #send_msg = "test"
        #print("write_to_Android(): ", send_msg)
        #rec.write_to_Android(send_msg.encode())

        #print("closing sockets")
        #rec.close_pc_socket()
