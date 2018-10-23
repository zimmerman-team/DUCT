import graphene

import gql.geodata.schema
import gql.metadata.schema
import gql.metadata.mutation


class Query(gql.geodata.schema.Query, gql.metadata.schema.Query,
            graphene.ObjectType):
    pass


class Mutation(gql.metadata.mutation.Mutation,
               graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
