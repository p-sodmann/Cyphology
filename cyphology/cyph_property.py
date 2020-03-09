def create_property_string(properties):
    if properties:
        property_string = "{"
        first = True

        for field, value in properties.items():
            if not first:
                property_string += ", "
            else:
                first = False

            if isinstance(value, (int, float, bool)):
                property_string += f"{field}: {value}"
            else: 
                property_string += f"{field}: '{value}'"

        property_string += "}"
    else:
        property_string = ""
    
    return property_string