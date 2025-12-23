import os
import json
import datetime
import math

def create_timestamp():
    now = datetime.datetime.now()
    timestamp = now.strftime("%y%m%d_%H%M")

    return timestamp

def create_part_json(part, timestamp = None):
    if timestamp is None:
        timestamp = create_timestamp()

    # 2. Prepare Data (Convert NumPy arrays to lists)
    export_data = {
        "timestamp": timestamp,
        "part_id": part.part_id,
        "tabs": {}
    }

    for tid, tab in part.tabs.items():
        export_data["tabs"][tid] = {
            "points": {label: pt.tolist() for label, pt in tab.points.items()}
        }

    return export_data

def export_to_json(part, output_dir="exports"):
    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Assuming part.tabs is a dict of your tab objects
    num_tabs = len(part.tabs)
    num_rects = getattr(part, 'number_rectangles', num_tabs) 
    
    timestamp = create_timestamp()

    filename = f"{timestamp}_part{part.part_id}_{num_rects}rects_{num_tabs}tabs.json"
    filepath = os.path.join(output_dir, filename)

    export_data = create_part_json(part, timestamp)    

    # 3. Write to file
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=4)

    print(f"Exported solution to: {filepath}")
    return filepath

# WARNING: THIS SECTION IS STILL EXPERIMENTAL
def export_to_onshape(part, output_dir="exports"):
    part_json = create_part_json(part)
    # Vector helpers
    sub = lambda a, b: [a[i] - b[i] for i in range(3)]
    cross = lambda a, b: [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
    dot = lambda a, b: sum(x*y for x, y in zip(a, b))
    norm = lambda v: [x / m for x in v] if (m := math.sqrt(sum(x*x for x in v))) else v
    mag_sq = lambda v: sum(x*x for x in v)

    fs = [
        'FeatureScript 2837;',
        'import(path : "onshape/std/geometry.fs", version : "2837.0");',
        'annotation { "Feature Type Name" : "hgen-sm-part" }',
        'export const jsonImport = defineFeature(function(context is Context, id is Id, definition is map)',
        '    precondition { }',
        '    {',
        '        const thickness = 1.0 * millimeter;'
    ]
    extrude_queries = []

    for tab_id, tab_data in part_json.get("tabs", {}).items():
        pts = list(tab_data["points"].values())
        # if len(pts) < 3: continue

        # --- Plane Detection & Basis Calculation ---
        p0 = pts[0]
        v1 = sub(pts[1], p0)
        
        # FIX: Find a point that is NOT collinear with p0 and p1 to determine normal
        z_axis = [0, 0, 1]
        valid_plane_found = False
        
        for i in range(2, len(pts)):
            v_temp = sub(pts[i], p0)
            cp = cross(v1, v_temp)
            # Check if cross product magnitude is sufficient (not collinear)
            if mag_sq(cp) > 1e-8: 
                z_axis = norm(cp)
                valid_plane_found = True
                break
        
        if not valid_plane_found:
            print(f"Skipping Tab {tab_id}: Points are collinear or degenerate.")
            continue

        x_axis = norm(v1)            
        y_axis = cross(z_axis, x_axis)

        # Project 3D points to 2D local plane
        points_2d = []
        for p in pts:
            vec = sub(p, p0)
            u, v = dot(vec, x_axis), dot(vec, y_axis)
            points_2d.append(f"vector({u}, {v}) * millimeter")
        
        # Ensure the loop is closed for 2D sketch
        if points_2d[0] != points_2d[-1]:
             points_2d.append(points_2d[0])

        # Format Vectors for FS
        fs_org = f"vector({p0[0]}, {p0[1]}, {p0[2]}) * millimeter"
        fs_norm = f"vector({z_axis[0]}, {z_axis[1]}, {z_axis[2]})"
        fs_x = f"vector({x_axis[0]}, {x_axis[1]}, {x_axis[2]})"

        # --- Generate FeatureScript ---
        fs.append(f'')
        fs.append(f'        // --- Tab {tab_id} ---')
        fs.append(f'        var sketch{tab_id} = newSketchOnPlane(context, id + "sketch{tab_id}", {{ "sketchPlane" : plane({fs_org}, {fs_norm}, {fs_x}) }});')
        fs.append(f'        skPolyline(sketch{tab_id}, "poly{tab_id}", {{ "points" : [{", ".join(points_2d)}] }});')
        fs.append(f'        skSolve(sketch{tab_id});')
        
        fs.append(f'        opExtrude(context, id + "extrude{tab_id}", {{')
        fs.append(f'            "entities" : qSketchRegion(id + "sketch{tab_id}"),')
        fs.append(f'            "direction" : {fs_norm},')
        fs.append(f'            "endBound" : BoundingType.BLIND,')
        fs.append(f'            "endDepth" : thickness')
        fs.append(f'        }});')
        extrude_queries.append(f'qCreatedBy(id + "extrude{tab_id}", EntityType.BODY)')

    # --- Merge Operation ---
    if extrude_queries:
        fs.append(f'')
        fs.append(f'        opBoolean(context, id + "unionBodies", {{')
        fs.append(f'            "tools" : qUnion([{", ".join(extrude_queries)}]),')
        fs.append(f'            "operationType" : BooleanOperationType.UNION')
        fs.append(f'        }});')

    fs.append('    });')
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = create_timestamp()
    num_rects = len(part.tabs)
    num_tabs = len(part.tabs)

    filename = f"{timestamp}_part{part.part_id}_{num_rects}rects_{num_tabs}tabs.fs"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w') as f:
        f.write("\n".join(fs))
    print(f"Done. Copy {filepath} to Onshape.")


# from dotenv import load_dotenv
# from onshape_client.client import Client
# load_dotenv() # Loads variables from .env into environment

# def export_to_onshape(part, solution_id = 0, output_dir="exports"):
#     part_json = create_part_json(part)
#     convert_to_fs(part_json)


    # API_KEY = os.getenv("ONSHAPE_API_KEY")
    # SECRET_KEY = os.getenv("ONSHAPE_SECRET_KEY")

    # # Authenticate
    # client = Client(configuration={
    #     "base_url": "https://cad.onshape.com",
    #     "access_key": API_KEY,
    #     "secret_key": SECRET_KEY
    # })

    # # Create a new document
    # doc = client.documents_api.create_document({"name": "Generated Tabs Sheet Metal"})
    # doc_id = doc.id

    # # Get workspace ID
    # workspaces = client.documents_api.get_document_workspaces(did=doc_id)
    # workspace_id = workspaces[0].id

    # print("Document ID:", doc_id)
    # print("Workspace ID:", workspace_id)

    # # Upload JSON file into the document
    # with open(export_data, "rb") as f:
    #     upload = client.blob_elements_api.upload_file_create_element(
    #         did=doc_id,
    #         wid=workspace_id,
    #         file=f
    #     )

    # print("Upload result:", upload)