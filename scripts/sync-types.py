#!/usr/bin/env python3
"""
Sync types between backend (Python/Pydantic) and frontend (TypeScript)
This script extracts Pydantic models from backend and generates TypeScript interfaces
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

# Add backend to path for importing
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


def get_openapi_schema() -> Dict[str, Any]:
    """Get OpenAPI schema from FastAPI application"""
    try:
        # Import the FastAPI app
        from main import app
        
        # Get the OpenAPI schema
        return app.openapi()
    except ImportError as e:
        print(f"Error importing FastAPI app: {e}")
        print("Make sure you're running this from the project root")
        sys.exit(1)


def generate_typescript_types(schema: Dict[str, Any], output_path: Path):
    """Generate TypeScript types from OpenAPI schema"""
    
    # Save schema to temp file
    schema_file = Path("temp_openapi_schema.json")
    with open(schema_file, "w") as f:
        json.dump(schema, f, indent=2)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate TypeScript types using openapi-typescript-codegen or similar
    try:
        # Using openapi-typescript (install with: npm install -D openapi-typescript)
        result = subprocess.run(
            [
                "npx",
                "openapi-typescript",
                str(schema_file),
                "--output",
                str(output_path),
            ],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error generating TypeScript types: {result.stderr}")
            # Fallback to manual generation
            generate_manual_types(schema, output_path)
    except FileNotFoundError:
        print("openapi-typescript not found, generating types manually")
        generate_manual_types(schema, output_path)
    finally:
        # Clean up temp file
        if schema_file.exists():
            schema_file.unlink()


def generate_manual_types(schema: Dict[str, Any], output_path: Path):
    """Manually generate TypeScript types from OpenAPI schema"""
    
    types_content = """/**
 * Auto-generated TypeScript types from FastAPI OpenAPI schema
 * Generated at: {timestamp}
 * DO NOT EDIT MANUALLY - Run 'npm run sync-types' to regenerate
 */

""".format(timestamp=__import__('datetime').datetime.now().isoformat())
    
    # Extract schemas from components
    if "components" in schema and "schemas" in schema["components"]:
        schemas = schema["components"]["schemas"]
        
        for schema_name, schema_def in schemas.items():
            types_content += convert_schema_to_typescript(schema_name, schema_def)
            types_content += "\n\n"
    
    # Write the generated types
    with open(output_path, "w") as f:
        f.write(types_content)
    
    print(f"TypeScript types generated at: {output_path}")


def convert_schema_to_typescript(name: str, schema: Dict[str, Any]) -> str:
    """Convert a single schema to TypeScript interface"""
    
    if schema.get("type") == "object" or "properties" in schema:
        return generate_interface(name, schema)
    elif "enum" in schema:
        return generate_enum(name, schema)
    elif "allOf" in schema or "oneOf" in schema or "anyOf" in schema:
        return generate_union_type(name, schema)
    else:
        return f"export type {name} = {python_to_typescript_type(schema)};"


def generate_interface(name: str, schema: Dict[str, Any]) -> str:
    """Generate TypeScript interface from object schema"""
    
    interface = f"export interface {name} {{\n"
    
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    
    for prop_name, prop_schema in properties.items():
        # Check if property is optional
        optional = "?" if prop_name not in required else ""
        
        # Convert property type
        ts_type = python_to_typescript_type(prop_schema)
        
        # Add description as comment if available
        description = prop_schema.get("description", "")
        if description:
            interface += f"  /** {description} */\n"
        
        interface += f"  {prop_name}{optional}: {ts_type};\n"
    
    interface += "}"
    
    return interface


def generate_enum(name: str, schema: Dict[str, Any]) -> str:
    """Generate TypeScript enum from enum schema"""
    
    enum_values = schema.get("enum", [])
    
    # Use const enum for better performance
    enum_def = f"export const enum {name} {{\n"
    
    for value in enum_values:
        # Convert to valid enum key
        key = str(value).upper().replace(" ", "_").replace("-", "_")
        
        if isinstance(value, str):
            enum_def += f'  {key} = "{value}",\n'
        else:
            enum_def += f"  {key} = {value},\n"
    
    enum_def += "}"
    
    return enum_def


def generate_union_type(name: str, schema: Dict[str, Any]) -> str:
    """Generate TypeScript union type"""
    
    if "allOf" in schema:
        # Intersection type
        types = [python_to_typescript_type(s) for s in schema["allOf"]]
        return f"export type {name} = {' & '.join(types)};"
    elif "oneOf" in schema or "anyOf" in schema:
        # Union type
        schemas = schema.get("oneOf", schema.get("anyOf", []))
        types = [python_to_typescript_type(s) for s in schemas]
        return f"export type {name} = {' | '.join(types)};"
    
    return f"export type {name} = unknown;"


def python_to_typescript_type(schema: Dict[str, Any]) -> str:
    """Convert Python/JSON Schema type to TypeScript type"""
    
    # Handle references
    if "$ref" in schema:
        ref = schema["$ref"]
        # Extract type name from reference (e.g., "#/components/schemas/User" -> "User")
        return ref.split("/")[-1]
    
    type_mapping = {
        "string": "string",
        "integer": "number",
        "number": "number",
        "boolean": "boolean",
        "array": "unknown[]",  # Will be refined below
        "object": "Record<string, unknown>",  # Will be refined below
        "null": "null",
    }
    
    schema_type = schema.get("type", "unknown")
    
    # Handle arrays with items
    if schema_type == "array" and "items" in schema:
        item_type = python_to_typescript_type(schema["items"])
        return f"{item_type}[]"
    
    # Handle objects with properties
    if schema_type == "object" and "properties" in schema:
        # Inline object type
        props = []
        for prop_name, prop_schema in schema["properties"].items():
            required = prop_name in schema.get("required", [])
            optional = "?" if not required else ""
            props.append(f"{prop_name}{optional}: {python_to_typescript_type(prop_schema)}")
        
        return "{ " + "; ".join(props) + " }"
    
    # Handle nullable types
    if schema.get("nullable", False):
        base_type = type_mapping.get(schema_type, "unknown")
        return f"{base_type} | null"
    
    return type_mapping.get(schema_type, "unknown")


def main():
    """Main function"""
    
    print("Syncing types between backend and frontend...")
    
    # Get OpenAPI schema
    schema = get_openapi_schema()
    
    # Define output path
    output_path = Path("frontend/types/generated/backend-types.ts")
    
    # Generate TypeScript types
    generate_typescript_types(schema, output_path)
    
    # Also save the raw schema for reference
    schema_path = Path("frontend/types/generated/openapi-schema.json")
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    with open(schema_path, "w") as f:
        json.dump(schema, f, indent=2)
    
    print(f"OpenAPI schema saved at: {schema_path}")
    print("Type sync completed successfully!")


if __name__ == "__main__":
    main()