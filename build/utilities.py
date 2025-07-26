#!/usr/bin/env python
# coding: utf-8


import os
import re
from datetime import datetime
import numpy as np
import pandas as pd
import platform
from shapely.ops import nearest_points


def walk_through_files(path, file_extension, fullpath=False, returnboth=False):
    # https://stackoverflow.com/questions/2922783/how-do-you-walk-through-the-directories-using-python
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith(file_extension): 
                if fullpath:
                    yield os.path.join(dirpath, filename)
                elif returnboth:
                	yield (dirpath, filename)
                else:
                    yield filename


def get_datestring(filename):
    """ Takes a filename (e.g. 'lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz')
        and retrives the date (2020 01 10 in year month day). Then parse the date string into a 
        datetime object.
        
        filename (str): e.g. 'lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz'

        Returns
        -------
        str (e.g. '2020_01_10')
    """   
    date_reg_exp = re.compile('(\d+[_]\d+[_]\d+)')
    
    date_str = date_reg_exp.findall(filename)[0]

    return date_str


def get_date(filename):
    """ Takes a filename (e.g. 'lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz')
        and retrives the date (2020 01 10 in year month day). Then parse the date string into a 
        datetime object.
        
        filename (str): e.g. 'lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz'
        
        Dependencies
        ------------
        get_datestring(filename)

        Returns
        -------
        date obj (e.g. datetime.date(2020, 1, 10))
    """   
    
    date_str = get_datestring(filename)
    
    date_obj = datetime.strptime(date_str, "%Y_%m_%d").date()
    
    return date_obj


def get_subzone_name_from_dir(dirname):
    """ Takes a dirname (e.g. '../raw-files/sg subzones devices/2020-01-10/lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz')
        and retrives the subzone name (choa chu kang north).
        
        dirname (str): e.g. '../raw-files/sg subzones devices/2020-01-10/lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz'

        Returns
        -------
        str (e.g. choa chu kang north)
    """
    
    if platform.system()=='Windows':
        subzone = get_subzone_name(dirname).split('\\')[-1].strip()
    else:
        subzone = get_subzone_name(dirname).split('/')[-1].strip()
    
    return subzone


def get_subzone_name(filename):
    """ Takes a filename (e.g. 'lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz')
        and retrives the subzone name (choa chu kang north).
        
        filename (str): e.g. 'lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz'

        Returns
        -------
        str (e.g. choa chu kang north)
    """
    # remove date
    date_str = get_datestring(filename)
    _subzone = filename.replace(date_str, '')
        
    # remove predictable naming patterns
    _subzone = _subzone.replace('lotadata', '')
    _subzone = _subzone.replace('subzone_sg', '')
    _subzone = _subzone.replace('deviceList.csv.gz', '')
    
    # strip off remaining _ and whitespaces
    subzone = _subzone.replace('_', ' ').strip()
    
    return subzone



def save_df_in_chunks(pd_df, savepath, n_chunks, prefix, fileformat, compression=None):
	""" Save pandas DataFrame in chunks. 

		Parameters:
		-----------
		pd_df (pandas DataFrame)

		savepath (str): directory to save to

		n_chunks (int): number of chunks to split df
		
		prefix (str): e.g. if prefix='mydf', save as mydf1.*, mydf2.*, ..., mydfn.*

		fileformat (str): e.g. csv or csv.gz

		compression (str): e.g. 'gzip'. See pandas read_csv docs.

		Returns
		-------
		None

		Example: save_df_in_chunks(df, 'temp-folder', 3, 'df', 'csv') saves to:
			temp-folder/mydf1.csv
			temp-folder/mydf2.csv
			temp-folder/mydf3.csv
	"""
	for ix, df_chunk in enumerate(np.array_split(pd_df,n_chunks)): 
		df_chunk.to_csv(os.path.join(savepath, f'{prefix}{ix+1}.{fileformat}'), index=False, compression=compression)


def mem_usage(pandas_obj, human_read=True):
    """ Returns memory usage of pandas object (DataFrame or Series). If human_read=True, then return
        a string for both memory and deep memory usage---e.g. 17 (75) MB, where value in parenthesis 
        is deep memory usage. If human_read=False, then returns the float value of memory usage.
        
        Parameters
        ----------
        pandas_obj (DataFrame, Series)
        
        human_read (bool)
        
    
        Returns
        -------
        String (human_read=True) or float (human_read=False)
    """
    if isinstance(pandas_obj,pd.DataFrame):
        usage_b = pandas_obj.memory_usage().sum()
        usage_b_deep = pandas_obj.memory_usage(deep=True).sum()
    else: # we assume if not a df it's a series
        usage_b = pandas_obj.memory_usage()
        usage_b_deep = pandas_obj.memory_usage(deep=True)
        
    usage_mb = usage_b / (1024 ** 2) # convert bytes to megabytes
    usage_mb_deep = usage_b_deep / (1024 ** 2) 
    
    if human_read:
        return f"{usage_mb:.1f} ({usage_mb_deep:.1f}) MB"
    else:
        return usage_mb, usage_mb_deep


def get_geo_nn(row, multipoints, gdf_from, gdf_to, uid='id'):
    """
    Get geographical nearest neightbour using distance between centroids.
    For each polygon in gpd_from (e.g. census tract), find nearest point from list of places in
    gpd_to (eg stations). Assumes all geomtry columns are named "geometry" and centroid column 
    is named "centroid".
    (From https://automating-gis-processes.github.io/2017/lessons/L3/nearest-neighbour.html)
    
    To use:
        Example in https://github.com/LSYS/who-goes-where/blob/master/build/map-weather.ipynb
        Step 1. multipoints = gdf_to.unary_union
        Step 2. gdf_from['nearestneighbour'] = gdf_from.apply(get_geo_nn, multipoints=multipoints, gdf_from=gdf_from, gdf_to=gdf_to)

    Inputs:
    -------
    multipoints (shapely.geometry.MultiPoint): "list" of points to match to (from gdf_to)
    
    uid (str): unique id of place in gdf_to
    
    gdf_from (geopandas df): contains polygons/lines/points to match from. Should have a column that
        is the centroid, named "centroid".
        
    gdf_to (geopandas df): contains and "id" column and a Point column to match to.
    
    Dependencies:
    -------------
    shapely.ops.nearest_points (Note: index=1 returns the nearest neighbour, index=0 is the comparison point itself)
    
    Returns:
    --------
    Pandas series
    """    
    # Get a pd series of True/False, True if row in gdf_to is geographically closest to given pt. in gdf_from
    nearest = (gdf_to['geometry'] == nearest_points(row['centroid'], multipoints)[1])
    
    # Retrieve relevant row from gdf_to
    nearest = gdf_to[nearest].reset_index()
    
    # Return relevant id from id column
    return nearest.loc[0, uid]        


def make_folder(dirpath):    
    try:
        os.makedirs(dirpath)
    except FileExistsError:
        print(f'{dirpath} already exists.')


def get_diff_stringval_from_2columns(df_from, from_col, df_to, to_col):
    """ 
    Compare a column from df_from and a column from df_to, and check to see if the unique list of strings
    are the same. If not, return differences as a dictionary of lists.
    
    Inputs:
    -------
    df_from (pd obj)  
    from_col (name of column in df_from for comparison)
    
    df_to (pd obj)  
    to_col (name of column in df_to for comparison)
    
    Returns:
    --------
    Dictionary with list of values only in df_to, and list of values only in df_from
    """
    
    from_col = df_from.sort_values(from_col)[from_col].unique().tolist()
    to_col = df_to.sort_values(to_col)[to_col].unique().tolist()
    
    if from_col==to_col:
        return None
    else:
        dic = {}
        from_col, to_col = set(from_col), set(to_col)
    
        dic['only in df_from'] = list(from_col - to_col)
        dic['only in df_to'] = list(to_col - from_col )
        
        return dic        


def auto_reduce_mem(pandas_df, log=True, errors='coerce', downcast_int='integer', downcast_float='float', downcast_cat=True):
    """
        Auto detect column types in a pandas DataFrame, downcast them, and report reduction in 
        memory usage.
        
        Parameters:
        -----------
        pandas_df (pandas DataFrame)
        
        errors (str): {‘ignore’, ‘raise’, ‘coerce’}, default ‘coerce’
            * If ‘raise’, then invalid parsing will raise an exception.
            * If ‘coerce’, then invalid parsing will be set as NaN.
            * If ‘ignore’, then invalid parsing will return the input.
            
        downcast_int (str): {'integer', 'signed', 'unsigned', None}, default 'integer'
            * ‘integer’ or ‘signed’: smallest signed int dtype (min.: np.int8)
            * ‘unsigned’: smallest unsigned int dtype (min.: np.uint8)
            * None: don't attempt downcast
            Note: errors during downcasting will still surface even if errors is set to 'ignore' or 'coerce'
            
        downcast_float (str): {'float', None}
            * ‘float’: smallest float dtype (min.: np.float32)
            * None: don't attempt downcast
            Note: errors during downcasting will still surface even if errors is set to 'ignore' or 'coerce'
            
        downcast_cateogorical (bool). If False, do not convert object column to categorical.
        log (bool): print log
        
        Warning:
        --------
        Please note that precision loss may occur if really large numbers are passed in. Due to the internal 
        limitations of ndarray, if numbers smaller than -9223372036854775808 (np.iinfo(np.int64).min) 
        or larger than 18446744073709551615 (np.iinfo(np.uint64).max) are passed in, it is very likely 
        they will be converted to float so that they can stored in an ndarray. These warnings apply similarly 
        to Series since it internally leverages ndarray. [See https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_numeric.html]
        
        Dependencies:
        -------------
        mem_usage(pandas_df)
        
        pandas (to_numeric, )
    """
    start_mem = mem_usage(pandas_df, human_read=False)
    if log:
        print(f'Memory usage of DataFrame is {mem_usage(pandas_df)}.')
    else: pass        
    
    for col in pandas_df.columns:
        col_type = pandas_df[col].dtype

        if log:
            # Print current column type
            print("******************************")
            print(f"Column: {col}")
            print(f"dtype before: {col_type}")
        else: pass
        
        # Handle integer types
        if 'int' in col_type.name:
            pandas_df[col] = pd.to_numeric(pandas_df[col], errors=errors, downcast=downcast_int)
            
            if log:
                # Print new column type
                print(f'dtype after: {pandas_df[col].dtype}')
                print("******************************\n")
            else: pass
            
        # Handle float types
        if 'float' in col_type.name:
            pandas_df[col] = pd.to_numeric(pandas_df[col], errors=errors, downcast=downcast_float)
            
            if log:
                # Print new column type
                print(f'dtype after: {pandas_df[col].dtype}')
                print("******************************\n")      
            else: pass
            
        # Handle categoricals/strings
        if col_type.name == 'object':
            if downcast_cat:
                pandas_df[col] = pandas_df[col].astype('category')
            
            if log:    
                # Print new column type
                print(f'dtype after: {pandas_df[col].dtype}')
                print("******************************\n")          
            else: pass
            
    if log:
        # Print final result
        print("___MEMORY USAGE AFTER COMPLETION:___")
        end_mem = mem_usage(pandas_df, human_read=False) 
        print(f'Memory usage of DataFrame is {mem_usage(pandas_df)}.')
        change_ratio = 100*end_mem[0]/start_mem[0]
        change_ratio_deep = 100*end_mem[1]/start_mem[1]
        print(f'This is {change_ratio:.2f}% ({change_ratio_deep:.2f}%) of initial size.')
    else: pass        


def get_html_table_metadata(
    dataframe: pd.DataFrame, table_col: str = "Description"
) -> pd.DataFrame:
    r"""Parse metadata stored in a column of HTML into columns.

    Used to handle the official KML/SHP files with missing labels. Labels are encoded
    in the "Description" column which is formatted as HTML.

    For example, for a dataframe with a 'Description' column of HTML,
    where a row could have an entry like
    <center><table><tr><th colspan=\'2\' align=\'center\'><em>Attributes</em></th></tr><tr bgcolor="#E3E3F3"> <th>LU_DESC</th> <td>OPEN SPACE</td> </tr><tr bgcolor=""> <th>LU_TEXT</th> <td> </td> </tr><tr bgcolor="#E3E3F3"> <th>GPR</th> <td>EVA</td> </tr><tr bgcolor=""> <th>WHI_Q_MX</th> <td></td> </tr><tr bgcolor="#E3E3F3"> <th>GPR_B_MN</th> <td></td> </tr><tr bgcolor=""> <th>INC_CRC</th> <td>2481817E4931D054</td> </tr><tr bgcolor="#E3E3F3"> <th>FMEL_UPD_D</th> <td>20191209171707</td> </tr></table></center>

    Prettyprinted: (from https://jsonformatter.org/html-pretty-print)
    <center>
        <table>
            <tr>
                <th colspan=\'2\' align=\'center\'>
                    <em>Attributes</em>
                </th>
            </tr>
            <tr bgcolor="#E3E3F3">
                <th>LU_DESC</th>
                <td>OPEN SPACE</td>
            </tr>
            <tr bgcolor="">
                <th>LU_TEXT</th>
                <td></td>
            </tr>
            <tr bgcolor="#E3E3F3">
                <th>GPR</th>
                <td>EVA</td>
            </tr>
            <tr bgcolor="">
                <th>WHI_Q_MX</th>
                <td></td>
            </tr>
            <tr bgcolor="#E3E3F3">
                <th>GPR_B_MN</th>
                <td></td>
            </tr>
            <tr bgcolor="">
                <th>INC_CRC</th>
                <td>2481817E4931D054</td>
            </tr>
            <tr bgcolor="#E3E3F3">
                <th>FMEL_UPD_D</th>
                <td>20191209171707</td>
            </tr>
        </table>
    </center>

    This function turns each row in the table containing some metadata for 'LU_DESC'
    into a column with that header 'LU_DESC' and the corresponding value (e.g., OPEN SPACE)
    in the column.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The pandas dataframe.
    table_col : str
        Name of the column containing the HTML table metadata.

    Returns
    -------
    pd.DataFrame
        Dataframe with additional column from the HTML table data.
    """
    payload = []
    for ix, row in dataframe.iterrows():
        parsed_output = pd.read_html(row[table_col])

        # each entry has only 1 table
        assert len(parsed_output) == 1
        parsed_output = parsed_output[0]

        # Use 1st row to store headers
        if ix == 0:
            headers = parsed_output.iloc[:, 0].tolist()

        payload.append(parsed_output.iloc[:, 1].tolist())

    df_payload = pd.DataFrame(payload, columns=headers)
    df_payload = dataframe.merge(
        df_payload, how="left", left_index=True, right_index=True, validate="1:1"
    )
    return df_payload