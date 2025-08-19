import duckdb
import xml.etree.ElementTree as ET
import datetime
import argparse
from country_bounding_boxes import (
    country_subunits_by_iso_code
)

def generate_osm_changeset_xml(name, category, country_code):
    # Connect to DuckDB
    con = duckdb.connect()
    con.sql("INSTALL spatial;")
    con.sql("LOAD spatial;")

    # Query overture maps parquet
    # Get bounding box for the country
    countries = [c for c in country_subunits_by_iso_code(country_code)]
    if len(countries) != 1:
        raise ValueError(f"Problem with code '{country_code}'!")
    
    lon_min, lat_min, lon_max, lat_max = countries[0].bbox

    query = f"""
    SELECT
        * EXCLUDE(id, confidence, geometry, version, bbox, phones, theme, type),
        ST_X(geometry) AS lon,
        ST_Y(geometry) AS lat,
    FROM read_parquet('s3://overturemaps-us-west-2/release/2025-07-23.0/theme=places/type=place/*')
    WHERE addresses[1].country = '{country_code.upper()}'
      AND names.primary ILIKE '%{name}%'
      AND categories.primary ILIKE '%{category}%'
      AND bbox.xmin > {lon_min} AND bbox.xmax < {lon_max}
      AND bbox.ymin > {lat_min} AND bbox.ymax < {lat_max};
    """

    row = con.execute(query).fetchone()
    if not row:
        raise ValueError(f"No results found for {name} in category {category}")

    cols = [c[0] for c in con.description]
    data = dict(zip(cols, row))

    # Build XML structure
    osm = ET.Element("osm", version="0.6", generator="duckdb-overture2osm")

    # Create changeset element
    changeset = ET.SubElement(osm, "changeset", id="1", created_at=datetime.datetime.utcnow().isoformat())

    # Add metadata tags
    ET.SubElement(changeset, "tag", k="created_by", v="duckdb-overture2osm")
    ET.SubElement(changeset, "tag", k="comment", v=f"Add place {data['names']['primary']} from Overture Maps")

    # Create node (OSM element for the place)
    node = ET.SubElement(
        osm,
        "node",
        id="-1",
        lat=str(data['lat']),
        lon=str(data['lon']),
        visible="true"
    )

    # Mandatory tags
    ET.SubElement(node, "tag", k="name", v=data["names"]["primary"])
    ET.SubElement(node, "tag", k="amenity", v=data["categories"]["primary"])

    # Optional tags from data
    if data.get("websites"):
        ET.SubElement(node, "tag", k="website", v=data["websites"][0])
    if data.get("socials"):
        ET.SubElement(node, "tag", k="contact:facebook", v=data["socials"][0])
    if data.get("emails") and data["emails"][0]:
        ET.SubElement(node, "tag", k="email", v=data["emails"][0])

    if data.get("addresses"):
        addr = data["addresses"][0]
        if addr.get("freeform"):
            ET.SubElement(node, "tag", k="addr:full", v=addr["freeform"])
        if addr.get("locality"):
            ET.SubElement(node, "tag", k="addr:city", v=addr["locality"])
        if addr.get("postcode"):
            ET.SubElement(node, "tag", k="addr:postcode", v=addr["postcode"])
        if addr.get("region"):
            ET.SubElement(node, "tag", k="addr:region", v=addr["region"])
        if addr.get("country"):
            ET.SubElement(node, "tag", k="addr:country", v=addr["country"])

    # Pretty-print XML
    return ET.tostring(osm, encoding="utf-8").decode("utf-8")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Place name, e.g. 'SYÖMÄÄN'")
    parser.add_argument("--category", required=True, help="Category, e.g. 'restaurant'")
    parser.add_argument("--country", required=True, help="ISO 3166-1 alpha-2 country code, e.g. 'FI' for Finland")
    args = parser.parse_args()

    xml_output = generate_osm_changeset_xml(args.name, args.category, args.country)
    print(xml_output)