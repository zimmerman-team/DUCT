import graphene

import gql.indicators


class Query(gql.indicators.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
