def categorize_indications(text):
    """
    Categorizes the indication based on keywords. If none are found,
    returns "Other".
    """
    indication_options = {
        "constipation": "Constipation",
        "incontinence": "Incontinence",
        "hirschsprung": "s/p Hirschprung",
        "anorectal malformation": "Anorectal malformation",
        "anal tear": "Anal Tear",
        "perianal tear": "Perianal Tear",
        "s/p perianal tear": "s/p Perianal Tear",  # ✅ Explicitly checks for "s/p perianal tear"
        "spina bifida": "Spina bifida"
    }
    
    text_lower = text.lower() if text != "N/A" else ""
    
    for key in indication_options.keys():
        if key in text_lower:
            return indication_options[key]  # ✅ Returns the correct formatted value
    
    return "Other"

