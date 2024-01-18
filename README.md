# predeftool
Work-in-progress tool for bulk extracting preinstalled content from Nokia firmware packages.

This collection of scripts is used to create [predefrepo](http://www.romphonix.org/dumbphone-repo/predefrepo%20(Preloaded%20content)/), a repository of preinstalled games, apps, and themes found on various Nokia phones.

## Status
* In theory, most GSM S40v2 (DCT4 platform) phones should be supported, but newer phones use a .NET based installer EXE with a different file structure, which are incompatible.
* S40v1 phones use a custom filesystem (PPM), which is not supported right now, but it seems to be relatively simple.
* DCT4.5 (TIKU) phones like the 6230 use a different image format (but the underlying file system is standard FAT16), so they shouldn't be too difficult to support.
* BB5 firmware packages cannot be extracted yet.

### Supported models
* 5070/6070/6080 (RM-166/RM-167)
* 6021 (RM-94)
* 6030 (RM-74)
* 6101/6102 (RM-76/RM-77)
* 6103 (RM-161/RM-162)
* 6822 (RM-68/RM-69)
* 7360 (RM-127)

### Partially supported models
* 2650/2652 (RH-53): early firmware versions will fail to extract
* 3220 (RH-37/RH-49): same as 2650
* 6020 (RM-30/RM-31): same as 2650
* 7260 (RM-17): same as 2650

### Unsupported models
* 2610 (RH-86)
* 2630 (RM-298)
* 6060 (RH-73)
* 6610 (NHL-4U)
* 3510i (RH-9)

## Usage
As the tool is primarily developed on Linux, support for other operating systems is untested and unlikely.

### Prerequisites
* Python 3
* Wine
* [binwalk](https://github.com/ReFirmLabs/binwalk)
* [unshield](https://github.com/twogood/unshield)

### Steps
1. Clone the repository.
2. Download firmware package EXEs (see Useful links below) and put them in the **packages** folder.
3. To extract content from the installer EXEs, run `./main.sh`. Content is placed into the **content** folder.
4. To create an index of all apps, games, and themes, run `python index.py content index.json`.
5. To create a sorted archive of all apps, games, and themes listed in the index, run `python sort.py index.json`. The sorted content is placed into the **sorted** folder.

### Advanced usage
* `./main.sh clean` - deletes all temporary files used for extraction, but keeps packages and extracted content
* `./main.sh mount /path/to/image.img` - mounts a file system image in the same way that the tool does
* `./main.sh unmount` - unmounts any temporary file systems used by the tool, useful in the case of an error, or when using the mount command
* `python extract.py /path/to/image` - converts a Nokia image file into a FAT16 filesystem image, outputs to /path/to/image.img

## Known issues
* When extracting, you will get a "no such file or directory" warning about a "ucp" or "image" folder, this is normal.
* "we got fault packet with status 0x1c010003" is a normal warning message produced by Wine and does not affect extraction.

## Useful links
* [PhoneTones, an existing repository of ringtones](http://onj3.andrelouis.com/phonetones/zipped/Nokia/)
* [Nokia DCT4 firmware packages](https://archive.org/details/Nokia_DCT4_firmwares)
* [Nokia BB5 firmware packages](https://archive.org/details/Nokia_BB5_firmwares)