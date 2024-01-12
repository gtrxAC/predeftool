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

    # Java games are stored on a separate partition on 6020/3220, example data structure:
        
    # ...some metadata that we don't care about...
    # 10 bytes: 0xFF FF 00 00 00 E8 00 00 00 F8 - we use these bytes to identify a file
    # 200 bytes: filename utf16be
    # 40 bytes: irrelevant
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
            javapath = sys.argv[1] + '_java'
            os.makedirs(javapath, exist_ok=True)

            with open(os.path.join(javapath, filename), 'wb') as java_file:
                i += 40
                # JAR files have a larger metadata header thing (not always the same size)
                # but we can find the beginning of the JAR data ('PK') and count backwards from it
                # to get the actual size
                if filename.endswith('jar'): #int.from_bytes(chunked[i:i+4], byteorder='big') < 50:
                    i += bytes(chunked[i:]).find(bytes([0x50, 0x4B])) - 8

                while True:
                    filesize = int.from_bytes(chunked[i:i+4], byteorder='big')
                    i += 8
                    java_file.write(bytes(chunked[i:i+filesize]))
                    i += filesize

                    # 0xF0 0xF0 means there is another chunk of this file, 0xFF 0xFF is the beginning of the next file
                    if chunked[i:i+2] == [0xF0, 0xF0]:
                        i += 22
                    else:
                        i -= 1
                        break

    i += 1
    if i >= len(chunked): break

with open(sys.argv[1] + ".img", 'wb') as out_file:
    out_file.write(bytes(unchunked))