data/mc_parking.json:
	./get_data.sh > $@

mc_parking.osm: data/mc_parking.json
	./main.py > $@
