

def pair_lists_by_key_with_unmatched(list1, list2, key):
    # Create a lookup dictionary from list2
    lookup = {item[key]: item for item in list2}

    # Pair items from list1 with matching items from list2
    paired = []
    for item in list1:
        pair = (item, lookup.get(item[key], None))  # None if no match found
        paired.append(pair)

    return paired


