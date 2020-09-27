appname="rclone-sync"

echo "###Create DEB file"
if [ -d ~/build ]; then echo '..'; else echo 'DEB folder missing!'; fi
mkdir ~/build/linux32/deb
mkdir ~/build/linux32/deb/DEBIAN
cp createdeb/deb/control ~/build/linux32/deb/DEBIAN/control
cp createdeb/deb/after-install.sh ~/build/linux32/deb/DEBIAN/postinst
cp createdeb/deb/after-remove.sh ~/build/linux32/deb/DEBIAN/postrm

mkdir ~/build/linux32/deb/opt

#opt
cp -avr opt ~/build/linux32/deb/tmp
mv ~/build/linux32/deb/tmp ~/build/linux32/deb/opt/$appname

#nautilus
mkdir ~/build/linux32/deb/usr
mkdir ~/build/linux32/deb/usr/share
mkdir ~/build/linux32/deb/usr/share/nautilus-python
mkdir ~/build/linux32/deb/usr/share/nautilus-python/extensions
cp -avr nautilus/. ~/build/linux32/deb/usr/share/nautilus-python/extensions

#autostart
mkdir ~/build/linux32/deb/etc
mkdir ~/build/linux32/deb/etc/xdg
mkdir ~/build/linux32/deb/etc/xdg/autostart
cp createdeb/deb/autostart.aldesktop ~/build/linux32/deb/etc/xdg/autostart/$appname.desktop

#app icon
cp createdeb/deb/app.aldesktop ~/build/linux32/deb/opt/$appname/$appname.desktop
cp createdeb/deb/icon.png ~/build/linux32/deb/opt/$appname/$appname.png

mkdir ~/build/linux32/deb/usr/share/applications
cp createdeb/deb/app.aldesktop ~/build/linux32/deb/usr/share/applications/$appname.desktop
mkdir ~/build/linux32/deb/usr/share/doc
mkdir ~/build/linux32/deb/usr/share/doc/$appname

sudo chmod 755 /home/vmarci21/build/linux32/deb -R
chmod 775 /home/vmarci21/build/linux32/deb/DEBIAN/postinst
chmod 775 /home/vmarci21/build/linux32/deb/DEBIAN/postrm

#echo "###MD5"
#cd /home/vmarci21/build/linux32/deb/opt
#md5sum > ../DEBIAN/md5sums

SIZE=$(du -hs -b | cut -f1)
cd ~/build/linux32
sed -i 's/_size_/'$SIZE'/' deb/DEBIAN/control

#nautilus

dpkg-deb --build deb
cp deb.deb $appname-nautilus.deb
cd ~/build/linux32
rm deb.deb
echo "### 64 bit finish"

sed -i 's/amd64/i386/' deb/DEBIAN/control

cd ~/build/linux32
dpkg-deb --build deb
cp deb.deb $appname-nautilus-32.deb
cd ~/build/linux32
rm deb.deb
echo "### 32 bit finish"

#Nemo

mkdir ~/build/linux32/deb/usr/share/nemo-python
mkdir ~/build/linux32/deb/usr/share/nemo-python/extensions
sleep 1
mv ~/build/linux32/deb/usr/share/nautilus-python/extensions ~/build/linux32/deb/usr/share/nemo-python
rm -rf ~/build/linux32/deb/usr/share/nautilus-python

sed -i 's/python-nautilus/python-nemo/' deb/DEBIAN/control
sed -i 's/i386/amd64/' deb/DEBIAN/control
sed -i 's/nautilus -q/nemo -q/' deb/DEBIAN/postinst

dpkg-deb --build deb
cp deb.deb $appname-nemo.deb
cd ~/build/linux32
rm deb.deb
echo "### 64 bit finish"

sed -i 's/amd64/i386/' deb/DEBIAN/control

cd ~/build/linux32
dpkg-deb --build deb
cp deb.deb $appname-nemo-32.deb
cd ~/build/linux32
rm deb.deb
echo "### 32 bit finish"

#Caja

mkdir ~/build/linux32/deb/usr/share/caja-python
mkdir ~/build/linux32/deb/usr/share/caja-python/extensions
sleep 1
mv ~/build/linux32/deb/usr/share/nemo-python/extensions ~/build/linux32/deb/usr/share/caja-python
rm -rf ~/build/linux32/deb/usr/share/nemo-python

sed -i 's/python-nemo/python-caja/' deb/DEBIAN/control
sed -i 's/i386/amd64/' deb/DEBIAN/control
sed -i 's/nemo -q/caja -q/' deb/DEBIAN/postinst

dpkg-deb --build deb
cp deb.deb $appname-caja.deb
cd ~/build/linux32
rm deb.deb
echo "### 64 bit finish"

sed -i 's/amd64/i386/' deb/DEBIAN/control

cd ~/build/linux32
dpkg-deb --build deb
cp deb.deb $appname-caja-32.deb
cd ~/build/linux32
rm deb.deb
echo "### 32 bit finish"

rm -rf deb
echo "###  finish"