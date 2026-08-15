#!/usr/bin/env python
# coding: utf-8


import os
import platform
import re
import statistics
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Polygon, Rectangle
from matplotlib.pyplot import Axes
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.ops import nearest_points
from sklearn.metrics.pairwise import haversine_distances


def walk_through_files(path, file_extension, fullpath=False, returnboth=False):
    # https://stackoverflow.com/questions/2922783/how-do-you-walk-through-the-directories-using-python
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(file_extension):
                if fullpath:
                    yield os.path.join(dirpath, filename)
                elif returnboth:
                    yield (dirpath, filename)
                else:
                    yield filename


def get_datestring(filename):
    """Takes a filename (e.g. 'lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz')
    and retrives the date (2020 01 10 in year month day). Then parse the date string into a
    datetime object.

    filename (str): e.g. 'lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz'

    Returns
    -------
    str (e.g. '2020_01_10')
    """
    date_reg_exp = re.compile("(\d+[_]\d+[_]\d+)")

    date_str = date_reg_exp.findall(filename)[0]

    return date_str


def get_date(filename):
    """Takes a filename (e.g. 'lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz')
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
    """Takes a dirname (e.g. '../raw-files/sg subzones devices/2020-01-10/lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz')
    and retrives the subzone name (choa chu kang north).

    dirname (str): e.g. '../raw-files/sg subzones devices/2020-01-10/lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz'

    Returns
    -------
    str (e.g. choa chu kang north)
    """

    if platform.system() == "Windows":
        subzone = get_subzone_name(dirname).split("\\")[-1].strip()
    else:
        subzone = get_subzone_name(dirname).split("/")[-1].strip()

    return subzone


def get_subzone_name(filename):
    """Takes a filename (e.g. 'lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz')
    and retrives the subzone name (choa chu kang north).

    filename (str): e.g. 'lotadata_choa_chu_kang_north_subzone_sg_2020_01_10_deviceList.csv.gz'

    Returns
    -------
    str (e.g. choa chu kang north)
    """
    # remove date
    date_str = get_datestring(filename)
    _subzone = filename.replace(date_str, "")

    # remove predictable naming patterns
    _subzone = _subzone.replace("lotadata", "")
    _subzone = _subzone.replace("subzone_sg", "")
    _subzone = _subzone.replace("deviceList.csv.gz", "")

    # strip off remaining _ and whitespaces
    subzone = _subzone.replace("_", " ").strip()

    return subzone


def save_df_in_chunks(pd_df, savepath, n_chunks, prefix, fileformat, compression=None):
    """Save pandas DataFrame in chunks.

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
    for ix, df_chunk in enumerate(np.array_split(pd_df, n_chunks)):
        df_chunk.to_csv(  # type: ignore[attr-defined]
            os.path.join(savepath, f"{prefix}{ix+1}.{fileformat}"),
            index=False,
            compression=compression,
        )


def mem_usage(pandas_obj, human_read=True):
    """Returns memory usage of pandas object (DataFrame or Series). If human_read=True, then return
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
    if isinstance(pandas_obj, pd.DataFrame):
        usage_b = pandas_obj.memory_usage().sum()
        usage_b_deep = pandas_obj.memory_usage(deep=True).sum()
    else:  # we assume if not a df it's a series
        usage_b = pandas_obj.memory_usage()
        usage_b_deep = pandas_obj.memory_usage(deep=True)

    usage_mb = usage_b / (1024**2)  # convert bytes to megabytes
    usage_mb_deep = usage_b_deep / (1024**2)

    if human_read:
        return f"{usage_mb:.1f} ({usage_mb_deep:.1f}) MB"
    else:
        return usage_mb, usage_mb_deep


def get_geo_nn(row, multipoints, gdf_from, gdf_to, uid="id"):
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
    nearest = gdf_to["geometry"] == nearest_points(row["centroid"], multipoints)[1]

    # Retrieve relevant row from gdf_to
    nearest = gdf_to[nearest].reset_index()

    # Return relevant id from id column
    return nearest.loc[0, uid]


def make_folder(dirpath):
    try:
        os.makedirs(dirpath)
    except FileExistsError:
        print(f"{dirpath} already exists.")


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

    if from_col == to_col:
        return None
    else:
        dic = {}
        from_col, to_col = set(from_col), set(to_col)

        dic["only in df_from"] = list(from_col - to_col)
        dic["only in df_to"] = list(to_col - from_col)

        return dic


def auto_reduce_mem(
    pandas_df,
    log=True,
    errors="coerce",
    downcast_int="integer",
    downcast_float="float",
    downcast_cat=True,
):
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
        print(f"Memory usage of DataFrame is {mem_usage(pandas_df)}.")
    else:
        pass

    for col in pandas_df.columns:
        col_type = pandas_df[col].dtype

        if log:
            # Print current column type
            print("******************************")
            print(f"Column: {col}")
            print(f"dtype before: {col_type}")
        else:
            pass

        # Handle integer types
        if "int" in col_type.name:
            pandas_df[col] = pd.to_numeric(
                pandas_df[col], errors=errors, downcast=downcast_int
            )

            if log:
                # Print new column type
                print(f"dtype after: {pandas_df[col].dtype}")
                print("******************************\n")
            else:
                pass

        # Handle float types
        if "float" in col_type.name:
            pandas_df[col] = pd.to_numeric(
                pandas_df[col], errors=errors, downcast=downcast_float
            )

            if log:
                # Print new column type
                print(f"dtype after: {pandas_df[col].dtype}")
                print("******************************\n")
            else:
                pass

        # Handle categoricals/strings
        if col_type.name == "object":
            if downcast_cat:
                pandas_df[col] = pandas_df[col].astype("category")

            if log:
                # Print new column type
                print(f"dtype after: {pandas_df[col].dtype}")
                print("******************************\n")
            else:
                pass

    if log:
        # Print final result
        print("___MEMORY USAGE AFTER COMPLETION:___")
        end_mem = mem_usage(pandas_df, human_read=False)
        print(f"Memory usage of DataFrame is {mem_usage(pandas_df)}.")
        change_ratio = 100 * end_mem[0] / start_mem[0]
        change_ratio_deep = 100 * end_mem[1] / start_mem[1]
        print(
            f"This is {change_ratio:.2f}% ({change_ratio_deep:.2f}%) of initial size."
        )
    else:
        pass


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


def save_mpl_fig(
    savepath: str, formats: Optional[Iterable[str]] = None, dpi: Optional[int] = None
) -> None:
    """Save matplotlib figures to ../output.

    Will handle saving in png and in pdf automatically using the same file stem.

    Parameters
    ----------
    savepath: str
        Name of file to save to. No extensions.
    formats: Array-like
        List containing formats to save in. (By default 'png' and 'pdf' are saved).
        Do a:
            plt.gcf().canvas.get_supported_filetypes()
        or:
            plt.gcf().canvas.get_supported_filetypes_grouped()
        To see the Matplotlib-supported file formats to save in.
        (Source: https://stackoverflow.com/a/15007393)
    dpi: int
        DPI for saving in png.

    Returns
    -------
    None
    """
    # Save pdf
    plt.savefig(f"{savepath}.pdf", dpi=None, bbox_inches="tight", pad_inches=0)

    # save png
    plt.savefig(f"{savepath}.png", dpi=dpi, bbox_inches="tight", pad_inches=0)

    # Save additional file formats, if specified
    if formats:
        for format in formats:
            plt.savefig(
                f"{savepath}.{format}",
                dpi=None,
                bbox_inches="tight",
                pad_inches=0,
            )
    return None


def add_scalebar(
    ax: Axes,
    location: str = "lower right",
    fontsize: int = 20,
    length_fraction: float = 0.25,
    height_fraction: float = 0.01,
) -> None:
    """Add scalebar to a matplotlib map.

    Parameters
    ----------
    ax: Axes
        Matplotlib Axes.
    location: str
        Where to place scalebar (e.g., lower left, upper right, etc.)
    fontsize: int
        Font size for the scale indicator text (e.g., "5km").
    length_fraction: float
        Fraction of the axes' width or height that the scale bar occupies.
    height_fraction: float
        Fraction of the axes' height that the scale bar's thickness occupies.

    Returns
    -------
    None
    """
    # Latitude of interest here 40.7 deg, longitude -74.5
    A = [-74.5 * np.pi / 180.0, 40.7 * np.pi / 180.0]
    # Latitude of interest here 40.7 deg, longitude -74.5+1
    B = [-73.5 * np.pi / 180.0, 40.7 * np.pi / 180.0]

    dx = (6371000) * haversine_distances([A, B])[0, 1]
    ax.add_artist(
        ScaleBar(
            dx=dx,
            units="m",
            location=location,
            box_alpha=0,
            font_properties={"size": fontsize},
            length_fraction=length_fraction,
            height_fraction=height_fraction,
        )
    )
    return None


def add_north_arrow(
    ax: Axes, x: float = 103.97, y: float = 1.46, fontsize: int = 20
) -> None:
    """Add a north arrow to a matplotlib map.

    Parameters
    ----------
    ax: Axes
        Matplotlib Axes.
    x: float
        X-axis coordinate.
    y: float
        Y-axis coordinate.
    fontsize: int
        Size of the text "N".

    Returns
    -------
    None
    """
    # Add north arrow
    ax.text(x=x, y=0.0009 + y, s="N", ha="center", va="bottom", fontsize=fontsize)
    ax.arrow(
        x,
        y,
        0.0,
        0.001,
        length_includes_head=True,
        head_width=0.008,
        head_length=0.02,
        overhang=0.2,
        facecolor="0.3",
        alpha=0.9,
    )
    return None


def add_north_arrow_2tone(
    ax: Axes,
    x_frac: float = 0.055,
    top_frac: float = 0.94,
    height_frac: float = 0.12,
    width_frac: float = 0.034,
    color: str = "0.15",
    fontsize: int = 10,
) -> None:
    """Add a two-tone cartographic north arrow to a north-up map.

    Draws a kite-shaped marker with a dark west half and a light east half, and
    an "N" above the tip. Position and size are given as fractions of the axes,
    so it renders correctly in any CRS (projected or geographic) and at any
    zoom, unlike ``add_north_arrow``, whose offsets are in lat/long degrees.

    Parameters
    ----------
    ax : Axes
        Matplotlib Axes, assumed north-up.
    x_frac : float, default 0.055
        Horizontal centre of the arrow, as a fraction of axes width from the left.
    top_frac : float, default 0.94
        Vertical position of the tip, as a fraction of axes height from the bottom.
    height_frac : float, default 0.12
        Arrow height as a fraction of axes height.
    width_frac : float, default 0.034
        Arrow width as a fraction of axes width.
    color : str, default "0.15"
        Colour of the dark (west) half, the outline, and the "N".
    fontsize : int, default 10
        Font size of the "N".

    Returns
    -------
    None
    """
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    width = x_max - x_min
    height = y_max - y_min
    cx = x_min + width * x_frac
    tip = y_min + height * top_frac
    tail = tip - height * height_frac
    barb = tail + (tip - tail) * 0.34
    half_width = width * width_frac / 2
    ax.add_patch(
        Polygon(
            [(cx, tip), (cx - half_width, barb), (cx, tail)],
            facecolor=color,
            edgecolor=color,
            linewidth=0.6,
            zorder=6,
        )
    )
    ax.add_patch(
        Polygon(
            [(cx, tip), (cx + half_width, barb), (cx, tail)],
            facecolor="white",
            edgecolor=color,
            linewidth=0.6,
            zorder=6,
        )
    )
    ax.text(
        cx,
        tip + height * 0.01,
        "N",
        ha="center",
        va="bottom",
        fontsize=fontsize,
        fontweight="bold",
        color=color,
        zorder=6,
    )
    return None


ryb_hex_colors = [
    # Reds
    "#830022",
    "#a34035",
    "#c26d4c",
    "#db9d6b",
    "#eecd94",
    # Yellows
    "#fffedf",
    # Blues
    "#cddcb3",
    "#9bbaa8",
    "#6f9799",
    "#4b7587",
    "#255474",
]

custom_cmap = LinearSegmentedColormap.from_list(
    "custom_ryb", ryb_hex_colors[::-1], N=256
)


def cat_to_num(
    array: List[str],
    rm_patterns: Optional[List[str]] = None,
    **kwargs: Union[int, float],
) -> Dict[str, Union[int, float]]:
    """
    Convert categorical string data to numerical values by extracting and processing digits.

    This function processes a list of strings by removing specified patterns, extracting
    numerical digits, and converting them to numerical values. If multiple digits are found
    in a string, their mean is calculated. The function returns a mapping from original
    strings to their corresponding numerical values.

    Parameters
    ----------
    array : List[str]
        List of strings containing categorical data to be converted to numerical values.
        Each string may contain digits along with other characters.
    rm_patterns : List[str], optional
        List of patterns/characters to remove from each string before processing.
        If None, defaults to ['$', ','] to handle common currency and number formatting.
    **kwargs : Union[int, float]
        Optional keyword arguments to override specific entries in the output dictionary.
        Keys should match strings from the input array, values should be numbers.

    Returns
    -------
    Dict[str, Union[int, float]]
        Dictionary mapping original strings to their numerical equivalents.
        Values are integers if only one digit is found, or floats if multiple digits
        are averaged.

    Raises
    ------
    IndexError
        If a string contains no digits after pattern removal and processing.
    ValueError
        If digit extraction or conversion fails.

    Examples
    --------
    >>> data = ["$10-20", "30,000", "5"]
    >>> cat_to_num(data)
    {'$10-20': 15.0, '30,000': 30000, '5': 5}

    >>> cat_to_num(["$100", "$200"], custom_override=150)
    {'$100': 100, '$200': 200, 'custom_override': 150}

    >>> cat_to_num(["low: 1-3", "high: 8-10"], rm_patterns=[':'])
    {'low: 1-3': 2.0, 'high: 8-10': 9.0}
    """
    DEFAULT_RM_PATTERNS = ["$", ","]

    if rm_patterns is None:
        rm_patterns = DEFAULT_RM_PATTERNS.copy()

    original_array = array
    processed_array = array.copy()

    # Remove specified patterns from strings
    for pattern in rm_patterns:
        processed_array = [s.replace(pattern, "").strip() for s in processed_array]

    # Extract numerical values
    values = []
    for cat in processed_array:
        digits = [int(token) for token in cat.split() if token.isdigit()]
        if len(digits) > 1:
            values.append(statistics.mean(digits))
        elif len(digits) == 1:
            values.append(digits[0])
        else:
            raise ValueError(
                f"No digits found in processed string: '{cat}' (original: '{original_array[processed_array.index(cat)]}')"
            )

    # Create output dictionary
    output = dict(zip(original_array, values))

    # Apply optional overrides from kwargs
    for key, val in kwargs.items():
        output[key] = val

    return output


def add_segmented_scalebar(
    ax: Axes,
    segments: List[float] = [2.5, 2.5, 5, 5, 5],
    unit_type: str = "km",
    location: str = "lower right",
    length_fraction: float = 0.25,
    height_fraction: float = 0.015,
    alternating_colors: bool = True,
    bar_color: str = "black",
    alt_color: str = "white",
    label_offset: float = 0.02,
    fontsize: int = 12,
    unit_fontsize: Optional[int] = None,
    unit_position: str = "bottom",
    unit_label_spacing: float = 0.02,
    map_crs: str = "geographic",
    unit_label: Optional[str] = None,
) -> None:
    """
    Add a segmented scalebar to a matplotlib map with custom segment sizes.

    Creates a traditional cartographic scalebar with alternating colored segments
    stacked in two rows (checkerboard pattern). Each segment can have different
    lengths, allowing for scales like 0-2.5-5-10-15-20.

    Parameters
    ----------
    ax : Axes
        Matplotlib Axes object to add the scalebar to
    segments : List[float], default [2.5, 2.5, 5, 5, 5]
        Individual segment lengths in specified units
    unit_type : {'km', 'm'}, default 'km'
        Unit type for segments and labels
    location : str, default 'lower right'
        Scalebar placement: 'lower left', 'lower right', 'upper left', 'upper right'
    length_fraction : float, default 0.25
        Fraction of axes width the scalebar occupies (0.0-1.0)
    height_fraction : float, default 0.015
        Fraction of axes height for each scalebar row thickness
    alternating_colors : bool, default True
        Whether to create checkerboard pattern with alternating colors
    bar_color : str, default 'black'
        Primary color for segments
    alt_color : str, default 'white'
        Alternating color for segments
    label_offset : float, default 0.02
        Vertical spacing above scalebar for numeric labels (fraction of axes height)
    fontsize : int, default 12
        Font size for numeric labels
    unit_fontsize : int, optional
        Font size for unit label. Uses fontsize if None.
    unit_position : {'bottom', 'right'}, default 'bottom'
        Unit label position relative to scalebar
    unit_label_spacing : float, default 0.02
        Spacing between unit label and scalebar (fraction of axes dimension)
    map_crs : {'geographic', 'projected'}, default 'geographic'
        Coordinate system: 'geographic' for lat/lon, 'projected' for meters
    unit_label : str, optional
        Text for the unit label. If None (default), the full word from
        unit_type ("Kilometers"/"Meters"). Pass e.g. "km" for the short form.

    Returns
    -------
    None
    """
    # ==============================================
    # Validate inputs
    if unit_type not in ["km", "m"]:
        raise ValueError("unit_type must be 'km' or 'm'")
    if map_crs not in ["geographic", "projected"]:
        raise ValueError("map_crs must be 'geographic' or 'projected'")
    if unit_position not in ["bottom", "right"]:
        raise ValueError("unit_position must be 'bottom' or 'right'")

    # ==============================================
    # Configs: Handle defaults
    if unit_fontsize is None:
        unit_fontsize = fontsize

    # Set up units and convert to consistent internal format (km)
    unit_labels = {"km": "Kilometers", "m": "Meters"}
    if unit_label is None:
        unit_label = unit_labels[unit_type]

    if unit_type == "m":
        segments_km = [seg / 1000 for seg in segments]
    else:
        segments_km = segments.copy()

    # ==============================================
    # Scaling
    # Get axes coordinate ranges
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    total_width = xlim[1] - xlim[0]
    total_height = ylim[1] - ylim[0]

    # Calculate distance conversion factor for coordinate system
    conversion_factor = _calculate_conversion_factor(xlim, ylim, map_crs)

    # Calculate scalebar dimensions
    bar_height = total_height * height_fraction
    total_length_km = sum(segments_km)

    # Convert total length to data coordinate units
    if map_crs == "geographic":
        scale_width_data = (total_length_km * 1000) / conversion_factor
    else:
        scale_width_data = total_length_km * 1000

    # ==============================================
    # Calculate individual segment widths
    segment_widths = [(seg / total_length_km) * scale_width_data for seg in segments_km]

    # Determine scalebar position
    x_start, y_pos = _calculate_scalebar_position(
        xlim, ylim, location, scale_width_data, height_fraction, unit_position
    )

    # ==============================================
    # Draw segments and labels
    _draw_scalebar_segments(
        ax,
        x_start,
        y_pos,
        bar_height,
        segment_widths,
        segments_km,
        alternating_colors,
        bar_color,
        alt_color,
        fontsize,
        label_offset,
        total_height,
        unit_type,
    )

    # Add unit label
    _add_unit_label(
        ax,
        x_start,
        y_pos,
        scale_width_data,
        unit_label,
        unit_position,
        unit_label_spacing,
        total_width,
        total_height,
        unit_fontsize,
    )

    return None


def _calculate_conversion_factor(xlim, ylim, map_crs):
    """Calculate conversion factor between real-world distance and data coordinates."""
    if map_crs == "geographic":
        from sklearn.metrics.pairwise import haversine_distances

        # Calculate meters per degree longitude at map center
        center_lon = (xlim[0] + xlim[1]) / 2
        center_lat = (ylim[0] + ylim[1]) / 2

        point_a = [np.radians(center_lon), np.radians(center_lat)]
        point_b = [np.radians(center_lon + 1), np.radians(center_lat)]

        return 6371000 * haversine_distances([point_a, point_b])[0, 1]
    else:
        return 1.0  # Assume projected coordinates are in meters


def _calculate_scalebar_position(
    xlim, ylim, location, scale_width, height_fraction, unit_position
):
    """Calculate x,y position for scalebar based on location parameter."""
    total_width = xlim[1] - xlim[0]
    total_height = ylim[1] - ylim[0]
    margin = 0.05

    # Vertical position
    if "lower" in location:
        y_pos = ylim[0] + total_height * margin
    else:  # upper
        y_pos = ylim[1] - total_height * (margin + 2 * height_fraction + 0.05)

    # Horizontal position
    if "left" in location:
        x_start = xlim[0] + total_width * margin
    else:  # right
        extra_space = total_width * 0.08 if unit_position == "right" else 0
        x_start = xlim[1] - total_width * margin - scale_width - extra_space

    return x_start, y_pos


def _draw_scalebar_segments(
    ax,
    x_start,
    y_pos,
    bar_height,
    segment_widths,
    segments_km,
    alternating_colors,
    bar_color,
    alt_color,
    fontsize,
    label_offset,
    total_height,
    unit_type,
):
    """Draw the scalebar segments and numeric labels."""
    current_x = x_start
    cumulative_distance = 0

    for i, (width, segment_km) in enumerate(zip(segment_widths, segments_km)):
        # Determine colors
        if alternating_colors:
            top_color = bar_color if i % 2 == 0 else alt_color
            bottom_color = alt_color if i % 2 == 0 else bar_color
        else:
            top_color = bottom_color = bar_color

        # Draw rectangles
        for row, color in enumerate([bottom_color, top_color]):
            rect = Rectangle(
                (current_x, y_pos + row * bar_height),
                width,
                bar_height,
                facecolor=color,
                edgecolor="black",
                linewidth=1.0,
            )
            ax.add_patch(rect)

        # Draw tick mark
        ax.plot(
            [current_x, current_x],
            [y_pos, y_pos + 2 * bar_height],
            color="black",
            linewidth=1,
        )

        # Add numeric label
        label_text = _format_distance_label(cumulative_distance, unit_type)
        label_y = y_pos + 2 * bar_height + total_height * label_offset
        ax.text(
            current_x,
            label_y,
            label_text,
            ha="center",
            va="bottom",
            color="0.3",
            fontsize=fontsize,
        )

        current_x += width
        cumulative_distance += segment_km

    # Final tick mark and label
    ax.plot(
        [current_x, current_x],
        [y_pos, y_pos + 2 * bar_height],
        color="black",
        linewidth=1,
    )

    final_label = _format_distance_label(cumulative_distance, unit_type)
    ax.text(
        current_x,
        y_pos + 2 * bar_height + total_height * label_offset,
        final_label,
        ha="center",
        va="bottom",
        color="0.3",
        fontsize=fontsize,
    )


def _format_distance_label(distance_km, unit_type):
    """Format distance label, showing integers when possible."""
    if unit_type == "m":
        distance = distance_km * 1000
        return f"{int(distance)}" if distance == int(distance) else f"{distance:.0f}"
    else:
        return (
            f"{int(distance_km)}"
            if distance_km == int(distance_km)
            else f"{distance_km:.1f}"
        )


def _add_unit_label(
    ax,
    x_start,
    y_pos,
    scale_width,
    unit_label,
    unit_position,
    spacing,
    total_width,
    total_height,
    fontsize,
):
    """Add the unit label (e.g., 'Kilometers') in specified position."""
    if unit_position == "right":
        unit_x = x_start + scale_width + total_width * spacing
        unit_y = y_pos
        ax.text(unit_x, unit_y, unit_label, ha="left", va="bottom", fontsize=fontsize)
    else:  # bottom
        unit_x = x_start + scale_width
        unit_y = y_pos - total_height * spacing
        ax.text(unit_x, unit_y, unit_label, ha="right", va="top", fontsize=fontsize)
