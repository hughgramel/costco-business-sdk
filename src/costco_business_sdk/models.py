"""Data models for the Costco Business SDK."""

from __future__ import annotations

from dataclasses import dataclass, field


def _first_or_join(val: object) -> str:
    """Flatten a list to a semicolon-separated string, or return the value as-is."""
    if isinstance(val, list):
        return "; ".join(str(v) for v in val)
    return str(val) if val else ""


@dataclass
class Product:
    """A product from the Costco Business Delivery catalog."""

    item_number: str
    name: str
    description: str
    short_description: str
    group_id: str
    brand: str
    case_count: str
    container_size: str
    upc: str
    category_path: str

    # Location-specific
    warehouse_id: str
    stock_status: str
    availability: str

    # Pricing
    list_price: float
    sale_price: float
    discount_pct: float
    on_sale: bool
    currency: str
    min_qty: str
    max_qty: str

    # Classification
    department: str
    category_code: str
    item_class: str

    # Attributes
    buyable: bool
    member_only: bool
    fsa_eligible: bool
    chdi_eligible: bool
    searchable: bool
    comparable: bool
    variable_weight: bool
    start_date: str
    price_in_cart_only: str

    # Media & ratings
    image_url: str
    marketing_statement: str
    marketing_features: str
    rating: float
    review_count: int

    # Dietary
    dietary_features: str
    caffeine_claim: str
    has_single_sku: bool

    @classmethod
    def from_api_doc(cls, doc: dict, warehouse_id: str) -> Product:
        """Create a Product from a raw Solr API document."""
        lp = doc.get("item_location_pricing_listPrice", 0) or 0
        sp = doc.get("item_location_pricing_salePrice", 0) or 0
        on_sale = lp > 0 and sp > 0 and lp != sp
        discount_pct = round((1 - sp / lp) * 100, 1) if on_sale else 0.0

        return cls(
            item_number=doc.get("item_number", ""),
            name=doc.get("name", ""),
            description=doc.get("description", ""),
            short_description=doc.get("item_short_description", ""),
            group_id=doc.get("group_id", ""),
            brand=_first_or_join(doc.get("Brand_attr", [])),
            case_count=_first_or_join(doc.get("Case_Count_attr", [])),
            container_size=_first_or_join(doc.get("Container_Size_attr", [])),
            upc=_first_or_join(doc.get("item_manufacturing_skus", [])),
            category_path=_first_or_join(doc.get("categoryPath_ss", [])),
            warehouse_id=warehouse_id,
            stock_status=doc.get("item_location_stockStatus", ""),
            availability=doc.get("item_location_availability", ""),
            list_price=float(lp),
            sale_price=float(sp),
            discount_pct=discount_pct,
            on_sale=on_sale,
            currency=doc.get("item_location_currencyCode", "USD"),
            min_qty=str(doc.get("item_location_fulfillment_restrictions_minQty", "")),
            max_qty=str(doc.get("item_location_fulfillment_restrictions_maxQty", "")),
            department=str(doc.get("item_as400_department", "")),
            category_code=str(doc.get("item_as400_category", "")),
            item_class=doc.get("item_classification_itemclass", ""),
            buyable=bool(doc.get("item_buyable", False)),
            member_only=bool(doc.get("item_member_only", False)),
            fsa_eligible=bool(doc.get("item_fsa_eligible", False)),
            chdi_eligible=bool(doc.get("item_chdi_eligible", False)),
            searchable=bool(doc.get("item_searchable", False)),
            comparable=bool(doc.get("item_comparable", False)),
            variable_weight=bool(doc.get("item_variableweight", False)),
            start_date=doc.get("item_startDate", ""),
            price_in_cart_only=str(doc.get("item_product_price_in_cart_only", "")),
            image_url=doc.get("item_product_primary_image", ""),
            marketing_statement=doc.get("item_product_marketing_statement", ""),
            marketing_features=_first_or_join(doc.get("item_product_marketing_features", [])),
            rating=float(doc.get("item_ratings", 0) or 0),
            review_count=int(doc.get("item_review_count", 0) or 0),
            dietary_features=_first_or_join(doc.get("Dietary_Features_attr", [])),
            caffeine_claim=_first_or_join(doc.get("Caffeine_Claim_attr", [])),
            has_single_sku=bool(doc.get("hasSingleSku", False)),
        )

    def to_dict(self) -> dict:
        """Convert to a flat dictionary for CSV/JSON export."""
        return {
            "item_number": self.item_number,
            "name": self.name,
            "description": self.description,
            "short_description": self.short_description,
            "group_id": self.group_id,
            "brand": self.brand,
            "case_count": self.case_count,
            "container_size": self.container_size,
            "upc": self.upc,
            "category_path": self.category_path,
            "warehouse_id": self.warehouse_id,
            "stock_status": self.stock_status,
            "availability": self.availability,
            "list_price": self.list_price,
            "sale_price": self.sale_price,
            "discount_pct": self.discount_pct,
            "on_sale": self.on_sale,
            "currency": self.currency,
            "min_qty": self.min_qty,
            "max_qty": self.max_qty,
            "department": self.department,
            "category_code": self.category_code,
            "item_class": self.item_class,
            "buyable": self.buyable,
            "member_only": self.member_only,
            "fsa_eligible": self.fsa_eligible,
            "chdi_eligible": self.chdi_eligible,
            "searchable": self.searchable,
            "comparable": self.comparable,
            "variable_weight": self.variable_weight,
            "start_date": self.start_date,
            "price_in_cart_only": self.price_in_cart_only,
            "image_url": self.image_url,
            "marketing_statement": self.marketing_statement,
            "marketing_features": self.marketing_features,
            "rating": self.rating,
            "review_count": self.review_count,
            "dietary_features": self.dietary_features,
            "caffeine_claim": self.caffeine_claim,
            "has_single_sku": self.has_single_sku,
        }


# CSV field names matching to_dict() keys
CSV_FIELDS = list(Product.__dataclass_fields__.keys())


@dataclass
class Category:
    """A product category from the megamenu."""

    name: str
    url: str
    count: int
    children: list[Category] = field(default_factory=list)

    @classmethod
    def from_megamenu(cls, node: dict) -> Category:
        """Create a Category tree from a megamenu API node."""
        children = [cls.from_megamenu(c) for c in node.get("children", [])]
        return cls(
            name=node.get("name", ""),
            url=node.get("url", ""),
            count=node.get("count", 0),
            children=children,
        )


@dataclass
class Location:
    """A Costco Business Center location."""

    id: str
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    latitude: float
    longitude: float
    phone: str = ""
    timezone: str = ""
    hours: list[dict] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    opening_date: str = ""
    distance_mi: float | None = None

    @classmethod
    def from_warehouse_api(cls, data: dict) -> Location:
        """Create a Location from the warehouse locator API response."""
        wh = data.get("warehouse", data)
        addr = wh.get("address", {})

        # Extract name (handles the nested locale format)
        name_list = wh.get("name", [])
        if isinstance(name_list, list) and name_list:
            name = name_list[0].get("value", "")
        elif isinstance(name_list, str):
            name = name_list
        else:
            name = ""

        # Extract service names
        services = []
        for svc in wh.get("services", []):
            svc_names = svc.get("name", [])
            if isinstance(svc_names, list) and svc_names:
                services.append(svc_names[0].get("value", ""))

        # Extract hours
        hours = []
        for h in wh.get("hours", []):
            title_list = h.get("title", [])
            title = title_list[0].get("value", "") if title_list else ""
            hours.append({
                "days": title,
                "open": h.get("open", ""),
                "close": h.get("close", ""),
            })

        return cls(
            id=wh.get("warehouseId", ""),
            name=name,
            address=addr.get("line1", ""),
            city=addr.get("city", ""),
            state=addr.get("territory", ""),
            zip_code=addr.get("postalCode", ""),
            latitude=float(addr.get("latitude", 0)),
            longitude=float(addr.get("longitude", 0)),
            phone=wh.get("phone", ""),
            timezone=wh.get("timeZone", ""),
            hours=hours,
            services=services,
            opening_date=wh.get("openingDate", ""),
        )
