"""
Disposal guide content for each waste category.
This is plain reference data (not AI-generated at runtime) — deterministic
and reliable, which is exactly what you want for safety-relevant instructions.
Edit the text to add local (city/ward) specifics if you know them — that
personal-context detail is a nice touch for judges.
"""

DISPOSAL_GUIDE = {
    "wet_waste": {
        "display_name": "Wet Waste (Organic)",
        "disposal_method": "Collect separately in a green bin. Hand over to the "
                            "municipal wet-waste collection or compost at home/community level.",
        "recycling_tip": "Home composting turns wet waste into nutrient-rich soil in "
                          "4-6 weeks. Even a small balcony compost bin works.",
        "environmental_impact": "Wet waste mixed with dry waste is the #1 reason "
                                 "Indian landfills generate methane. Segregating it "
                                 "at source cuts landfill methane significantly.",
        "safety_precaution": "Empty food waste daily to avoid odor and pests.",
    },
    "dry_waste_paper": {
        "display_name": "Dry Waste — Paper/Cardboard",
        "disposal_method": "Keep dry and flat. Hand over to the dry-waste collector "
                            "or a local kabadiwala/scrap dealer.",
        "recycling_tip": "Flatten boxes to save space. Remove tape and staples "
                          "before recycling for a cleaner recycling stream.",
        "environmental_impact": "Recycling 1 tonne of paper saves roughly 17 trees "
                                 "and significant water compared to making new paper.",
        "safety_precaution": "Keep separate from wet/food waste — soggy paper "
                              "usually can't be recycled.",
    },
    "dry_waste_plastic": {
        "display_name": "Dry Waste — Plastic",
        "disposal_method": "Rinse and dry before disposal. Hand over to the "
                            "dry-waste collector or nearest recycling drop-off point.",
        "recycling_tip": "Check the recycling number (1-7) on the item — PET (1) "
                          "and HDPE (2) are the most widely recyclable in India.",
        "environmental_impact": "Plastic can take 400+ years to degrade in a landfill. "
                                 "Proper segregation is the main lever we have today.",
        "safety_precaution": "Never burn plastic waste — it releases toxic fumes.",
    },
    "dry_waste_glass": {
        "display_name": "Dry Waste — Glass",
        "disposal_method": "Wrap broken glass in paper/cloth and label it before "
                            "disposal to protect waste workers. Hand over to dry-waste collection.",
        "recycling_tip": "Glass is 100% recyclable indefinitely without quality loss — "
                          "keep bottles/jars intact where possible.",
        "environmental_impact": "Recycled glass uses ~40% less energy to produce than "
                                 "new glass from raw sand.",
        "safety_precaution": "Handle broken glass with care; always wrap before disposing.",
    },
    "dry_waste_metal": {
        "display_name": "Dry Waste — Metal",
        "disposal_method": "Hand over to the dry-waste collector or scrap dealer — "
                            "metal has high resale/recycling value in India.",
        "recycling_tip": "Cans and metal scrap are usually bought directly by "
                          "kabadiwalas, giving you a small return.",
        "environmental_impact": "Recycling aluminium uses about 95% less energy than "
                                 "producing it from raw ore.",
        "safety_precaution": "Watch for sharp edges on cans/tins.",
    },
    "dry_waste_other": {
        "display_name": "Dry Waste — Other/Mixed",
        "disposal_method": "General non-recyclable dry waste. Hand over to municipal "
                            "dry-waste collection for landfill/processing.",
        "recycling_tip": "Check if the item can be reused or repurposed before "
                          "discarding — many 'trash' items have a second life.",
        "environmental_impact": "This category typically ends up in landfill — "
                                 "minimizing it matters more than recycling it.",
        "safety_precaution": "Keep dry and separate from wet waste.",
    },
}

# Categories the current model does NOT cover — be upfront about this in your
# README under "Future Work". Trying to fake-classify these would be worse
# than admitting the scope limit.
NOT_YET_SUPPORTED = [
    "E-Waste (batteries, electronics)",
    "Hazardous waste (chemicals, paint)",
    "Biomedical waste",
]
