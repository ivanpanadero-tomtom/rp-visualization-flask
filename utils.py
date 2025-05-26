# utils.py
import pandas as pd
from geopy.distance import geodesic
from folium import Element
import folium
import logging
from flask import jsonify
from data_info import data_paths_dict

def load_data(country_name):
    """
    Load parquet data based on the country and extract 'rppa' into a separate column.
    """
    data_paths = data_paths_dict()

    df = pd.read_parquet(data_paths[country_name])

    df['num_reference_routing_points'] = df["reference_routing_points"].apply(len)
    df['num_provider_routing_points'] = df["provider_routing_points"].apply(len)
    df = df.dropna(subset=["rppa"])
    df['routing_points_count_str'] = (
        df['routing_points_count_str']
        .str.replace('Reference', 'Google', case=False)
        .str.replace('Provider', 'Orbis', case=False)
    )
    df = df.reset_index(drop=True)    # ensure a clean 0..n numeric index

    # Convert 'rppa' to float, coercing errors to NaN and then drop those rows
    df['rppa'] = pd.to_numeric(df['rppa'], errors='coerce')
    df = df.dropna(subset=['rppa'])

    df['poi_id'] = df.index          # use the row index as unique ID
    df['rppa'] = df['rppa'].astype(float)
    df['rppa'] = df['rppa'].apply(lambda x: round(x, 2))
        

    # Log the assignment for verification
    logging.info(f"POI ID column type: {df['poi_id'].dtype}")
    logging.info(f"First few POI IDs:\n{df[['poi_id', 'name']].head()}")

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

from tabulate import tabulate

def prepare_poi_options(data, include_release_version=False):
    data = data.copy()

    # 1) Precompute truncated name
    max_name_length = min(40, data['name'].str.len().max())
    data['trunc_name'] = data['name'].astype(str).apply(
        lambda x: x[:max_name_length - 3] + '...' if len(x) > max_name_length else x
    )
    max_name_length = min(max_name_length, data['name'].str.len().max())

    # 2) Optionally compute max lengths for all columns for alignment
    max_category_length = max(data['category_name'].astype(str).str.len().max(), len('Category'))
    max_count_length = len('Count')  # Header length
    max_match_length = len('Match')  # Header length
    max_version_length = len('Version') if include_release_version else 0
    max_distance_length = len('Characteristic Distance[m]')  # Header length

    # Update max lengths based on data
    # Count column is fixed as "[Ref, Prov]", which is 9 characters
    # So max_count_length remains 9 or len('Count'), whichever is larger
    max_count_length = max(max_count_length, len('[Ref, Prov]'))

    # Match (rppa) is a float with two decimals, e.g., "0.95", so max_match_length remains len('Match') unless rppa values are longer
    max_rppa_length = 4
    max_match_length = max(max_match_length, max_rppa_length)

    # Version column length
    if include_release_version:
        max_version_length = max(max_version_length, data['release_version'].astype(str).str.len().max())

    # Characteristic Distance[m] is formatted as float with two decimals and padding
    # Example: "  150.00", which is 8 characters
    max_distance_length = max(max_distance_length, len(f"{data['poi_characteristic_distance'].max():8.2f}"))

    # 3) Build the line for each row
    def build_label(row):
        label = (
            f"{row['trunc_name']:<{max_name_length}} | "
            f"{row['category_name']:<{max_category_length}} | "
            f"[{row['num_reference_routing_points']}, {row['num_provider_routing_points']}] | "
            f"{row['rppa']:<{max_match_length}.2f}"
        )
        if include_release_version and 'release_version' in row:
            label += f" | {row['release_version']:<{max_version_length}}"
        label += f" | {row['poi_characteristic_distance']:<{max_distance_length}.2f}"
        return label.replace(' ', '\u00A0')  # Replace spaces with non-breaking spaces

    # 4) Build a list of {id, label} dictionaries
    pois = []
    for _, row in data.iterrows():
        label = build_label(row)
        pois.append({
            'id': row['poi_id'],   # Unique ID
            'label': label,
        })

    # 5) Add Title Row at the Beginning
    # Construct the title using the same formatting as labels
    title_label = (
        f"{'POI_Name':<{max_name_length}} | "
        f"{'Category':<{max_category_length}} | "
        f"Count  | "
        f"{'Match':<{max_match_length}} | "
    )
    if include_release_version:
        title_label += f"{'Version':<{max_version_length}} | "
    title_label += f"{'Characteristic_Distance[m]':<{max_distance_length}}"
    title_label = title_label.replace(' ', '\u00A0')  # Replace spaces with non-breaking spaces
    title_label = title_label.replace('_', '\u00A0')  # Replace spaces with non-breaking spaces

    format_str = ''
    for i in title_label:
        if i == '|':
            format_str += '|'
        else:
            format_str += '-'
    
    pois.insert(0, {
        'id': '',  # Empty ID to differentiate from valid POIs
        'label': format_str,
    })

    pois.insert(0, {
        'id': '',  # Empty ID to differentiate from valid POIs
        'label': title_label,
    })

    return pois  # Return list of dictionaries instead of list of strings

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

             # Create the top-left box with reference POI details
        reference_lat, reference_lon = reference_latlon
        icon_color = 'black'
        icon_name = 'info-sign'  # Update based on actual icon used

        # HTML template for the info box
        info_html = f"""
        <div style="
            position: fixed;
            top: 10px;
            right: 10px;
            width: 200px;
            padding: 10px;
            background-color: white;
            border: 2px solid grey;
            border-radius: 5px;
            box-shadow: 3px 3px 6px rgba(0,0,0,0.3);
            z-index: 9999;
            font-family: Arial, sans-serif;
            font-size: 14px;
        ">
            <h4>Google POI:</h4>
            <p>({reference_lat:.6f}, {reference_lon:.6f})</p>
        </div>
        """

        # Add the HTML to the map
        m.get_root().html.add_child(Element(info_html))

        return m
    except Exception as e:
        logging.error(f"Error creating Folium map: {e}")
        raise e
    
def filter_df(df_pandas, release_version, category, selected_rppa, selected_routing_points_count, min_characteristic_distance, max_characteristic_distance):
    
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
        try:
            rppa_value = float(selected_rppa)
            df_pandas = df_pandas[df_pandas['rppa'] == rppa_value]
            logging.info(f"Filtered data by rppa: {rppa_value}")
        except ValueError:
            logging.error(f"Invalid selected_rppa value: '{selected_rppa}'. Skipping RPPA filter.")


    # Apply Characteristic Distance Filtering outside RPPA condition
    if min_characteristic_distance is not None:
        df_pandas = df_pandas[df_pandas['poi_characteristic_distance'] >= min_characteristic_distance]
        logging.info(f"Filtered POIs with characteristic_distance >= {min_characteristic_distance}")

    if max_characteristic_distance is not None:
        df_pandas = df_pandas[df_pandas['poi_characteristic_distance'] <= max_characteristic_distance]
        logging.info(f"Filtered POIs with characteristic_distance <= {max_characteristic_distance}")

    return df_pandas