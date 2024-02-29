from typing import Annotated
import re

from litestar.datastructures import UploadFile
from fastapi.datastructures import UploadFile


def get_annotation_metadata(annotation):
    if isinstance(annotation, Annotated):
        # Get the string representation of the annotation
        annotation_str = str(annotation)

        # Use regular expression to extract the metadata
        match = re.search(r"'(.*?)'", annotation_str)
        if match:
            return match.group(1)
    return None


# Define an annotated variable
my_variable: Annotated[float, 'some metadata'] = 10.5

# Extract metadata associated with the annotated variable
metadata = get_annotation_metadata(my_variable)
print(metadata)  # Output: some metadata
