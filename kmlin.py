import os,sys,string
from fastkml import kml



def main(kml_file_path, extras):
    with open(kml_file_path, 'rb') as kml_file:
        csv = kml_file_path.replace(".kml","")+".csv"
        doc = kml.KML.parse(kml_file_path, validate=False)
        #print(("doc", doc, dir(doc), doc.features))
        f=open(csv,  "w")

        features = list(doc.features)
        if not features:
            print("El archivo KML no contiene características (features).")
        else:
            # Asumiendo que el primer elemento es el que contiene las features
            kml_document = features[0]

            # Recorrer todas las features dentro del documento
            for feature in list(kml_document.features):
                print(f"Tipo de Característica: {feature.name}")

                # 4. Acceder a la geometría (puntos, líneas, polígonos)
                if feature.geometry:
                    geom = feature.geometry
                    color='ff000000'
                    try:
                        print(("fea", feature.styles[0].styles[0].color))
                        color = feature.styles[0].styles[0].color
                    except:
                        pass
                    #print(("geom", geom, dir(geom), "feature", feature, dir(feature), "styles", dir(feature.styles[0]), feature.styles[0]))

                    if geom.geom_type == 'LineString':

                        r = ",".join([" ".join(x.split()[:2]) for x in  geom._wkt_coords.split(",")])



                        print((f"  Geometría: {geom.geom_type}"), dir(geom))
                        f.write("%s\t%s\t%s\t%s\n" % (
                        feature.name, r, color, "\t".join(extras)))

                    if geom.geom_type != 'Point': continue

                    print(f"  Geometría: {geom.geom_type}")



                    # Ejemplo para un Point
                    if geom.geom_type == 'Point':
                        # Las coordenadas están en (longitud, latitud, elevación)
                        print(f"  Coordenadas: {geom.coords[0]}")
                        f.write("%s\t%s\t%s\t%s\n"%(feature.name, geom.coords[0][0], geom.coords[0][1], "\t".join(extras)))


                    # Ejemplo para un LineString
                    elif geom.geom_type == 'LineString':
                        print(f"  Coordenadas: {list(geom.coords)}")

                    # Ejemplo para un Polygon
                    elif geom.geom_type == 'Polygon':
                        # El polígono tiene un exterior y puede tener interiores
                        print(f"  Coordenadas del Polígono Exterior: {list(geom.exterior.coords)}")




if __name__=="__main__":

    main(sys.argv[1], sys.argv[2:])