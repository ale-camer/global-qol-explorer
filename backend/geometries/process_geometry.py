import pandas as pd
import json
import ast
import os

def create_geojson_from_excel(input_path, output_path):
    print("--- STARTING GEOMETRY PROCESS ---")
    
    try:
        df = pd.read_excel(input_path)
        print(f"[DEBUG] Excel File '{input_path}' read. Columns found: {df.columns.tolist()}")

        features = []
        for index, row in df.iterrows():
            try:
                geometry_obj = ast.literal_eval(row['GEOMETRY'])

                feature = {
                    "type": "Feature",
                    "properties": {
                        "iso_a3": row['ISO_CODE'],
                        "name": row['COUNTRY']
                    },
                    "geometry": geometry_obj
                }
                features.append(feature)
            except (ValueError, SyntaxError) as e:
                print(f"[ERROR] Row {index+2}: The geometry was not processed {row.get('COUNTRY', 'Unknown Country')}. Error: {e}")
                continue
        
        feature_collection = {
            "type": "FeatureCollection",
            "features": features
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(feature_collection, f)
        
        print(f"[SUCCESS] GeoJSON file '{output_path}' created with {len(features)} countries.")
        print("--- ENDED GEOMETRY PROCESS ---")

    except FileNotFoundError:
        print(f"[ERROR] File not found in: '{input_path}'")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file = os.path.join(base_dir, 'world_administrative_boundaries.xlsx') 
    geojson_file = os.path.join(base_dir, '..', 'app', 'api', 'static', 'world-geometry.json')
    create_geojson_from_excel(excel_file, geojson_file)