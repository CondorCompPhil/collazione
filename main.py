import falcon.collation as coll
import falcon.lemmatise as lemm
import falcon.simple as simple
import collatex

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('folder_path', help="unix string")
    parser.add_argument('--simple', action='store_true')
    parser.add_argument('--collate', action='store_true')
    parser.add_argument('--lemmatise', action='store_true')
    parser.add_argument('--lang', action='store', choices=['fro', 'spo'], default='fro')  # choices generate
    # error messages if arg is not correct, can be useful
    parser.add_argument('--engine', action='store', choices=['pie', 'freeling'], default='pie')
    args = parser.parse_args()

    if args.simple:
        simple.collateSimple(args.folder_path)
 
    if args.lemmatise:
        # path = "./data/preproc/chevLyon/txt"
        lemm.choose_lemmatiser(args.folder_path, args.lang, args.engine)
        
    if args.collate:
        # then we need to load an xml annotated folder
        # path = "./data/input/chevLyon/xml"
        json_input = coll.load_annotated_folder(args.folder_path)

        table = collatex.collate(json_input, output="table", layout="vertical", segmentation=False, near_match=True)
        xml_output = coll.table_to_xml(table)

        with open(args.folder_path.split("/sources")[0] + "/out.xml", 'w') as f:
            print(xml_output, file=f)

        with open(args.folder_path.split("/sources")[0] + "/out.table", 'w') as f:
            print(table, file=f)
