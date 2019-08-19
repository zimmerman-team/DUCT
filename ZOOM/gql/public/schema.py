import graphene

import gql.geodata.schema
import gql.mapping.schema
import gql.metadata.schema
import gql.public.indicator.schema


class Query(gql.geodata.schema.Query, gql.metadata.schema.Query,
            gql.public.indicator.schema.Query, gql.mapping.schema.Query,
            graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
