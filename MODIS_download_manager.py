from MODIS_download import MODISDownload
import datetime


def main():
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


if __name__ == '__main__':
    main()
