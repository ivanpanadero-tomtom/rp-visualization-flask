# app.py
from flask import Flask, render_template, request, jsonify, make_response
import folium
from utils import (
    load_data,
    prepare_poi_options,
    extract_unique_rrpa,
    extract_unique_routing_points_counts,
    create_folium_map,
    filter_df
)
import logging
from data_info import country_list
import re

app = Flask(__name__)

# Constants for pagination
DEFAULT_START_INDEX = 0
DEFAULT_END_INDEX = 100

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

def get_cached_data(country):
    """
    Retrieve data from cache or load it if not present.
    """
    if country in data_cache:
        logging.info(f"Loaded data from cache for {country}")
        return data_cache[country]
    try:
        df = load_data(country)
        data_cache[country] = df
        logging.info(f"Data loaded and cached for {country}")
        return df
    except (ValueError, FileNotFoundError) as e:
        logging.error(e)
        raise e

def extract_filter_options(df, selected_version, selected_category, selected_rppa, selected_routing_points_count):
    """
    Extract and prepare filter options from the dataframe.
    """
    rrpa_list = [f"{float(rppa):.2f}" for rppa in extract_unique_rrpa(df)]
    rrpa_list = sorted(rrpa_list)
    routing_points_counts = extract_unique_routing_points_counts(df)
    release_versions = df['release_version'].unique().tolist()
    release_versions = sorted(release_versions)
    categories =  df['category_name'].unique().tolist()
    categories = sorted(categories)

    logging.info(f"Extracted RPPA list: {rrpa_list}")
    logging.info(f"Extracted Routing Points Counts: {routing_points_counts}")
    logging.info(f"Extracted categories: {categories}")

    return {
        'rrpa_list': rrpa_list,
        'routing_points_counts': routing_points_counts,
        'release_versions': release_versions,
        'categories': categories
    }

@app.errorhandler(Exception)
def handle_exception(e):
    """
    Global error handler.
    """
    logging.error(f"Unhandled exception: {e}")
    return render_template('error.html', message=str(e)), 500

@app.route('/')
def index():
    try:
        countries = sorted(country_list())
        selected_country = countries[0]

        df = get_cached_data(selected_country)

        filter_options = extract_filter_options(df, 'All', 'All', 'All', 'All')

        # Apply default filters
        filtered_df = filter_df(
            df,
            release_version='All',
            category='All',
            selected_rppa='All',
            selected_routing_points_count='All',
            min_characteristic_distance= 0,
            max_characteristic_distance= df['poi_characteristic_distance'].max()
        )

        len_df = len(filtered_df)
        paginated_df = filtered_df.iloc[DEFAULT_START_INDEX:DEFAULT_END_INDEX]

        pois = prepare_poi_options(paginated_df, include_release_version=True)
        logging.info(f"Prepared POI options: {pois[:5]}...")  # Log first 5 for brevity

        return render_template(
            'index.html',
            countries=countries,
            selected_country=selected_country,
            release_versions=filter_options['release_versions'],
            selected_version='All',
            categories=filter_options['categories'],
            pois=pois,
            selected_poi=None,
            rrpa_list=filter_options['rrpa_list'],
            selected_rppa='All',
            routing_points_counts=filter_options['routing_points_counts'],
            selected_routing_points_count='All',
            len_df_pandas=len_df
        )
    except Exception as e:
        return render_template('error.html', message=str(e)), 500

@app.route('/update_pois', methods=['GET'])
def update_pois():
    try:
        # Retrieve query parameters with defaults
        country = request.args.get('country')
        release_version = request.args.get('release_version', 'All')
        category = request.args.get('category', 'All')
        selected_rppa = request.args.get('selected_rppa', 'All').strip()
        selected_routing_points_count = request.args.get('routing_points_count', 'All')
        start_index = int(request.args.get('start_index', DEFAULT_START_INDEX))
        end_index = int(request.args.get('end_index', DEFAULT_END_INDEX))
        search_query = request.args.get('search', '')
        min_characteristic_distance = request.args.get('min_characteristic_distance', type=float)
        max_characteristic_distance = request.args.get('max_characteristic_distance', type=float)

        
        start_index = start_index - 1
        logging.info(
            f"Received /update_pois request with country={country}, release_version={release_version}, "
            f"category={category}, selected_rppa={selected_rppa}, routing_points_count={selected_routing_points_count}, "
            f"start_index={start_index}, end_index={end_index}, search_query='{search_query}'"
        )

        df = get_cached_data(country)

        filter_options = extract_filter_options(df, release_version, category, selected_rppa, selected_routing_points_count)

        # Apply filters
        filtered_df = filter_df(df, release_version, category, selected_rppa, selected_routing_points_count, min_characteristic_distance, max_characteristic_distance)

        # Apply search if provided
        if search_query:
            filtered_df = filtered_df[
                filtered_df['name'].str.contains(re.escape(search_query), case=False, na=False)
            ]
            logging.info(f"Applied search filter with query: '{search_query}'")

        # Apply pagination
        total_length = len(filtered_df)
        end_index = min(end_index, total_length)
        start_index = max(start_index, 0)
        if start_index > end_index:
            start_index = 0
        paginated_df = filtered_df.iloc[start_index:end_index]

        pois = prepare_poi_options(paginated_df, include_release_version=(release_version == 'All'))
        logging.info(f"Prepared POI options: {pois[:5]}...")  # Log first 5 for brevity

        return jsonify({
            'pois': pois,
            'rrpa_list': filter_options['rrpa_list'],
            'selected_rppa': selected_rppa,
            'routing_points_counts': filter_options['routing_points_counts'],
            'selected_routing_points_count': selected_routing_points_count,
            'len_df_pandas': total_length
        })
    except Exception as e:
        logging.error(f"Error in /update_pois: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_map', methods=['POST'])
def get_map():
    try:
        data = request.form
        selected_country = data.get('country')
        selected_rppa = data.get('rppa', 'All')
        selected_version = data.get('release_version', 'All')
        selected_category = data.get('category', 'All')
        selected_poi_id = data.get('poi')
        selected_routing_points_count = data.get('routing_points_count', 'All')
        search_query = data.get('search', '')



        logging.info(
            f"Received /get_map request with country={selected_country}, rppa={selected_rppa}, "
            f"release_version={selected_version}, category={selected_category}, poi_id={selected_poi_id}, "
            f"routing_points_count={selected_routing_points_count}, search_query='{search_query}'"
        )

        df = get_cached_data(selected_country)
        logging.info(f"First rows of the loaded DataFrame:\n{df.head()}")
        logging.info(f"LEN:\n{len(df)}")

        selected_poi_id = int(selected_poi_id)
        # Find the POI by unique ID
        # Find the POI by unique ID
        matching_rows = df[df['poi_id'] == selected_poi_id]
        if matching_rows.empty:
            logging.error(f"No POI found with id: {selected_poi_id}")
            return jsonify({'error': 'POI not found'}), 404

        row = matching_rows.iloc[0]

        # Extract necessary fields with error handling
        try:
            rppa = row['rppa']
            reference_routing_points = row["reference_routing_points"]
            provider_routing_points = row["provider_routing_points"]
            poi_characteristic_distance = row['poi_characteristic_distance']
            assignation = row['assignation']
            reference_latlon = (float(row['ref_lat']), float(row['ref_lon']))
            provider_latlon = (float(row['query_lat']), float(row['query_lon']))
            poi_name = row['name']
            poi_category = row['category_name']
        except (KeyError, TypeError, ValueError) as e:
            logging.error(f"Error extracting fields from POI: {e}")
            return jsonify({'error': 'Selected POI does not contain required fields.'}), 400

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

        # Generate color based on RPPA
        try:
            rppa_float = float(rppa)
            rppa_color = f"rgb({int(255 * (1 - rppa_float))}, {int(rppa_float * 200)}, 0)"
        except ValueError:
            rppa_color = "rgb(0, 0, 0)"  # Default color if conversion fails

        logging.info(f"Map generated for POI: {poi_name}")

        return jsonify({
            'map_html': map_html,
            'rppa': rppa,
            'rppa_color': rppa_color,
            'poi_name': poi_name,
            'poi_category': poi_category
        })
    except Exception as e:
        logging.error(f"Error in /get_map: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)  # Ensure debug=False in production