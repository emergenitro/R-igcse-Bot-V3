import nextcord as discord

def add_fields(embed_obj, fields_dict):
    for field_name, field_value in fields_dict.items():
        embed_obj.add_field(name=field_name, value=field_value, inline=False)


def add_fields_for_functions(before, after, list_to_add, fields_dict):
    for attr_name, attr_value in list_to_add:
        before_value = getattr(before, attr_value)
        after_value = getattr(after, attr_value)
        if before_value != after_value:
            fields_dict[attr_name] = f"Changed from `{before_value}` to `{after_value}`"
