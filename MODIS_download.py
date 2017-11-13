import urllib2
import datetime
import os
import glob
import shutil
import arcpy


class MODISDownload(object):
    def __init__(self, product="MOD13Q1", version="006", tile_list=None,
                 data_dir="", modis_grid_wgs84=None, study_area_wgs84=None,
                 start_date="2016-01-01", end_date="2016-12-31", wget_cmd=".\wget\wget64.exe"):

        self.name = "MODIS Download"
        self.product = product
        self.version = version.zfill(3) if type(version) == str else(
            str(version).zfill(3) if type(version) == int else "006")

        self.tile_list = [] if tile_list is None else tile_list
        self.modis_grid_wgs84 = modis_grid_wgs84
        self.study_area_wgs84 = study_area_wgs84
        self.start_date = start_date
        self.end_date = end_date

        self.wget_cmd = wget_cmd
        self.earth_data_url = "https://urs.earthdata.nasa.gov"

        # set directory name for sensor, MOTA for combined data products
        self.category_dir = "MOLT" if self.product[:3] == "MOD" else ("MOLA" if self.product[:3] == "MYD" else "MOTA")

        self.product_url = "https://e4ftl01.cr.usgs.gov/{category_dir}/{product}.{version}/".format(
            category_dir=self.category_dir, product=self.product, version=self.version)
        self.data_dir = data_dir
        self.temp_dir = os.path.join(self.data_dir, "Temp")

    def execute(self):
        if not self._is_valid_download():
            return

        if (len(self.tile_list) == 0) and (self.modis_grid_wgs84 is not None and self.study_area_wgs84 is not None):
            tlist = self._get_tile_list()
            self.tile_list = tlist
        elif (len(self.tile_list) == 0) and self.modis_grid_wgs84 is None:
            print "MODIS grid is missing"
            return
        elif (len(self.tile_list) == 0) and self.study_area_wgs84 is None:
            print "Study area is missing"
            return

        print self.tile_list

        self._download()

    def _is_valid_download(self):
        try:
            request = urllib2.Request(self.product_url)
            response = urllib2.urlopen(request)

            # read date directory page
            html = response.read()

            if len(html) > 500:
                return True
            else:
                print "No valid product found"
                return False
        except:
            print "Cannot connect to the datapool or product not found"

    def _set_temp_directory(self):
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

            os.mkdir(self.temp_dir)
        except:
            print "Could not create Temp directory"

    def _get_tile_list(self):

        self._set_temp_directory()

        # WGS 1984 check
        if not self._is_CGS_WGS_1984(self.modis_grid_wgs84):
            print "MODIS grid is not in GCS_WGS_1984"
            exit(0)

        if not self._is_CGS_WGS_1984(self.study_area_wgs84):
            print "MODIS study area is not in GCS_WGS_1984"
            exit(0)

        # check h and v fields
        fields = [f.name.encode("utf-8") for f in arcpy.ListFields(self.modis_grid_wgs84)]
        if not ("h" in fields and "v" in fields):
            print "H and V tile index fields are not found in the MODIS grid"
            exit(0)

        clip_output = os.path.join(self.temp_dir, "selected_tiles.shp")
        arcpy.Clip_analysis(self.modis_grid_wgs84, self.study_area_wgs84, clip_output)

        cursor = arcpy.da.SearchCursor(clip_output, ['h', 'v'])
        tiles = []
        for row in cursor:
            tiles.append("h{h}v{v}".format(h=str(int(row[0])).zfill(2), v=str(int(row[1])).zfill(2)))
        del cursor

        try:
            arcpy.Delete_management(clip_output)
            os.rmdir(self.temp_dir)
        except:
            print "Cannot delete the temporary directory"

        if tiles:
            tiles.sort()
            return tiles
        else:
            print "No MODIS grid tiles found"
            exit(0)

    def _is_CGS_WGS_1984(self, shape_file_path):
        spatial_ref = arcpy.Describe(shape_file_path).spatialReference
        if spatial_ref.name.encode("utf-8") == 'GCS_WGS_1984':
            return True
        else:
            return False

    def _download(self):

        request = urllib2.Request(self.product_url)
        response = urllib2.urlopen(request)

        # read date directory
        html = response.read()
        dirs = [line.split('href="')[1].split('/">')[0] for line in html.split('\n') if line.find('[DIR]') != -1][1:]
        selected_dirs = []
        for temp_dir in dirs:
            dir_date = temp_dir.split(".")
            temp_date = datetime.date(int(dir_date[0]), int(dir_date[1]), int(dir_date[2]))

            if self.start_date <= temp_date <= self.end_date:
                selected_dirs.append(temp_dir)

        print "Selected dirs ..."
        print selected_dirs

        for date_dir in selected_dirs:
            temp_url = self.product_url + date_dir + "/"
            print temp_url
            self._download_all(temp_url)

        for tile in self.tile_list:
            tile_dir = os.path.join(self.data_dir, tile)
            os.mkdir(tile_dir)

            tile_files = glob.glob(os.path.join(self.data_dir, "*." + tile + ".*"))
            self._move_files(tile_files, tile_dir)

    def _download_all(self, temp_url):
        str_tiles = "|".join(self.tile_list)
        wget_cmd = "{wget_cmd} --quiet -L -r -np -nH --cut-dirs=3 --load-cookies ./.cookies --save-cookies ./.cookies --accept-regex=\"({tiles})(\.)[a-zA-Z0-9.]*\.(xml|hdf)\" --reject=\"*.html,*.tmp\" --directory-prefix={destination} --no-hsts {url}".format(
            wget_cmd=self.wget_cmd, tiles=str_tiles, destination=self.data_dir, url=temp_url)
        print wget_cmd
        os.system(wget_cmd)

    def _move_files(self, file_list, destination_dir):
        for f in file_list:
            shutil.move(f, destination_dir)
