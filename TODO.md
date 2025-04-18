- Scan for new Extensions AKA `set` from Scryfall API
- Docker image to download the MGTA Game (https://steamdb.info/app/2141910/) & extract music files with Top 2 `set` with https://github.com/Vextil/Wwise-Unpacker

``docker run -it -v $PWD:/data steamcmd/steamcmd:latest +login anonymous +force_install_dir /data +app_update 2141910 +quit``

- Image to download from Wizards website
- Output to be named after "MTG Arena OST - `set` - X/X"

```
#!/bin/bash
image="image.jpg"
audio="audio.mp3"
output="output.mp4"

ffmpeg -loop 1 -i $image -i $audio -filter_complex \
"[0:v]fade=t=in:st=0:d=2,fade=t=out:st=58:d=2[v];[1:a]afade=t=in:st=0:d=2,afade=t=out:st=58:d=2[a]" \
-map "[v]" -map "[a]" -c:v libx264 -c:a aac -shortest -s hd1080 $output
```
- Redirect output to pyyuploader and adapt with https://www.youtube.com/@mtgarenaost ``credentials.json`` & ``token.json``