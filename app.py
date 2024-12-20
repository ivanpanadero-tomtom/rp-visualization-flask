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

    # Filter out rows where 'rppa' is NaN
    df_pandas = df_pandas.dropna(subset=['rpav_matching'])
    df_pandas = df_pandas[df_pandas['rpav_matching'].apply(
        lambda x: x['fields']['rppa'] if isinstance(x, dict) and 'fields' in x and 'rppa' in x['fields'] else None
    ).notna()]

    release_versions = df_pandas['release_version'].unique().tolist()
    release_versions.insert(0, 'All')  # Add 'All' as the first option
    selected_version = release_versions[0]  # Default to 'All'

    selected_version = release_versions[0] if release_versions else None
    if selected_version != 'All':
        df_pandas = df_pandas[df_pandas['release_version'] == selected_version]

    # Filter the DataFrame if a specific version is selected
    include_release_version = False
    if selected_version != 'All':
        df_pandas = df_pandas[df_pandas['release_version'] == selected_version]
    else:
        include_release_version = True

    pois = prepare_poi_options(df_pandas, include_release_version=include_release_version)

    return render_template(
        'index.html',
        countries=countries,
        selected_country=selected_country,
        release_versions=release_versions,
        selected_version=selected_version,
        pois=pois,
        selected_poi=None
    )

@app.route('/update_pois', methods=['GET'])
def update_pois():
    country = request.args.get('country')
    release_version = request.args.get('release_version')

    df_pandas = load_data(country)
    df_pandas = df_pandas.dropna(subset=['rpav_matching'])
    df_pandas = df_pandas[df_pandas['rpav_matching'].apply(
        lambda x: x['fields']['rppa'] if isinstance(x, dict) and 'fields' in x and 'rppa' in x['fields'] else None
    ).notna()]

    if release_version and release_version != 'All':
        df_pandas = df_pandas[df_pandas['release_version'] == release_version]

    # Filter the DataFrame if a specific version is selected
    include_release_version = False
    if release_version != 'All':
        df_pandas = df_pandas[df_pandas['release_version'] == release_version]
    else:
        include_release_version = True

    pois = prepare_poi_options(df_pandas, include_release_version=include_release_version)

    return jsonify({'pois': pois})

@app.route('/get_map', methods=['POST'])
def get_map():
    data = request.form
    selected_country = data.get('country')
    selected_version = data.get('release_version')
    selected_poi = data.get('poi')

    df_pandas = load_data(selected_country)
    df_pandas = df_pandas.dropna(subset=['rpav_matching'])
    df_pandas = df_pandas[df_pandas['rpav_matching'].apply(
        lambda x: x['fields']['rppa'] if isinstance(x, dict) and 'fields' in x and 'rppa' in x['fields'] else None
    ).notna()]

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
    rppa_color = f"rgb({int(255 * (1 - rppa))}, {int(rppa * 255)}, 0)"

    return jsonify({
        'map_html': map_html,
        'rppa': rppa,
        'rppa_color': rppa_color,
        'poi_name': poi_name,
        'poi_category': poi_category
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)