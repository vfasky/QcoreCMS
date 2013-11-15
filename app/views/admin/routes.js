define(['angular', 'admin/app', 'jQuery'], function(angular, app, $) {
    'use strict';

    function getCookie(name) {
      var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
      return r ? r[1] : undefined;
    }

    return app.config(['$routeProvider', '$httpProvider', 'MsgProvider', 
      function($routeProvider, $httpProvider, MsgProvider) {
        var csrfToken = getCookie("_xsrf");
 
        $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
        $httpProvider.defaults.transformRequest = function(data) {
          data = data || {};
          data._xsrf = csrfToken;
          return $.param(data);
        };
        $httpProvider.defaults.transformResponse = function(data, headersGetter) {
          var json;
          if (headersGetter()['content-type'].indexOf('json') !== -1) {
            json = angular.fromJson(data);
            if (json.success) {
              return json.data;
            } else {
              //console.log(MsgProvider.$get())
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
