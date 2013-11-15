define ['angular', 'admin/provider', 'admin/factory', 'admin/filters', 'admin/services', 'admin/directives', 'adminControllers', 'angularRoute', 'angularResource'],
    (angular, provider, factory, filters, services, directives, controllers) ->
        'use strict'

        angular.module('admin', [
                'ngRoute',
                'ngResource',
                'admin.provider',
                'admin.factory',
                'admin.controllers',
                'admin.filters',
                'admin.services',
                'admin.directives'
        ])
   
