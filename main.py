import subprocess, zlib, tarfile, io, sqlite3, datetime


print subprocess.check_output(['adb','backup','-f','export_data.ab','-noapk','com.huami.watch.sport'])

with open('export_data.ab', 'rb') as f:
    f.seek(24)
    data = f.read()

tarstream = zlib.decompress(data)
tf = tarfile.open(fileobj=io.BytesIO(tarstream))
f = tf.extractfile('apps/com.huami.watch.sport/db/sport_data.db')

file = open("db.db", "w")
file.write(f.read())
file.close()

gpx = open("gpx.gpx", "w")
gpx.write("""<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
<gpx version="1.0" creator="AmazGPX" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/0" xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
""")

conn = sqlite3.connect('db.db')

"""
counter = 0
ids = []
for summary in conn.execute('SELECT track_id, start_time, end_time FROM sport_summary ORDER BY track_id ASC'):

    counter += 1

    id = summary[0]
    ids[counter] = id
    start_time = datetime.datetime.utcfromtimestamp(summary[1] / 1000)
    end_time = datetime.datetime.utcfromtimestamp(summary[2] / 1000)


    print counter, id, start_time, end_time


start_id = raw_input("Start with ID: ")

"""


counter = 0
for summary in conn.execute('SELECT track_id, start_time, end_time FROM sport_summary ORDER BY track_id ASC'):

    counter += 1

    id = summary[0]
    start_time = datetime.datetime.utcfromtimestamp(summary[1]/1000)
    end_time = datetime.datetime.utcfromtimestamp(summary[2]/1000)

    print id, start_time, end_time

    gpx.write("""
    <trk>
      <name>GPX Track - """ + str(id) + """</name>
      <number>""" + str(counter) + """</number>
    <trkseg>""")

    ccounter = 0

    for location in conn.execute('SELECT timestamp, latitude, longitude, bar, altitude, accuracy, speed, course FROM location_data WHERE track_id = "' + str(id) + '" ORDER BY timestamp ASC'):

        ccounter += 1

        timestamp = datetime.datetime.utcfromtimestamp((summary[1]+location[0])/1000)
        latitude = location[1]
        longitude = location[2]
        bar = location[3]
        altitude = location[4]
        if altitude > -500:
            alt = "<ele>" + str(altitude) + "</ele>"
        else:
            alt = ""
        accuracy = location[5]
        speed = location[6]
        course = location[7]

        print timestamp, latitude, longitude, bar, altitude, accuracy, speed, course

        gpx.write("<trkpt lat=\"" + str(latitude) + "\" lon=\"" + str(longitude) + "\">\n\
            " + alt + "<time>" + str(timestamp.isoformat()) + "Z</time>\n\
            <course>" + str(course) + "</course>\n\
            <speed>" + str(speed) + "</speed>\n\
            <name>" + str(ccounter) + "</name>\n</trkpt>\n")

    gpx.write("""
     </trkseg>
    </trk>
    """)

gpx.write("""
</gpx>
""")