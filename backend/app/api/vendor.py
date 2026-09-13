from fastapi import APIRouter
from pydantic import BaseModel
from ..database import vendor_repository  # adjust import path to wherever vendor_repository.py lives
from ..database import connection  # adjust import path to wherever vendor_repository.py lives

router = APIRouter()


@router.get("/")
def get_vendors():
    return {"message": "Vendors API"}


class VendorCreate(BaseModel):
    vendor_name: str
    vendor_url: str
    camera_number: int


@router.post("/vendor/add")
def add_vendor(vendor: VendorCreate):
    vendor_id = vendor_repository.add_vendor(vendor.vendor_name, vendor.vendor_url, vendor.camera_number)
    return {"ok": True, "vendor_id": vendor_id}


class VendorRemove(BaseModel):
    vendor_id: int


@router.post("/vendor/delete")
def remove_vendor(vendor: VendorRemove):
    deleted = vendor_repository.remove_vendor(vendor.vendor_id)
    if deleted == 0:
        return {"ok": False, "message": "Vendor not found"}
    return {"ok": True, "message": "Vendor removed"}


class VendorUpdate(BaseModel):
    vendor_id: int
    vendor_name: str | None = None
    vendor_url: str | None = None
    camera_number: int | None = None


class VendorUpdate(BaseModel):
    change_where: str          # column to match on, e.g. "VendorID"
    change_what: str 
    change_where_data: int | str
    change_what_data: int | str

@router.post("/vendor/update")
def update_vendor(vendor: VendorUpdate):
    result = vendor_repository.updated_vendor(
        vendor.change_where, vendor.change_what,vendor.change_where_data, vendor.change_what_data
    )
    if not result["ok"]:
        return result
    if result["rowcount"] == 0:
        return {"ok": False, "message": "No matching vendor found"}
    return {"ok": True, "message": "Vendor updated"}
 


@router.get("/vendor/{vendor_id}/info")
def info_vendor(vendor_id: int):
    info = vendor_repository.get_vendor_info(vendor_id)
    if info is None:
        return {"ok": False, "message": "Vendor not found"}
    return info