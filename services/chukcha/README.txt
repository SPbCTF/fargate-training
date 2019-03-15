echo 0 > /proc/sys/kernel/randomize_va_space
apt install cmake gcc-multilib g++-multilib
sudo dpkg --add-architecture i386
sudo apt-get update
apt install libevent-dev:i386
mkdir files
