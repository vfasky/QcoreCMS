define(['angular', 'admin/services'], function (angular) {
    'use strict';

    /* Controllers */
    return angular.module('admin.controllers', ['admin.services'])
                  {% for v in menu['routes'] %}
                  .controller('{{v['name']}}', ['$scope', '$injector', function($scope, $injector) {
                        require(['{{v['js']}}'], function({{v['name']}}) {
                            $injector.invoke({{v['name']}}, this, {'$scope': $scope});
                        });
                  }]){% endfor %};
    });
