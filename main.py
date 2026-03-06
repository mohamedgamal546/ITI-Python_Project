import subprocess
import os
import getpass
import logging
import re

# ================= Logging =================

logging.basicConfig(
    filename="user_manager.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ================= Messages =================

def success(msg):
    print(f"[SUCCESS] {msg}")

def error(msg):
    print(f"[ERROR] {msg}")

def info(msg):
    print(f"[INFO] {msg}")

# ================= Helpers =================

def run_command(command):
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)

        if result.stdout:
            print(result.stdout.strip())

        if result.stderr:
            print(result.stderr.strip())

        logging.info(f"Executed command: {' '.join(command)}")

    except subprocess.CalledProcessError as e:
        error("Command failed")

        if e.stderr:
            print(e.stderr.strip())

        logging.error(f"Command failed: {' '.join(command)}")


def username_exists(username):
    with open("/etc/passwd") as f:
        return any(line.split(":")[0] == username for line in f)


def group_exists(group):
    with open("/etc/group") as f:
        return any(line.split(":")[0] == group for line in f)


def valid_username(username):
    return re.match("^[a-z_][a-z0-9_-]{2,15}$", username)


# ================= Backup =================

def backup_system_files():

    info("Creating backup for system files")

    run_command(["cp","/etc/passwd","/etc/passwd.bak"])
    run_command(["cp","/etc/group","/etc/group.bak"])
    run_command(["cp","/etc/shadow","/etc/shadow.bak"])

    success("Backup created successfully")


# ================= Users =================

def add_user():

    username = input("Enter username: ")

    if not valid_username(username):
        error("Invalid username format")
        return

    if username_exists(username):
        error("User already exists")
        return

    password = getpass.getpass("Enter password: ")

    info("Creating user")

    run_command(["useradd","-m",username])

    proc = subprocess.Popen(["chpasswd"], stdin=subprocess.PIPE, text=True)
    proc.communicate(f"{username}:{password}")

    success("User created successfully")
    logging.info(f"User created: {username}")


def modify_user():

    username = input("Enter username: ")

    if not username_exists(username):
        error("User does not exist")
        return

    print("\n1 Change Home Directory")
    print("2 Change Shell")
    print("3 Change UID")
    print("4 Change Primary Group")

    choice = input("Choose: ")

    if choice == "1":

        home = input("New home path: ")
        run_command(["usermod","-d",home,username])

    elif choice == "2":

        shell = input("Shell path (example /bin/bash): ")
        run_command(["usermod","-s",shell,username])

    elif choice == "3":

        uid = input("New UID: ")
        run_command(["usermod","-u",uid,username])

    elif choice == "4":

        group = input("Group name: ")

        if not group_exists(group):
            error("Group does not exist")
            return

        run_command(["usermod","-g",group,username])

    success("User modified")


def delete_user():

    username = input("Enter username: ")

    if not username_exists(username):
        error("User does not exist")
        return

    run_command(["userdel","-r",username])

    success("User deleted")


def list_users():

    info("Listing users")

    with open("/etc/passwd") as f:

        for line in f:

            parts = line.split(":")

            if int(parts[2]) >= 1000 and parts[0] != "nobody":
                print(parts[0])


def disable_user():

    username = input("Enter username: ")

    run_command(["usermod","-L",username])

    success("User disabled")


def enable_user():

    username = input("Enter username: ")

    run_command(["usermod","-U",username])

    success("User enabled")


def change_password():

    username = input("Enter username: ")

    if not username_exists(username):
        error("User does not exist")
        return

    password = getpass.getpass("Enter new password: ")

    proc = subprocess.Popen(["chpasswd"], stdin=subprocess.PIPE, text=True)
    proc.communicate(f"{username}:{password}")

    success("Password changed")


def show_user_info():

    username = input("Enter username: ")

    run_command(["id",username])


def add_user_to_group():

    username = input("Enter username: ")
    group = input("Enter group: ")

    if not group_exists(group):
        error("Group does not exist")
        return

    run_command(["usermod","-aG",group,username])

    success("User added to group")


# ================= Groups =================

def add_group():

    group = input("Enter group name: ")

    if group_exists(group):
        error("Group already exists")
        return

    run_command(["groupadd",group])

    success("Group created")


def modify_group():

    group = input("Enter group name: ")

    if not group_exists(group):
        error("Group does not exist")
        return

    print("\n1 Change Group Name")
    print("2 Change GID")

    choice = input("Choose: ")

    if choice == "1":

        newname = input("Enter new name: ")

        run_command(["groupmod","-n",newname,group])

    elif choice == "2":

        gid = input("Enter new GID: ")

        run_command(["groupmod","-g",gid,group])

    success("Group modified")


def delete_group():

    group = input("Enter group name: ")

    if not group_exists(group):
        error("Group does not exist")
        return

    run_command(["groupdel",group])

    success("Group deleted")


def list_groups():

    info("Listing groups")

    with open("/etc/group") as f:

        for line in f:

            parts = line.split(":")

            if int(parts[2]) >= 1000:
                print(parts[0])


# ================= Menu =================

def menu():

    print("\n===== Linux User Manager =====\n")

    print("1 Add User")
    print("2 Modify User")
    print("3 Delete User")
    print("4 List Users")
    print("5 Add Group")
    print("6 Modify Group")
    print("7 Delete Group")
    print("8 List Groups")
    print("9 Disable User")
    print("10 Enable User")
    print("11 Change Password")
    print("12 Show User Info")
    print("13 Add User To Group")
    print("14 Backup System Files")
    print("15 Exit\n")


# ================= Main =================

def main():

    if os.getuid() != 0:
        error("Please run with sudo")
        return

    while True:

        menu()

        choice = input("Choose: ")

        if choice == "1":
            add_user()

        elif choice == "2":
            modify_user()

        elif choice == "3":
            delete_user()

        elif choice == "4":
            list_users()

        elif choice == "5":
            add_group()

        elif choice == "6":
            modify_group()

        elif choice == "7":
            delete_group()

        elif choice == "8":
            list_groups()

        elif choice == "9":
            disable_user()

        elif choice == "10":
            enable_user()

        elif choice == "11":
            change_password()

        elif choice == "12":
            show_user_info()

        elif choice == "13":
            add_user_to_group()

        elif choice == "14":
            backup_system_files()

        elif choice == "15":
            info("Exiting program")
            break

        else:
            error("Invalid choice")


if __name__ == "__main__":
    main()
