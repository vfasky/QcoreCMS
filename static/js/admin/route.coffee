define ['admin/app', 'admin/ctrls/category'], (app, categoryCtrl)->
    tplPath = '/static/js/admin/tpls'

    app.config ['$routeProvider', ($routeProvider, $http)->
        $http.defaults.headers.post;


        $routeProvider.when('/category',
            controller: "categoryCtrl",
            templateUrl: "#{tplPath}/category.html"
        )
    ]
    
    return
