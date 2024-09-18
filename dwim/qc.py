import logging
import json
import re
import jsonpath_ng


"""
How checking works...

The check dict is a dictionary of lists where the keys correspond to the 
toplevel keys in the data and each entry in the list is an expression
to evaluate.  If the value for the given key in data is a list, the
expressions will run on each of the items in the list, otherwise it will be
run directly on the value.

The syntax for expressions is a sub-/super-set of the mongodb query syntax.  
Each toplevel expression is a dict where the key can be one of:
* A json path that will be resolved to a value
* A logical operator:  $and, $or, $not
The value 


"""



def test_data(data: dict, checks: dict) -> list[str]:
    """run the specified checks against the given data, and return a list of things that failed."""

    results = {'general': []}    
    for section, tests in checks.items():
        if section not in data or len(data[section]) == 0:
            results['general'].append(f"Checks for section {section} cannot run because it doesn't exist in the data")
            continue
        
        data_to_test = []
        if isinstance(data[section], list):
            # there's a list of items...so we need to do it for all.
            for i, sect in enumerate(data[section]):
                data_to_test.append([sect, f"{section}-{i}"])
        else:
            # just do it for this set.
            data_to_test.append([data[section], section])

        for tdata, context in data_to_test:
            res = []
            for test in tests:
                r = run_expression(tdata, test)
                if r:
                    res.extend(*[x[1:] for x in r])
            results[context] = res

    results = {k: v for k, v in results.items() if v}

    return results






def run_expression(data: dict, expr: dict, keep_true=False) -> list:
    results = []
    if isinstance(expr, dict):        
        for k, v in expr.items():
            match k:
                case '$and':
                    and_val = True
                    children = []
                    for x in v:
                        r = run_expression(data, x, keep_true=True)
                        # check to see if any of the returned checks are true...
                        if any([x[0] == False for x in r]):
                            and_val = False
                        children.append([x[1] for x in r])
                    results.append([and_val,
                                    f"Expected at all of these expressions to be true, but none of them are",
                                    *children])

                case '$or':
                    children = []
                    or_val = False
                    for x in v:
                        r = run_expression(data, x, keep_true=True)
                        # check to see if any of the returned checks are true...
                        if all([x[0] for x in r]):
                            or_val = True
                        children.append([x[1] for x in r])
                    results.append([or_val,
                                    f"Expected at least one of these expressions to be true, but none of them are",
                                    *children])
                case _:
                    # resolve the key to a value
                    p = jsonpath_ng.parse(k)
                    value: list[jsonpath_ng.DatumInContext] = p.find(data)
                    if not value:
                        results.append([False,
                                        f"The json path {k} doesn't exist in the test data"])
                        continue
                    value = value[0].value
                    if isinstance(v, dict):
                        # this is an operator rather than a value. First key
                        # is the operator name, value is what's passed to the
                        # operator's function
                        k1 = list(v.keys())[0]
                        v1 = v[k1]
                        match k1:
                            case '$in':
                                # Assuming all values are constants of some sort
                                results.append([value in [convert(value, x) for x in v1],
                                                f"Expected {k} to be one of these values {v1}, but it is {value}"])
                            case '$nin':
                                # Assume all values are constants                                
                                results.append([value not in [convert(value, x) for x in v1],
                                                f"Expected {k} not to be one of these values {v1}, but it is {value}"])
                            case '$regex':
                                return re.search(str(v1), value)
                            case '$eq':
                                results.append([value == convert(value, v1),
                                                f"Expected {k1} to be {v1} but got {value}"])
                            case '$ne':
                                results.append([value != convert(value, v1),
                                                f"Expected {k1} to not be {v1} but it is"])
                            case '$gt':
                                results.append([value > convert(value, v1),
                                                f"Expected {k1} to have a value greater than {v1}, but it is {value}"])
                            case '$lt':
                                results.append([value < convert(value, v1),
                                                f"Expected {k1} to be less than {v1}, but it is {value}"])
                            case '$gte':
                                results.append([value >= convert(value, v1),
                                                f"Expected {k1} to be greater than or equal to {v1}, but it is {value}"])
                            case '$lte':
                                results.append([value <= convert(value, v1),
                                                f"Expected {k1} to be less than or equal to {v1}, but it is {value}"])
                            case '$within':
                                ...
                    else:
                        # not a dict, so must be a value
                        results.append([value == v,
                                        f"Expected {k} to be {v}, but it is {value}"])
                        
    else:
        # assume that this is a simple equality
        print(f"WTF: {expr}")

    # filter the results:  only return items where the expression failed.
    if keep_true:
        return results
    else:
        return [x for x in results if not x[0]]
    



def convert(old, new):
    """Convert the new data into the same type as the old data"""
    return type(old)(new)



if __name__ == "__main__":
    import argparse
    import yaml
    from .probulator import Probulator
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help="File to qc")
    args = parser.parse_args()
    p = Probulator()

    print(yaml.safe_dump(p.get_metadata(args.file), default_flow_style=False))
    metadata = p.get_metadata(args.file)
    
    qc = {'format': [
              {'format_name': 'wav'},
          ],
          'audio': [
              {'bits_per_sample': 24},
              {'sample_rate': 96000},
              {'codec_name': 'pcm_s24le'},
              {'channels': {'$in': [2, 1]}}
          ],
          'video': [
              {'$or': [{'width': 640, 'height': 480},
                       {'width': 480, 'height': 360}]},
              {'$and': [{'width': 717, 'height': 480},
                        {'width': 718, 'height': 480}]}


          ]
    }
    print(yaml.safe_dump(test_data(metadata, qc)))