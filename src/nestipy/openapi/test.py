import json

from openapidocs.v3 import OpenAPI, Info, Response, Components, Schema, SecuritySchemeType
from openapidocs.v3 import PathItem, Operation, SecurityRequirement, ValueType, SecurityScheme
from openapidocs.v3 import Tag, HTTPSecurity, APIKeySecurity, ParameterLocation, Parameter
from openapidocs.common import Serializer
from dataclasses import asdict

open_api = OpenAPI(
    info=Info(
        title='Test openapi',
        description='This is the description',
        version='v1'
    ),
    paths={
        '/test': PathItem(
            summary='Test',
            get=Operation(
                responses={
                    '200': Response(description='Response successfully')
                },
                tags=['Test'],
                operation_id='test',
                security=[
                    SecurityRequirement(
                        name='Bearer',
                        value=['bearer']
                    )
                ],
                parameters=[
                    Parameter(
                        name='test',
                        in_=ParameterLocation.PATH
                    ),
                    Parameter(
                        name='test2',
                        in_=ParameterLocation.QUERY
                    ),
                    Parameter(
                        name='test3',
                        in_=ParameterLocation.HEADER
                    ),
                    Parameter(
                        name='test3',
                        in_=ParameterLocation.HEADER
                    )
                ]
            )
        )
    },
    components=Components(
        schemas={
            'User': Schema(
                type=ValueType.OBJECT,
                properties={
                    'id': Schema(
                        type=ValueType.INTEGER,
                        example=1,
                        default=1
                    ),
                    'name': Schema(
                        type=ValueType.STRING,
                        example="name",
                        default="name"
                    )
                }
            )
        },

        security_schemes={
            'bearer': HTTPSecurity(
                scheme='bearer',
            ),
            'apiKey': APIKeySecurity(
                name='X-API',
                in_=ParameterLocation.HEADER
            ),
            'basicAuth': HTTPSecurity(
                scheme='basicAuth',
                type=SecuritySchemeType.HTTP
            ),
        }
    ),
    tags=[
        Tag(name='Test'),
        Tag(name='Test2')
    ],
)

serializer = Serializer()
if __name__ == '__main__':
    print(serializer.to_json(open_api))
