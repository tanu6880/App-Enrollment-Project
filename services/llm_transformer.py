import json
import httpx
from services.validator import validate_against_schema

def extract_arguments(response_json):
    """Always return dict from LLM response."""
    try:
        if "message" in response_json and "tool_calls" in response_json["message"]:
            arguments = response_json["message"]["tool_calls"][0]["function"]["arguments"]
            return _safe_load_json(arguments)

        if isinstance(response_json, list):
            msg = response_json[0].get("message", {})
            if "tool_calls" in msg:
                arguments = msg["tool_calls"][0]["function"]["arguments"]
                return _safe_load_json(arguments)

        if "message" in response_json and "content" in response_json["message"]:
            content_str = response_json["message"]["content"]
            parsed = _safe_load_json(content_str)
            if isinstance(parsed, dict) and "parameters" in parsed:
                return parsed["parameters"]
            return parsed
    except Exception as e:
        return {"error": f"Failed to extract arguments: {str(e)}"}

    return {"error": "No arguments found"}

def _safe_load_json(raw):
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    return raw

async def call_llm_with_retry(client, url, payload, schema, max_retries=5):
    for attempt in range(max_retries + 1):
        response = await client.post(url, json=payload)
        response_json = response.json()
        arguments = extract_arguments(response_json)
        if isinstance(arguments, list) and len(arguments) > 0:
            arguments = arguments[0]
        return arguments
        # is_valid, validated_args = validate_against_schema(arguments, schema)
        # if is_valid:
        #     return validated_args

        # if attempt < max_retries:
        #     payload["messages"].append({
        #         "role": "system",
        #         "content": f"Your last response did not match this schema. Please strictly output valid JSON conforming to: {json.dumps(schema)}"
        #     })
        #     continue
        # else:
        #     raise Exception(f"LLM failed to return valid JSON after {max_retries+1} attempts. Last error: {validated_args}")
