
## Sample GraphQL queries.
-------

* __Query for Indicator.__
```
# Query:
{
  allIndicators {
    edges {
      node {
        id
        entryId
        name
        fileSource {
          id
          entryId
          name
        }
      }
    }
  }
}
 
# Query Result:
{
  "data": {
    "allIndicators": {
      "edges": [
        {
          "node": {
            "id": "SW5kaWNhdG9yTm9kZTox",
            "entryId": "1",
            "name": " People living with HIV",
            "fileSource": {
              "id": "RmlsZVNvdXJjZU5vZGU6MQ==",
              "entryId": "1",
              "name": "The one"
            }
          }
        },
        {
          "node": {
            "id": "SW5kaWNhdG9yTm9kZToy",
            "entryId": "2",
            "name": "People living with HIV",
            "fileSource": {
              "id": "RmlsZVNvdXJjZU5vZGU6MQ==",
              "entryId": "1",
              "name": "The one"
            }
          }
        }
      ]
    }
  }
}

```

* __Query for Mapping.__
```
# Query
{
  allMappings {
    edges {
      node {
        id
        entryId
        file {
          id
          entryId
          title
        }
        data
      }
    }
  }
}
 
# Query Result
{
  "data": {
    "allMappings": {
      "edges": [
        {
          "node": {
            "id": "TWFwcGluZ05vZGU6MTE=",
            "entryId": "11",
            "file": {
              "id": "RmlsZU5vZGU6OQ==",
              "entryId": "9",
              "title": "test"
            },
            "data": "{\"id\": \"9\", \"dict\": {\"date\": [\"Time Period\"], \"value\": [\"Data Value\"], \"comment\": [\"Source\"], \"filters\": [\"Subgroup\"], \"headings\": {\"Subgroup\": \"Subgroup\"}, \"indicator\": [\"Indicator\"], \"geolocation\": [\"Area\"], \"value_format\": [\"Unit\"]}}"
          }
        }
      ]
    }
  }
}
```
* __Query for FileSource.__
```
# Query:
{
  allFileSources {
    edges {
      node {
        id
        entryId
        name
      }
    }
  }
}
 
# Query Result:
{
  "data": {
    "allFileSources": {
      "edges": [
        {
          "node": {
            "id": "RmlsZVNvdXJjZU5vZGU6MQ==",
            "entryId": "1",
            "name": "The one"
          }
        }
      ]
    }
  }
}
```
* __Query for File.__
```
# Query:
{
  allFiles {
    edges {
      node {
        id
        entryId
        title
        description
        organisation
        maintainer
        dateOfDataset
        methodology
        defineMethodology
        comments
        accessibility
        dataQuality
        fileTypes
        fileHeadingList
        dataModelHeading
      }
    }
  }
}
 
# Query Result
{
  "data": {
    "allFiles": {
      "edges": [
        {
          "node": {
            "id": "RmlsZU5vZGU6OQ==",
            "entryId": "9",
            "title": "test",
            "description": "test",
            "organisation": "test",
            "maintainer": "test",
            "dateOfDataset": "2009-01-01",
            "methodology": "test",
            "defineMethodology": "tets",
            "comments": "test",
            "accessibility": "P",
            "dataQuality": "test",
            "fileTypes": "CSV",
            "fileHeadingList": "{\"0\": \"Indicator\", \"1\": \"Unit\", \"2\": \"Subgroup\", \"3\": \"Area\", \"4\": \"Area ID\", \"5\": \"Time Period\", \"6\": \"Source\", \"7\": \"Data Value\", \"8\": \"Footnotes\"}",
            "dataModelHeading": "{\"0\": \"indicator\", \"1\": \"date\", \"2\": \"filters\", \"3\": \"geolocation\", \"4\": \"comment\", \"5\": \"value_format\", \"6\": \"value\"}"
          }
        }
      ]
    }
  }
}
```
* __Query for Aggregation group by Indicator Name.__
```
{
  datapointsAggregation(groupBy: ["indicatorName"], orderBy: ["indicatorName"], aggregation: ["Sum(value)"]) {
    indicatorName
    value
  }
}

# Query Result:
{
  "data": {
    "datapointsAggregation": [
      {
        "indicatorName": " People living with HIV",
        "value": 29104
      },
      {
        "indicatorName": "People living with HIV",
        "value": 146835
      }
    ]
  }
}
```
* __Query for Aggregation group by Indicator Name & Geolocation Tag.__
```
{
  datapointsAggregation(groupBy: ["indicatorName", "geolocationTag"], orderBy: ["geolocationTag"], aggregation: ["Sum(value)"]) {
    indicatorName
    geolocationTag
    value
  }
}

# Query Result:
{
  "data": {
    "datapointsAggregation": [
      {
        "indicatorName": " People living with HIV",
        "geolocationTag": "lesotho",
        "value": 29104
      },
      {
        "indicatorName": "People living with HIV",
        "geolocationTag": "mongolia",
        "value": 5
      }
    ]
  }
}
```
* __Query for Aggregation group by Indicator Name, Geolocation Tag & Date. And 
order by Date descending.__
```
# Query:
{
  datapointsAggregation(groupBy: ["indicatorName", "geolocationTag", "date"], orderBy: ["-date"], aggregation: ["Sum(value)"]) {
    indicatorName
    geolocationTag
    date
    value
  }
}

# Query Result:
{
  "data": {
    "datapointsAggregation": [
      {
        "indicatorName": " People living with HIV",
        "geolocationTag": "lesotho",
        "date": "2015",
        "value": 29104
      },
      {
        "indicatorName": "People living with HIV",
        "geolocationTag": "mongolia",
        "date": "2001",
        "value": 2
      },
      {
        "indicatorName": "People living with HIV",
        "geolocationTag": "mongolia",
        "date": "1990",
        "value": 0
      }
    ]
  }
}
```
* __Query for Aggregation group by Indicator Name, Geolocation Tag & Date, 
Order by Date descending, Filter by Geolocation Tag.__
```
# Query:
{
  datapointsAggregation(groupBy: ["indicatorName", "geolocationTag", "date"], orderBy: ["-date"], aggregation: ["Sum(value)"], geolocationTag_In: ["lesotho"]) {
    indicatorName
    geolocationTag
    date
    value
  }
}
 
# Query Result:
{
  "data": {
    "datapointsAggregation": [
      {
        "indicatorName": " People living with HIV",
        "geolocationTag": "lesotho",
        "date": "2015",
        "value": 29104
      },
      {
        "indicatorName": "People living with HIV",
        "geolocationTag": "lesotho",
        "date": "1998",
        "value": 31830
      },
      {
        "indicatorName": "People living with HIV",
        "geolocationTag": "lesotho",
        "date": "1997",
        "value": 29224
      },
      {
        "indicatorName": "People living with HIV",
        "geolocationTag": "lesotho",
        "date": "1996",
        "value": 26034
      },
      {
        "indicatorName": "People living with HIV",
        "geolocationTag": "lesotho",
        "date": "1995",
        "value": 21894
      },
      {
        "indicatorName": "People living with HIV",
        "geolocationTag": "lesotho",
        "date": "1994",
        "value": 16954
      },
      {
        "indicatorName": "People living with HIV",
        "geolocationTag": "lesotho",
        "date": "1993",
        "value": 12261
      },
      {
        "indicatorName": "People living with HIV",
        "geolocationTag": "lesotho",
        "date": "1992",
        "value": 8633
      }
    ]
  }
}
```

* __Aggregation group by Indicator Name, Geolocation Tag, FilterName & Date,
 Order by Indicator Name, Filter by Multiple filters.__
 
```
# Query:{
  datapointsAggregation(
    groupBy: ["indicatorName", "geolocationTag", "valueFormatType", "filterName", "date"],
    orderBy: ["indicatorName"],
    aggregation: ["Sum(value)"],
        filterName_And:["females", "15-19"],
  ){
    indicatorName
    value
    valueFormatType
    geolocationTag
    filterName
    date
  }
}
 
#Query Result:
{
  "data": {
    "datapointsAggregation": [
      {
        "indicatorName": "demand for family planning satisfied by modern methods",
        "value": 68.4,
        "valueFormatType": "percent",
        "geolocationTag": "bangladesh",
        "filterName": "females, 15-19",
        "date": "2014"
      },
      {
        "indicatorName": "demand for family planning satisfied by modern methods",
        "value": 35.6,
        "valueFormatType": "percent",
        "geolocationTag": "benin",
        "filterName": "females, 15-19",
        "date": "2012"
      },
      {
        "indicatorName": "demand for family planning satisfied by modern methods",
        "value": 12,
        "valueFormatType": "percent",
        "geolocationTag": "tajikistan",
        "filterName": "females, 15-19",
        "date": "2012"
      },
      {
        "indicatorName": "demand for family planning satisfied by modern methods",
        "value": 97.8,
        "valueFormatType": "percent",
        "geolocationTag": "thailand",
        "filterName": "females, 15-19",
        "date": "2016"
      },
      {
        "indicatorName": "demand for family planning satisfied by modern methods",
        "value": 41.5,
        "valueFormatType": "percent",
        "geolocationTag": "togo",
        "filterName": "females, 15-19",
        "date": "2014"
      },
      {
        "indicatorName": "demand for family planning satisfied by modern methods",
        "value": 40.6,
        "valueFormatType": "percent",
        "geolocationTag": "united republic of tanzania",
        "filterName": "females, 15-19",
        "date": "2016"
      },
      {
        "indicatorName": "demand for family planning satisfied by modern methods",
        "value": 71.7,
        "valueFormatType": "percent",
        "geolocationTag": "zimbabwe",
        "filterName": "females, 15-19",
        "date": "2015"
      }
    ]
  }
}
```

## Sample GraphQL mutations.
-------
* __Mutation for Indicator.__
```
# Query:
mutation indicator($input: IndicatorMutationInput!) {
  indicator(input: $input) {
    name
    description
    fileSource
  }
}
 
# Query Variable:
{"input": {
  "name": "test.name.1",
  "description": "test.description.1",
  "fileSource": "2"
}}
```
Note: FileSource should be value of the field of entryId of the model 
FileSource and the data for this table also automatically comes from the 
Mapping and maybe does not need to have a mutation module on this table.  


* __Mutation for Mapping.__
```
# Mutation:
mutation mapping($input: MappingMutationInput!) {
  mapping(input: $input) {
    id
    file
    data
  }
}
 
# Mutation Variables:
{"input": {
  "file": "9",
  "data": "{\"id\": \"9\", \"dict\": {\"indicator\": [\"Indicator\"], \"value_format\": [\"Unit\"],  \"geolocation\": [\"Area\"], \"value\": [\"Data Value\"], \"date\": [\"Time Period\"], \"comment\": [\"Source\"], \"filters\": [\"Subgroup\"], \"headings\": {\"Subgroup\": \"Subgroup\"}}}"
}}
```
Note: the fileSource value  should be id of the FileSource.

* __Mutation for FileSource.__
```
# Mutation:
mutation fileSource($input: FileSourceMutationInput!) {
  fileSource(input: $input) {
    name
  }
}
 
# Mutation Variable:
{"input": {
  "name": "The one"
}}
```
* __Mutation for File.__
```
# Mutation:
mutation file($input: FileMutationInput!) {
  file(input: $input) {
    id
    title
    description
    containsSubnationalData
    organisation
    maintainer
    dateOfDataset
    methodology
    defineMethodology
    updateFrequency
    comments
    accessibility
    dataQuality
    numberOfRows
    fileTypes
    location
    source
    file
  }
}
 
# Mutation Variable:
{"input": {
  "title": "test",
  "description": "test",
  "containsSubnationalData": true,
  "organisation": "test",
  "maintainer": "test",
  "dateOfDataset": "2009-01-01",
  "methodology": "test",
  "defineMethodology": "tets",
  "updateFrequency": "test",
  "comments": "test",
  "accessibility": "p",
  "dataQuality": "test",
  "numberOfRows": 1,
  "fileTypes": "csv",
  "location": "1",
  "source": "1",
  "file": "datasets/AIDSinfotest.csv"
}}
```