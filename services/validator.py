import json
import jsonschema

def validate_against_schema(arguments, schema):
    try:
        if isinstance(arguments, str):
            arguments = json.loads(arguments)
        jsonschema.validate(instance=arguments, schema=schema)
        return True, arguments
    except jsonschema.exceptions.ValidationError as e:
        return False, f"Schema validation error: {e.message}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
