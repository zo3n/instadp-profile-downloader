from urllib.request import urlopen, urlretrieve
import os
import sqlite3
import hashlib
import time
from random import randint
import ctypes

os.system("@echo off")
os.system("color a")
os.system("title Mistya")
os.system("mkdir profiles")
os.system("cls")

connection = sqlite3.connect("scan_list.db") # or use :memory: to put it in RAM
sql_executer = connection.cursor()

sql_executer.execute("CREATE TABLE IF NOT EXISTS scan_list(profile_name STRING, lastHash STRING);")
connection.commit()

updateCheck = False

def FlashWindow():
    ctypes.windll.user32.FlashWindow(ctypes.windll.kernel32.GetConsoleWindow(), True)

def FocusWindow():
    ctypes.windll.user32.SetFocus(ctypes.windll.kernel32.GetConsoleWindow())

def GetProfilePictureLink(username):
    html = urlopen("https://instadp.com/profile/" + username).read().decode('utf-8')
    begin = html.find("img.src = '")
    link = html[begin + 11 : html.find("'", begin + 11)]
    return link

def DownloadPicture(link, saveAs):
    try:
        urlretrieve(link, saveAs)
    except:
        #print("Invalid profile name")
        return False
    else:
        return saveAs

def CreateFolder(folderName):
    currentPath = os.getcwd()
    finalPath = currentPath + "\\profiles\\" + folderName
    if not os.path.isdir(finalPath):
        os.mkdir(finalPath)

def DeleteFolder(folderName):
    currentPath = os.getcwd()
    finalPath = currentPath + "\\profiles\\" + folderName
    if os.path.isdir(finalPath):
        os.rmdir(finalPath)

def PrintSection(sectionName):
    print("\n============================== " + sectionName + " ==============================\n")

def ShowHelp():
    PrintSection("HELP")
    print("* add -- adds a profile to database")
    print("* del -- deletes a profile from database")
    print("* exit -- exits current program")
    print("* help -- shows all available commands")
    print("* list -- lists all profiles stored in database")
    print("* switch -- switches to a non-returnable way of working by automatically updating every 60-300 seconds, meaning that input in this program won't work anymore until it is restarted")
    print("* update -- manually checks for profile picture updates")
    PrintSection("HELP")

def ExitProgram():
    exit(0)

def GetFileHash(filename, blocksize=65536):
    hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()

def GetFilenameFromLink(link):
    begin = link.rfind("/") + 1
    end = link.rfind(".jpg") + 4
    result = link[begin:end]
    return result

def GetNumberOfProfiles():
    sql_executer.execute("SELECT * FROM scan_list")
    rows = sql_executer.fetchall()
    return len(rows)   

def CheckUpdate(profile):
    link = GetProfilePictureLink(profile)
    #hashsum = hashlib.sha256(link.encode('utf-8')).hexdigest()
    dbProfile = GetProfile(profile)
    fileName = GetFilenameFromLink(link)
    downloaded = DownloadPicture(link, os.getcwd() + "\\profiles\\" + profile + "\\" + fileName)
    if downloaded:
        fileHash = GetFileHash(downloaded)
        if fileHash != dbProfile[1]:
            print("Found an update for: '" + profile + "'")
            FlashWindow()
            sql_executer.execute("UPDATE scan_list SET lastHash=? WHERE profile_name=?", [fileHash, profile])
            connection.commit()
    else:
        print("Update of '" + profile + "' went wrong.")
        print("Possible issue might be that the username has been changed or isn't valid anymore")

def GetScanList():
    sql_executer.execute("SELECT * FROM scan_list")
    rows = sql_executer.fetchall()
    if rows is None or len(rows) == 0:
        print("Profile scan list is empty. There is nothing to scan.")
    else:
        print("Checking for profile updates...")
        analyzing = 0
        os.system("title Mistya 0/" + str(GetNumberOfProfiles()))
        os.system("color c")
        for row in rows:
            analyzing += 1
            os.system("title Mistya " + str(analyzing) + "/" + str(GetNumberOfProfiles()) + "(" + row[0] + ")")
            CheckUpdate(row[0])
        os.system("title Mistya")
        os.system("color a")

def DoesProfileExist(profile):
    sql_executer.execute("SELECT * FROM scan_list WHERE profile_name=?", (profile,))
    rows = sql_executer.fetchone()
    if rows is None or len(rows) == 0:
        return False
    else:
        return True

def GetProfile(profile):
    sql_executer.execute("SELECT * FROM scan_list WHERE profile_name=?", (profile,))
    rows = sql_executer.fetchone()
    if rows is None or len(rows) == 0:
        return False
    else:
        return rows

def AddProfile(profile):
    if not DoesProfileExist(profile):
        CreateFolder(profile)
        pictureLink = GetProfilePictureLink(profile)
        fileName = GetFilenameFromLink(pictureLink)
        #hashsum = hashlib.sha256(filename.encode('utf-8')).hexdigest()
        downloaded = DownloadPicture(pictureLink, os.getcwd() + "\\profiles\\" + profile + "\\" + fileName)
        if downloaded:
            hashsum = GetFileHash(downloaded)
            sql_executer.execute("INSERT INTO scan_list(profile_name, lastHash) VALUES(?,?)", [profile, hashsum])
            connection.commit()
            print("Profile '" + profile + "' has been stored successfully.")
        else:
            DeleteFolder(profile)
            print("Download of '" + profile + "' went wrong.")
    else:
        print("Profile '" + profile + "' already exists in database.")

def DeleteProfile(profile):
    if DoesProfileExist(profile):
        sql_executer.execute("DELETE FROM scan_list WHERE profile_name=?", [profile])
        connection.commit()
        print("Deleted profile '" + profile + "' from database.")

def ListProfiles():
    sql_executer.execute("SELECT * FROM scan_list")
    rows = sql_executer.fetchall()
    if rows is not None and len(rows) > 0:
        print("Found " + str(len(rows)) + " profiles in database.\n")
        for row in rows:
            print(row)
        print("\n")

def ProcessCommand(command):
    if command:
        if command == "help":
            ShowHelp()
        elif command == "exit":
            ExitProgram()
        elif command.find("add") == 0 and len(command.split()) > 1:
            AddProfile(command.split()[1])
        elif command == "list":
            ListProfiles()
        elif command == "switch":
            global updateCheck
            updateCheck = True
        elif command == "update":
            GetScanList()
        elif command.find("del") == 0 and len(command.split()) > 1:
            DeleteProfile(command.split()[1])
        else: print("") # idk why but i need this print here otherwise it gives error
    else:
        print("")

def CheckUpdateTimer():
    GetScanList()

def Process():
    global updateCheck
    while(1):
        if not updateCheck:
            command = input(">> ")
            ProcessCommand(command)
        else:
            CheckUpdateTimer()
            time.sleep(randint(60, 300))

def Boot():
    GetScanList()

#Boot()
Process()