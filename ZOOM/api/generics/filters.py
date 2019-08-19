from django_filters import BooleanFilter, CharFilter, Filter, FilterSet
from rest_framework import filters


class CommaSeparatedCharFilter(CharFilter):
    def filter(self, qs, value):

        if value:
            value = value.split(',')

        self.lookup_type = 'in'

        return super(CommaSeparatedCharFilter, self).filter(qs, value)


class StickyCharFilter(CharFilter):
    def filter(self, qs, value):
        qs._next_is_sticky()
        return super(StickyCharFilter, self).filter(qs, value)


class CommaSeparatedStickyCharFilter(CharFilter):
    def filter(self, qs, value):

        if value:
            value = value.split(',')

        self.lookup_type = 'in'
        qs._next_is_sticky()

        return super(CommaSeparatedStickyCharFilter, self).filter(qs, value)


class CommaSeparatedDateRangeFilter(Filter):
    def filter(self, qs, value):

        if value in ([], (), {}, None, ''):
            return qs

        values = value.split(',')

        return super(CommaSeparatedDateRangeFilter, self).filter(qs, values)
