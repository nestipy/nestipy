import re


class RouteParamsExtractor:
    @staticmethod
    def extract_params(route_path) -> dict:
        params = {}
        regex_pattern = r"{(\w+)(:\w+)?}"  # Pattern to match route parameters like {param_name:type}
        matches = re.findall(regex_pattern, route_path)
        for match in matches:
            param_name = match[0]
            param_type = (
                match[1][1] if match[1] else "str"
            )  # Default to str if type not specified
            params[param_name] = param_type
        return params
