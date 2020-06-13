## Getting started

Add the required libraries pymunk and pygame, the pygame version should be 1.9.4 or higher:

To run the game you simply need to go in the source code directory and run the following
command: python3 ctf.py

Read maps from a text file is supported for example notepad:
The command: python3 ctf.py --map my\_map.txt <=== Your own created text file

Level editor: 
This editor should be started using the following command:
python3 ctf-editor.py [width] [height].
Where [width] and [height] are parameters pass by the user which defines the size of the map, for instance, if a user wants to create a 10x12 map, he will use the following command: python3 ctf-editor.py 10x12

