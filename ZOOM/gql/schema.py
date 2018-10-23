import graphene

import gql.geodata.schema
import gql.metadata.schema


class Query(gql.geodata.schema.Query, gql.metadata.schema.Query,
            graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
