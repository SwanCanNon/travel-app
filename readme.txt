Alan Airlines Travel Application
Author: Alan Paniagua
Youtube URL: https://youtu.be/kKdg3iZubqM

Prerequisites:
-Install Python 3
-Set up environment variables

No installation of this application is required.

To run the app, navigate to the directory where you placed the zip files and open a command prompt.
Begin the server by typing:
"python serverTravel.py"
Once the server is running, open a new command prompt and type:
'serverTravel.py'

Available commands:
LIST - list available flights
SEARCHD [destination] - search one-way flights with specified destination
SEARCHALL [destination] - search one-way flights with specified destination or departure
SEARCHS [departure] - search one-way flights with specified departure
BUY_TICKET [where] [seats] - purchase specified amount of tickets to flight
BUYRT-TICKET [where] [seats] - purchase specified amount of roundtrip tickets
RETURN_TICKET [where] [seats] - return specified amount of one-way tickets
RETURNRT_RICKET [where] [seats] - return specified amount of roundtrip tickets
[destination] and [departures] must be in the form of a 3-letter code. (ex: MIA)
[where] must be in the form of 3-letter codes, separated by a dash. (ex: MIA-ORL)
[seats] must be a number.
