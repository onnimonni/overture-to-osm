# overture2osm demo

> [!WARNING]  
> Using this has not been approved by OvertureMaps nor OpenStreetMap. This is just a demo for an idea and exploration to help tagging more information and reduce manual burden

This uses data from https://overturemaps.org to populate data for new places in OpenStreetMap.

It outputs OSM changeset XML which can then be uploaded into OpenStreetMap.

## Example case

I noticed that a restaurant in Finland existed in Overture Maps but did not exist in OpenStreetMap.

I wanted to add it to OSM so that I could tag following information:

```
dog=outside
toilets=yes
toilets:position=seated
lunch=buffet
lunch:buffet=Mo-Fr 10:30-14
wheelchair=no
stroller=limited
changing_table=no
```

This would help others to not enter with dogs and to know about these basic details.

But adding the whole place manually seems like a bit stupid use of time.

## Usage

Here's an example which reads information of the restaurant called "SYÖMÄÄN" in Valkeakoski Finland. 

If you run following commands you will get the xml output below:

```
$ brew install uv
$ uv venv
$ uv run ./overture2osm.py --name "SYÖMÄÄN" --category "restaurant" --country "FI"
```

Produces following output:

```xml
<osm version="0.6" generator="duckdb-overture2osm">
    <changeset id="1" created_at="2025-08-19T13:04:36.268982">
        <tag k="created_by" v="duckdb-overture2osm" />
        <tag k="comment" v="Add place SYÖMÄÄN from Overture Maps" />
    </changeset>
    <node id="-1" lat="61.2683742" lon="24.0251439" visible="true">
        <tag k="name" v="SYÖMÄÄN" />
        <tag k="amenity" v="restaurant" />
        <tag k="website" v="http://www.syomaan.net/" />
        <tag k="contact:facebook" v="https://www.facebook.com/101807046049128" />
        <tag k="addr:full" v="Valtakatu 27-29" />
        <tag k="addr:city" v="Valkeakoski" />
        <tag k="addr:postcode" v="37600" />
        <tag k="addr:country" v="FI" />
    </node>
</osm>
```

I would then want to upload this changeset to OSM and then on next changeset to add the missing details.

It's not possible to tag information like wheelchair entrances or toilets directly to OvertureMaps so this should be win win for both ecosystems.

## License

MIT
