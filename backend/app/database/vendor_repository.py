from .connection import get_db
import mysql.connector
import mysql.connector.errors



#----------------
# ADD VENDOR 
#----------------------------------------

def add_vendor(vendor_name: str , vendor_url: str,camera_number:int):
     conn = get_db()
     cursor = conn.cursor()
     try:
          sql = """ insert into vendor (VendorName,NUMBER_CAM,URL,enable) values(%s,%s,%s,%s)""" 
          values = (vendor_name,camera_number,vendor_url,"true")
          cursor.execute(sql, values)
          conn.commit()
          return {"message" : "vendor added into database"}
     finally:
           cursor.close()
           conn.close()

    


#------------------------------------------------------
# REMOVE VENDOR 
#-----------------------------------------------------


def remove_vendor(vendor_id:int):
     conn = get_db()
     cursor = conn.cursor()
     try:
          sql = """ DELETE from vendor where VendorID = %s""" 
          values = (vendor_id,)
          cursor.execute(sql, values)
          deleted = cursor.rowcount 
          if deleted is None  :
               return {"messag" : "sorry faild to  delet"}
          conn.commit()
          return {"message" : "vendor removed into database"}

     finally:
           cursor.close()
           conn.close()

     

#------------------------------------------------------
# UPDATE VENDOR 
#------------------------------------------------

def updated_vendor(change_were ,change_what,change_were_data,change_what_data ):
    conn = get_db()
    cursor = conn.cursor()
    try:
        sql = f"UPDATE vendor SET {change_what} = %s where {change_were} = %s" 
        values = (change_what_data , change_were_data)
        cursor.execute(sql, values)
        updated = cursor.rowcount
        if updated == 0:
              return {"ok": False,"messag" : "sorry faild to  delet"}
        conn.commit()
 
        return {"ok": True, "rowcount": cursor.rowcount, "message": "Vendor updated"} 
             
    finally:
        cursor.close()
        conn.close()
    
    


#---------------------------------------------
# VENDOR INFO 
#-----------------------------------------------

def info_vendor(vendor_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        
        cursor.execute("select * from vendor where vendor_id = %s",(vendor_id,))
        vendor = cursor.fetchone()
        if vendor is None :
              return {"messag" : "sorry faild to  featch"}
        

        conn.commit()

        return {"message" : "vendor updated into database",
            "number_of_vendor": len(vendor),"vendor":vendor
            }
    finally:
        cursor.close()
        conn.close()
    
    

#-------------------------------------
# VENOR 
#---------------------------------

def vendor():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT VendorID, VendorName, NUMBER_CAM, URL, enable FROM vendor")
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return [
        {
            "VendorID": r[0],
            "VendorName": r[1],
            "NUMBER_CAM": r[2],
            "URL": r[3],
            "enable": r[4]
        }
        for r in rows
    ]
    
    

