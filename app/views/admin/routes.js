define(['angular', 'admin/app', 'jQuery'], function(angular, app, $) {
    'use strict';

    return app.config(['$routeProvider', '$httpProvider', 'MsgProvider', 
      function($routeProvider, $httpProvider, MsgProvider) {

        $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
        $httpProvider.defaults.transformRequest = function(data) {
          return $.param(data != null ? data : {});
        };
        $httpProvider.defaults.transformResponse = function(data, headersGetter) {
          var json;
          if (headersGetter()['content-type'].indexOf('json') !== -1) {
            json = angular.fromJson(data);
            if (json.success) {
              return json.data;
            } else {
              MsgProvider.$get().error(json.msg);
              return null;
            }
          } else {
            return data;
          }
        };

        {% for v in menu['routes'] %}
        $routeProvider.when('{{v['uri']}}', {
            templateUrl: '{{v['tpl']}}',
            controller: '{{v['name']}}'
        });
        {% endfor %}
    
        //TODO 首页
        //$routeProvider.otherwise({redirectTo: '/'});
    }]);

});
