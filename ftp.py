import sys
import socket
import os

# TASKS:
# Open a TCP socket.
# FTP listens on port 21. User may override.
# Request example COMMAND <param> <...>
# Some reqeusts will recieve two responses
# Recieves welcome message after connection before sending request.
# FTP response example: CODE <explanation> <param>
# For any data transfer you have to open a second data channel on a specific ip and port
# Still send the command over the control channel but listen on the data channel.

# Help method for throwing generic error messages and exiting the program
def error():
        exit("USAGE: ./3700ftp COMMAND <param1> <param2>\n\nEnsure validity of all urls provided and check the responses above.")

# Checker for whenever we are receiving messages back from the ftp server. If error, exit with standard error message.
def errorHuh(res):
        if (res[0] == "4" or res[0] == "5" or res[0] == "6"):
                error()

# Send TYPE request.
def type(s):
        s.send("TYPE I\r\n")
        r = s.recv(2048)
        errorHuh(r)
        print r

# Send MODE request.
def mode(s):
        s.send("MODE S\r\n")
        r = s.recv(2048)
        errorHuh(r)
        print r

# Send STRU request.
def stru(s):
        s.send("STRU F\r\n")
        r = s.recv(2048)
        errorHuh(r)
        print r

# Initiate passive mode. Needs to be done before data transfer can take place through the data channel.
def pasv(s):
        s.send("PASV\r\n")
        r = s.recv(2048)
        errorHuh(r)
        print r
        return r

# Login method for the initial connection specified the passed in command line arguments.
def login(usr, pwd, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Need to ensure what we were given is in fact a valid port number.
        try:
                p = int(port)
        except ValueError:
                error()

        # Catch if invalid hostname.
        try:
                hostIP = socket.gethostbyname(host)
        except:
                error()

        # Catch if port number is not available.
        try:
                s.connect ((hostIP, p))
        except:
                error()

        # Recieve the greeting message.
        r1 = s.recv(2048)
        errorHuh(r1)
        print r1

        # Send username from provided url.
        s.send("USER " + usr + "\r\n")
        r2 = s.recv(2048)
        errorHuh(r2)
        print r2

        # Send password from provided url.
        s.send("PASS " + pwd + "\r\n")
        r3 = s.recv(2048)
        errorHuh(r3)
        print r3
        return s

# Helper method to send a QUIT request.
def quit(s):
        s.send("QUIT\r\n")
        r = s.recv(2048)
        errorHuh(r)
        print r

# Handles functionality of 'make directory' command from user.
def mkd(usr, pwd, host, port, path):
        s = login(usr, pwd, host, port)
        s.send("MKD " + path + "\r\n")
        r = s.recv(2048)
        errorHuh(r)
        print r
        quit(s)

# Handles functionality of 'remove directory' command from user.
def rmd(usr, pwd, host, port, path):
        s = login(usr, pwd, host, port)
        s.send("RMD " + path + "\r\n")
        r = s.recv(2048)
        errorHuh(r)
        print r
        quit(s)

# This helper is to parse out the PASV response and return "ip:port"
def response_helper(r):
        ip = top = bottom = ""
        counter = 0
        ipStarted = 0
        # Separate the ip, and the two 8-bit numbers representing the top and bottom bits of the specific port number.
        for ii in range(len(r)):
                if (r[ii] == "("):
                        ipStarted = 1
                elif (ipStarted and counter < 4):
                        if (r[ii] == ","):
                                if (counter < 3):
                                        ip += "."
                                counter += 1
                        else:
                                ip += r[ii]
                elif (ipStarted and counter == 4):
                        if (r[ii] == ","):
                                counter += 1
                        else:
                                top += r[ii]
                elif (ipStarted and counter == 5):
                        if (r[ii] != ")" and r[ii] != "."):
                                bottom += r[ii]

        # Translate the top and bottom 8 bits of the 16 bit port number.
        b = "{0:b}".format(int(top)) + "00000000"
        port = int(b, 2) + int(bottom)

        # Format "ip:port"
        out = ip + ":" + str(port)
        return out


# Method to handle user request to list what is in the given directory on the provided host.
def ls(usr, pwd, host, port, path):
        s = login(usr, pwd, host, port)

        # Must enter passive mode before sending a LIST request.
        r = pasv(s)

        # Handle the response from entering passive mode.
        ip_port = response_helper(r)
        dataIP = ip_port[0:ip_port.index(":")]
        dataPort = ip_port[ip_port.index(":") + 1:]

        # Open the data channel.
        dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataSocket.connect ((dataIP, int(dataPort))) 

        # Still send command to the control channel but listen for responses on both.
        s.send("LIST " + path + "\r\n")
        print dataSocket.recv(2048)
        res = s.recv(2048)
        errorHuh(res)
        print res
        quit(s)

# Implement request to ftp server to delete file at the given path.
def dele(s, path):
        s.send("DELE " + path + "\r\n")
        print s.recv(2048)

# Method to handle user request to remove file on the FTP server.
def rm(usr, pwd, host, port, path):
        s = login(usr, pwd, host, port)
        dele(s, path)
        quit(s)

# FTP server command to send a file.
def stor(s, path):
        s.send("STOR " + path + "\r\n")
        r = s.recv(2048)
        errorHuh(r)
        print r

# FTP server command to retrieve a file.
def retr(s, path):
        s.send("RETR " + path + "\r\n")
        r = s.recv(2048)
        errorHuh(r)
        print r

# Method to handle cp function requested by user.
def cp(usr1, pwd1, host1, port1, path1, usr2, pwd2, host2, port2, path2, rmvAtSrc):
        # Copying from local to remote.
        if (usr1 == ""):
                # Set up the control channel.
                s = login(usr2, pwd2, host2, port2)

                # Set up the data channel.
                r = pasv(s)
                ip_port = response_helper(r)
                dataIP = ip_port[0:ip_port.index(":")]
                dataPort = ip_port[ip_port.index(":") + 1:]
                dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dataSocket.connect ((dataIP, int(dataPort)))

                # Alert control channel that we want to send file.
                stor(s, path2)

                # Send file.
                try:
                        f = open(path1, 'rb')
                except:
                        exit("Error: Make sure source file exists in the specified location")
                buff = f.read(2048)
                while buff:
                        dataSocket.send(buff)
                        buff = f.read(2048)
                f.close()

                # Close down because we sent data.
                dataSocket.shutdown(socket.SHUT_WR)
                dataSocket.recv(2048)
                resp = s.recv(2048)
                errorHuh(resp)
                print resp

                # if this was a mv instead of a cp then we need to remove from the source.
                if (rmvAtSrc):
                        # remove local file
                        os.remove(path1)
                quit(s)
        # Copying from remote to local.
        else:
                # Set up the control channel.
                s = login(usr1, pwd1, host1, port1)

                # Set up the data channel.
                r = pasv(s)
                ip_port = response_helper(r)
                dataIP = ip_port[0:ip_port.index(":")]
                dataPort = ip_port[ip_port.index(":") + 1:]
                dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dataSocket.connect ((dataIP, int(dataPort)))

                # Tell the control channel that we want to recieve a file.
                retr(s, path1)
                try:
                        with open(path2, 'wb') as f:
                                while True:
                                        data = dataSocket.recv(2048)
                                        if not data:
                                                break
                                        f.write(data)
                except:
                        error()
                respo = s.recv(2048)
                errorHuh(respo)
                print respo

                # If this was a mv instead of a cp, then we need to remove the source file.
                if (rmvAtSrc):
                        dele(s, path1)
                quit(s)

# Grabs the username from the provided url. If not present, returns empty string.
def parseUser(url):
        # If username is not provided login as anonymous.
        if (not("@" in url)):
                return "anonymous"

        # Go through the provided url and pull out the user.
        count = ii = 0
        while (ii < url.index("@") and count < 2):
                if (url[ii] == ":"):
                        count += 1
                ii += 1

        # If a password is present.
        if (count == 2):
                return url[6:(ii -1)]
        # If no password is present but a username is.
        else:
                return url[6:url.index("@")]

# Grabs the password from provided url. If not present, returns empty string.
def parsePass(url):
        # If no username or password is present.
        if (not("@" in url)):
                return ""

        # If at least a username is there.
        idx = url.index("@")
        subs = url[6:idx]
        # See if there is no password with that username.
        if (not(":" in subs)):
                return ""
        # But if there is, extract.
        pwdStart = subs.index(":")
        return subs[pwdStart + 1:]

# Extract the port number as a string and return '21' as default if not present.
def parsePort(url):
        # Start by extracting the host:port/path grouping.
        hpp = ""
        # If preceded by username.
        if ("@" in url):
                hpp = url[url.index("@") + 1:]
        else:
                hpp = url[6:]

        p = "21"
        # If the port is specified.
        if (":" in hpp):
                if (not("/" in hpp)):
                        return ""
                p = hpp[hpp.index(":") + 1:hpp.index("/")]
        # Will be the string rep of the port number if present and "21" if not.
        return p

# Extract the hostname provided.
def parseHost(url):
        # Start by extracting the host:port/path grouping.
        hpp = ""
        # If preceded by a username.
        if ("@" in url):
                hpp = url[url.index("@") + 1:]
        else:
                hpp = url[6:]

        h = ""
        # If the port is specified.
        if (":" in hpp):
                h = hpp[0:hpp.index(":")]
        elif (not("/" in hpp)):
                return ""
        else:
                h = hpp[0:hpp.index("/")]
        return h

# Extract the path provided in the url.
def parsePath(url):
        p = ""
        Nurl = url[6:]
        if ("/" in Nurl):
                for ii in range(len(Nurl)):
                        if (Nurl[ii] == "/"):
                                break
                p = Nurl[ii + 1:]
        return p

# XOR for one ftp address
def xorFTP(s1, s2):
        if ("ftp://" in s1 and "ftp://" in s2):
                error()
        if (not("ftp://" in s1) and not("ftp://" in s2)):
                error()

# Main method for ftp client.
def main():
        # Parse the command line arguments.
        if (len(sys.argv) < 3 or len(sys.argv) > 4):
                error()
        cmd, p1 = sys.argv[1], sys.argv[2]
        if (len(sys.argv) == 4):
                p2 = sys.argv[3]
        else:
                p2 = ""

        # Parse out present parameters.
        user1 = pass1 = port1 = host1 = path1 = user2 = pass2 = port2 = host2 = path2 = ""
        # If this is an ftp address.
        if ("ftp://" in p1):
                user1 = parseUser(p1)
                pass1 = parsePass(p1)
                port1 = parsePort(p1)
                host1 = parseHost(p1)
                path1 = parsePath(p1)
        # If this is a local address.
        else:
                path1 = p1
        # If this has a second address.
        if (len(p2) > 0):
                # If we need to parse out an FTP address.
                if ("ftp://" in p2):
                        user2 = parseUser(p2)
                        pass2 = parsePass(p2)
                        port2 = parsePort(p2)
                        host2 = parseHost(p2)
                        path2 = parsePath(p2)
                # If this is a local address.
                else:
                        path2 = p2
                 
        # Execute the operation.
        if (cmd == "mkdir"):
                if (len(sys.argv) != 3):
                        exit("Usage: ./3700ftp mkdir [URL]")
                mkd(user1, pass1, host1, port1, path1)
        elif (cmd == "rmdir"):
                if (len(sys.argv) != 3):
                        exit("Usage: ./3700ftp rmdir [URL]")
                rmd(user1, pass1, host1, port1, path1)
        elif (cmd == "ls"):
                if (len(sys.argv) != 3):
                        exit("Usage: ./3700ftp ls [URL]")
                ls(user1, pass1, host1, port1, path1)
        elif (cmd == "rm"):
                if (len(sys.argv) != 3):
                        exit("Usage: ./3700ftp rm [URL]")
                rm(user1, pass1, host1, port1, path1)
        elif (cmd == "cp"):
                if (len(sys.argv) != 4):
                        exit("Usage: ./3700 cp [source] [dest]")
                xorFTP(p1,p2)
                cp(user1, pass1, host1, port1, path1, user2, pass2, host2, port2, path2, 0)
        elif (cmd == "mv"):
                if (len(sys.argv) != 4):
                        exit("Usage: ./3700 mv [source] [dest]")
                xorFTP(p1,p2)
                cp(user1, pass1, host1, port1, path1, user2, pass2, host2, port2, path2, 1)
        else:
                exit("That command is not recognized by this client. Sorry chap.")

# To call the main function.
if __name__ == "__main__":
        main()
