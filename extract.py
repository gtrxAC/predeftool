import os, sys, re

chunked = []
unchunked = []

with open(sys.argv[1], 'rb') as file:
    header = file.read(500)
    file.seek(header.find(bytes([0x14, 0x01])) + 10)

    while chunk := file.read(16384):
        chunked += chunk
        file.seek(10, 1)

i = 0
count = 0
last_chunk_idx = -1
top_chunk_idx = -1

while True:
    # (0xFF 0xF0 0xFF 0xFF) (4 bytes: chunk index) (512 bytes: chunk data) - write chunk
    if chunked[i:i+4] == [0xff, 0xf0, 0xff, 0xff]:
        i += 4
        chunk_idx = int.from_bytes(chunked[i:i+4], byteorder='big')
        i += 4

        # If skipped through chunks, write blank chunks between the last one and the current one's position
        while chunk_idx > last_chunk_idx + 1:
            unchunked += [0] * 512
            last_chunk_idx += 1

        top_chunk_idx = -1
        if chunk_idx > top_chunk_idx:
            # Append new chunk
            unchunked += bytes(chunked[i:i+512])
            top_chunk_idx = chunk_idx
        else:
            # if chunk indexes are not in sequential order (some images like 6020, but not 6030), we need to insert the data in between
            unchunked = unchunked[:chunk_idx*512] + bytes(chunked[i:i+512]) + unchunked[chunk_idx*512 + 512:]
            
        i += 511
        last_chunk_idx = chunk_idx

    # PPM file system structure for 2650
    # Also used as a separate partition for storing Java content on 3220/6020/7260
    #
    # Data structure (big endian):
    # ...some metadata that we don't care about...
    # 10 bytes: 0xFF FF 00 00 00 E8 00 00 00 F8 - we use these bytes to identify a file
    # 200 bytes: filename utf16be
    # 32 bytes: irrelevant
    # ...keep seeking until we find 0xFF FF or 0x01 FF (skip those two bytes)
    # 4 bytes: chunk size
    # 4 bytes: irrelevant
    # ...first chunk data...
    # 2 bytes: 0xF0 0xF0 means the start of another chunk
    # 22 bytes: irrelevant
    # 4 bytes: chunk size
    # 4 bytes: irrelevant
    # ...second chunk data...
    # 2 bytes: 0xFF 0xFF means the end of this file and beginning of another
        
    # There are file system entries for folders and such, so we could preserve
    # the original folder structure, but that's not too important to me and it
    # requires a bit more work
    if chunked[i:i+10] == [0xFF, 0xFF, 0x00, 0x00, 0x00, 0xE8, 0x00, 0x00, 0x00, 0xF8]:
        i += 10
        filename = bytes.decode(bytes(chunked[i:i+200]), "utf_16_be")
        filename = filename.replace("\x00", "") # because bytes.decode apparently doesn't null terminate
        i += 200
        if chunked[i] == 0x07:
            with open(os.path.join(sys.argv[2], filename), 'wb') as java_file:
                i += 32
                filesize = 0
                while filesize <= 16:
                    while chunked[i:i+3] != [0xFF, 0x00, 0x00]: i += 1
                    i += 1
                    filesize = int.from_bytes(chunked[i:i+4], byteorder='big')

                while True:
                    i += 8
                    java_file.write(bytes(chunked[i:i+filesize]))
                    i += filesize

                    # 0xF0 0xF0 means there is another chunk of this file, 0xFF 0xFF is the beginning of the next file
                    if chunked[i:i+2] == [0xF0, 0xF0]:
                        # i += 22
                        while chunked[i:i+3] != [0xFF, 0x00, 0x00]: i += 1
                        i += 1
                        filesize = int.from_bytes(chunked[i:i+4], byteorder='big')
                    else:
                        i -= 1
                        break

    i += 1
    if i >= len(chunked): break

with open(sys.argv[1] + ".img", 'wb') as out_file:
    out_file.write(bytes(unchunked))