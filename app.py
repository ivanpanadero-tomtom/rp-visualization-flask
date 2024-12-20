# app.py
from flask import Flask, render_template, request, jsonify
import folium
from utils import (
    load_data,
    prepare_poi_options,
    extract_unique_rrpa,
    extract_unique_routing_points_counts,
    create_folium_map
)
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Simple in-memory cache for loaded data
data_cache = {}

@app.route('/')
def index():
    countries = ['Spain', 'Netherlands', 'Great Britain']
    selected_country = countries[0]

    # Load data with caching
    if selected_country in data_cache:
        df_pandas = data_cache[selected_country]
        logging.info(f"Loaded data from cache for {selected_country}")
    else:
        try:
            df_pandas = load_data(selected_country)
            data_cache[selected_country] = df_pandas
            logging.info(f"Data loaded and cached for {selected_country}")
        except (ValueError, FileNotFoundError) as e:
            logging.error(e)
            return render_template('error.html', message=str(e)), 400

    # Extract unique RPPA values
    rrpa_list = extract_unique_rrpa(df_pandas)
    logging.info(f"Extracted RPPA list: {rrpa_list}")

    # Extract unique Routing Points Counts
    routing_points_counts = extract_unique_routing_points_counts(df_pandas)
    logging.info(f"Extracted Routing Points Counts: {routing_points_counts}")

    # Convert numeric RPPA values to strings for consistent handling
    rrpa_list = [str(rppa) for rppa in rrpa_list]
    rrpa_list.insert(0, 'All')  # Add 'All' as the first option
    selected_rppa = rrpa_list[0]  # Default to 'All'

    # Extract unique release versions
    release_versions = df_pandas['release_version'].unique().tolist()
    release_versions.insert(0, 'All')  # Add 'All' as the first option
    selected_version = release_versions[0]  # Default to 'All'

    if selected_version != 'All':
        df_pandas = df_pandas[df_pandas['release_version'] == selected_version]
        logging.info(f"Filtered data by release_version: {selected_version}")

    # Extract unique categories
    categories = df_pandas['category_name'].unique().tolist()
    categories.insert(0, 'All')  # Add 'All' as the first option
    logging.info(f"Extracted categories: {categories}")

    # Prepare POI options
    include_release_version = selected_version == 'All'
    pois = prepare_poi_options(df_pandas, include_release_version=include_release_version)
    logging.info(f"Prepared POI options: {pois[:5]}...")  # Log first 5 for brevity

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
        routing_points_counts=routing_points_counts,
        selected_routing_points_count='All'  # Default to 'All'
    )

@app.route('/update_pois', methods=['GET'])
def update_pois():
    country = request.args.get('country')
    release_version = request.args.get('release_version')
    category = request.args.get('category')
    selected_rppa = request.args.get('selected_rppa')  # Get selected RPPA value
    selected_routing_points_count = request.args.get('routing_points_count')  # Get selected Routing Points Count

    logging.info(f"Received /update_pois request with country={country}, release_version={release_version}, category={category}, selected_rppa={selected_rppa}, routing_points_count={selected_routing_points_count}")

    # Load data with caching
    if country in data_cache:
        df_pandas = data_cache[country]
        logging.info(f"Loaded data from cache for {country}")
    else:
        try:
            df_pandas = load_data(country)
            data_cache[country] = df_pandas
            logging.info(f"Data loaded and cached for {country}")
        except (ValueError, FileNotFoundError) as e:
            logging.error(e)
            return jsonify({'error': str(e)}), 400

    # Extract unique RPPA values
    rrpa_list = extract_unique_rrpa(df_pandas)
    logging.info(f"Extracted RPPA list: {rrpa_list}")

    # Extract unique Routing Points Counts
    routing_points_counts = extract_unique_routing_points_counts(df_pandas)
    logging.info(f"Extracted Routing Points Counts: {routing_points_counts}")

    # Convert numeric RPPA values to strings for consistent handling
    rrpa_list = [str(rppa) for rppa in rrpa_list]
    rrpa_list.insert(0, 'All')  # Add 'All' as the first option

    # Apply filters for release version and category
    if release_version and release_version != 'All':
        df_pandas = df_pandas[df_pandas['release_version'] == release_version]
        logging.info(f"Filtered data by release_version: {release_version}")

    if category and category != 'All':
        df_pandas = df_pandas[df_pandas['category_name'] == category]
        logging.info(f"Filtered data by category: {category}")

    # Apply Routing Points Count filter
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

    # Prepare POI options
    pois = prepare_poi_options(df_pandas, include_release_version=(release_version == 'All'))
    logging.info(f"Prepared POI options: {pois[:5]}...")  # Log first 5 for brevity

    return jsonify({
        'pois': pois,
        'rrpa_list': rrpa_list,
        'selected_rppa': selected_rppa,
        'routing_points_counts': routing_points_counts,
        'selected_routing_points_count': selected_routing_points_count
    })

@app.route('/get_map', methods=['POST'])
def get_map():
    data = request.form
    selected_country = data.get('country')
    selected_rppa = data.get('rppa')
    selected_version = data.get('release_version', 'All')
    selected_category = data.get('category', 'All')
    selected_poi = data.get('poi')

    logging.info(f"Received /get_map request with country={selected_country}, rppa={selected_rppa}, release_version={selected_version}, category={selected_category}, poi={selected_poi}")

    # Load data with caching
    if selected_country in data_cache:
        df_pandas = data_cache[selected_country]
        logging.info(f"Loaded data from cache for {selected_country}")
    else:
        try:
            df_pandas = load_data(selected_country)
            data_cache[selected_country] = df_pandas
            logging.info(f"Data loaded and cached for {selected_country}")
        except (ValueError, FileNotFoundError) as e:
            logging.error(e)
            return jsonify({'error': str(e)}), 400

    # Apply filters based on RPPA
    if selected_rppa and selected_rppa != 'All':
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
            try:
                min_rppa = max_rppa = float(selected_rppa)
                logging.info(f"Filtering RPPA for value: {min_rppa}")
            except ValueError:
                logging.error("Invalid RPPA value.")
                return jsonify({'error': 'Invalid RPPA value.'}), 400

        # Filter the DataFrame based on the 'rppa' column
        df_pandas = df_pandas[(df_pandas['rppa'] >= min_rppa) & (df_pandas['rppa'] <= max_rppa)]
        logging.info(f"Number of POIs after RPPA filtering: {len(df_pandas)}")

    # Apply release version filter
    if selected_version and selected_version != 'All':
        df_pandas = df_pandas[df_pandas['release_version'] == selected_version]
        include_release_version = False
        logging.info(f"Filtered data by release_version: {selected_version}")
    else:
        include_release_version = True

    # Apply category filter
    if selected_category and selected_category != 'All':
        df_pandas = df_pandas[df_pandas['category_name'] == selected_category]
        logging.info(f"Filtered data by category: {selected_category}")

    # Prepare POI options
    names_with_info = prepare_poi_options(df_pandas, include_release_version=include_release_version)
    name_to_index = {info: idx for idx, info in enumerate(names_with_info)}
    logging.info(f"Name to index mapping created for POIs.")

    if selected_poi not in name_to_index:
        logging.error(f"POI not found: {selected_poi}")
        return jsonify({'error': 'POI not found'}), 400

    # Retrieve the selected POI row
    row = df_pandas.iloc[name_to_index[selected_poi]]
    try:
        rppa = row['rppa']
    except KeyError as e:
        logging.error(f"Error extracting 'rppa' from selected POI: {e}")
        return jsonify({'error': 'Selected POI does not contain valid RPPA information.'}), 400

    reference_routing_points = row["reference_routing_points"]
    provider_routing_points = row["provider_routing_points"]
    try:
        poi_characteristic_distance = row['rpav_matching']['fields']['poi_characteristic_distance']
        assignation = row['rpav_matching']['fields']['assignation']
    except (KeyError, TypeError) as e:
        logging.error(f"Error extracting fields from selected POI: {e}")
        return jsonify({'error': 'Selected POI does not contain required fields.'}), 400

    try:
        reference_latlon = (float(row['ref_lat']), float(row['ref_lon']))
        provider_latlon = (float(row['query_lat']), float(row['query_lon']))
    except (ValueError, TypeError) as e:
        logging.error(f"Error extracting lat/lon from selected POI: {e}")
        return jsonify({'error': 'Selected POI has invalid latitude or longitude.'}), 400

    poi_name = row['name']
    poi_category = row['category_name']

    # Create the map
    try:
        m = create_folium_map(
            reference_latlon=reference_latlon,
            provider_latlon=provider_latlon,
            provider_routing_points=provider_routing_points,
            reference_routing_points=reference_routing_points,
            poi_characteristic_distance=poi_characteristic_distance,
            assignation=assignation,
            rppa=rppa
        )
    except Exception as e:
        logging.error(f"Failed to create map: {e}")
        return jsonify({'error': 'Failed to create map.'}), 500

    # Convert the Folium map to HTML
    map_html = m._repr_html_()

    rppa_color = f"rgb({int(255 * (1 - rppa))}, {int(rppa * 200)}, 0)"
    logging.info(f"Map generated for POI: {poi_name}")

    return jsonify({
        'map_html': map_html,
        'rppa': rppa,
        'rppa_color': rppa_color,
        'poi_name': poi_name,
        'poi_category': poi_category
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)  # Ensure debug=False in production
