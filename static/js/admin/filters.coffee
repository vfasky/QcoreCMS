define ['angular', 'admin/services'], (angular, services) ->
    'use strict'

    angular.module('admin.filters', ['admin.services'])
           .filter('interpolate', ['version', (version) ->
                (text) ->
                    String(text).replace(/\%VERSION\%/mg, version)

            ])

    return
