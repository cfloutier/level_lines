# level_lines
creates svg level lines from osm files

# installation

* install python

```powershell

  # in this folder. creates the local virtual env in the venv folder (ignored in git)
  python -m venv venv
  # Activate the environment:

  #source ./venv/bin/activate # bash/zsh shells, like on mac, ubuntu
  .\venv\Scripts\Activate.ps1 # windows powershell

  # install dependencies
  pip install -e . 
```

* add Srtm2Osm folder containing the Srtm2Osm.exe

see https://wiki.openstreetmap.org/wiki/Srtm2Osm

on windows : 
`osm2svg\Srtm2Osm\Srtm2Osm.exe`

# run 

the command line use simplified parameters using only the bounding rect









