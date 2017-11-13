# ArcMODIS-Downloader
Download any MODIS data product for any given spatial and temporal extent

## Summary
ArcMODIS-Downloader was developed with three primary goals.

* Making a simple data download tool that works for all MODIS products
* Data download tool that supports bulk data download (across multiple MODIS grid cells)
* Data download tool that accepts spatial and temporal data download criteria

This tool has been tested only for ArcGIS/Windows environments. But it can be simply changed to work with Non-ArcGIS/Unix like environments.

## Running ArcMODIS-Downloader Tool

## Prerequisites
* arcpy - ArcGIS Pyhton package (Python 2.7)
* wget - you need the right wget version for your envionrmnet, a 64-bit wget implementation for windows is included here
* NASA earth data account - you need to enter your user name and password in the wget/.wgetrc file. If you needs more security, think about password encryption etc.

First, determine the spatial extent of your study area. You can provide it as a list of MODIS grid tiles (cells) or makea polygon shapefile representing the study area. Polygon shapefile should be in WGS 1984. Put it inside the data directory.

Then, determine the date range for your downloading dataset. Start and end dates should be provided as Python `datetime.date`.

ex: Selected MODIS grid cells for CONUS

```Python
    arr_tiles = ["h08v06",
                 "h09v06",
                 "h10v06",
                 "h08v05",
                 "h09v05",
                 "h10v05",
                 "h11v05",
                 "h12v05",
                 "h08v04",
                 "h09v04",
                 "h10v04",
                 "h11v04",
                 "h12v04",
                 "h13v04"]
```

Use `MODIS_download_manager.py` file for configuring and running your download job. 

If you use a MODIS tile list:

```Python
 md = MODISDownload(
        product="MYD17A3H",
        version="006",
        tile_list=arr_tiles,
        data_dir=r"\\Test\NPP\Aqua\rawdata",
        modis_grid_wgs84=None,
        study_area_wgs84=None,
        start_date=datetime.date(2013, 1, 1),
        end_date=datetime.date(2016, 12, 31),
        wget_cmd=r".\wget\wget64.exe")

    md.execute()
```

If you use a shapefile for specifying the study area:

```Python
 md = MODISDownload(
        product="MYD17A3H",
        version="006",
        tile_list=None,
        data_dir=r"\\Test\NPP\Aqua\rawdata",
        modis_grid_wgs84=r".\data\modis_grid_wgs84.shp",
        study_area_wgs84=r".\data\CONUS_border_wgs84.shp",
        start_date=datetime.date(2013, 1, 1),
        end_date=datetime.date(2016, 12, 31),
        wget_cmd=r".\wget\wget64.exe")

  md.execute()
```

## Support for Non-ArcGIS/Unix like envionrmnets

You can use GDAL/OGR with Shapely to do the necessary changes. Think about alternative ways for reading attribute tables, clipping, and reading spatial reference information of shapefiles.
