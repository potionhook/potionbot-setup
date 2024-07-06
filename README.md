# Download and Install potionbots

    git clone https://github.com/potionhook/potionbot-setup; cd potionbot-setup; chmod +x ./fix; ./fix; ./install-catbots; ./update; cd .


You need to do "chmod +x ./fix; ./fix;" everytime you update.

After installing you need to edit accounts.txt and add your bot accounts in the following format
USERNAME:PASSWORD
USERNAME:PASSWORD

## Required Dependencies
Arch (High Support)
`sudo pacman -Syu git boost cmake make gcc gdb lib32-sdl2 lib32-glew lib32-freetype2 rsync lib32-libglvnd dialog curl nodejs npm firejail net-tools xorg-xhost xorg-server-xvfb dialog`

Debian
`sudo apt-get install nodejs firejail net-tools x11-xserver-utils npm`

Fedora/Centos
`sudo dnf install nodejs firejail net-tools xorg-x11-server-utils`


