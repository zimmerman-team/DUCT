import graphene

from gql.query import metadata, geodata


class Query(geodata.Query, metadata.Query, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query)
