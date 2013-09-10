define ['admin/app'], (app)->
    app.controller('categoryCtrl' , ['$scope', '$resource', ($scope, $resource)->
        actions =
            mulit: method: 'GET', isArray: true

        Catgory = $resource('/api/category', {}, actions)

        catgory = Catgory.mulit (data)->
            console.log data

        return
    ])
    return
