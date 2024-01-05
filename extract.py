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

    # TODO: Java app extraction from 6020

    i += 1
    if i >= len(chunked): break

with open(sys.argv[1] + ".img", 'wb') as out_file:
    out_file.write(bytes(unchunked))