define ['admin/factory'], (app)->
    app.controller('system_me' , ['$scope', '$resource', '$http',
    ($scope, $resource, $http)->
        console.log 'me'
        return
    ])

    return
