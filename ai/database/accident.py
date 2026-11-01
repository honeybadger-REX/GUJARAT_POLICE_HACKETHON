from ...database.connection  import mogodb

mongo = mogodb["CCTV_accident"]
def accident_store(dicst):
    mongo.insert(dicst)
