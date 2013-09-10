define ['jQuery', 'admin/app', 'admin/ctrls/category'], ($, app, categoryCtrl)->
    tplPath = '/static/js/admin/tpls'
    app.config ['$routeProvider', '$httpProvider', ($routeProvider, $httpProvider)->
        $httpProvider.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded'

        $httpProvider.defaults.transformRequest = (data) ->
            $.param data ? {}

        $httpProvider.defaults.transformResponse = (data, headersGetter) ->
            if headersGetter()['content-type'].indexOf('json') != -1
                json = angular.fromJson data
                if json.success
                    return json.data
                else
                    #todo error msg
                    console.log json.msg
                    return null
            else
                return data


        $routeProvider.when('/category',
            controller: "categoryCtrl",
            templateUrl: "#{tplPath}/category.html"
        )
    ]
    
    return
