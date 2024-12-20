# utils.py
import pandas as pd
from geopy.distance import geodesic
import folium

def load_data(country):
    """
    Load parquet data based on the country and extract 'rppa' into a separate column.
    """
    data_paths = {
        'Spain': 'data/data_esp',
        'Netherlands': 'data/data_nld',
        'Great Britain': 'data/data_gbr',
    }
    try:
        df = pd.read_parquet(data_paths[country])
        
        # Filter out rows where 'query_lat' is null
        df = df[df["query_lat"].notnull()]
        
        # Extract 'rppa' from 'rpav_matching' and create a new column
        df['rppa'] = df['rpav_matching'].apply(
            lambda x: x['fields']['rppa'] if isinstance(x, dict) and 'fields' in x and 'rppa' in x['fields'] else None
        )
        
        # Optionally, handle missing 'rppa' values
        missing_rppa = df['rppa'].isnull().sum()
        if missing_rppa > 0:
            df = df[df['rppa'].notnull()]
        
        return df
    except KeyError:
        raise ValueError(f"Unsupported country: {country}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file for {country} not found.")

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