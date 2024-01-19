#!/bin/bash

if [[ "$1" == "clean" ]]; then
    rm -rf logs
    rm -rf packages/*/
    rm -rf images
    while sudo umount mountpoint 2> /dev/null; do true; done
    exit 0
fi
if [[ "$1" == "mount" ]]; then
    sudo mount -t vfat -o utf8=1 $2 mountpoint
    exit 0
fi
if [[ "$1" == "unmount" ]]; then
    while sudo umount mountpoint 2> /dev/null; do true; done
    exit 0
fi

# -k to keep temporary files, useful for testing
if [[ "$1" == "-k" ]]; then
    KEEP=1
else
    KEEP=0
fi

# ______________________________________________________________________________
#
#  Check for command availability
# ______________________________________________________________________________
#
EXIT=0

if ! command -v python3 > /dev/null; then
    echo "Please install Python 3"
    EXIT=1
fi
if [[ "$(uname)" != "Windows_NT" && $(! command -v wine > /dev/null) ]]; then
    echo "Please install Wine"
    EXIT=1
fi
if ! command -v unshield > /dev/null; then
    echo "Please install unshield from https://github.com/twogood/unshield"
    EXIT=1
fi

[[ $EXIT == 1 ]] && exit 1

# ______________________________________________________________________________
#
#  Extract packages (Nokia firmware EXEs) to images (filesystem contents)
# ______________________________________________________________________________
#
mkdir -p logs packages images mountpoint content

echo "You may soon get asked for your sudo password. This is so we can mount filesystem images to extract content from."
echo "After extraction, make sure to check the error logs in each content folder."

cd packages
PACKAGES=$(ls)
cd ..

for PKG in $PACKAGES; do
    PKGBASE=$(basename $PKG .exe)

    mkdir -p images/$PKGBASE content/$PKGBASE

    # Use IsXunpack to extract CAB files from the firmware EXE
    # Note: IsXunpack requires user input to exit(?!) but we give it any file
    #       as stdin to make it automatically exit
    echo Extracting: $PKGBASE
    cd packages
    wine ../IsXunpack.exe $PKG < ../main.sh > ../logs/isxunpack.log
    cd ..

    # Use unshield to extract InstallShield installation package
    if [[ -e packages/Disk1 ]]; then
        for CAB in packages/Disk*/data*.cab; do
            unshield x $CAB -d packages > logs/unshield.log
        done
    else
        echo "This package is currently unsupported. Try a DCT4 firmware, such as Nokia 6030."
        continue
    fi

    # Older packages have a products folder, newer ones have ProductData
    if [[ -e packages/products ]]; then
        PRODUCTDIR=packages/products
    elif [[ -e packages/ProductData ]]; then
        PRODUCTDIR=packages/ProductData
    fi

    # DPC file contains the image files, the firmware package includes an
    # extractor EXE that normally runs at installation time
    cd $PRODUCTDIR
    if cd * 2> /dev/null; then
        SUBDIR=1
    else
        SUBDIR=0
    fi
    if [[ $PRODUCTDIR == packages/products ]]; then
        COMPACTOR=*ompactor.exe
    else
        COMPACTOR=../_Support_Language_Independent_OS_Independent_Files/*ompactor.exe
    fi
    wine $COMPACTOR *.dpc
    cd ../..
    if [[ $SUBDIR == 1 ]]; then cd .. ; fi

    # Move image files to a separate folder
    # Older phones (e.g. 6610) use 'ucp' (user content package) in the file name
    # Newer phones (e.g. 6020, 6030) use 'image' instead
    # And then there's some phones that don't have a subdirectory under products/
    if [[ $SUBDIR == 1 ]]; then
        mv $PRODUCTDIR/*/*ucp* images/$PKGBASE
        mv $PRODUCTDIR/*/*image* images/$PKGBASE
    else
        mv $PRODUCTDIR/*ucp* images/$PKGBASE
        mv $PRODUCTDIR/*image* images/$PKGBASE
    fi

    IMGDIR=images/$PKGBASE
    cd $IMGDIR
    IMAGES=$(ls)
    cd ../..

    # Use a custom Python extractor to convert Nokia image files to standard
    # FAT16 filesystem images, then mount and dump the filesystem images
    for IMG in $IMAGES; do
        mkdir -p content/$PKGBASE/$IMG/
        LOG=content/$PKGBASE/log.txt
        echo $IMG: >> $LOG

        python extract.py $IMGDIR/$IMG content/$PKGBASE/$IMG 2>> $LOG
        sudo mount -t vfat -o utf8=1 $IMGDIR/$IMG.img mountpoint 2>> $LOG
        cp -rf mountpoint/* content/$PKGBASE/$IMG/ 2>> $LOG
        sudo umount mountpoint 2>> $LOG

        # Delete original Nokia image file and converted filesystem image
        if [[ $KEEP == 0 ]]; then
        rm $IMGDIR/$IMG $IMGDIR/$IMG.img
        fi

        echo "" >> $LOG
    done

    # Delete IsXunpack extracted folder to save disk space, it's not needed anymore
    if [[ $KEEP == 0 ]]; then
        rm -rf packages/*/ $IMGDIR
    fi
done