from flask import Flask, render_template, request, jsonify
import folium
import json
from geopy.distance import geodesic
import pandas as pd

app = Flask(__name__)

# Replace these paths with your actual parquet data files
def load_data(country):
    if country == 'Spain':
        df =  pd.read_parquet('data/data_esp')
    elif country == 'Netherlands':
        df =  pd.read_parquet('data/data_nld')
    elif country == 'Great Britain':
        df =  pd.read_parquet('data/data_gbr')
    non_null_query_lat = df[df["query_lat"].notnull()]

    
    return non_null_query_lat


def provider_latlon_(res):
    try:
        return res['responses'][0]['lat'], res['responses'][0]['lon']
    except (KeyError, IndexError, TypeError):
        return []

def max_distance(centroid, markers):
    return max(geodesic(centroid, marker).km for marker in markers) * 1000  # meters

def calculate_bounds(lat, lon, distance_meters):
    lat_offset = distance_meters / 111320
    lon_offset = distance_meters / (40008000 * (1 / 360)) * (1 / (111320 * 2))
    return [[lat - lat_offset, lon - lon_offset], [lat + lat_offset, lon + lon_offset]]

def prepare_poi_options(data, include_release_version=False):
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
            data["rpav_matching"].apply(lambda x: x['fields']['rppa']),
            data["release_version"]
        )
    ]
    return names_with_info

@app.route('/')
def index():
    countries = ['Spain', 'Netherlands', 'Great Britain']
    selected_country = countries[0]
    df_pandas = load_data(selected_country)

    # Extract unique RPPA values
    try:
        rrpa_list = df_pandas['rpav_matching'].apply(
            lambda x: x['fields']['rppa'] if isinstance(x, dict) and 'fields' in x and 'rppa' in x['fields'] else None
        ).dropna().unique().tolist()
    except KeyError as e:
        print(f"KeyError: {e}")
        rrpa_list = []  # Fallback in case of error

    # Convert numeric values to strings for consistent handling
    rrpa_list = [str(rppa) for rppa in rrpa_list]
    rrpa_list.insert(0, 'All')  # Add 'All' as the first option
    selected_rppa = rrpa_list[0]  # Default to 'All'

    # Extract unique release versions
    release_versions = df_pandas['release_version'].unique().tolist()
    release_versions.insert(0, 'All')  # Add 'All' as the first option
    selected_version = release_versions[0]  # Default to 'All'

    if selected_version != 'All':
        df_pandas = df_pandas[df_pandas['release_version'] == selected_version]

    # Extract unique categories
    categories = df_pandas['category_name'].unique().tolist()
    categories.insert(0, 'All')  # Add 'All' as the first option


    # Prepare POI options
    include_release_version = selected_version == 'All'
    pois = prepare_poi_options(df_pandas, include_release_version=include_release_version)

    return render_template(
        'index.html',
        countries=countries,
        selected_country=selected_country,
        release_versions=release_versions,
        selected_version=selected_version,
        categories=categories,
        pois=pois,
        selected_poi=None,
        rrpa_list=rrpa_list,
        selected_rppa=selected_rppa,
    )



@app.route('/update_pois', methods=['GET'])
def update_pois():
    country = request.args.get('country')
    release_version = request.args.get('release_version')
    category = request.args.get('category')
    selected_rppa = request.args.get('selected_rppa')  # Get selected RPPA value
    selected_count = request.args.get('selected_count')  # Get the selected count value

    # Load data for the selected country
    df_pandas = load_data(country)

    # Extract unique RPPA values
    try:
        rrpa_list = df_pandas['rpav_matching'].apply(
            lambda x: x['fields']['rppa'] if isinstance(x, dict) and 'fields' in x and 'rppa' in x['fields'] else None
        ).dropna().unique().tolist()
    except KeyError as e:
        print(f"KeyError: {e}")
        rrpa_list = []  # Fallback in case of error


    # Convert numeric values to strings for consistent handling
    rrpa_list = [str(rppa) for rppa in rrpa_list]
    rrpa_list.insert(0, 'All')  # Add 'All' as the first option

    # Apply filters for release version and category
    if release_version and release_version != 'All':
        df_pandas = df_pandas[df_pandas['release_version'] == release_version]

    if category and category != 'All':
        df_pandas = df_pandas[df_pandas['category_name'] == category]


    # Apply RPPA filter to the DataFrame (but do not modify the RPPA list)
    if selected_rppa != 'All':
    # Check if selected_rppa contains a split character
        if '-' in selected_rppa:
            rppa_range = selected_rppa.split('-')
            min_rppa = float(rppa_range[0])
            max_rppa = float(rppa_range[1]) if len(rppa_range) > 1 else 1.0
        else:
            # If it's a single value like '0.9'
            min_rppa = max_rppa = float(selected_rppa)

        # Extract 'rppa' values into a new column
        df_pandas['rppa'] = df_pandas['rpav_matching'].apply(
            lambda x: x['fields']['rppa'] if isinstance(x, dict) and 'fields' in x and 'rppa' in x['fields'] else None
        )
        # Filter the DataFrame based on the extracted 'rppa'
        df_pandas = df_pandas[(df_pandas['rppa'] >= min_rppa) & (df_pandas['rppa'] <= max_rppa)]


    # Prepare POI options
    pois = prepare_poi_options(df_pandas, include_release_version=(release_version == 'All'))

    return jsonify({'pois': pois, 'rrpa_list': rrpa_list, 'selected_rppa': selected_rppa})



@app.route('/get_map', methods=['POST'])
def get_map():
    data = request.form
    selected_country = data.get('country')
    selected_rppa = data.get('rppa')
    selected_version = data.get('release_version', 'All')
    selected_category = data.get('category', 'All')
    selected_poi = data.get('poi')

    df_pandas = load_data(selected_country)

    # Filter based on selected RPPA
    if selected_rppa != 'All':
        # Check if selected_rppa contains a split character
        if '-' in selected_rppa:
            rppa_range = selected_rppa.split('-')
            min_rppa = float(rppa_range[0])
            max_rppa = float(rppa_range[1]) if len(rppa_range) > 1 else 1.0
        else:
            # If it's a single value like '0.9'
            min_rppa = max_rppa = float(selected_rppa)

        # Extract 'rppa' values into a new column
        df_pandas['rppa'] = df_pandas['rpav_matching'].apply(
            lambda x: x['fields']['rppa'] if isinstance(x, dict) and 'fields' in x and 'rppa' in x['fields'] else None
        )
        # Filter the DataFrame based on the extracted 'rppa'
        df_pandas = df_pandas[(df_pandas['rppa'] >= min_rppa) & (df_pandas['rppa'] <= max_rppa)]

    include_release_version = False
    if selected_version and selected_version != 'All':
        df_pandas = df_pandas[df_pandas['release_version'] == selected_version]
    else:
        include_release_version = True

    names_with_info = prepare_poi_options(df_pandas, include_release_version=include_release_version)
    name_to_index = {info: idx for idx, info in enumerate(names_with_info)}

    if selected_poi not in name_to_index:
        return jsonify({'error': 'POI not found'}), 400

    row = df_pandas.iloc[name_to_index[selected_poi]]
    rppa = row['rpav_matching']['fields']['rppa']
    reference_routing_points = row["reference_routing_points"]
    provider_routing_points = row["provider_routing_points"]
    poi_characteristic_distance = row['rpav_matching']['fields']['poi_characteristic_distance']
    assignation = row['rpav_matching']['fields']['assignation']
    reference_latlon = (float(row['ref_lat']), float(row['ref_lon']))
    provider_latlon = (float(row['query_lat']), float(row['query_lon']))
    poi_name = row['name']
    poi_category = row['category_name']

    # Create the map
    m = folium.Map(location=reference_latlon, zoom_start=17, tiles='openstreetmap')
    folium.Marker(location=reference_latlon, icon=folium.Icon(color='black', icon="")).add_to(m)

    if provider_latlon and isinstance(provider_latlon, tuple) and len(provider_latlon) == 2:
        folium.Marker(location=provider_latlon, icon=folium.Icon(color='red', icon="")).add_to(m)

    markers = [reference_latlon, provider_latlon]

    for rp in provider_routing_points:
        folium.Circle(location=rp, radius=0.7*poi_characteristic_distance, color="red", fill = True, fill_color = 'red', fill_opacity = 0.2).add_to(m)
        folium.CircleMarker(location=rp, radius=4, color="red", fill=False, fill_color = 'red', fill_opacity = 1).add_to(m)
        folium.PolyLine(locations=[rp, provider_latlon], color="red", weight=2, dashArray="5, 5").add_to(m)
        markers.append(rp)

    if rppa > 0:
        for asign in assignation:
            if geodesic(reference_routing_points[asign[0]], provider_routing_points[asign[1]]).m < 0.7 * poi_characteristic_distance:
                folium.PolyLine(locations=[reference_routing_points[asign[0]], provider_routing_points[asign[1]]], color="green", weight=4).add_to(m)

    for rp in reference_routing_points:
        folium.CircleMarker(location=rp, radius=4, color="black", fill=False, fill_color = 'black', fill_opacity = 1).add_to(m)
        folium.PolyLine(locations=[rp, reference_latlon], color="black", weight=2, dashArray="5, 5").add_to(m)

        bounds = calculate_bounds(reference_latlon[0], reference_latlon[1], 1.5 * max_distance(reference_latlon, markers))
        m.fit_bounds(bounds)

    map_html = m._repr_html_()
    rppa_color = f"rgb({int(255 * (1 - rppa))}, {int(rppa * 200)}, 0)"

    return jsonify({
        'map_html': map_html,
        'rppa': rppa,
        'rppa_color': rppa_color,
        'poi_name': poi_name,
        'poi_category': poi_category
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)