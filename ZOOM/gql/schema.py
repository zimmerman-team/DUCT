import graphene

from gql import geodata, metadata


class Query(geodata.Query, metadata.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
