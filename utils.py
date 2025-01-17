# utils.py
import pandas as pd
from geopy.distance import geodesic
import folium
import logging

def load_data(country_name):
    """
    Load parquet data based on the country and extract 'rppa' into a separate column.
    """
    data_paths = {
    'Albania': 'data-branch/data_alb',
    'Algeria': 'data-branch/data_dza',
    'Andorra': 'data-branch/data_and',
    'Argentina': 'data-branch/data_arg',
    'Australia': 'data-branch/data_aus',
    'Austria': 'data-branch/data_aut',
    'Bahrain': 'data-branch/data_bhr',
    'Belarus': 'data-branch/data_blr',
    'Belgium': 'data-branch/data_bel',
    'Bosnia and Herzegovina': 'data-branch/data_bih',
    'Brazil': 'data-branch/data_bra',
    'Brunei Darussalam': 'data-branch/data_brn',
    'Bulgaria': 'data-branch/data_bgr',
    'Canada': 'data-branch/data_can',
    'Chile': 'data-branch/data_chl',
    'Colombia': 'data-branch/data_col',
    'Croatia': 'data-branch/data_hrv',
    'Cyprus': 'data-branch/data_cyp',
    'Czech Republic': 'data-branch/data_cze',
    'Denmark': 'data-branch/data_dnk',
    'Egypt': 'data-branch/data_egy',
    'Eswatini': 'data-branch/data_swz',  # Formerly Swaziland
    'Estonia': 'data-branch/data_est',
    'Finland': 'data-branch/data_fin',
    'France': 'data-branch/data_fra',
    'Germany': 'data-branch/data_deu',
    'Gibraltar': 'data-branch/data_gib',
    'Greece': 'data-branch/data_grc',
    'Great Britain': 'data-branch/data_gbr',
    'Guadeloupe': 'data-branch/data_glp',
    'Hong Kong': 'data-branch/data_hkg',
    'Hungary': 'data-branch/data_hun',
    'Iceland': 'data-branch/data_isl',
    'India': 'data-branch/data_ind',
    'Indonesia': 'data-branch/data_idn',
    'Ireland': 'data-branch/data_irl',
    'Israel': 'data-branch/data_isr',
    'Italy': 'data-branch/data_ita',
    'Kazakhstan': 'data-branch/data_kaz',
    'Kuwait': 'data-branch/data_kwt',
    'Latvia': 'data-branch/data_lva',
    'Liechtenstein': 'data-branch/data_lie',
    'Lithuania': 'data-branch/data_ltu',
    'Luxembourg': 'data-branch/data_lux',
    'Macau': 'data-branch/data_mac',
    'Malta': 'data-branch/data_mlt',
    'Martinique': 'data-branch/data_mtq',
    'Mayotte': 'data-branch/data_myt',
    'Mexico': 'data-branch/data_mex',
    'Montenegro': 'data-branch/data_mne',
    'Morocco': 'data-branch/data_mar',
    'Netherlands': 'data-branch/data_nld',
    'New Zealand': 'data-branch/data_nzl',
    'North Macedonia': 'data-branch/data_mkd',
    'Norway': 'data-branch/data_nor',
    'Oman': 'data-branch/data_omn',
    'Peru': 'data-branch/data_per',
    'Philippines': 'data-branch/data_phl',
    'Poland': 'data-branch/data_pol',
    'Portugal': 'data-branch/data_prt',
    'Qatar': 'data-branch/data_qat',
    'Réunion': 'data-branch/data_reu',
    'Russian Federation': 'data-branch/data_rus',
    'San Marino': 'data-branch/data_smr',
    'Serbia': 'data-branch/data_srb',
    'Slovakia': 'data-branch/data_svk',
    'Slovenia': 'data-branch/data_svn',
    'South Africa': 'data-branch/data_zaf',
    'Spain': 'data-branch/data_esp',
    'Sweden': 'data-branch/data_swe',
    'Switzerland': 'data-branch/data_che',
    'Taiwan': 'data-branch/data_twn',
    'Thailand': 'data-branch/data_tha',
    'Turkey': 'data-branch/data_tur',
    'Ukraine': 'data-branch/data_ukr',
    'United Arab Emirates': 'data-branch/data_are',
    'USA': 'data-branch/data_usa',
    'Vatican City': 'data-branch/data_vat',
    'Venezuela': 'data-branch/data_ven',
    'Vietnam': 'data-branch/data_vnm',
    'Kosovo': 'data-branch/data_xks',  # Non-standard ISO code
    }


    df = pd.read_parquet(data_paths[country_name])
    df = df.iloc[5:20000]
    return df

def max_distance(centroid, markers):
    """
    Calculate the maximum distance in meters from the centroid to any marker.
    """
    if not markers:
        return 0
    return max(geodesic(centroid, marker).km for marker in markers) * 1000  # meters

def calculate_bounds(lat, lon, distance_meters):
    """
    Calculate map bounds based on latitude, longitude, and distance.
    """
    lat_offset = distance_meters / 111320
    lon_offset = distance_meters / (40008000 * (1 / 360)) * (1 / (111320 * 2))
    return [[lat - lat_offset, lon - lon_offset], [lat + lat_offset, lon + lon_offset]]

def prepare_poi_options(data, include_release_version=False):
    """
    Prepare Point of Interest (POI) options with additional information.
    """
    data = data.copy()  # Avoid modifying the original DataFrame
    data['num_reference_routing_points'] = data["reference_routing_points"].apply(len)
    data['num_provider_routing_points'] = data["provider_routing_points"].apply(len)

    names_with_info = [
        f"{name} - {category} - [{num_ref}, {num_provider}] - RPPA = {rppa}" +
        (f" - {release_version}" if include_release_version else "")
        for name, category, num_ref, num_provider, rppa, release_version in zip(
            data["name"], 
            data["category_name"], 
            data["num_reference_routing_points"], 
            data["num_provider_routing_points"], 
            data["rppa"],
            data["release_version"]
        )
    ]
    return names_with_info

def extract_unique_rrpa(df_pandas):
    """
    Extract unique RPPA values from the 'rppa' column.
    """
    rrpa_list = df_pandas['rppa'].dropna().unique().tolist()
    return rrpa_list

def extract_unique_routing_points_counts(df_pandas):
    """
    Extract unique routing_points_count_str values from the DataFrame.
    """
    routing_counts = df_pandas['routing_points_count_str'].dropna().unique().tolist()
    routing_counts.sort(key=lambda x: (int(x.split()[0]), int(x.split(',')[1].split()[0])))
    return routing_counts


def create_folium_map(reference_latlon, provider_latlon, provider_routing_points,
                     reference_routing_points, poi_characteristic_distance,
                     assignation, rppa):
    """
    Create a Folium map with the given parameters.

    Parameters:
    - reference_latlon (tuple): (latitude, longitude) of the reference point.
    - provider_latlon (tuple or None): (latitude, longitude) of the provider point.
    - provider_routing_points (list of tuples): List of (latitude, longitude) tuples.
    - reference_routing_points (list of tuples): List of (latitude, longitude) tuples.
    - poi_characteristic_distance (float): Distance metric related to POI.
    - assignation (list of lists/tuples): Pairs indicating routing point assignments.
    - rppa (float): RPPA value.

    Returns:
    - folium.Map: The generated Folium map object.
    """
    try:
        # Initialize the map centered at the reference location
        m = folium.Map(location=reference_latlon, zoom_start=17, tiles='openstreetmap')
        folium.Marker(location=reference_latlon, icon=folium.Icon(color='black', icon="")).add_to(m)

        # Add provider marker if valid
        if provider_latlon and isinstance(provider_latlon, tuple) and len(provider_latlon) == 2:
            folium.Marker(location=provider_latlon, icon=folium.Icon(color='red', icon="")).add_to(m)

        # Initialize markers list
        markers = [reference_latlon]
        if provider_latlon and isinstance(provider_latlon, tuple) and len(provider_latlon) == 2:
            markers.append(provider_latlon)

        # Add provider routing points
        for rp in provider_routing_points:
            folium.Circle(
                location=rp,
                radius=0.7 * poi_characteristic_distance,
                color="red",
                fill=True,
                fill_color='red',
                fill_opacity=0.2
            ).add_to(m)
            folium.CircleMarker(
                location=rp,
                radius=4,
                color="red",
                fill=False,
                fill_opacity=1,
                fill_color='red'
            ).add_to(m)
            folium.PolyLine(
                locations=[rp, provider_latlon],
                color="red",
                weight=2,
                dashArray="5,5"
            ).add_to(m)
            markers.append(rp)

        # Add green polylines based on assignation and rppa
        if rppa > 0:
            for asign in assignation:
                try:
                    ref_point = reference_routing_points[asign[0]]
                    prov_point = provider_routing_points[asign[1]]
                    distance = geodesic(ref_point, prov_point).meters
                    if distance < 0.7 * poi_characteristic_distance:
                        folium.PolyLine(
                            locations=[ref_point, prov_point],
                            color="green",
                            weight=4
                        ).add_to(m)
                except (IndexError, TypeError) as e:
                    continue  # Skip invalid assignations

        # Add reference routing points
        for rp in reference_routing_points:
            folium.CircleMarker(
                location=rp,
                radius=4,
                color="black",
                fill=False,
                fill_opacity=1,
                fill_color='black'
            ).add_to(m)
            folium.PolyLine(
                locations=[rp, reference_latlon],
                color="black",
                weight=2,
                dashArray="5,5"
            ).add_to(m)

        # Calculate and set map bounds
        bounds = calculate_bounds(reference_latlon[0], reference_latlon[1], 1.5 * max_distance(reference_latlon, markers))
        m.fit_bounds(bounds)

        return m
    except Exception as e:
        logging.error(f"Error creating Folium map: {e}")
        raise e
    
def filter_df(df_pandas, release_version, category, selected_rppa, selected_routing_points_count):
    
    # Apply filters for release version and category
    if release_version and release_version != 'All':
        df_pandas = df_pandas[df_pandas['release_version'] == release_version]
        logging.info(f"Filtered data by release_version: {release_version}")

    if category and category != 'All':
        df_pandas = df_pandas[df_pandas['category_name'] == category]
        logging.info(f"Filtered data by category: {category}")

    # Apply Routing Points Count filter
    print(selected_routing_points_count)
    if selected_routing_points_count and selected_routing_points_count != 'All':
        df_pandas = df_pandas[df_pandas['routing_points_count_str'] == selected_routing_points_count]
        logging.info(f"Filtered data by routing_points_count: {selected_routing_points_count}")

    # Apply RPPA filter to the DataFrame using the 'rppa' column
    if selected_rppa and selected_rppa != 'All':
        # Check if selected_rppa contains a split character
        if '-' in selected_rppa:
            rppa_range = selected_rppa.split('-')
            try:
                min_rppa = float(rppa_range[0])
                max_rppa = float(rppa_range[1]) if len(rppa_range) > 1 else 1.0
                logging.info(f"Filtering RPPA in range: {min_rppa} - {max_rppa}")
            except ValueError:
                logging.error("Invalid RPPA range format.")
                return jsonify({'error': 'Invalid RPPA range format.'}), 400
        else:
            # If it's a single value like '0.9'
            try:
                min_rppa = max_rppa = float(selected_rppa)
                logging.info(f"Filtering RPPA for value: {min_rppa}")
            except ValueError:
                logging.error("Invalid RPPA value.")
                return jsonify({'error': 'Invalid RPPA value.'}), 400

        # Filter the DataFrame based on the 'rppa' column
        df_pandas = df_pandas[(df_pandas['rppa'] >= min_rppa) & (df_pandas['rppa'] <= max_rppa)]
        logging.info(f"Number of POIs after RPPA filtering: {len(df_pandas)}")

    return df_pandas