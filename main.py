#!/usr/bin/env python3
"""OSM changeset for motorcycle parking in Hong Kong"""

# pylint: disable=invalid-name

import json
from xml.dom import minidom
from dataclasses import dataclass
from typing import NamedTuple, Optional, TypeVar

T = TypeVar("T")

Coordinates = NamedTuple("Coordinates", [("lat", float), ("long", float)])
StreetName = NamedTuple("StreetName", [("en", str), ("tc", str)])

class OSMChange:
    """OSM Changeset"""

    def __init__(self) -> None:
        self.root = minidom.Document()
        osmchange = self.root.createElement("osmChange")
        self.root.appendChild(osmchange)
        self.create = self.root.createElement("create")
        osmchange.appendChild(self.create)
        self.counter = 0

    @property
    def _node_id(self) -> int:
        self.counter -= 1
        return self.counter

    def create_node(self, coordinates: Coordinates,
                    tags: Optional[dict] = None) -> None:
        """Create a node"""
        node = self.root.createElement("node")
        node.setAttribute("id", str(self._node_id))
        node.setAttribute("lat", str(coordinates.lat))
        node.setAttribute("long", str(coordinates.long))

        if tags:
            for k, v in tags.items():
                tag = self.root.createElement("tag")
                tag.setAttribute("k", str(k))
                tag.setAttribute("v", str(v))
                node.appendChild(tag)

        self.create.appendChild(node)

    def render(self) -> str:
        """Dump OSM XML data"""
        return self.root.toprettyxml(indent="  ").strip()

@dataclass
class Feature:
    """Motorcycle parking spot"""
    id: str
    street_name: StreetName
    coordinates: Coordinates


def try_title(x: T) -> T:
    """Title case if possible"""
    try:
        return x.title() # type: ignore
    except AttributeError:
        return x

def feature_builder(raw_feature: dict) -> Feature:
    """Helper to build features"""
    prop = raw_feature["properties"]
    coordinates = Coordinates(*raw_feature["geometry"]["coordinates"][::-1])
    struct = {"id": prop["PARKING_SPACE_ID"],
              "street_name": StreetName(try_title(prop["STREET_NAME_EN"]),
                                        prop["STREET_NAME_TC"]),
              "coordinates": coordinates}
    return Feature(**struct)


def sanitize_raw_features(raw_features: list[dict]) -> list[dict]:
    """Sort and remove invalid features"""
    for feature in raw_features:
        try:
            int(feature["properties"]["PARKING_SPACE_ID"])
        except ValueError:
            raw_features.remove(feature)

    raw_features = sorted(raw_features,
        key = lambda k: int(k["properties"]["PARKING_SPACE_ID"]))

    return raw_features


def main() -> None:
    """Entry point"""

    with open("data/mc_parking.json", encoding="utf-8") as fd:
        mc_parking = sanitize_raw_features(json.load(fd)["features"])

    osmchange = OSMChange()

    for spot in mc_parking:
        feature = feature_builder(spot)
        try:
            tags = {"id": feature.id,
                    "name": feature.street_name.tc + " " + feature.street_name.en,
                    "name:en": feature.street_name.en,
                    "name:zh": feature.street_name.tc,
                    "amenity": "motorcycle_parking",
                    "parking": "street_side",
                    "access": "yes"}
            osmchange.create_node(feature.coordinates, tags)
        except TypeError:
            pass

    print(osmchange.render())


if __name__ == "__main__":
    main()
