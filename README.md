# predeftool
Work-in-progress tool for bulk extracting preinstalled content from Nokia firmware packages. The ultimate goal is to create a massive repository of preinstalled games, apps, and themes found on various Nokia phones.

## Status
### Supported models
* 6030 (RM-74)
* 5070/6070/6080 (RM-166)

### Partially supported models
* 6020 (RM-30): Java apps are stored in a different format, so they are not extracted

### Unsupported models
All of these use a different installer file structure compared to the supported models.
* 2610 (RH-86)
* 2630 (RM-298)
* 6610 (NHL-4U)

## Usage
As the tool is primarily developed on Linux, support for other operating systems is untested and unlikely.

### Prerequisites
* Python 3
* Wine
* [binwalk](https://github.com/ReFirmLabs/binwalk)
* [unshield](https://github.com/twogood/unshield)

### Usage examples
* `./main.sh` - extracts all firmware EXE packages
* `./main.sh clean` - deletes all temporary files used for extraction, but keeps packages and extracted content

### Advanced usage
* `python extract.py /path/to/image` - converts a Nokia image file into a FAT16 filesystem image, outputs to /path/to/image.img
* `./main.sh mount /path/to/image.img` - mounts a file system image in the same way that the tool does
* `./main.sh unmount` - unmounts any temporary file systems used by the tool, useful in the case of an error, or when using the mount command

## Known issues
* When extracting, you will get a "no such file or directory" warning about a "ucp" or "image" folder, this is normal.

## Useful links
* [PhoneTones, an existing repository of ringtones](http://onj3.andrelouis.com/phonetones/zipped/Nokia/)
* [Nokia DCT4 firmware packages](https://archive.org/details/Nokia_DCT4_firmwares)
* [Nokia BB5 firmware packages](https://archive.org/details/Nokia_BB5_firmwares)