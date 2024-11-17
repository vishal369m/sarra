import os
import subprocess
from pathlib import Path

# User creation part
username = "user"
password = "root"
os.system(f"useradd -m {username}")
os.system(f"adduser {username} sudo")
os.system(f"echo '{username}:{password}' | sudo chpasswd")
os.system("sed -i 's/\/bin\/sh/\/bin\/bash/g' /etc/passwd")

# RDP part
CRP = "DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=\"4/0AeanS0aVEvZ9QWXoxmCJm3pvEGVFjHousksXxw-tF3T_FiFi7nTxF2n59txE8oN0pkBrjw\" --redirect-url=\"https://remotedesktop.google.com/_/oauthredirect\" --name=$(hostname)"
Pin = 123456
Autostart = False

class CRD:
    def __init__(self, user):
        self.installCRD()
        self.installDesktopEnvironment()
        self.installGoogleChorme()
        self.finish(user)
        print("\nRDP created successfully. You can now access it.")

    @staticmethod
    def installCRD():
        print("Installing Chrome Remote Desktop")
        subprocess.run(['wget', 'https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb'], stdout=subprocess.PIPE)
        subprocess.run(['dpkg', '--install', 'chrome-remote-desktop_current_amd64.deb'], stdout=subprocess.PIPE)
        subprocess.run(['apt', 'install', '--assume-yes', '--fix-broken'], stdout=subprocess.PIPE)

    @staticmethod
    def installDesktopEnvironment():
        print("Installing Desktop Environment")
        os.system("export DEBIAN_FRONTEND=noninteractive")
        os.system("apt install --assume-yes xfce4 desktop-base xfce4-terminal")
        os.system("bash -c 'echo \"exec /etc/X11/Xsession /usr/bin/xfce4-session\" > /etc/chrome-remote-desktop-session'")
        os.system("apt remove --assume-yes gnome-terminal")
        os.system("apt install --assume-yes xscreensaver")
        os.system("systemctl disable lightdm.service")

    @staticmethod
    def installGoogleChorme():
        print("Installing Google Chrome")
        subprocess.run(["wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"], stdout=subprocess.PIPE)
        subprocess.run(["dpkg", "--install", "google-chrome-stable_current_amd64.deb"], stdout=subprocess.PIPE)
        subprocess.run(['apt', 'install', '--assume-yes', '--fix-broken'], stdout=subprocess.PIPE)

    @staticmethod
    def finish(user):
        print("Finalizing")
        if Autostart:
            autostart_dir = Path(f"/home/{user}/.config/autostart")
            autostart_dir.mkdir(parents=True, exist_ok=True)
            link = "https://colab.research.google.com/github/PradyumnaKrishna/Colab-Hacks/blob/master/Colab%20RDP/Colab%20RDP.ipynb"
            colab_autostart = f"""[Desktop Entry]
Type=Application
Name=Colab
Exec=sh -c "sensible-browser {link}"
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true"""
            with open(autostart_dir / "colab.desktop", "w") as f:
                f.write(colab_autostart)
            os.system(f"chmod +x {autostart_dir / 'colab.desktop'}")
            os.system(f"chown {user}:{user} {autostart_dir}")

        os.system(f"adduser {user} chrome-remote-desktop")
        command = f"{CRP} --pin={Pin}"
        os.system(f"su - {user} -c '{command}'")
        os.system("service chrome-remote-desktop start")

try:
    if CRP == "":
        print("Please enter authcode from the given link")
    elif len(str(Pin)) < 6:
        print("Enter a pin more or equal to 6 digits")
    else:
        CRD(username)
except NameError as e:
    print("'username' variable not found, Create a user first")

# Google Drive Mount part
mount_method = "GDFuse"
label = "default"
mount_team_drive = False
force_mount = False

class Drive():
    def __init__(self, mountpoint="/home/user/drives"):
        self.mountpoint = Path(mountpoint)
        os.makedirs(self.mountpoint, exist_ok=True)

    def _mount_gdfuse(self, mount_dir):
        os.makedirs(mount_dir, exist_ok=True)

        subprocess.run(
            ['google-drive-ocamlfuse',
             '-o',
             'allow_other',
             '-label',
             label,
             mount_dir,
            ]
        )

        print(f"Drive Mounted at {mount_dir}. If you get input/output error, then `team_drive_id` might be wrong or not accessible.")

    def auth(self):
        pass  # No authentication needed in GitHub Codespace

    def gdfuse(self, label, mound_team_drive=False, force_mount=False):
        base_dir = Path('/root/.gdfuse')
        config_dir = base_dir / label
        mount_dir = self.mountpoint / label

        if force_mount and mount_dir.exists():
            self._unmount_gdfuse(mount_dir)
        elif mount_dir.exists():
            print("Drive already mounted")
            return

        self._mount_gdfuse(mount_dir)

    def native(self):
        pass  # Not applicable in GitHub Codespace

if mount_method == "GDFuse":
    drive = Drive()
    drive.gdfuse(label, mount_team_drive, force_mount)
